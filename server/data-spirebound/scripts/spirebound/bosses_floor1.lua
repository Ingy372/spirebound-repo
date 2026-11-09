-- Floor 1 bosses (DESIGN.md 9.2): the Gate Hound (field boss at the Pass) and the Axe-Lord of the Stair (floor boss).
-- Uses lib/spirebound/bosses.lua and lib/spirebound/floors.lua.

local FLOOR = 1

-- Remove the boulders that seal a gate (positions come from the generated world_points.lua)
local function openGate(prefix)
	for name, pos in pairs(WorldPoints) do
		if name == prefix or name:sub(1, #prefix + 1) == prefix .. "_" then
			local tile = Tile(pos)
			local boulder = tile and tile:getItemById(1772)
			if boulder then
				boulder:remove()
				pos:sendMagicEffect(CONST_ME_POFF)
			end
		end
	end
end
SpireGates = { open = openGate }

SpireBoss.register("Gate Hound", {
	floor = FLOOR, kind = "field", spawnPoint = "gate_hound_spawn",
	room = { nw = "pass_arena", radius = 12 },
	onThink = function(boss, state, now)
		-- Howl every 20 s: telegraphed ring around the hound
		if not state.flags.nextHowl or now >= state.flags.nextHowl then
			state.flags.nextHowl = now + 20
			local c = boss:getPosition()
			local tiles = {}
			for dx = -2, 2 do
				for dy = -2, 2 do
					if math.max(math.abs(dx), math.abs(dy)) == 2 then
						table.insert(tiles, Position(c.x + dx, c.y + dy, c.z))
					end
				end
			end
			boss:say("The Gate Hound howls!", TALKTYPE_MONSTER_YELL)
			SpireBoss.markTiles(boss:getId(), tiles, -120, -220)
		end
	end,
	onFirstKill = function(credit, lastHit)
		if Floors.markFieldBoss(FLOOR, credit) then
			openGate("gate_pass")
			Game.broadcastMessage("The Gate Hound has fallen! The labyrinth of Floor 1 is open to all.", MESSAGE_EVENT_ADVANCE)
		end
	end,
})

SpireBoss.register("Axe-Lord of the Stair", {
	floor = FLOOR, kind = "floor", spawnPoint = "axe_lord_spawn",
	roomNW = "boss_room_floor1_nw", roomSE = "boss_room_floor1_se",
	onThink = function(boss, state, now)
		local hpPct = boss:getHealth() / boss:getMaxHealth()
		-- Phase 2 at 60%: summon two Sentinel guards (once); mark covers 2 tiles
		if state.phase == 1 and hpPct <= 0.60 then
			state.phase = 2
			boss:say("Guards! To me!", TALKTYPE_MONSTER_YELL)
			for _ = 1, 2 do
				Game.createMonster("Ruin Sentinel", boss:getPosition(), true, false)
			end
		end
		-- Phase 3 below 25%: drops the axe, draws a long curved blade; 3-tile line toward the furthest player
		if state.phase == 2 and hpPct <= 0.25 then
			state.phase = 3
			boss:say("Enough! Face the blade!", TALKTYPE_MONSTER_YELL)
			local o = boss:getOutfit()
			o.lookType = 131
			o.lookBody, o.lookLegs = 79, 114
			boss:setOutfit(o)
		end
		if not state.flags.nextMark or now >= state.flags.nextMark then
			state.flags.nextMark = now + 6
			local players = SpireBoss.playersInArea(WorldPoints["boss_room_floor1_nw"], WorldPoints["boss_room_floor1_se"])
			if #players == 0 then
				return
			end
			local tiles = {}
			if state.phase < 3 then
				local p = players[math.random(#players)]:getPosition()
				table.insert(tiles, Position(p.x, p.y, p.z))
				if state.phase == 2 then
					table.insert(tiles, Position(p.x + 1, p.y, p.z))
				end
				SpireBoss.markTiles(boss:getId(), tiles, -180, -320)
			else
				-- furthest player, 3-tile line from the boss toward them
				local bp, far, best = boss:getPosition(), nil, -1
				for _, pl in ipairs(players) do
					local d = bp:getDistance(pl:getPosition())
					if d > best then
						far, best = pl, d
					end
				end
				local tp = far:getPosition()
				local dx = tp.x == bp.x and 0 or (tp.x > bp.x and 1 or -1)
				local dy = tp.y == bp.y and 0 or (tp.y > bp.y and 1 or -1)
				for i = 1, 3 do
					table.insert(tiles, Position(bp.x + dx * i, bp.y + dy * i, bp.z))
				end
				SpireBoss.markTiles(boss:getId(), tiles, -260, -420)
			end
		end
	end,
	onFirstKill = function(credit, lastHit, duration)
		if Floors.recordClear(FLOOR, credit, lastHit, duration) then
			openGate("gate_floor2")
			Floors.announceClear(FLOOR, credit)
			local town = SpireHouses.floorTown[FLOOR + 1]
			if town then
				local size = 0
				for _, h in ipairs(Game.getHouses()) do
					if h:getTown():getId() == town then size = size + 1 end
				end
				SpireHouses.startHeadStart(town, credit, size, os.time())
			end
			for _, name in ipairs(credit) do
				local p = Player(name)
				if p then
					p:kv():scoped("spirebound-titles"):set(Floors.titles[FLOOR], os.time())
					p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. Floors.titles[FLOOR] .. ".")
				end
			end
			if lastHit then
				local p = Player(lastHit)
				if p then
					p:kv():scoped("spirebound-titles"):set("Last Blow (Floor " .. FLOOR .. ")", os.time())
				end
			end
			for _, cid in ipairs(Game.getPlayers()) do
				cid:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
			end
		end
	end,
	respawn = true,
})

-- Wiring --------------------------------------------------------------

local health = CreatureEvent("SpireBossHealth")
function health.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local state = SpireBoss.fights[creature:getId()]
	local player = attacker and (attacker:getPlayer() or (attacker:getMaster() and attacker:getMaster():getPlayer()))
	if state and player and primaryType ~= COMBAT_HEALING then
		local now = os.time()
		if not state.started then
			state.started = now
		end
		SpireBoss.recordHit(state, player:getName(), primaryDamage + secondaryDamage, now)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
health:register()

local think = CreatureEvent("SpireBossThink")
function think.onThink(creature, interval)
	local def = SpireBoss.defs[creature:getName()]
	local state = SpireBoss.fights[creature:getId()]
	if not def or not state then
		return true
	end
	local now = os.time()
	local players
	if def.roomNW then
		players = SpireBoss.playersInArea(WorldPoints[def.roomNW], WorldPoints[def.roomSE])
	else
		local c = WorldPoints[def.room.nw]
		players = Game.getSpectators(c, false, true, def.room.radius, def.room.radius, def.room.radius, def.room.radius)
	end
	-- headcount for enrage: most players present during the first 60 s
	if state.started and now - state.started <= 60 then
		state.headcount = math.max(state.headcount, #players)
	end
	if SpireBoss.shouldReset(state, now, #players) then
		creature:addHealth(creature:getMaxHealth())
		SpireBoss.fights[creature:getId()] = SpireBoss.newState()
		creature:say("The " .. creature:getName() .. " recovers.", TALKTYPE_MONSTER_SAY)
		return true
	end
	if def.onThink and state.started then
		def.onThink(creature, state, now)
	end
	return true
end
think:register()

local death = CreatureEvent("SpireBossDeath")
function death.onDeath(creature, corpse, killer, mostDamageKiller, unjustified, mostDamageUnjustified)
	local def = SpireBoss.defs[creature:getName()]
	local state = SpireBoss.fights[creature:getId()]
	SpireBoss.fights[creature:getId()] = nil
	if not def or not state then
		return true
	end
	local now = os.time()
	local credit = SpireBoss.credited(state, now)
	local lastHit = nil
	if killer then
		local kp = killer:getPlayer() or (killer:getMaster() and killer:getMaster():getPlayer())
		lastHit = kp and kp:getName() or nil
	end
	logger.info("[Spirebound] {} killed; credit: {}; last hit: {}", creature:getName(), table.concat(credit, ", "), tostring(lastHit))
	def.onFirstKill(credit, lastHit, state.started and (now - state.started) or 0)
	for _, name in ipairs(credit) do
		SpireHouses.awardSigil(name, creature:getName())
	end
	if def.respawn then
		local name = creature:getName()
		addEvent(function()
			SpireBoss.spawn(name)
		end, SpireBoss.REPEAT_RESPAWN * 1000)
	end
	return true
end
death:register()

-- Enrage: bosses hit harder after the enrage timer (applies to damage players take from a boss)
local enrage = CreatureEvent("SpireBossEnrage")
function enrage.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local state = attacker and SpireBoss.fights[attacker:getId()]
	if state and primaryType ~= COMBAT_HEALING then
		local mult = SpireBoss.enrageMultiplier(state, os.time())
		if mult > 1 then
			primaryDamage = math.floor(primaryDamage * mult)
			secondaryDamage = math.floor(secondaryDamage * mult)
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
enrage:register()

local login = CreatureEvent("SpireBossLogin")
function login.onLogin(player)
	player:registerEvent("SpireBossEnrage")
	return true
end
login:register()

-- Startup: open gates that are already open, spawn bosses that should exist
local startup = GlobalEvent("SpireFloor1Startup")
function startup.onStartup()
	if Floors.isLabyrinthOpen(FLOOR) then
		openGate("gate_pass")
	else
		SpireBoss.spawn("Gate Hound")
	end
	if Floors.isOpen(FLOOR + 1) then
		openGate("gate_floor2")
	end
	SpireBoss.spawn("Axe-Lord of the Stair")
	return true
end
startup:register()
