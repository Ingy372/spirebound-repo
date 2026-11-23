-- Hidden mini-bosses and their trophies (gear progression spec 4.8). Each boss wakes when someone steps on its
-- secret's trigger tile (and its rest is over); everyone who hurt it gets its trophy once per character.
-- Trophies belong to the character (its style), so switching weapons never loses them.
-- GM notes on where they are: docs/gm/floor1_minibosses.md (never in player docs).
SpireTrophies = SpireTrophies or {}

SpireTrophies.LIST = {
	{ id = "old_tusk", boss = "Old Tusk", secret = "s2", spawn = "old_tusk_spawn", name = "Old Tusk's Tusk",
		text = "+3% maximum health", health = 0.03 },
	{ id = "hollowfang", boss = "Hollowfang", secret = "s9", name = "Hollowfang's Pelt",
		text = "+5 movement speed", speed = 5 },
	{ id = "briar_mother", boss = "Briar Mother", secret = "s11", name = "Briar Mother's Thorn",
		text = "+2% damage", damage = 0.02 },
	{ id = "drowned_warden", boss = "Drowned Warden", secret = "s10", name = "Drowned Warden's Seal",
		text = "one level of style at once", style = 1 },
}
SpireTrophies.REST_MIN, SpireTrophies.REST_MAX = 3600, 10800 -- a mini-boss rests 1 to 3 hours after it dies

function SpireTrophies.get(id)
	for _, t in ipairs(SpireTrophies.LIST) do
		if t.id == id then
			return t
		end
	end
end

function SpireTrophies.byBoss(name)
	for _, t in ipairs(SpireTrophies.LIST) do
		if t.boss == name then
			return t
		end
	end
end

-- Pure: rest in seconds; roll() returns 0..1
function SpireTrophies.respawnDelay(roll)
	return math.floor(SpireTrophies.REST_MIN + (SpireTrophies.REST_MAX - SpireTrophies.REST_MIN) * roll() + 0.5)
end

-- Pure: does this kill give a new trophy? have = { [id] = time }
function SpireTrophies.newOnes(have, id)
	return have[id] == nil
end

local function total(have, field)
	local sum = 0
	for _, t in ipairs(SpireTrophies.LIST) do
		if have[t.id] and t[field] then
			sum = sum + t[field]
		end
	end
	return sum
end

function SpireTrophies.damagePure(have) return total(have, "damage") end
function SpireTrophies.speedPure(have) return total(have, "speed") end
function SpireTrophies.healthPure(have) return total(have, "health") end

-- Pure: style points a trophy gives at once
function SpireTrophies.stylePointsPure(id)
	local t = SpireTrophies.get(id)
	return (t and t.style) and SpireGearData.STYLE_POINTS[1] * t.style or 0
end

-- ---------------------------------------------------------------- the character
local function kv(player)
	return player:kv():scoped("spirebound")
end

function SpireTrophies.have(player)
	local out = {}
	for _, t in ipairs(SpireTrophies.LIST) do
		local at = kv(player):get("trophy_" .. t.id)
		if at then
			out[t.id] = at
		end
	end
	return out
end

function SpireTrophies.found(player)
	local out = {}
	for id in pairs(SpireTrophies.have(player)) do
		table.insert(out, id)
	end
	return out
end

function SpireTrophies.foundNames(player)
	local out = {}
	local have = SpireTrophies.have(player)
	for _, t in ipairs(SpireTrophies.LIST) do
		if have[t.id] then
			table.insert(out, t.name .. " (" .. t.text .. ")")
		end
	end
	return out
end

-- read by SpireProgress.onDealt
function SpireTrophies.bonus(player, ctx)
	return SpireTrophies.damagePure(SpireTrophies.have(player))
end

local HEALTH_SUBID = 4600
local speedApplied = {}
function SpireTrophies.apply(player)
	local have = SpireTrophies.have(player)
	player:removeCondition(CONDITION_ATTRIBUTES, CONDITIONID_DEFAULT, HEALTH_SUBID)
	local hp = SpireTrophies.healthPure(have)
	if hp > 0 then
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, HEALTH_SUBID)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		c:setParameter(CONDITION_PARAM_STAT_MAXHITPOINTSPERCENT, 100 + math.floor(hp * 100 + 0.5))
		player:addCondition(c)
	end
	local want, had = SpireTrophies.speedPure(have), speedApplied[player:getId()] or 0
	if want ~= had then
		player:changeSpeed(want - had)
		speedApplied[player:getId()] = want
	end
end
SpireCleanup.add(function(pid) speedApplied[pid] = nil end)

function SpireTrophies.grant(player, id)
	local t = SpireTrophies.get(id)
	if not t or not SpireTrophies.newOnes(SpireTrophies.have(player), id) then
		return false
	end
	kv(player):set("trophy_" .. id, os.time())
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Trophy: %s! %s, for good.", t.name, t.text))
	player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_RED)
	local pts = SpireTrophies.stylePointsPure(id)
	if pts > 0 then
		SpireStyle.addPoints(player, pts)
	end
	SpireTrophies.apply(player)
	return true
end
