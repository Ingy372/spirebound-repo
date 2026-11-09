-- House management spell (from Canary, with Spirebound words and vocations).
local spell = Spell("instant")

function spell.onCastSpell(creature, variant)
	local currentPos = creature:getPosition()
	local forwardPos = creature:getPosition()
	forwardPos:getNextPosition(creature:getDirection())

	local tile = Tile(currentPos)
	local house = tile and tile:getHouse()
	local doorId = house and house:getDoorIdByPosition(forwardPos)

	if not doorId then
		tile = Tile(currentPos)
		house = tile and tile:getHouse()
		doorId = house and house:getDoorIdByPosition(currentPos)
	end

	if not doorId or not house:canEditAccessList(doorId, creature) then
		creature:sendCancelMessage(RETURNVALUE_NOTPOSSIBLE)
		creature:getPosition():sendMagicEffect(CONST_ME_POFF)
		return false
	end

	creature:setEditHouse(house, doorId)
	creature:sendHouseWindow(house, doorId)
	return true
end

spell:name("House Door List")
spell:words("house doors")
spell:group("support")
spell:vocation("arcanist;true", "high arcanist;true", "mystic;true", "elder mystic;true", "ranger;true", "far warden;true", "vanguard;true", "blade warden;true")
spell:level(8)
spell:cooldown(2 * 1000)
spell:groupCooldown(2 * 1000)
spell:castSound(SOUND_EFFECT_TYPE_SPELL_EDIT_DOOR)
spell:needCasterTargetOrDirection(true)
spell:isAggressive(false)
spell:register()
