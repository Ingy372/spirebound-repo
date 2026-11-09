-- Field and floor bosses for floors 2-10 (DESIGN.md 3.2, 9.3). Placeholder fights built from a small pattern library;
-- each floor's spec lives in maps/floors.py and is mirrored in SpireFloorBosses below.
-- Floor 1's bosses are hand-scripted in bosses_floor1.lua.

SpireFloorBosses = {
	[2] = { field = "Horn Brute", fieldPattern = "stomp", boss = "Crowned Aurochs", bossPattern = "charge", elite = "Herd Bull" },
	[3] = { field = "Mossback Warden", fieldPattern = "root", boss = "Sleeping Trunk", bossPattern = "sleep", elite = "Moss Elder" },
	[4] = { field = "Lake Knight", fieldPattern = "lance", boss = "Knight of the Closed Helm", bossPattern = "silence", elite = "Drowned Sergeant" },
	[5] = { field = "Arena Warden", fieldPattern = "stances", boss = "Empty Colossus", bossPattern = "split", elite = "Deserter Lieutenant" },
	[6] = { field = "Bellows Giant", fieldPattern = "stomp", boss = "Cinder Matriarch", bossPattern = "charge", elite = "Forge Overseer" },
	[7] = { field = "Mire Colossus", fieldPattern = "root", boss = "The Many-Mouthed", bossPattern = "sleep", elite = "Bog Elder" },
	[8] = { field = "Avalanche Brute", fieldPattern = "lance", boss = "Rimebound Jarl", bossPattern = "silence", elite = "Raider Chieftain" },
	[9] = { field = "The Auctioneer", fieldPattern = "stances", boss = "The Ledger King", bossPattern = "split", elite = "Debt Collector" },
	[10] = { field = "Sapphire Gatekeeper", fieldPattern = "stomp", boss = "Azhrakkar, the Cerulean Ruin", bossPattern = "ruin", elite = "Cobalt Champion" },
}

local function around(c, r)
	local t = {}
	for dx = -r, r do
		for dy = -r, r do
			if math.max(math.abs(dx), math.abs(dy)) == r then
				table.insert(t, Position(c.x + dx, c.y + dy, c.z))
			end
		end
	end
	return t
end

local function line(from, to, len)
	local dx = to.x == from.x and 0 or (to.x > from.x and 1 or -1)
	local dy = to.y == from.y and 0 or (to.y > from.y and 1 or -1)
	if dx == 0 and dy == 0 then dy = 1 end
	local t = {}
	for i = 1, len do
		table.insert(t, Position(from.x + dx * i, from.y + dy * i, from.z))
	end
	return t
end

local function arc(boss, target)
	local b, t = boss:getPosition(), target:getPosition()
	local dx = t.x == b.x and 0 or (t.x > b.x and 1 or -1)
	local dy = t.y == b.y and 0 or (t.y > b.y and 1 or -1)
	local tiles = {}
	for i = -1, 1 do
		if dx ~= 0 and dy == 0 then
			table.insert(tiles, Position(b.x + dx, b.y + i, b.z))
		elseif dy ~= 0 and dx == 0 then
			table.insert(tiles, Position(b.x + i, b.y + dy, b.z))
		else
			table.insert(tiles, Position(b.x + dx, b.y + dy, b.z))
		end
	end
	return tiles
end

local function players(def)
	if def.roomNW then
		return SpireBoss.playersInArea(WorldPoints[def.roomNW], WorldPoints[def.roomSE])
	end
	local c = WorldPoints[def.room.nw]
	local out = {}
	for _, cr in ipairs(Game.getSpectators(c, false, true, def.room.radius, def.room.radius, def.room.radius, def.room.radius)) do
		table.insert(out, cr)
	end
	return out
end

local function every(state, key, seconds, now)
	if not state.flags[key] or now >= state.flags[key] then
		state.flags[key] = now + seconds
		return true
	end
	return false
end

local function hit(n, mult)
	local base = math.floor(60 * n ^ 1.35)
	return -math.floor(base * mult * 0.7), -math.floor(base * mult)
end

-- pattern(boss, state, now, def) -> runs telegraphed attacks
local PATTERNS = {}
PATTERNS.stomp = function(boss, state, now, def)
	if every(state, "stomp", 12, now) then
		local mn, mx = hit(def.floor, 1.6)
		boss:say("The ground shakes!", TALKTYPE_MONSTER_YELL)
		SpireBoss.markTiles(boss:getId(), around(boss:getPosition(), 1), mn, mx)
	end
	if not state.flags.enraged and boss:getHealth() / boss:getMaxHealth() < 0.4 then
		state.flags.enraged = true
		boss:changeSpeed(60)
		boss:say("RAAAGH!", TALKTYPE_MONSTER_YELL)
	end
