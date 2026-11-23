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

-- Pure: what the character's style looks like with its choices
function SpireStyle.view(voc, points, path, final)
	local s, l = SpireStyle.levelOf(points)
	local v = { voc = voc, points = points or 0, path = path, final = final, choiceReady = false }
	if not path then
		if s > 1 or l == 10 then
			s, l, v.choiceReady = 1, 10, true
		end
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
			v.options = findPath(voc, path).finals
		end
	end
	return v
end

-- Pure: may this choice be made now? -> ok, message
function SpireStyle.canChoose(voc, points, path, final, key)
	local v = SpireStyle.view(voc, points, path, final)
	if final then
		return false, "Your style is complete: there is nothing left to choose."
	end
	if not v.choiceReady then
		return false, "Your next choice comes when this stage reaches level 10."
	end
	for _, o in ipairs(v.options or {}) do
		if o.key == key then
			return true, o.name
		end
	end
	return false, "That is not one of your choices. Say !style to see them."
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

local function sum(v, kinds, ctx)
	local total = 0
	for key, lvl in pairs(SpireStyle.levels(v)) do
		local p = SpireGearData.PASSIVES[key]
		if p and kinds[p.kind] and (p.kind ~= "far_damage" or (ctx and (ctx.distance or 0) >= 4)) then
			total = total + lvl * p.per
		end
	end
	return total
end

-- Pure: extra damage share (0.05 = +5%). ctx = { distance }
function SpireStyle.damageBonus(v, ctx)
	return sum(v, { damage = true, far_damage = true }, ctx)
end

-- Pure: multiplier on damage taken (below 1 = less)
function SpireStyle.takenFactor(v)
	return 1 - sum(v, { taken = true })
end

-- Pure: multiplier on healing done
function SpireStyle.healFactor(v)
	return 1 + sum(v, { heal = true })
end

-- Pure: extra movement speed
function SpireStyle.speedBonus(v)
	return sum(v, { speed = true })
end

-- ---------------------------------------------------------------- the character
local function kv(player)
	return player:kv():scoped("spirebound")
end

function SpireStyle.get(player)
	local k = kv(player)
	return SpireStyle.view(player:getVocation():getBaseId(), k:get("style_points") or 0, k:get("style_path"), k:get("style_final"))
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
	local key = (v.stage == 3 and v.final) or (v.stage == 2 and v.path) or tree(v.voc).key
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
	end
	if after.choiceReady and not before.choiceReady then
		local names = {}
		for _, o in ipairs(after.options) do
			table.insert(names, o.name)
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s is complete! Choose %s: say !style to read both.",
			SpireStyle.stageName(after), table.concat(names, " or ")))
	end
end

-- Make a choice (permanent). Returns ok, message.
function SpireStyle.choose(player, key)
	local k = kv(player)
	local voc = player:getVocation():getBaseId()
	local path, final = k:get("style_path"), k:get("style_final")
	local ok, msg = SpireStyle.canChoose(voc, k:get("style_points") or 0, path, final, key)
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
