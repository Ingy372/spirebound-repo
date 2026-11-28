-- Ground chests (rules: lib/spirebound/chests.lua). Placed at start-up on the map's chest_<ground> points.
local byAid = {} -- action id -> ground record from SpireWilds.grounds

local function groundOf(gid)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.id == gid then
			return g
		end
	end
end

local startup = GlobalEvent("SpireChestsStartup")
function startup.onStartup()
	local names = {}
	for name in pairs(WorldPoints) do
		if name:sub(1, 6) == "chest_" then
			table.insert(names, name)
		end
	end
	table.sort(names) -- the same action id for the same chest on every start
	for i, name in ipairs(names) do
		local g = groundOf(name:sub(7))
		local tile = Tile(WorldPoints[name])
		if g and tile then
			local chest = tile:getItemById(SpireChests.ITEM) or Game.createItem(SpireChests.ITEM, 1, WorldPoints[name])
			if chest then
				chest:setActionId(SpireChests.AID + i)
				byAid[SpireChests.AID + i] = g
			end
		end
	end
	return true
end
startup:register()

local open = Action()
function open.onUse(player, item)
	local g = byAid[item:getActionId()]
	if not g then
		return false
	end
	local store = player:kv():scoped("spirebound-chests")
	local rec = store:get(g.id) or {}
	local now = os.time()
	-- tester 2026-11-26: the first-time reward is once per ACCOUNT (a second character got the full reward again);
	-- another character of the account starts on the daily refill straight away
	local acc = kv.scoped("account"):scoped(tostring(player:getAccountId())):scoped("spirebound-chests-first")
	if not rec.first and acc:get(g.id) then
		rec.first = 0
	end
	local kind, wait = SpireChests.claim(rec, now)
	if not kind then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The chest is empty. It fills again in about %d hours.", math.ceil(wait / 3600)))
		return true
	end
	if kind == "first" then
		local r = SpireChests.reward(g.lo, g.hi)
		local bag, bank = SpireGive.gold(player, r.gold) -- the backpack; the bank only if it is full (Q76)
		acc:set(g.id, now)
		SpireGive.reward(player, r.potions[1], r.potions[2])
		if SpireDiscoveries then -- the chest's row on the Discoveries page fills once the record below is saved
			local pid = player:getId()
			addEvent(function() local p = Player(pid) if p then SpireDiscoveries.checkMilestones(p, 1) end end, 100)
		end
		SpireGive.reward(player, SpireGearData.tokens[1].rough, 1)
		rec.first = now
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You found %s's chest: %d gold (%s), %d %s and a rough Hearth Shard. It fills again every 20 hours.",
			g.title, r.gold, SpireGive.goldWhere(bag, bank), r.potions[2], ItemType(r.potions[1]):getPluralName()))
	else
		local r = SpireChests.daily(g.lo, g.hi)
		local bag, bank = SpireGive.gold(player, r.gold)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The chest has filled again: %d gold, %s. Come back in 20 hours.", r.gold, SpireGive.goldWhere(bag, bank)))
	end
	rec.last = now
	store:set(g.id, rec)
	item:getPosition():sendMagicEffect(CONST_ME_GIFT_WRAPS)
	return true
end
for i = 1, 20 do
	open:aid(SpireChests.AID + i)
end
open:register()
