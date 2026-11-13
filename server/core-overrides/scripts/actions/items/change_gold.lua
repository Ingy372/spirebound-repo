-- Spirebound: using (right-clicking) a coin stack changes it up (Jay's playtest 2026-11-13:
-- "when you right click a gold stack, make it auto convert to platinum. same for a platinum stack to crystal").
-- Replaces Canary's version, which only changed a stack of exactly 100 and broke small platinum stacks into gold.
--   gold 100+      -> every full 100 becomes 1 platinum, the rest stays gold
--   platinum 100+  -> every full 100 becomes 1 crystal, the rest stays platinum
--   crystal        -> breaks one crystal into 100 platinum (the only way back down; shops give change anyway)

SpireCoins = SpireCoins or {}
SpireCoins.UP = { [ITEM_GOLD_COIN] = ITEM_PLATINUM_COIN, [ITEM_PLATINUM_COIN] = ITEM_CRYSTAL_COIN }

-- Pure: how many coins of the next kind a stack of `count` makes, and how many stay behind
function SpireCoins.split(count)
	return math.floor(count / 100), count % 100
end

function SpireCoins.use(player, item)
	local id, count = item:getId(), item:getCount()
	local up = SpireCoins.UP[id]
	if up then
		local made = SpireCoins.split(count)
		if made == 0 then
			player:sendCancelMessage(string.format("You need 100 %s to change them up.", ItemType(id):getPluralName()))
			return true
		end
		item:remove(made * 100)
		player:addItem(up, made)
		player:sendTextMessage(MESSAGE_STATUS, string.format("Changed into %d %s.", made, made == 1 and ItemType(up):getName() or ItemType(up):getPluralName()))
		return true
	end
	if id == ITEM_CRYSTAL_COIN then
		item:remove(1)
		player:addItem(ITEM_PLATINUM_COIN, 100)
		return true
	end
	return false
end

local changeGold = Action()
function changeGold.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	return SpireCoins.use(player, item)
end
changeGold:id(ITEM_GOLD_COIN, ITEM_PLATINUM_COIN, ITEM_CRYSTAL_COIN)
changeGold:register()
