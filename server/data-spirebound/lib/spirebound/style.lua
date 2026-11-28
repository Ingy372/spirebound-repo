-- Style tree (gear progression spec 4.2): the character's permanent mastery, filled by raw monster experience.
-- Stage 1 = <Class> Mastery 1-10, then a path (2 choices) 1-10, then a final style (2 choices) 1-10.
-- Points keep counting while a choice waits; they count once the choice is made.
-- Stored on the character: kv "spirebound" keys style_points, style_path, style_final, style_respec_at.
SpireStyle = SpireStyle or {}

local P = SpireGearData.STYLE_POINTS

-- Pure: stage (1-3) and level (0-10) for raw points, ignoring choices
function SpireStyle.levelOf(points)
	local reached = 0
	for i, need in ipairs(P) do
		if (points or 0) >= need then
			reached = i
		end
	end
	if reached == 0 then
		return 1, 0
	end
	return math.floor((reached - 1) / 10) + 1, (reached - 1) % 10 + 1
end

local function tree(voc)
	return SpireGearData.style[voc]
end

local function findPath(voc, key)
	local t = tree(voc)
	for _, p in ipairs(t and t.paths or {}) do
		if p.key == key then
			return p
		end
	end
end

-- ST1 (style trees v2, Jay 2026-11-28, spec 9.2): the free stance at Mastery 5 is gone. Each option is tried in a sealed
-- Path Trial at the class trainer instead, and the choice window opens only after both have been tried.
SpireStyle.STANCE_LEVEL = 5 -- (kept for older readers; no stance is offered any more)
function SpireStyle.canStance()
	return false, "The free stance is gone: your class trainer's Path Trial lets you try each path before you choose."
end

-- ctx (optional): { arrived = the character has reached Floor 2 (the path choice comes then, spec 8.1),
--   trials = { [key] = true } options whose Path Trial is done }
-- Pure: what the character's style looks like with its choices
function SpireStyle.view(voc, points, path, final, _stance, ctx)
	ctx = ctx or {}
	local s, l = SpireStyle.levelOf(points)
	local v = { voc = voc, points = points or 0, path = path, final = final, choiceReady = false }
	if not path then
		if s > 1 then
			s, l = 1, 10
		end
		v.choiceReady = ctx.arrived == true -- the first choice comes on arrival on Floor 2, whatever the Mastery
	elseif not final then
		if s == 3 then
			s, l, v.choiceReady = 2, 10, true
		elseif s == 2 and l == 10 then
			v.choiceReady = true
		end
	end
	v.stage, v.level = s, l
	local t = tree(voc)
	if v.choiceReady and t then
		if not path then
			v.options = t.paths
		else
			local fp = findPath(voc, path)
			v.options = fp and fp.finals or nil
			v.choiceReady = v.options ~= nil
		end
	end
	v.trials = ctx.trials or {}
	return v
end

-- Pure: may this choice be made now? -> ok, message
function SpireStyle.canChoose(voc, points, path, final, key, ctx)
	local v = SpireStyle.view(voc, points, path, final, nil, ctx)
	if final then
		return false, "Your style is complete: there is nothing left to choose."
	end
	if not v.choiceReady then
		if not path then
			return false, "Your path is chosen when you reach Floor 2: your class trainer will send for you."
		end
		return false, "Your next choice comes when this stage reaches level 10."
	end
	local found
	for _, o in ipairs(v.options or {}) do
		if o.key == key then
			found = o
		end
	end
	if not found then
		return false, "That is not one of your choices. Say !style to see them."
	end
	if ctx then -- (pure tests pass no ctx: the trial rule is checked by the game path)
		for _, o in ipairs(v.options) do
			if not v.trials[o.key] then
				return false, string.format("Take the Path Trial for %s first: your class trainer runs it. Both trials come before the choice.", o.name)
			end
		end
	end
	return true, found.name
end

-- Pure: levels earned in each stage key, e.g. { ranger = 10, marksman = 5 }
function SpireStyle.levels(v)
	local t = tree(v.voc)
	local out = {}
	if not t then
		return out
	end
	out[t.key] = v.stage > 1 and 10 or v.level
	if v.path and v.stage >= 2 then
		out[v.path] = v.stage > 2 and 10 or v.level
	end
	if v.final and v.stage >= 3 then
		out[v.final] = v.level
	end
	return out
end

