-- The "Next upgrade" window (gear progression spec 4.7): a Journal tab, `!upgrade`, and a reminder at login.
-- SpireUpgrade.lines(view) is pure; SpireUpgrade.viewFor(player) gathers the view from the game.
SpireUpgrade = SpireUpgrade or {}

local GRADE_WHERE = {
	rough = "any Floor 1 hunting ground",
	cut = "Wolf Copse and harder grounds",
	flawless = "Grey Alpha, Bandit Captain, Old Watchtower",
}

local function nextTier(view)
	local w = view.weapon
	if not w or w.shop or w.tier >= SpireGearData.MAX_TIER then
		return nil
	end
	local cost = SpireGearData.TIER_COST[w.tier + 1]
	local id = SpireGearData.tokens[w.floor][cost.grade]
	return { tier = w.tier + 1, grade = cost.grade, gold = cost.gold * w.floor, names = SpireGearData.tokenNames[id][2],
		have = (view.shards or {})[cost.grade] or 0 }
end

local function firstUndone(view, ready)
	for _, s in ipairs(view.steps or {}) do
		if not s.done and (not ready or (s.level or 0) <= view.level) then
			return s
		end
	end
end

-- Pure: the one sentence at the top of the window
function SpireUpgrade.nextLine(view)
	for _, s in ipairs(view.steps or {}) do
		if s.key == "weapon" and not s.done and view.level < (s.level or 10) then
			return string.format("Reach level %d, then %s.", s.level or 10, s.where)
		end
	end
	if view.style and view.style.choiceReady and view.style.options then
		return "Next: choose " .. table.concat(view.style.options, " or ") .. ". Say !style to read both."
	end
	local step = firstUndone(view, true)
	if step then
		return "Next: " .. step.where .. "."
	end
	local t = nextTier(view)
	if t then
		local need = SpireGearData.SHARDS_PER_TIER - t.have
		if need <= 0 then
			return string.format("Next: take %d %s and %d gold to Weaponsmith Garrick: tier %d.", SpireGearData.SHARDS_PER_TIER, t.names, t.gold, t.tier)
		end
		return string.format("Next: collect %d more %s for tier %d (%s).", need, t.names, t.tier, GRADE_WHERE[t.grade])
	end
	local later = firstUndone(view, false)
	if later then
		return string.format("Next: from level %d, %s.", later.level or 0, later.where)
	end
	return "Floor 1 is done. Next: Floor 2's new weapons, or keep raising this one's familiarity."
end

-- Pure: the familiarity bar (P10, FLOOR1_REVIEW.md F1-41): "FAMILIARITY [######----] 60% to level 4"
function SpireUpgrade.famBar(fam, pct)
	if not pct then
		return "FAMILIARITY [##########] 10/10, mastered"
	end
	local filled = math.floor(pct / 10)
	return string.format("FAMILIARITY [%s%s] %d%% to level %d (kills with this weapon raise it)",
		string.rep("#", filled), string.rep("-", 10 - filled), pct, fam + 1)
end

-- Pure: every line of the window
function SpireUpgrade.lines(view)
	local L = { SpireUpgrade.nextLine(view), "" }
	local w = view.weapon
	if w then
		local extra = w.shop and "  (shop starter gear: cannot be upgraded)" or
			string.format("  tier %d/%d  familiarity %d/10  %+d%% damage%s", w.tier, SpireGearData.MAX_TIER, w.fam,
				math.floor(((w.power or 1) - 1) * 100 + 0.5), w.awakened and "  awakened" or "")
		table.insert(L, "WEAPON  " .. w.name .. extra)
		if not w.shop then
			table.insert(L, SpireUpgrade.famBar(w.fam, w.famPct))
		end
	else
		table.insert(L, "WEAPON  none yet: Captain Dorrow gives one at level 10")
	end
	local a = view.armour
	table.insert(L, a and string.format("ARMOUR  %s  tier %d/%d", a.name, a.tier, SpireGearData.MAX_TIER)
		or "ARMOUR  none yet: Iron for the Stair (Hunter Brannoch) makes yours")
	local sh = view.shards or {}
	table.insert(L, string.format("SHARDS  rough %d, cut %d, flawless %d", sh.rough or 0, sh.cut or 0, sh.flawless or 0))
	table.insert(L, "")
	table.insert(L, "FLOOR 1 PATH")
	local marked = false
	for _, s in ipairs(view.steps or {}) do
		table.insert(L, (s.done and "[x] " or "[ ] ") .. s.text)
		if not s.done and not marked then
			marked = true
			table.insert(L, "      " .. s.where)
		end
	end
	table.insert(L, "")
	local st = view.style
	if st then
		table.insert(L, string.format("STYLE  %s %d/10", st.stageName, st.level))
		if st.choiceReady and st.options then
			table.insert(L, "      choice ready: " .. table.concat(st.options, " or ") .. " (say !style)")
		elseif st.stanceOpen then
			table.insert(L, "      stance: " .. (st.stance or "none") .. " (try a path free until Mastery 10: say !style)")
		end
	end
	if #(view.trophies or {}) == 0 then
		table.insert(L, "TROPHIES  none found yet")
	else
		table.insert(L, "TROPHIES  " .. table.concat(view.trophies, ", "))
	end
	return L
end

-- For tests and previews: the Floor 1 steps, none done
function SpireUpgrade.sampleSteps()
	local out = {}
	for _, s in ipairs(SpireClimb.FLOOR1) do
		table.insert(out, { key = s.key, level = s.level, text = s.text, where = s.where, done = false })
	end
	return out
end

-- ---------------------------------------------------------------- from the game
function SpireUpgrade.viewFor(player)
	local view = { level = player:getLevel(), steps = {}, trophies = {} }
	local item = SpireGear.mainWeapon(player) or SpireGear.floorWeapon(player, 1)
	local s = item and SpireGear.state(item)
	if s then
		view.weapon = { name = item:getName(), floor = s.floor, tier = s.tier, fam = s.fam, awakened = s.awakened,
			shop = s.shop, power = SpireGear.power(s), famPct = not s.shop and SpireGear.famProgress(s.famPoints, s.floor) or nil }
	end
	for _, it in ipairs(SpireGear.carried(player)) do
		local d = SpireGear.defOf(it)
		if d and d.kind == "armour" and not view.armour then
			view.armour = { name = it:getName(), tier = SpireGear.state(it).tier }
		end
	end
	local floor = view.weapon and view.weapon.floor or 1
	view.shards = {}
	for grade, id in pairs(SpireGearData.tokens[floor]) do
		view.shards[grade] = player:getItemCount(id)
	end
	for _, st in ipairs(SpireClimb.FLOOR1) do
		table.insert(view.steps, { key = st.key, level = st.level, text = st.text, where = st.where, done = st.done(player) })
	end
	local v = SpireStyle.get(player)
	view.style = { stageName = SpireStyle.stageName(v), level = v.level, choiceReady = v.choiceReady,
		stance = v.stance and SpireStyle.name(v.voc, v.stance) or nil,
		stanceOpen = not v.path and not v.choiceReady and SpireStyle.canStance(v.voc, v.points, nil, (SpireGearData.style[v.voc] or { paths = { {} } }).paths[1].key) }
	if v.options then
		view.style.options = {}
		for _, o in ipairs(v.options) do
			table.insert(view.style.options, o.name)
		end
	end
	if SpireTrophies and SpireTrophies.foundNames then
		view.trophies = SpireTrophies.foundNames(player)
	end
	return view
end
