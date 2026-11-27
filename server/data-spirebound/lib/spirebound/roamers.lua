-- Rare roaming monsters (roadmap AD4; adventure design 4.4, takes over N6, Jay's "money monsters").
-- One roamer per level band. Every 25-45 minutes one of them comes out at a random monster spot of one of its grounds
-- (never within 8 tiles of a gate, never in a party cave) and stays 15 minutes. The server hears when someone first
-- sees it, when it falls (with the names) and when it slips away. Loot: a purse of about 10 minutes of its grounds'
-- income, 2 rough Hearth Shards, a 25% Beacon Ember, and a 4% keepsake (house trophy + title) with the shards' pity rule.
-- Numbers: tools/gen_adventure.py (adventure_data.lua). The game side: scripts/spirebound/roamers.lua.
SpireRoamers = SpireRoamers or { current = nil }

local D = SpireAdventureData

function SpireRoamers.list()
	return D.roamers
end

function SpireRoamers.get(id)
	for _, r in ipairs(D.roamers) do
		if r.id == id or r.name:lower() == tostring(id):lower() then
			return r
		end
	end
end

function SpireRoamers.byName(name)
	for _, r in ipairs(D.roamers) do
		if r.name == name then
			return r
		end
	end
end

-- Pure: seconds until the next roamer; roll in [0, 1]
function SpireRoamers.delay(roll)
	return math.floor(D.roamerEvery[1] + (D.roamerEvery[2] - D.roamerEvery[1]) * roll + 0.5)
end

-- Pure: may a roamer appear at this spot? gate = {x, y} or nil; caves = list of { x1, y1, x2, y2, z }
function SpireRoamers.spotOk(spot, gate, caves, gap)
	if gate and math.max(math.abs(spot.x - gate.x), math.abs(spot.y - gate.y)) < (gap or D.roamerGateGap) then
		return false
	end
	for _, c in ipairs(caves or {}) do
		if spot.z == c.z and spot.x >= c.x1 and spot.x <= c.x2 and spot.y >= c.y1 and spot.y <= c.y2 then
			return false
		end
	end
	return true
end

function SpireRoamers.ground(gid)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.id == gid then
			return g
		end
	end
end

-- The spots of a ground a roamer may use (from the map's own monster spots, SpireWilds)
function SpireRoamers.spots(gid)
	local g = SpireRoamers.ground(gid)
	if not g then
		return {}
	end
	local caves = {}
	for _, c in ipairs(SpireWilds.caves or {}) do
		if c.id == gid then
			table.insert(caves, c)
		end
	end
	local gate = WorldPoints and WorldPoints["gate_" .. gid]
	local out = {}
	for _, s in ipairs(g.spots or {}) do
		if SpireRoamers.spotOk(s, gate, caves) then
			table.insert(out, s)
		end
	end
	return out
end

-- Pure: which roamer, ground and spot next. rand(n) returns 1..n.
function SpireRoamers.pick(rand, spotsOf)
	local r = D.roamers[rand(#D.roamers)]
	local grounds = {}
	for _, gid in ipairs(r.grounds) do
		if #spotsOf(gid) > 0 then
			table.insert(grounds, gid)
		end
	end
	if #grounds == 0 then
		return r
	end
	local gid = grounds[rand(#grounds)]
	local spots = spotsOf(gid)
	return r, gid, spots[rand(#spots)]
end

-- Pure: the purse as coins: { platinum, gold }
function SpireRoamers.coins(gold)
	return math.floor(gold / 100), gold % 100
end

-- Pure: does this kill give the keepsake? sinceLast = this character's kills of this roamer since its last keepsake
function SpireRoamers.keepsakeRoll(sinceLast, roll)
	return SpireGear.shardRoll(D.keepsakeChance, sinceLast, roll)
end

function SpireRoamers.groundAt(pos)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.zs and g.zs[pos.z] and pos.x >= g.x1 and pos.x <= g.x2 and pos.y >= g.y1 and pos.y <= g.y2 then
			return g.id
		end
	end
end

function SpireRoamers.groundTitle(gid)
	local g = SpireRoamers.ground(gid)
	return g and g.title or gid
end

-- what the character has: kills per roamer, and keepsakes
local function kv(player)
	return player:kv():scoped("spirebound-roamers")
end

function SpireRoamers.kills(player, id)
	return kv(player):get("kills_" .. id) or 0
end

function SpireRoamers.hasKeepsake(player, id)
	return kv(player):get("keepsake_" .. id) ~= nil
end

-- One credited kill: counts it, rolls the keepsake (pity: sure at three times the expected wait). True if it dropped.
function SpireRoamers.creditKill(player, r, roll)
	local k = kv(player)
	k:set("kills_" .. r.id, SpireRoamers.kills(player, r.id) + 1)
	local since = (k:get("since_" .. r.id) or 0) + 1
	if not SpireRoamers.keepsakeRoll(since, roll or math.random()) then
		k:set("since_" .. r.id, since)
		return false
	end
	k:set("since_" .. r.id, 0)
	k:set("keepsake_" .. r.id, os.time())
	SpireGive.reward(player, r.keepsake, 1)
	player:kv():scoped("spirebound-titles"):set(r.title, os.time())
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Keepsake: %s! It is in your backpack (a trophy for your house), and you earned the title %s.", r.keepsakeName, r.title))
	player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
	return true
end

-- Server-wide lines go through Session A's finds (rate limit + notice board) when it is there, a plain broadcast if not
function SpireRoamers.say(kind, names, thing, groundName)
	if SpireFinds and SpireFinds.announce then
		return SpireFinds.announce(kind, names, thing, groundName)
	end
	local text
	if kind == "roamer_seen" then
		text = string.format("%s has been sighted in %s!", thing:match("^The ") and thing or ("A " .. thing), groundName)
	elseif kind == "roamer_killed" then
		local list = {}
		for _, n in ipairs(names or {}) do
			table.insert(list, type(n) == "string" and n or n:getName())
		end
		text = string.format("%s brought down %s!", table.concat(list, ", "), thing:match("^The ") and ("t" .. thing:sub(2)) or ("the " .. thing))
	else
		text = tostring(thing)
	end
	Game.broadcastMessage(text, MESSAGE_EVENT_ADVANCE)
	return text, true
end

-- "The Frenzied Boar has slipped away." (no find kind for it: an ordinary broadcast, it names no one)
function SpireRoamers.goneLine(r)
	return string.format("%s has slipped away.", r.name:match("^The ") and r.name or ("The " .. r.name))
end