-- Does a passive part apply in this situation? ctx = { distance, shield (holding a shield), area (an area attack),
-- unmarked (the target carries no mark) }
local function applies(kind, ctx)
	ctx = ctx or {}
	if kind == "far_damage" then
		return (ctx.distance or 0) >= 4
	elseif kind == "taken_shield" then
		return ctx.shield == true
	elseif kind == "damage_noshield" then
		return ctx.shield ~= true
	elseif kind == "single_damage" then
		return ctx.area ~= true
	elseif kind == "area_damage" then
		return ctx.area == true
	elseif kind == "unmarked_damage" then
		return ctx.unmarked == true
	end
	return true
end

local function sum(v, kinds, ctx)
	local total = 0
	for key, lvl in pairs(SpireStyle.levels(v)) do
		for _, part in ipairs(SpireGearData.PASSIVES[key] or {}) do
			if kinds[part.kind] and applies(part.kind, ctx) then
				total = total + lvl * part.per
			end
		end
	end
	return total
end
SpireStyle.sum = sum

-- Pure: extra damage share (0.05 = +5%; negative for the extreme finals' minus). ctx as in applies()
function SpireStyle.damageBonus(v, ctx)
	return sum(v, { damage = true, far_damage = true, damage_noshield = true, single_damage = true, area_damage = true,
		unmarked_damage = true }, ctx)
end

-- Pure: multiplier on damage taken (below 1 = less; Bloodedge's minus makes it above 1)
function SpireStyle.takenFactor(v, ctx)
	return 1 - sum(v, { taken = true, taken_shield = true }, ctx)
end

-- Pure: multiplier on healing done
function SpireStyle.healFactor(v)
	return 1 + sum(v, { heal = true })
end

-- Pure: extra movement speed
function SpireStyle.speedBonus(v)
	return sum(v, { speed = true })
end

-- Pure: extra maximum health share (Ironwall)
function SpireStyle.maxHealthBonus(v)
	return sum(v, { max_health = true })
end

-- Pure: chance of a critical hit (Deadeye), as a share
function SpireStyle.critChance(v)
	return sum(v, { crit = true })
end

-- Pure: how much longer holds, roots, slows and knock-backs last on monsters (spec 9.3: up to 20% on the paths,
-- 25% on the control finals). 1 = unchanged.
function SpireStyle.ccFactor(v)
	local raw = sum(v, { cc = true })
	local cap = (v.final and v.stage >= 3) and SpireGearData.CC_CAP.final or SpireGearData.CC_CAP.path
	return 1 + math.min(raw, cap)
end

-- Pure: how much stronger the party buffs this character casts are (Dawnmender)
function SpireStyle.buffFactor(v)
	return 1 + sum(v, { buff = true })
end

-- Pure: the Reaver's off-hand strike, as a share of the off-hand blade's damage (20% plus 1% a level; 0 if not Reaver)
SpireStyle.OFFHAND_BASE = 0.20
function SpireStyle.offhandShare(v)
	local extra = sum(v, { offhand = true })
	if extra <= 0 then
		return 0
	end
	return SpireStyle.OFFHAND_BASE + extra
end

-- Pure: Stormbreaker's cleave, as a share of the hit that also lands on monsters beside the target
function SpireStyle.cleaveShare(v)
	return sum(v, { cleave = true })
end

-- Pure: the dodge chance a Pathfinder gives party members near them
function SpireStyle.partyDodge(v)
	return sum(v, { party_dodge = true })
end

-- Pure: does this style view have the signature ability of `stage` (that stage complete)?
function SpireStyle.hasAbilityPure(v, stage)
	return v.stage > stage or (v.stage == stage and v.level == 10)
end

-- Pure: may the character respec now? path = its first choice (nil = nothing to undo), lastAt = last respec time
SpireStyle.RESPEC_WAIT = 7 * 86400
function SpireStyle.respecCheck(path, lastAt, now)
	if not path then
		return false, "You have not chosen a style yet: there is nothing to undo."
	end
	if lastAt and now - lastAt < SpireStyle.RESPEC_WAIT then
		local days = math.ceil((SpireStyle.RESPEC_WAIT - (now - lastAt)) / 86400)
		return false, string.format("Your style settled too recently. You can respec again in %d day%s.", days, days == 1 and "" or "s")
	end
	return true
end

-- ---------------------------------------------------------------- the character
local function kv(player)
	return player:kv():scoped("spirebound")
end

-- the gates a character has passed: Floor 2 reached, the Path Trials done (kv "spirebound": style_arrived2,
-- style_trial_<key>)
function SpireStyle.ctxOf(player)
	local k = kv(player)
	local trials = {}
	local t = tree(player:getVocation():getBaseId())
	for _, p in ipairs(t and t.paths or {}) do
		trials[p.key] = k:get("style_trial_" .. p.key) ~= nil
		for _, f in ipairs(p.finals) do
			trials[f.key] = k:get("style_trial_" .. f.key) ~= nil
		end
	end
	local arrived = k:get("style_arrived2") ~= nil or (Floors and Floors.at and Floors.at(player:getPosition()) >= 2)
	return { arrived = arrived, trials = trials }
end

function SpireStyle.get(player)
	local k = kv(player)
	return SpireStyle.view(player:getVocation():getBaseId(), k:get("style_points") or 0, k:get("style_path"), k:get("style_final"),
		nil, SpireStyle.ctxOf(player))
end

function SpireStyle.markTrial(player, key)
	kv(player):set("style_trial_" .. key, os.time())
end

function SpireStyle.markArrived(player)
	local k = kv(player)
	if k:get("style_arrived2") then
		return false
	end
	k:set("style_arrived2", os.time())
	return true
end

-- Second version of the trees: a final that changed meaning is cleared and chosen again for free (not a respec)
function SpireStyle.migrate(player)
	local k = kv(player)
	local final = k:get("style_final")
	if final and SpireGearData.RETIRED_STYLE[final] then
		k:remove("style_final")
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The style trees have changed: your final style is free to choose again. Your class trainer will help you (free, no respec needed).")
		return true
	end
	k:remove("style_stance")
	return false
end

function SpireStyle.setStance()
	return SpireStyle.canStance()
end

function SpireStyle.hasAbility(player, stage)
	return SpireStyle.hasAbilityPure(SpireStyle.get(player), stage)
end

function SpireStyle.name(voc, key)
	local t = tree(voc)
	if not t then
		return key
	end
	if t.key == key then
		return t.name
	end
	for _, p in ipairs(t.paths) do
		if p.key == key then
			return p.name
		end
		for _, f in ipairs(p.finals) do
			if f.key == key then
				return f.name
			end
		end
	end
	return key
end

-- The name of the stage the character is levelling now
function SpireStyle.stageName(v)
	local t = tree(v.voc)
	if not t then
		return "" -- no path yet: the Journal of a character fresh out of the Arrival Yard crashed here (Grok session 3)
	end
	local key = (v.stage == 3 and v.final) or (v.stage == 2 and v.path) or t.key
	return SpireStyle.name(v.voc, key)
end

function SpireStyle.addPoints(player, n)
	if n <= 0 or not tree(player:getVocation():getBaseId()) then
		return
	end
	local before = SpireStyle.get(player)
	local k = kv(player)
	k:set("style_points", (k:get("style_points") or 0) + n)
	local after = SpireStyle.get(player)
	if after.stage ~= before.stage or after.level ~= before.level then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s %d/10.", SpireStyle.stageName(after), after.level))
		player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
		if SpireStyle.applySpeed then
			SpireStyle.applySpeed(player)
		end
		if SpireStyle.applyBody then
			SpireStyle.applyBody(player)
		end
	end
	if after.choiceReady and not before.choiceReady then
		local names = {}
		for _, o in ipairs(after.options) do
			table.insert(names, o.name)
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s is complete! Your class trainer will send for you: %s or %s.",
			SpireStyle.stageName(after), names[1] or "?", names[2] or "?"))
		if SpireCalling and SpireCalling.summon and after.path then
			SpireCalling.summon(player, true) -- the final style: the trainer's second letter (the path's comes on Floor 2)
		end
	end
end

-- Make a choice (permanent). Returns ok, message.
function SpireStyle.choose(player, key)
	local k = kv(player)
	local voc = player:getVocation():getBaseId()
	local path, final = k:get("style_path"), k:get("style_final")
	local ok, msg = SpireStyle.canChoose(voc, k:get("style_points") or 0, path, final, key, SpireStyle.ctxOf(player))
	if not ok then
		return false, msg
	end
	if not path then
		k:set("style_path", key)
	else
		k:set("style_final", key)
	end
	return true, "You chose " .. msg .. ". This is your style for good."
end

-- The Mastery Respec Scroll (shop only): clears both choices, keeps every point. Returns ok, message.
function SpireStyle.respec(player, now)
	local k = kv(player)
	local ok, msg = SpireStyle.respecCheck(k:get("style_path"), k:get("style_respec_at"), now)
	if not ok then
		return false, msg
	end
	k:remove("style_path")
	k:remove("style_final")
	k:set("style_respec_at", now)
	return true, "Your style is undone. Your Mastery points stay: say !style to choose again."
end
