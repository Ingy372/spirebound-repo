-- Our gear on the market (roadmap WA2, 2026-11-28). The engine's market keeps only an item's type and amount, so a
-- Spirebound weapon listed there would reach the buyer as a plain item: its tier, familiarity, awakening, a secret
-- piece's bonus or a keepsake's name all lost (tested: a tier 3 sword was listed and taken from the depot). The engine
-- has no market hook, so the one way in is guarded: opening the market from the depot locker (this replaces the core
-- datapack's market item, removed by tools/build_server.py). Everything of ours in the depot moves to the Store Inbox,
-- which the market never sells from, and while the market is open nothing of ours can be put in the depot.
SpireMarket = SpireMarket or { open = {} }
SpireMarket.OPEN_TIME = 15 * 60 -- the market counts as open this long after it was opened (it closes when you walk away)
SpireMarket.TEXT = "Spirebound gear can't be sold on the market: it would lose its tier, familiarity and name. Trade it hand to hand. Yours was moved to your Store Inbox."

-- an item of ours: Spirebound gear, secret gear, or anything with its own name or text written on it
function SpireMarket.ours(item)
	if not item or not item.isItem or not item:isItem() then
		return false
	end
	if SpireGear.state(item) or SpireGear.secretOf(item) then
		return true
	end
	return item:hasAttribute(ITEM_ATTRIBUTE_NAME) or item:hasAttribute(ITEM_ATTRIBUTE_DESCRIPTION)
end

local function containersOf(player)
	local list = {}
	local inbox = player.getInbox and player:getInbox()
	if inbox then
		table.insert(list, inbox)
	end
	for id = 0, 20 do -- the depot chests (Spirebound's lockers share one; the loop covers every town id)
		local chest = player:getDepotChest(id, false)
		if chest then
			table.insert(list, chest)
		end
	end
	return list
end

-- Moves our items out of the depot into the Store Inbox. Returns how many moved.
function SpireMarket.sweep(player)
	local store = player:getStoreInbox()
	if not store then
		return 0
	end
	local moved = 0
	for _, c in ipairs(containersOf(player)) do
		for _, item in ipairs(c:getItems(true) or {}) do
			if SpireMarket.ours(item) and item:moveTo(store) then
				moved = moved + 1
			end
		end
	end
	return moved
end

function SpireMarket.openFor(player)
	local moved = SpireMarket.sweep(player)
	if moved > 0 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, SpireMarket.TEXT)
	end
	SpireMarket.open[player:getGuid()] = os.time()
	player:openMarket()
	return moved
end

SpireCleanup.add(function(pid, guid) SpireMarket.open[guid] = nil end)

local market = Action()
function market.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	SpireMarket.openFor(player)
	return true
end
market:id(12903)
market:register()

-- Is this container part of the depot (the locker, a depot chest or box, the depot inbox)?
local DEPOT_IDS = { [3497] = true, [3498] = true, [3499] = true, [3500] = true }
local function inDepot(cylinder)
	local c = cylinder
	while c and c.isItem and c:isItem() do
		local id = c:getId()
		if DEPOT_IDS[id] or (ITEM_INBOX and id == ITEM_INBOX) or (ITEM_DEPOT and id == ITEM_DEPOT) then
			return true
		end
		local name = ItemType(id):getName():lower()
		if name:find("depot", 1, true) or name == "inbox" then
			return true
		end
		c = c:getParent()
	end
	return false
end

local move = EventCallback("SpireMarketGuardMove")
function move.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	local at = SpireMarket.open[player:getGuid()]
	if at and os.time() - at < SpireMarket.OPEN_TIME and toCylinder and toCylinder.isItem and toCylinder:isItem()
		and inDepot(toCylinder) then
		local holds = SpireMarket.ours(item)
		if not holds and item:isContainer() then
			for _, inner in ipairs(item:getItems(true) or {}) do
				if SpireMarket.ours(inner) then
					holds = true
					break
				end
			end
		end
		if holds then
			player:sendCancelMessage("While the market is open, Spirebound gear can't go in the depot: the market would strip it.")
			return false
		end
	end
	return true
end
move:register()