end
PATTERNS.root = function(boss, state, now, def)
	local ps = players(def)
	if #ps > 0 and every(state, "root", 15, now) then
		local p = ps[math.random(#ps)]
		local c = Condition(CONDITION_PARALYZE)
		c:setParameter(CONDITION_PARAM_TICKS, 1500)
		c:setFormula(-0.95, 0, -0.95, 0)
		p:addCondition(c)
		p:getPosition():sendMagicEffect(CONST_ME_SMALLPLANTS)
	end
	if every(state, "spores", 25, now) then
		local mn, mx = hit(def.floor, 1.2)
		local tiles = around(boss:getPosition(), 1)
		table.insert(tiles, boss:getPosition())
		SpireBoss.markTiles(boss:getId(), tiles, mn, mx)
	end
end
PATTERNS.lance = function(boss, state, now, def)
	local t = boss:getTarget()
	if t and every(state, "lance", 10, now) then
		local mn, mx = hit(def.floor, 1.8)
		SpireBoss.markTiles(boss:getId(), line(boss:getPosition(), t:getPosition(), 3), mn, mx)
	end
end
PATTERNS.stances = function(boss, state, now, def)
	if every(state, "stance", 20, now) then
		state.flags.stance = ((state.flags.stance or 0) % 3) + 1
		boss:say(({ "Shield stance!", "Spear stance!", "Net stance!" })[state.flags.stance], TALKTYPE_MONSTER_YELL)
	end
	local t = boss:getTarget()
	if state.flags.stance == 2 and t and every(state, "spear", 6, now) then
		local mn, mx = hit(def.floor, 2.0)
		SpireBoss.markTiles(boss:getId(), line(boss:getPosition(), t:getPosition(), 4), mn, mx)
	elseif state.flags.stance == 3 and every(state, "net", 8, now) then
		local ps = players(def)
		if #ps > 0 then
			local c = Condition(CONDITION_PARALYZE)
			c:setParameter(CONDITION_PARAM_TICKS, 2000)
			c:setFormula(-0.95, 0, -0.95, 0)
			ps[math.random(#ps)]:addCondition(c)
		end
	end
end
PATTERNS.charge = function(boss, state, now, def)
	local ps = players(def)
	if #ps > 0 and every(state, "charge", 15, now) then
		local p = ps[math.random(#ps)]
		local mn, mx = hit(def.floor, 2.2)
		boss:say("The " .. boss:getName() .. " lowers its head!", TALKTYPE_MONSTER_YELL)
		SpireBoss.markTiles(boss:getId(), line(boss:getPosition(), p:getPosition(), 7), mn, mx)
	end
	if not state.flags.adds and boss:getHealth() / boss:getMaxHealth() < 0.5 then
		state.flags.adds = true
		for _ = 1, 2 do
			Game.createMonster(def.elite, boss:getPosition(), true, false)
		end
	end
end
PATTERNS.sleep = function(boss, state, now, def)
	-- Punishes running around: every 4 s it slams whoever moved the most since the last check
	state.flags.lastPos = state.flags.lastPos or {}
	if every(state, "slam", 4, now) then
		local worst, far = nil, 2
		for _, p in ipairs(players(def)) do
			local last = state.flags.lastPos[p:getId()]
			local pos = p:getPosition()
			if last then
				local d = math.max(math.abs(pos.x - last.x), math.abs(pos.y - last.y))
				if d > far then
					worst, far = p, d
				end
			end
			state.flags.lastPos[p:getId()] = { x = pos.x, y = pos.y }
		end
		if worst then
			local mn, mx = hit(def.floor, 2.4)
			boss:say("It stirs... and slams!", TALKTYPE_MONSTER_YELL)
			SpireBoss.markTiles(boss:getId(), { worst:getPosition() }, mn, mx)
		end
	end
end
PATTERNS.silence = function(boss, state, now, def)
	if every(state, "visor", 20, now) then
		boss:say("The visor slams shut!", TALKTYPE_MONSTER_YELL)
		for _, p in ipairs(players(def)) do
			local c = Condition(CONDITION_PACIFIED)
			c:setParameter(CONDITION_PARAM_TICKS, 4000)
			p:addCondition(c)
			p:getPosition():sendMagicEffect(CONST_ME_STUN)
		end
	end
	local hp = boss:getHealth() / boss:getMaxHealth()
	if hp < 0.6 and every(state, "bounce", 10, now) then
		-- Jay's favourite fight: the boss's attention jumps between players
		local ps = players(def)
		if #ps > 0 then
			boss:setTarget(ps[math.random(#ps)])
		end
	end
end
PATTERNS.split = function(boss, state, now, def)
	if not state.flags.split and boss:getHealth() / boss:getMaxHealth() < 0.5 then
		state.flags.split = true
		boss:say("The " .. boss:getName() .. " cracks in two!", TALKTYPE_MONSTER_YELL)
		for _ = 1, 2 do
			Game.createMonster(def.elite, boss:getPosition(), true, false)
		end
		boss:addHealth(math.floor(boss:getMaxHealth() * 0.1))
	end
	PATTERNS.stomp(boss, state, now, def)
end
PATTERNS.ruin = function(boss, state, now, def)
	local hp = boss:getHealth() / boss:getMaxHealth()
	local phase = hp > 0.70 and 1 or (hp > 0.35 and 2 or 3)
	if phase > (state.phase or 1) then
		state.phase = phase
		boss:say(phase == 2 and "My blade burns!" or "Dance with ruin!", TALKTYPE_MONSTER_YELL)
		if phase == 2 then
			for _ = 1, 2 do
				Game.createMonster(def.elite, boss:getPosition(), true, false)
			end
		end
	end
	local t = boss:getTarget()
	local sweeps = phase == 3 and 3 or 1
	if t and every(state, "sweep", phase == 1 and 8 or 6, now) then
		for i = 0, sweeps - 1 do
			addEvent(function(bid, tid)
				local b, tg = Creature(bid), Creature(tid)
				if b and tg then
					local mn, mx = hit(def.floor, 2.6)
					SpireBoss.markTiles(bid, arc(b, tg), mn, mx)
				end
			end, i * 900, boss:getId(), t:getId())
		end
	end
	local ps = players(def)
	if #ps > 0 and every(state, "lunge", 14, now) then
		local far, best = nil, -1
		for _, p in ipairs(ps) do
			local d = boss:getPosition():getDistance(p:getPosition())
			if d > best then far, best = p, d end
		end
		local mn, mx = hit(def.floor, 2.8)
		SpireBoss.markTiles(boss:getId(), line(boss:getPosition(), far:getPosition(), 5), mn, mx)
	end
	if phase == 3 and #ps > 0 and every(state, "bounce", 10, now) then
		boss:setTarget(ps[math.random(#ps)])
	end
end

local function registerFloor(n, f)
	local P = "f" .. n .. "_"
	if not WorldPoints[P .. "boss_spawn"] then
		return false -- this floor has no map yet
	end
	SpireBoss.register(f.field, {
		floor = n, kind = "field", spawnPoint = P .. "field_spawn", elite = f.elite,
		room = { nw = P .. "pass_arena", radius = 12 },
		onThink = function(boss, state, now) PATTERNS[f.fieldPattern](boss, state, now, SpireBoss.defs[f.field]) end,
		onFirstKill = function(credit)
			if Floors.markFieldBoss(n, credit) then
				SpireGates.open(P .. "gate_pass")
				Game.broadcastMessage(string.format("%s has fallen! The labyrinth of Floor %d is open to all.", f.field, n), MESSAGE_EVENT_ADVANCE)
			end
		end,
	})
	SpireBoss.register(f.boss, {
		floor = n, kind = "floor", spawnPoint = P .. "boss_spawn", elite = f.elite,
		roomNW = P .. "boss_nw", roomSE = P .. "boss_se",
		onThink = function(boss, state, now) PATTERNS[f.bossPattern](boss, state, now, SpireBoss.defs[f.boss]) end,
		onFirstKill = function(credit, lastHit, duration)
			if Floors.recordClear(n, credit, lastHit, duration) then
				SpireGates.open(P .. "gate_next")
				Floors.announceClear(n, credit)
				for _, name in ipairs(credit) do
					local p = Player(name)
					if p and Floors.titles[n] then
						p:kv():scoped("spirebound-titles"):set(Floors.titles[n], os.time())
					end
				end
				if lastHit and Player(lastHit) then
					Player(lastHit):kv():scoped("spirebound-titles"):set("Last Blow (Floor " .. n .. ")", os.time())
				end
				local town = SpireHouses.floorTown[n + 1]
				if town then
					local size = 0
					for _, h in ipairs(Game.getHouses()) do
						if h:getTown():getId() == town then size = size + 1 end
					end
					SpireHouses.startHeadStart(town, credit, size, os.time())
				end
			end
		end,
		respawn = true,
	})
	return true
end

local startup = GlobalEvent("SpireFloorsStartup")
function startup.onStartup()
	SpireRemix.applyBosses(SpireFloorBosses, SpireSeason.current()) -- season remix (roadmap 8.2)
	for n, f in pairs(SpireFloorBosses) do
		if registerFloor(n, f) then
			local P = "f" .. n .. "_"
			if Floors.isLabyrinthOpen(n) then
				SpireGates.open(P .. "gate_pass")
			else
				SpireBoss.spawn(f.field)
			end
			if Floors.isOpen(n + 1) then
				SpireGates.open(P .. "gate_next")
			end
			SpireBoss.spawn(f.boss)
		end
	end
	return true
end
startup:register()
