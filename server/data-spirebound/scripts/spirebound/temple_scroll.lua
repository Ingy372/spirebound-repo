-- Temple teleport scroll (roadmap J8, from the top-server research): back to your home temple, used up on use.
-- A small everyday gold sink sold by Runewright Mael. Never in a fight, never out of a boss room or a Deadzone.
local templeScroll = Action()

function templeScroll.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local zone = SpirePvP and SpirePvP.zoneAt(player:getPosition()) or "open"
	if zone == "bossroom" or zone == "deadzone" or zone == "arena" or zone == "siege" then
		player:sendCancelMessage("The tower's magic is too strong here: the scroll won't work.")
		return true
	end
	local inPz = player:getTile():hasFlag(TILESTATE_PROTECTIONZONE)
	local inFight = player:isPzLocked() or player:getCondition(CONDITION_INFIGHT, CONDITIONID_DEFAULT)
	if not inPz and inFight then
		player:sendCancelMessage("You can't use this while you're in a fight.")
		fromPosition:sendMagicEffect(CONST_ME_POFF)
		return true
	end
	fromPosition:sendMagicEffect(CONST_ME_TELEPORT)
	player:teleportTo(player:getTown():getTemplePosition())
	player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	item:remove(1)
	return true
end

templeScroll:id(25718)
templeScroll:register()
