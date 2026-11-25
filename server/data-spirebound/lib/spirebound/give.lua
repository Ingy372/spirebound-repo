-- Handing items to a player that must never go missing (starter kits, tutorial cheese).
-- Grok session 3 (2026-11-25): a level 3 Ranger could not carry the whole starter kit, so the game dropped the last
-- pieces (the torch and the quiver with its arrows) on the Registrar's floor and teleported the character away: a
-- Ranger with a bow and nothing to shoot. These items ignore carrying weight, and only if even that fails do they
-- land at the player's feet.
SpireGive = {}

-- The weight flag only works for items going into the backpack; worn slots (the quiver in the shield hand) still check
-- carrying weight. So a whole kit is handed over inside SpireGive.withRoom: the limit is lifted for that moment, and if
-- the character ends up overloaded (they could not pick up loot), they get just enough room back (FREE_AFTER, in
-- hundredths of an oz as the engine counts).
SpireGive.FREE_AFTER = 100 * 100

function SpireGive.withRoom(player, fn)
	local cap = player:getCapacity()
	player:setCapacity(cap + 1000000 * 100)
	local ok, err = pcall(fn)
	player:setCapacity(cap)
	local free = player:getFreeCapacity()
	if free < SpireGive.FREE_AFTER then
		player:setCapacity(cap + SpireGive.FREE_AFTER - free)
	end
	if not ok then
		error(err)
	end
end

-- slot: a CONST_SLOT_* to wear the item there when it fits (otherwise it goes in the backpack)
function SpireGive.item(player, id, count, slot)
	local item = Game.createItem(id, count or 1)
	if not item then
		return nil
	end
	if slot and slot ~= CONST_SLOT_WHEREEVER and not player:getSlotItem(slot)
		and player:addItemEx(item, false, slot, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		return item
	end
	if player:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		return item
	end
	-- the backpack is full: fall back to the game's usual rule (it lands at the player's feet)
	if player:addItemEx(item, true) == RETURNVALUE_NOERROR then
		return item
	end
	return nil
end

-- into a container the player carries (arrows into a quiver), ignoring weight
function SpireGive.into(container, id, count)
	local item = Game.createItem(id, count or 1)
	if item and container:addItemEx(item, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		return item
	end
	return nil
end
