-- The Proving (roadmap G2; Jay, 2026-11-24: "continue the tutorial after picking a class", "a small one person boss
-- fight. you decide how should all go"). The Registrar sends every new character to a hall under the Arrival Yard
-- (maps/layout_floor1.py, z 9). There: try the new spells on a few rats, then step on the glowing stone and face
-- Bramblejaw alone in one of three closed pits. Nobody can die here: at the last point of health the Warden pulls you
-- out to try again (this matters for Death Game characters). Winning sends you to Hearthgate with a small reward.

SpireProving = SpireProving or {
	PITS = 3,
	TIME_LIMIT = 300, -- seconds in a pit before the Warden calls it off
	STOMP_EVERY = 7, -- seconds between Bramblejaw's stomps
	STOMP_WARN_MS = 1200, -- red smoke first, then the hit: long enough for a new player to step away
	STOMP_MIN = 10, STOMP_MAX = 18,
	REWARD_GOLD = 150,
	pits = {}, -- i -> { pid, boss, t, stomp }
}

local function point(name)
	local p = WorldPoints[name]
	return p and Position(p.x, p.y, p.z)
end

local function scope(player)
	return player:kv():scoped("spirebound-proving")
end

function SpireProving.done(player)
	return scope(player):get("done") == true
end

-- Pure: the first free pit, or nil
function SpireProving.freePit(pits, n)
	for i = 1, n do
		if not pits[i] then
			return i
		end
	end
	return nil
end

-- Pure: is pos inside the box nw..se (same floor)?
function SpireProving.inBox(pos, nw, se)
	return nw ~= nil and se ~= nil and pos.z == nw.z and pos.x >= nw.x and pos.x <= se.x and pos.y >= nw.y and pos.y <= se.y
end

function SpireProving.pitAt(pos)
	for i = 1, SpireProving.PITS do
		if SpireProving.inBox(pos, WorldPoints["proving_pit_" .. i .. "_nw"], WorldPoints["proving_pit_" .. i .. "_se"]) then
			return i
		end
	end
	return nil
end

local function pitOf(field, id)
	for i, pit in pairs(SpireProving.pits) do
		if pit[field] == id then
			return i, pit
		end
	end
	return nil
end

-- Empty pit i: remove the boss, send its climber (if still inside) to `sendTo`.
function SpireProving.close(i, sendTo)
	local pit = SpireProving.pits[i]
	if not pit then
		return
	end
	SpireProving.pits[i] = nil
	local boss = Creature(pit.boss)
	if boss then
		boss:remove()
	end
	local p = Player(pit.pid)
	if p then
		p:unregisterEvent("SpireProvingGuard")
		if sendTo and SpireProving.pitAt(p:getPosition()) == i then
			p:teleportTo(sendTo)
			sendTo:sendMagicEffect(CONST_ME_TELEPORT)
		end
	end
end

function SpireProving.enter(player)
	if SpireProving.done(player) then
		local temple = player:getTown() and player:getTown():getTemplePosition()
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You have already passed the Proving. On to Hearthgate.")
		if temple then
			player:teleportTo(temple)
			temple:sendMagicEffect(CONST_ME_TELEPORT)
		end
		return true
	end
	if pitOf("pid", player:getId()) then
		return true
	end
	local i = SpireProving.freePit(SpireProving.pits, SpireProving.PITS)
	if not i then
		player:sendCancelMessage("All three pits are in use. Wait a moment and step on the stone again.")
		return false
	end
	local boss = Game.createMonster("Bramblejaw", point("proving_pit_" .. i .. "_boss"), false, true)
	if not boss then
		player:sendCancelMessage("The pit is not ready. Try again in a moment.")
		return false
	end
	SpireProving.pits[i] = { pid = player:getId(), boss = boss:getId(), t = os.time(), stomp = os.time() + 3 }
	player:registerEvent("SpireProvingGuard")
	player:addHealth(player:getMaxHealth())
	player:addMana(player:getMaxMana())
	local to = point("proving_pit_" .. i .. "_player")
	player:teleportTo(to)
	to:sendMagicEffect(CONST_ME_TELEPORT)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Bramblejaw! Click it to target it, then use your attack spell (on your action bar, or say its words). "
		.. "When red smoke rises around it, step away. Heal yourself when your health drops below half.")
	return true
end

-- The glowing stone in the hall
local stone = MoveEvent()
function stone.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player then
		return true
	end
	if not SpireProving.enter(player) then
		player:teleportTo(fromPosition, true)
	end
	return true
end
if WorldPoints.proving_entry then
	stone:position(WorldPoints.proving_entry)
end
stone:type("stepin")
stone:register()

-- The skip in the north-east corner (Grok session 2: a tester took it for the fight stone). The first step only
-- warns; a second step within 30 seconds goes to Hearthgate.
SpireProving.SKIP_CONFIRM = 30
local skipWarned = {} -- player id -> os.time() of the warning
local skip = MoveEvent()
function skip.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player then
		return true
	end
	local pid = player:getId()
	local since = systemTime() - (skipWarned[pid] or 0) -- milliseconds
	if not SpireProving.done(player) and since < 2500 then -- still walking on from the warning: not a real second step
		player:teleportTo(fromPosition, true)
		return true
	end
	if not SpireProving.done(player) and since > SpireProving.SKIP_CONFIRM * 1000 then
		skipWarned[pid] = systemTime()
		player:teleportTo(fromPosition, true)
		position:sendMagicEffect(CONST_ME_TELEPORT)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "This swirl skips Bramblejaw and goes straight to Hearthgate. "
			.. "The fight is the glowing stone with the sparks, 4 steps south of this swirl. Step on the swirl again to leave anyway.")
		return true
	end
	skipWarned[pid] = nil
	local temple = player:getTown() and player:getTown():getTemplePosition() or point("temple_hearthgate")
	player:teleportTo(temple)
	temple:sendMagicEffect(CONST_ME_TELEPORT)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Welcome to Hearthgate. " .. SpireHunt.advice(player:getLevel()) .. " Say !hunt any time to hear this again.")
	return true
