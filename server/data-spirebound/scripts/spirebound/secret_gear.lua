-- Secret gear in the game (adventure layer 4.1). Rules: lib/spirebound/gear.lua (secret gear section).
-- Bonuses follow what is worn; the pieces stay with their finder: no trading, dropping, storing in a depot,
-- house chest or Store Inbox (so no market), and no handing over.

local function refresh(player)
	local pid = player:getId()
	addEvent(function()
		local p = Player(pid)
		if p then
			SpireGear.applySecret(p)
		end
	end, 50)
end

local moved = EventCallback("SpireSecretGearMoved")
function moved.playerOnItemMoved(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if fromPosition.x == 0xFFFF or toPosition.x == 0xFFFF then
		refresh(player)
	end
end
moved:register()

-- Pure-ish: may this secret item go to toCylinder at toPosition? Only somewhere in its owner's own backpack or slots.
local function allowedPlace(player, toPosition, toCylinder)
	if toPosition.x ~= 0xFFFF then
		return false -- the ground (or a container lying on it)
	end
	if not toCylinder then
		return true
	end
	if toCylinder.isPlayer and toCylinder:isPlayer() then
		return toCylinder:getId() == player:getId()
	end
	if toCylinder.isItem and toCylinder:isItem() then
		if ITEM_STORE_INBOX and toCylinder:getId() == ITEM_STORE_INBOX then
			return false
		end
		local top = toCylinder:getTopParent()
		if not (top and top.isPlayer and top:isPlayer() and top:getId() == player:getId()) then
			return false -- a depot, a house chest, someone else's bag
		end
		local parent = toCylinder
		while parent and parent.isItem and parent:isItem() do
			if ITEM_STORE_INBOX and parent:getId() == ITEM_STORE_INBOX then
				return false
			end
			parent = parent:getParent()
		end
	end
	return true
end

local move = EventCallback("SpireSecretGearMove")
function move.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if SpireGear.holdsSecret(item) and not allowedPlace(player, toPosition, toCylinder) then
		player:sendCancelMessage("That is bound to you. It can't be dropped, stored or handed over.")
		return false
	end
	return true
end
move:register()

local trade = EventCallback("SpireSecretGearTrade")
function trade.playerOnTradeRequest(player, target, item)
	if SpireGear.holdsSecret(item) then
		player:sendCancelMessage("That is bound to you. It can't be traded.")
		return false
	end
	return true
end
trade:register()

local login = CreatureEvent("SpireSecretGearLogin")
function login.onLogin(player)
	refresh(player)
	return true
end
login:register()
