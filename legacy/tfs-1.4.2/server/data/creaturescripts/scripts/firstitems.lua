-- Starting kit (06 Creation). Phase 0 gives the shared part; the path weapon arrives with vocations in phase 1.
-- Ids: 2012 backpack, 8001 Travel Bread, 8011 Minor Salve, 8021 Minor Tonic, 2002 silver col (100 col).
function onLogin(player)
	if player:getLastLoginSaved() == 0 then
		local backpack = player:addItem(2012, 1, true, 1, CONST_SLOT_BACKPACK)
		if backpack then
			backpack:addItem(8001, 10)
			backpack:addItem(8011, 5)
			backpack:addItem(8021, 2)
			backpack:addItem(2002, 1)
		end
	end
	return true
end
