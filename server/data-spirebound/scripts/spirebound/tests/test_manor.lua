-- Spire Manor (lib/spirebound/manor.lua, scripts/spirebound/manor.lua, maps/manor.py).
local function manor()
	for _, h in ipairs(Game.getHouses()) do
		if SpireManor.is(h) then return h end
	end
	error("Spire Manor is not on the map")
end

local function houseAt(pos)
	local t = Tile(pos)
	return t and t:getHouse()
end

local function hasItem(pos, ids)
	local t = Tile(pos)
	if not t then return false end
	for _, id in ipairs(ids) do
		if t:getItemById(id) then return true end
	end
	return false
end

SpireTest.add("manor: every room the deed promises is part of the house, on four levels", function()
	local h = manor()
	for _, name in ipairs({ "spire_manor", "manor_steward", "manor_housekeeper", "manor_gallery", "manor_training", "manor_suite", "manor_waystone" }) do
		local p = WorldPoints[name]
		if not p then error("the map has no point " .. name) end
		local at = houseAt(p)
		SpireTest.eq(at ~= nil and at:getId() == h:getId(), true, name .. " is inside Spire Manor")
	end
	local levels = {}
	for _, name in ipairs({ "spire_manor", "manor_gallery", "manor_suite", "manor_waystone" }) do
		levels[WorldPoints[name].z] = true
	end
	local n = 0
	for _ in pairs(levels) do n = n + 1 end
	SpireTest.eq(n, 4, "hall, gallery, suite and roof are four different levels")
	SpireTest.eq(h:getRent(), 0, "no rent")
end)

SpireTest.add("manor: the private depot, mailbox, training dummies and Waystone stand where the map puts them", function()
	local s = WorldPoints.manor_steward -- the lockers and mailbox are on the office's north wall, 3 tiles above him
	SpireTest.eq(hasItem(Position(s.x - 1, s.y - 3, s.z), { 3497, 3498, 3499, 3500 }), true, "first locker")
	SpireTest.eq(hasItem(Position(s.x, s.y - 3, s.z), { 3497, 3498, 3499, 3500 }), true, "second locker")
	SpireTest.eq(hasItem(Position(s.x + 1, s.y - 3, s.z), { 3501 }), true, "mailbox")
	local t = WorldPoints.manor_training
	local dummies = 0
	for dx = -3, 3, 3 do
		if hasItem(Position(t.x + dx, t.y - 2, t.z), { 28559, 28560, 28561, 28562, 28563, 28564 }) then dummies = dummies + 1 end
	end
	SpireTest.eq(dummies, 3, "three exercise dummies")
	local d = Tile(Position(t.x - 3, t.y - 2, t.z)):getItemById(28559)
	SpireTest.eq(d ~= nil and d:getActionId(), SpireManor.FIXTURE_AID, "a dummy is a fixture: it carries the lock nobody can move")
	local w = WorldPoints.manor_waystone
	SpireTest.eq(hasItem(Position(w.x, w.y - 1, w.z), { 1841 }), true, "the Waystone crystal")
	SpireTest.eq(Tile(w):isWalkable(false, false, false, false, true), true, "you can stand by it")
end)

SpireTest.add("manor: the steward and the housekeeper stand in the house", function()
	for name, point in pairs({ ["Steward Aldous"] = "manor_steward", ["Housekeeper Mirelle"] = "manor_housekeeper" }) do
		local npc = Npc(name)
		if not npc then error(name .. " is not in the game") end
		SpireTest.eq(npc:getPosition():getDistance(WorldPoints[point]) <= 3, true, name .. " is at home")
		local at = houseAt(npc:getPosition())
		SpireTest.eq(at ~= nil and SpireManor.is(at), true, name .. " stands inside the manor")
	end
end)

SpireTest.add("manor: its perks are comfort and convenience, by the rules", function()
	SpireTest.eq(SpireManor.mannequinSlots(true, 3), 10, "ten mannequins in the manor")
	SpireTest.eq(SpireManor.mannequinSlots(false, 3), 3, "three anywhere else")
	SpireTest.eq((SpireManor.openHouseAllowed(1000, 1000 + 3600)), false, "not open again within 12 hours")
	SpireTest.eq((SpireManor.openHouseAllowed(1000, 1000 + 13 * 3600)), true, "again after 12 hours")
	local now = 100000
	local ok = { nearStone = true, floor = 2, floorOpen = true, inFight = false, lastUse = nil, now = now }
	SpireTest.eq((SpireManor.waystoneOut(ok)), true, "by the stone, an open floor, at peace: it works")
	local function without(k, v)
		local a = {}
		for kk, vv in pairs(ok) do a[kk] = vv end
		a[k] = v
		return a
	end
	SpireTest.eq((SpireManor.waystoneOut(without("nearStone", false))), false, "not from anywhere else")
	SpireTest.eq((SpireManor.waystoneOut(without("floorOpen", false))), false, "never to a sealed floor")
	SpireTest.eq((SpireManor.waystoneOut(without("inFight", true))), false, "never out of a fight")
	SpireTest.eq((SpireManor.waystoneOut(without("lastUse", now - 60))), false, "not twice in half an hour")
	SpireTest.eq((SpireManor.waystoneOut(without("lastUse", now - 31 * 60))), true, "again after half an hour")
	local home = { isOwner = true, inTown = true, inFight = false, lastUse = nil, now = now }
	SpireTest.eq((SpireManor.recall(home)), true, "the owner, in a town, at peace: called home")
	SpireTest.eq((SpireManor.recall({ isOwner = false, inTown = true, inFight = false, now = now })), false, "only the owner")
	SpireTest.eq((SpireManor.recall({ isOwner = true, inTown = false, inFight = false, now = now })), false, "only from a town: never an escape from the wilds")
	SpireTest.eq((SpireManor.recall({ isOwner = true, inTown = true, inFight = true, now = now })), false, "never out of a fight")
	local text = table.concat(SpireManor.lines(), " "):lower()
	for _, word in ipairs({ "more experience", "more damage", "more loot" }) do
		SpireTest.eq(text:find(word, 1, true), nil, "the manor never promises " .. word)
	end
end)

SpireTest.add("manor: only the shop hands it out, and the town's own traders set its prices", function()
	SpireTest.eq(SpireShop.SHOP_HOUSES[SpireManor.HOUSE], true, "!buyhouse refuses it")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.manor_waystone), "town", "the roof is town ground (a safe zone)")
end)
