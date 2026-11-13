function onSpeak(player, type, message)
	if SpireMod and SpireMod.blocked(message) and player:getGroup():getId() < GROUP_TYPE_GAMEMASTER then
		player:sendCancelMessage("That word isn't allowed in public chat. Say !rules for the rules.")
		return false
	end
	local playerGroupType = player:getGroup():getId()
	if player:getLevel() == 1 and playerGroupType < GROUP_TYPE_GAMEMASTER then
		player:sendCancelMessage("You may not speak into channels as long as you are on level 1.")
		return false
	end

	if type == TALKTYPE_CHANNEL_Y then
		if playerGroupType >= GROUP_TYPE_GAMEMASTER then
			type = TALKTYPE_CHANNEL_O
		end
	elseif type == TALKTYPE_CHANNEL_O then
		if playerGroupType < GROUP_TYPE_GAMEMASTER then
			type = TALKTYPE_CHANNEL_Y
		end
	elseif type == TALKTYPE_CHANNEL_R1 then
		if playerGroupType < GROUP_TYPE_GAMEMASTER and not player:hasFlag(PlayerFlag_CanTalkRedChannel) then
			type = TALKTYPE_CHANNEL_Y
		end
	end
	return type
end
