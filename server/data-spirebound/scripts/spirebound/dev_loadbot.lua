-- Load-test brain (roadmap 9.2 and N2; tools/loadtest.py). Makes the scripted test clients hunt like players, so a load
-- test measures a real crowd (combat, walking, monsters reacting, packets to every watcher) without 100 game windows.
-- The clients (tools/loadbot.py) only log in and stay connected; this script does the playing for them, server-side.
--
-- Only runs when the server was started with SPIRE_LOADTEST=1 (tools/loadtest.py does that on its own test copy; the
-- live server never sets it), and only for accounts whose e-mail is loadbotN@localhost (made by tools/loadtest.py in
-- the test database; the sign-up page refuses any e-mail without a real domain, so no player can have one).
--
-- Each bot hunts one walled ground (SpireWilds), named in the plan file SPIRE_LOADTEST_PLAN ("name;ground;dps" lines).
-- It picks the nearest monster nobody else is fighting, walks to it and hits it at the economy model's damage per
-- second (tools/gen_economy.py: 4 + level, times its class speed); with nothing in sight it walks on to the next spot
-- of its ground (a spot on another level costs the walking time, then it goes there). Health is topped up, as
-- potions would.
-- It logs, every 10 seconds: players online and how late the server's 50 ms heartbeat ran (the tick lag), and every
-- 60 seconds: bots and kills per ground.
if os.getenv("SPIRE_LOADTEST") ~= "1" then
	return
end

