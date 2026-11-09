-- Exercise dummy kit (Housewright Orla): use it on your house floor to build your own training room dummy.
-- (Ordinary furniture kits are handled by scripts/actions/other/construction_kits.lua.)
local kit = Action()
function kit.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if item:getCustomAttribute("unWrapId") then
		return false -- a wrapped piece of furniture: the normal unwrap handles it
	end
	local onFloor = fromPosition.x ~= CONTAINER_POSITION
	local tile = onFloor and Tile(fromPosition) or nil
	local house = tile and tile:getHouse()
	local access = house and (house:getOwnerGuid() == player:getGuid() or house:canEditAccessList(GUEST_LIST, player)) or false
	local ok, why = SpireHouses.canBuild(item:getId(), onFloor, house ~= nil, access)
	if not ok then
		player:sendCancelMessage(why)
		return true
	end
	item:transform(SpireHouses.KITS[item:getId()])
	fromPosition:sendMagicEffect(CONST_ME_POFF)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your training room is ready. Use training weapons on the dummy, just like the one in town.")
	return true
end
kit:id(23398)
kit:register()