end
if WorldPoints.proving_skip then
	skip:position(WorldPoints.proving_skip)
end
skip:type("stepin")
skip:register()

-- Bramblejaw's stomp: red smoke on the tiles around it, then a hit on anyone still standing there
local think = CreatureEvent("SpireProvingThink")
function think.onThink(creature, interval)
	local i, pit = pitOf("boss", creature:getId())
	if not pit or os.time() < pit.stomp then
		return true
	end
	pit.stomp = os.time() + SpireProving.STOMP_EVERY
	local c = creature:getPosition()
	local tiles = {}
	for dx = -1, 1 do
		for dy = -1, 1 do
			local p = Position(c.x + dx, c.y + dy, c.z)
			table.insert(tiles, p)
			p:sendMagicEffect(CONST_ME_REDSMOKE)
		end
	end
	creature:say("Bramblejaw rears up! Step back!", TALKTYPE_MONSTER_SAY)
	-- say what to do in the Server Log too (Grok session 3: "rears up" and the red smoke didn't tell anyone where to go)
	local climber = pit.pid and Player(pit.pid)
	if climber then
		climber:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Bramblejaw is about to stomp: step two tiles away from it, out of the red smoke, then come back and hit it.")
	end
	local bossId = creature:getId()
	addEvent(function()
		local boss = Creature(bossId)
		if not boss then
			return
		end
		for _, p in ipairs(tiles) do
			p:sendMagicEffect(CONST_ME_GROUNDSHAKER)
			local tile = Tile(p)
			for _, cr in ipairs(tile and tile:getCreatures() or {}) do
				if cr:isPlayer() then
					doTargetCombatHealth(boss, cr, COMBAT_PHYSICALDAMAGE, -SpireProving.STOMP_MIN, -SpireProving.STOMP_MAX, CONST_ME_DRAWBLOOD)
				end
			end
		end
	end, SpireProving.STOMP_WARN_MS)
	return true
end
think:register()

-- Winning
local death = CreatureEvent("SpireProvingDeath")
function death.onDeath(creature, corpse, killer, mostDamageKiller, lastHitUnjustified, mostDamageUnjustified)
	local i, pit = pitOf("boss", creature:getId())
	if not pit then
		return true
	end
	pit.boss = nil
	local player = Player(pit.pid)
	if player then
		scope(player):set("done", true)
		player:addItem(3031, SpireProving.REWARD_GOLD)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You passed the Proving! %d gold is in your backpack. "
			.. "Open Bramblejaw's body to take what it carried: in 10 seconds you are sent to Hearthgate.", SpireProving.REWARD_GOLD))
	end
	local pid = pit.pid
	addEvent(function()
		local pi = pitOf("pid", pid)
		local p = Player(pid)
		local temple = p and p:getTown() and p:getTown():getTemplePosition()
		if pi then
			SpireProving.close(pi, temple)
		end
		if p then
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Welcome to Hearthgate. " .. SpireHunt.advice(p:getLevel()) .. " Say !hunt any time to hear this again.")
		end
	end, 10000)
	return true
end
death:register()

-- Nobody dies in the Proving: at the last point of health the Warden pulls you out
local guard = CreatureEvent("SpireProvingGuard")
function guard.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local player = creature:getPlayer()
	if not player or primaryType == COMBAT_HEALING then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local i = pitOf("pid", player:getId())
	if not i or SpireProving.pitAt(player:getPosition()) ~= i then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	if primaryDamage + secondaryDamage >= player:getHealth() then
		primaryDamage, secondaryDamage = math.max(0, player:getHealth() - 1), 0
		local pid = player:getId()
		addEvent(function()
			local p = Player(pid)
			local pi = pitOf("pid", pid)
			if pi then
				SpireProving.close(pi, point("proving_arrival"))
			end
			if p then
				p:addHealth(p:getMaxHealth())
				p:addMana(p:getMaxMana())
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Warden Ketta pulls you out just in time. Heal sooner (your heal spell is on the action bar), "
					.. "step out of the red smoke, and step on the red glowing stone to try again.")
			end
		end, 0)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
guard:register()

-- Every 2 seconds: the stone glows, and pits whose climber left, logged out or ran out of time are emptied
local tick = GlobalEvent("SpireProvingTick")
function tick.onThink(interval)
	if WorldPoints.proving_entry then
		point("proving_entry"):sendMagicEffect(CONST_ME_MAGIC_RED) -- red: the fight
	end
	if WorldPoints.proving_skip then
		point("proving_skip"):sendMagicEffect(CONST_ME_TELEPORT) -- blue swirl: the way out
	end
	local now = os.time()
	for i, pit in pairs(SpireProving.pits) do
		local p = Player(pit.pid)
		if not p or SpireProving.pitAt(p:getPosition()) ~= i then
			if pit.boss or not p then
				SpireProving.close(i)
			end
		elseif now - pit.t > SpireProving.TIME_LIMIT then
			SpireProving.close(i, point("proving_arrival"))
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Time is up. Rest a moment and step on the red glowing stone to try again.")
		end
	end
	return true
end
tick:interval(2000)
tick:register()

-- Logged out inside a pit: start the next session back in the hall
local login = CreatureEvent("SpireProvingLogin")
function login.onLogin(player)
	if SpireProving.pitAt(player:getPosition()) and not pitOf("pid", player:getId()) then
		local to = point("proving_arrival")
		if to then
			player:teleportTo(to)
		end
	end
	return true
end
login:register()
