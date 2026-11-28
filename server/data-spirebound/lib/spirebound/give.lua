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

-- A reward that must reach the player (shards, chest prizes): ignores carrying weight; with no free backpack slot it
-- goes to the Store Inbox instead of the floor (party playtest 2026-11-26, hand-off P1-1). Returns the item or nil.
function SpireGive.reward(player, id, count)
	local item = Game.createItem(id, count or 1)
	if not item then
		return nil
	end
	if player:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		return item
	end
	local inbox = player.getStoreInbox and player:getStoreInbox()
	if inbox and inbox:addItemEx(item, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your backpack is full: " .. item:getName() .. " was put in your Store Inbox (the box in your equipment).")
		return item
	end
	if player:addItemEx(item, true) == RETURNVALUE_NOERROR then
		return item
	end
	return nil
end

-- Gold for a reward (quests, tasks, chests, secrets, a boss's hoard). Jay, 2026-11-27 (Q76): coins "should stay in the
-- bag until the player deposits them in the bank". So the coins go into the backpack (weight ignored, the biggest coins
-- first); only what finds no free slot goes to the bank, so nothing is ever lost on the floor.
-- Returns the gold put in the bag and the gold banked.
SpireGive.COINS = { { 3043, 10000 }, { 3035, 100 }, { 3031, 1 } } -- crystal, platinum, gold

-- Pure: how many of each coin make `amount` (largest first, stacks of at most 100)
function SpireGive.coinStacks(amount)
	local out, left = {}, math.max(0, math.floor(amount or 0))
	for _, c in ipairs(SpireGive.COINS) do
		local n = math.floor(left / c[2])
		left = left - n * c[2]
		while n > 0 do
			local k = math.min(n, 100)
			table.insert(out, { id = c[1], count = k, value = k * c[2] })
			n = n - k
		end
	end
	return out
end

function SpireGive.gold(player, amount)
	local bag, bank = 0, 0
	for _, s in ipairs(SpireGive.coinStacks(amount)) do
		local item = Game.createItem(s.id, s.count)
		if item and player:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
			bag = bag + s.value
		else
			if item then
				item:remove()
			end
			bank = bank + s.value
		end
	end
	if bank > 0 then
		player:setBankBalance(player:getBankBalance() + bank)
	end
	return bag, bank
end

-- Pure: the words for where the gold went ("in your backpack", or the bank part when the backpack was full)
function SpireGive.goldWhere(bag, bank)
	if bank <= 0 then
		return "in your backpack"
	elseif bag <= 0 then
		return "in your bank (your backpack was full)"
	end
	return string.format("in your backpack, %d of it in your bank (your backpack was full)", bank)
end