SpireLoadbot = { plan = {}, bots = {}, claims = {}, kills = {}, ground = {} }
local L = SpireLoadbot
local THINK = 500 -- ms between decisions
local STEP = 300 -- ms between steps while walking (about a player's walking speed on Floor 1)
local SIGHT = 7
local PAUSE = 2000 -- ms after each kill

local function readPlan()
	local path = os.getenv("SPIRE_LOADTEST_PLAN")
	local f = path and io.open(path, "r")
	if not f then
		logger.warn("[LOADTEST] no plan file ({})", tostring(path))
		return
	end
	for line in f:lines() do
		local name, ground, dps = line:match("^([^;]+);([^;]+);([%d%.]+)")
		if name then
			L.plan[name] = { ground = ground, dps = tonumber(dps) }
		end
	end
	f:close()
	for _, g in ipairs(SpireWilds.grounds) do
		-- patrol only the spots on levels that count as the ground (a party cave below is a different place)
		local spots = {}
		for _, sp in ipairs(g.spots or {}) do
			if sp.z == g.z or (g.zs and g.zs[sp.z]) then
				table.insert(spots, sp)
			end
		end
		L.ground[g.id] = { id = g.id, z = g.z, zs = g.zs, x1 = g.x1, y1 = g.y1, x2 = g.x2, y2 = g.y2, spots = spots }
	end
end
readPlan()

local function isBot(player)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	return email and email:match("^loadbot%d*@localhost$") ~= nil
end

local function inside(g, pos)
	return SpireCrowd.inside(g, pos)
end

local function dist(a, b)
	return math.max(math.abs(a.x - b.x), math.abs(a.y - b.y))
end

-- nearest monster in sight, inside the ground, on this level, that no other bot is fighting
local function pickTarget(player, b)
	local pos = player:getPosition()
	local best, bd
	for _, c in ipairs(Game.getSpectators(pos, false, false, SIGHT, SIGHT, SIGHT, SIGHT)) do
		if c:isMonster() and not c:getMaster() and c:getHealth() > 0 then
			local cp = c:getPosition()
			local owner = L.claims[c:getId()]
			local skip = b.skip[c:getId()]
			if cp.z == pos.z and inside(b.g, cp) and (not owner or owner == player:getId() or not Creature(owner))
				and not (skip and skip > systemTime()) then
				local d = dist(pos, cp)
				if not bd or d < bd then
					best, bd = c, d
				end
			end
		end
	end
	return best
end

local function stepToward(player, to)
	local path = player:getPathTo(to, 0, 1, true, true, 40)
	if path and path[1] then
		player:move(path[1])
		return true
	end
	return false
end

local function think(pid)
	local player = Player(pid)
	local b = L.bots[pid]
	if not player or not b then
		L.bots[pid] = nil
		return
	end
	addEvent(think, THINK, pid)
	local now = systemTime()
	if player:getHealth() < player:getMaxHealth() * 0.6 then
		player:addHealth(player:getMaxHealth())
	end
	if b.pauseUntil then -- a moment after each kill: reacting, loot, a look round (as a player would)
		if now < b.pauseUntil then
			return
		end
		b.pauseUntil = nil
	end
	if b.travelUntil then -- walking to a spot on another level
		if now < b.travelUntil then
			return
		end
		player:teleportTo(b.travelTo)
		b.travelUntil, b.travelTo = nil, nil
	end
	local pos = player:getPosition()
	if not inside(b.g, pos) then -- first tick (or pushed out): start at the ground's first spot
		local s = b.g.spots[1]
		player:teleportTo(Position(s.x, s.y, s.z))
		b.n.reset = b.n.reset + 1
		return
	end
	local t = b.target and Creature(b.target)
	if not t or t:getHealth() <= 0 or dist(pos, t:getPosition()) > SIGHT or t:getPosition().z ~= pos.z then
		if b.target then
			L.claims[b.target] = nil
		end
		t = pickTarget(player, b)
		b.target = t and t:getId() or nil
		if t then
			L.claims[t:getId()] = pid
			player:setFollowCreature(t)
			b.chased = 0
		end
	end
	if t then
		local reach = b.range
		if dist(pos, t:getPosition()) <= reach then
			local dmg = math.max(1, math.floor(b.dps * THINK / 1000 + math.random()))
			doTargetCombatHealth(player, t, COMBAT_PHYSICALDAMAGE, -dmg, -dmg, CONST_ME_NONE)
			b.n.hit = b.n.hit + 1
		else
			b.n.chase = b.n.chase + 1
			b.chased = (b.chased or 0) + 1
			if b.chased > 10 then -- 5 s without reaching it: out of reach (water, a wall): leave it for 30 s
				b.skip[t:getId()] = now + 30000
				L.claims[t:getId()] = nil
				b.target = nil
				player:setFollowCreature(nil)
				return
			end
			if reach > 1 then
				stepToward(player, t:getPosition())
			end
		end
		return
	end
	-- nothing in sight: walk on to the next spot of the ground
	player:setFollowCreature(nil)
	local s = b.g.spots[b.spot]
	local to = Position(s.x, s.y, s.z)
	if s.z ~= pos.z or not player:getPathTo(to, 0, 1, true, true, 60) then
		b.travelTo = to
		b.n.travel = b.n.travel + 1
		b.travelUntil = now + math.max(2, dist(pos, to)) * STEP + 4000 -- the walk, plus finding the stairs
		b.spot = b.spot % #b.g.spots + 1
		return
	end
	if dist(pos, to) <= 2 then
		b.spot = b.spot % #b.g.spots + 1
		b.walkStart = nil
		return
	end
	-- stuck on the way (a blocked path, a door): after twice the walking time, go there as if the way round was found
	if b.walkSpot ~= b.spot then
		b.walkSpot, b.walkStart, b.walkFrom = b.spot, now, dist(pos, to)
	elseif now - b.walkStart > b.walkFrom * STEP * 2 + 3000 then
		b.travelTo, b.travelUntil = to, now + 1000
		b.n.travel = b.n.travel + 1
		b.spot = b.spot % #b.g.spots + 1
		return
	end
	b.n.walk = b.n.walk + 1
	-- walk a few steps during this think
	for i = 0, math.floor(THINK / STEP) - 1 do
		addEvent(function()
			local p = Player(pid)
			if p and L.bots[pid] and not L.bots[pid].target then
				stepToward(p, to)
			end
		end, i * STEP)
	end
end

local login = CreatureEvent("SpireLoadbotLogin")
function login.onLogin(player)
	local plan = L.plan[player:getName()]
	if not plan or not isBot(player) then
		return true
	end
	local g = L.ground[plan.ground]
	if not g then
		logger.warn("[LOADTEST] {}: no ground {}", player:getName(), plan.ground)
		return true
	end
	local voc = player:getVocation():getId()
	L.bots[player:getId()] = { g = g, dps = plan.dps, spot = math.random(#g.spots), range = (voc == 4) and 1 or 3,
		n = { reset = 0, travel = 0, hit = 0, walk = 0, chase = 0 }, skip = {} } -- what it spent its thinks on (the minute report)
	player:registerEvent("SpireLoadbotKill")
	addEvent(think, 1000 + math.random(THINK), player:getId())
	return true
end
login:register()

local kill = CreatureEvent("SpireLoadbotKill")
function kill.onKill(player, target)
	local b = L.bots[player:getId()]
	if b and target:isMonster() and not target:getMaster() then
		L.kills[b.g.id] = (L.kills[b.g.id] or 0) + 1
		L.claims[target:getId()] = nil
		b.target = nil
		b.pauseUntil = systemTime() + PAUSE
	end
	return true
end
kill:register()

-- the heartbeat: a 100 ms timer; how late it fires is how far behind the server's game loop is
local HEART = 100 -- the scheduler runs timers on a 50 ms grid, so a 100 ms timer that is on time reads 0-50
local beat = { last = 0, n = 0, sum = 0, max = 0, over = 0 }
local function heartbeat()
	local now = systemTime()
	if beat.last > 0 then
		local late = math.max(0, now - beat.last - HEART)
		beat.n, beat.sum = beat.n + 1, beat.sum + late
		beat.max = math.max(beat.max, late)
		if late > 100 then
			beat.over = beat.over + 1
		end
	end
	beat.last = now
	addEvent(heartbeat, HEART)
end

local report = GlobalEvent("SpireLoadbotReport")
function report.onStartup()
	addEvent(heartbeat, HEART)
	return true
end
report:register()

local every10 = GlobalEvent("SpireLoadbotLag")
function every10.onThink()
	local bots = 0
	for _ in pairs(L.bots) do
		bots = bots + 1
	end
	logger.info("[LOADTEST] lag online={} bots={} monsters={} beats={} lag_avg_ms={} lag_max_ms={} late_over_100ms={}", Game.getPlayerCount(), bots, Game.getMonsterCount(), beat.n, beat.n > 0 and math.floor(beat.sum / beat.n * 10) / 10 or 0, beat.max, beat.over)
	beat.n, beat.sum, beat.max, beat.over = 0, 0, 0, 0
	return true
end
every10:interval(10000)
every10:register()

-- monsters alive inside a ground right now, on its own levels (is the ground empty, or are the bots not finding them?)
local function aliveIn(g)
	if not g then
		return 0
	end
	local cx, cy = math.floor((g.x1 + g.x2) / 2), math.floor((g.y1 + g.y2) / 2)
	local rx, ry = math.ceil((g.x2 - g.x1) / 2) + 1, math.ceil((g.y2 - g.y1) / 2) + 1
	local n = 0
	for z = 0, 15 do
		if z == g.z or (g.zs and g.zs[z]) then
			for _, c in ipairs(Game.getSpectators(Position(cx, cy, z), false, false, rx, rx, ry, ry)) do
				if c:isMonster() and not c:getMaster() and SpireCrowd.inside(g, c:getPosition()) then
					n = n + 1
				end
			end
		end
	end
	return n
end

local every60 = GlobalEvent("SpireLoadbotKills")
function every60.onThink()
	local per = {}
	for _, b in pairs(L.bots) do
		per[b.g.id] = (per[b.g.id] or 0) + 1
	end
	if os.getenv("SPIRE_LOADTEST_DEBUG") == "1" then
		for pid, b in pairs(L.bots) do
			local p = Player(pid)
			if p then
				local pos = p:getPosition()
				logger.info("[LOADTEST] bot {} ground={} pos={},{},{} hp={} target={} thinks: hit={} chase={} walk={} travel={} reset={}", p:getName(), b.g.id, pos.x, pos.y, pos.z, p:getHealth(), b.target and Creature(b.target) and Creature(b.target):getName() or "-", b.n.hit, b.n.chase, b.n.walk, b.n.travel, b.n.reset)
				b.n = { reset = 0, travel = 0, hit = 0, walk = 0, chase = 0 }
			end
		end
	end
	for id, n in pairs(per) do
		local rec = SpireCrowd.grounds[id]
		logger.info("[LOADTEST] kills ground={} bots={} kills_total={} crowd={} alive={}", id, n, L.kills[id] or 0, rec and rec.state or "quiet", aliveIn(L.ground[id]))
	end
	return true
end
every60:interval(60000)
every60:register()

-- Scripted test characters (tools/loadtest.py addon): a few shortcuts so a test can walk a quest through the real NPCs
-- and the real kill event without the walk there. Same gates as above (SPIRE_LOADTEST=1, loadbot accounts only).
--   /lt goto <name>     stand next to that NPC (or creature)
--   /lt kill <monster> [n]  n fresh <monster>s appear next to you, one at a time, and you kill each (kill events,
--                       quest counters, loot run)
--   /lt state           log your quests' states and which class-outfit addons you own
local lt = TalkAction("/lt")
function lt.onSay(player, words, param)
	if not isBot(player) then
		return false
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	if cmd == "goto" then -- an NPC or creature by name, or a named map point (AD5: loop_smugglers_ridge_b)
		local c = Creature(rest)
		local wp = not c and WorldPoints[rest]
		if wp then
			c = { getPosition = function() return wp end }
		end
		if c then
			local p = c:getPosition()
			local spot = Game.getClosestFreeTile and Game.getClosestFreeTile(player, p) or p
			player:teleportTo(spot or p, true)
		end
		logger.info("[LOADTEST] script {} goto {} found={}", player:getName(), rest, c and "yes" or "no")
	elseif cmd == "kill" then -- "/lt kill <monster> [count]": one command, so the chat-spam guard never mutes the bot
		local name, n = rest:match("^(.-)%s+(%d+)$")
		name, n = name or rest, tonumber(n) or 1
		local pid = player:getId()
		for i = 1, n do
			addEvent(function()
				local p = Player(pid)
				if p then -- healed between kills, as potions would (a shardling's death burst hurts whoever stands by it)
					p:addHealth(p:getMaxHealth())
				end
				local m = p and Game.createMonster(name, p:getPosition(), true, true)
				if m then
					doTargetCombatHealth(p, m, COMBAT_PHYSICALDAMAGE, -m:getMaxHealth() * 2, -m:getMaxHealth() * 2, CONST_ME_NONE)
				end
				if i == n then
					logger.info("[LOADTEST] script {} killed {} x{} last_made={}", p and p:getName() or "?", name, n, m and "yes" or "no")
				end
			end, i * 200)
		end
		addEvent(function()
			local p = Player(pid)
			if p then
				p:addHealth(p:getMaxHealth())
			end
		end, n * 200 + 1500)
	elseif cmd == "state" then
		local parts = {}
		for _, q in ipairs(SpireQuests.list) do
			if q.addon then
				local st = player:getStorageValue(q.storage)
				if st ~= -1 then
					table.insert(parts, q.id .. "=" .. st)
				end
			end
		end
		local owned = {}
		for sex = 0, 1 do
			for _, look in pairs(ClassOutfits.LOOKS[sex]) do
				for a = 1, 2 do
					if player:hasOutfit(look, a) then
						table.insert(owned, look .. "+" .. a)
					end
				end
			end
		end
		table.sort(owned)
		logger.info("[LOADTEST] state {} voc={} quests={} addons={}", player:getName(), player:getVocation():getBaseId(), table.concat(parts, ","), table.concat(owned, ","))
	end
	return true
end
lt:separator(" ")
lt:groupType("normal")
lt:register()
