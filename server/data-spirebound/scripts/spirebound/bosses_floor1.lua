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
				SpireBoss.grantTitle(name, Floors.titles[FLOOR])
			end
			if lastHit then
				SpireBoss.grantTitle(lastHit, "Last Blow (Floor " .. FLOOR .. ")")
			end
			for _, cid in ipairs(Game.getPlayers()) do
				cid:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
			end
		end
	end,
	respawn = true,
	private = { spawn = "boss_private_floor1", nw = "boss_private_floor1_nw", se = "boss_private_floor1_se", door = "lab3_up" },
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
	local nwName, seName = state.roomNW or def.roomNW, state.roomSE or def.roomSE
	if nwName then
		players = SpireBoss.playersInArea(WorldPoints[nwName], WorldPoints[seName])
	else
		local c = WorldPoints[def.room.nw]
		players = Game.getSpectators(c, false, true, def.room.radius, def.room.radius, def.room.radius, def.room.radius)
	end
	local out = WorldPoints.lab3_up and Position(WorldPoints.lab3_up.x + 1, WorldPoints.lab3_up.y, WorldPoints.lab3_up.z)
	-- Q13: a floor boss room stays sealed until its day this season
	if def.kind == "floor" and not state.private then
		local open, at = SpireBoss.calendarOpen(def.floor, now)
		if not open and out then
			for _, p in ipairs(players) do
				if not p:getGroup():getAccess() then
					p:teleportTo(out)
					p:sendCancelMessage("This hall is sealed until " .. os.date("%A %d %B, %H:%M", at) .. ". The whole tower waits for it.")
				end
			end
			return true
		end
	end
	-- 20 players at most: the latest to arrive are sent back out
	state.arrived = state.arrived or {}
	for _, p in ipairs(players) do
		state.arrived[p:getName()] = state.arrived[p:getName()] or now
	end
	if #players > SpireBoss.ROOM_CAP and out then
		table.sort(players, function(a, b)
			return state.arrived[a:getName()] < state.arrived[b:getName()]
		end)
		for i = SpireBoss.ROOM_CAP + 1, #players do
			players[i]:teleportTo(out)
			players[i]:sendCancelMessage("The hall holds " .. SpireBoss.ROOM_CAP .. " climbers at most.")
		end
	end
	-- headcount for enrage: the most players present at any time (more arrivals shorten the timer)
	if state.started then
		state.headcount = math.max(state.headcount, math.min(#players, SpireBoss.ROOM_CAP))
	end
	if SpireBoss.shouldReset(state, now, #players) then
		if state.private then -- a private fight that was abandoned: the hall empties
			SpireBoss.privateBusy[def.floor] = nil
			SpireBoss.fights[creature:getId()] = nil
			creature:remove()
			return true
		end
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
	SpireGear = SpireGear or {}
	SpireGear.lastTopFighter = SpireGear.lastTopFighter or {}
	SpireGear.lastTopFighter[creature:getName()] = credit[1] -- R12: the boss piece goes to the fiercest foe
	local lastHit = nil
	if killer then
		local kp = killer:getPlayer() or (killer:getMaster() and killer:getMaster():getPlayer())
		lastHit = kp and kp:getName() or nil
	end
	logger.info("[Spirebound] {} killed; credit: {}; last hit: {}", creature:getName(), table.concat(credit, ", "), tostring(lastHit))
	if state.private then -- a private repeat kill: lock the party out for 20 hours, no world-first actions
		SpireBoss.privateBusy[def.floor] = nil
		for _, name in ipairs(state.private.members) do
			local p = Player(name)
			if p then
				p:kv():scoped("spirebound-bosslock"):set(tostring(def.floor), now)
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Private victory! You may face this hall alone again in 20 hours.")
			end
		end
		for _, name in ipairs(credit) do
			SpireHouses.awardSigil(name, creature:getName())
		end
		return true
	end
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
	local now = os.time()
	if primaryType == COMBAT_HEALING and attacker and attacker:isPlayer() and creature:isPlayer() then
		-- healing a fighter counts toward the healer's credit in that fight (R9)
		for _, st in pairs(SpireBoss.fights) do
			local h = st.started and st.hits[creature:getName()]
			if h and now - h.last <= SpireBoss.CREDIT_WINDOW then
				SpireBoss.recordHit(st, attacker:getName(), math.max(0, primaryDamage), now)
			end
		end
	end
	if state and primaryType ~= COMBAT_HEALING and creature:isPlayer() then
		-- soaking the boss's hits counts half (R9)
		SpireBoss.recordHit(state, creature:getName(), math.floor((math.max(0, primaryDamage) + math.max(0, secondaryDamage)) * SpireBoss.TAKEN_WEIGHT), now)
	end
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
	SpireBoss.applyPending(player) -- titles earned while offline
	return true
end
login:register()

-- Private repeat kills (R9): after a floor is cleared, a party of 1-5 can fight its boss in a hall of its own,
-- once per character every 20 hours. The party leader says !private at the top of the labyrinth.
SpireBoss.privateBusy = SpireBoss.privateBusy or {}
local private = TalkAction("!private")
function private.onSay(player, words, param)
	local floor, def, name = nil, nil, nil
	for n, d in pairs(SpireBoss.defs) do
		if d.private and WorldPoints[d.private.door] and player:getPosition():getDistance(WorldPoints[d.private.door]) <= 4
			and player:getPosition().z == WorldPoints[d.private.door].z then
			floor, def, name = d.floor, d, n
		end
	end
	if not def then
		player:sendCancelMessage("Say !private at the top of a labyrinth, by the way into the boss hall.")
		return false
	end
	local party = player:getParty()
	local members = { player }
	if party then
		if party:getLeader() ~= player then
			player:sendCancelMessage("Only the party leader can open the private hall.")
			return false
		end
		for _, m in ipairs(party:getMembers()) do
			table.insert(members, m)
		end
	end
	local now, list, near = os.time(), {}, true
	for _, m in ipairs(members) do
		table.insert(list, { name = m:getName(), lockedAt = m:kv():scoped("spirebound-bosslock"):get(tostring(floor)) })
		if m:getPosition():getDistance(player:getPosition()) > 5 or m:getPosition().z ~= player:getPosition().z then
			near = false
		end
	end
	local ok, why = SpireBoss.privateCheck(list, near, Floors.isOpen(floor + 1), SpireBoss.privateBusy[floor] ~= nil, now)
	if not ok then
		player:sendCancelMessage(why)
		return false
	end
	local boss = Game.createMonster(name, WorldPoints[def.private.spawn], false, true)
	if not boss then
		player:sendCancelMessage("The private hall could not be prepared. Try again.")
		return false
	end
	local st = SpireBoss.newState()
	st.private = { floor = floor, members = {} }
	st.roomNW, st.roomSE = def.private.nw, def.private.se
	st.started = now
	st.lastPlayerDamage = now
	SpireBoss.fights[boss:getId()] = st
	SpireBoss.privateBusy[floor] = boss:getId()
	local entry = WorldPoints[def.private.spawn]
	for i, m in ipairs(members) do
		table.insert(st.private.members, m:getName())
		m:teleportTo(Position(entry.x - 2 + (i - 1), entry.y + 8, entry.z))
		m:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The private hall seals behind your party.")
	end
	return false
end
private:groupType("normal")
private:register()

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
