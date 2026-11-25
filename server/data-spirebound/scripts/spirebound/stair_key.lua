-- The Stair Key (P9; rules in lib/spirebound/quests.lua, SpireStairKey). The labyrinth's last teleport lands at the
-- Axe-Lord's hall door; without the key the climber is sent back with a note of what is missing.

-- the Stonehorn Ram: everyone who hurt it gets the piece
local ram = CreatureEvent("SpireStairKeyRam")
function ram.onDeath(creature, corpse, killer, mostDamageKiller)
	local seen = {}
	for cid, _ in pairs(creature:getDamageMap() or {}) do
		local c = Creature(cid)
		local p = c and (c:getPlayer() or (c:getMaster() and c:getMaster():getPlayer()))
		if p and not seen[p:getId()] then
			seen[p:getId()] = true
			if SpireQuests.find(p, "stairkey", "ram") then
				SpireStairKey.update(p)
			end
		end
	end
	return true
end
ram:register()

-- the hall door: the arrival tile of the labyrinth's top teleport (maps/layout_floor1.py: boss room door at y + 21)
local hall = WorldPoints.boss_room_floor1
local door = hall and Position(hall.x, hall.y + 9, hall.z)
local back = WorldPoints.lab3_up and Position(WorldPoints.lab3_up.x + 1, WorldPoints.lab3_up.y, WorldPoints.lab3_up.z)
SpireStairKey.door, SpireStairKey.back = door, back

function SpireStairKey.missingText(player)
	local p = SpireStairKey.pieces(player)
	local miss = {}
	if not p.hound then table.insert(miss, "help defeat the Gate Hound in the Pass") end
	if not p.ram then table.insert(miss, "help defeat the Stonehorn Ram at the Old Watchtower") end
	if not p.iron then table.insert(miss, "finish Hunter Brannoch's Iron for the Stair") end
	return table.concat(miss, ", ")
end

local step = MoveEvent()
function step.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player or player:getGroup():getAccess() or SpireStairKey.has(player) then
		return true
	end
	player:teleportTo(back)
	back:sendMagicEffect(CONST_ME_TELEPORT)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "A sealed door bars the Axe-Lord's hall. It opens only with the Stair Key ("
		.. SpireStairKey.count(player) .. " of 3 pieces). Still to do: " .. SpireStairKey.missingText(player) .. ".")
	return true
end
if door and back then
	step:type("stepin")
	step:position(door)
	step:register()
end

local login = CreatureEvent("SpireStairKeyLogin")
function login.onLogin(player)
	SpireStairKey.update(player, true) -- pieces earned before the key existed count (old Gate Hound credit, Iron for the Stair)
	return true
end
login:register()
