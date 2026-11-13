-- Roadmap R16: house fixes.
local function walkable(pos)
	local t = Tile(pos)
	return t ~= nil and t:getGround() ~= nil and t:isWalkable(false, false, false, false, true)
end

SpireTest.add("houses: Open House keeps the real guest list, survives a restart and has a daily cooldown", function()
	local house = Game.getHouses()[1]
	local key = tostring(house:getId())
	local store = kv.scoped("spirebound-openhouse")
	local oldRec, oldList = store:get(key), house:getAccessList(GUEST_LIST) or ""
	house:setAccessList(GUEST_LIST, "Friend One\nFriend Two")
	store:set(key, { opened = 1000, closesAt = 1000 + SpireHouses.OPEN_HOUSE_TIME, guests = "Friend One\nFriend Two" })
	house:setAccessList(GUEST_LIST, "*") -- open, as !openhouse does
	-- a restart forgets every timer; the closer still finds the record in the database
	SpireTest.eq(SpireHouses.closeOpenHouses(1000 + SpireHouses.OPEN_HOUSE_TIME + 1) >= 1, true, "the open house closes on time")
	local list = house:getAccessList(GUEST_LIST) or ""
	SpireTest.eq(list:find("Friend One") ~= nil and list:find("%*") == nil, true, "the owner's own guests are back")
	SpireTest.eq((SpireHouses.openHouseAllowed(1000, 1000 + 3600)), false, "not again within a day")
	SpireTest.eq((SpireHouses.openHouseAllowed(1000, 1000 + 25 * 3600)), true, "again the next day")
	house:setAccessList(GUEST_LIST, oldList)
	if oldRec then store:set(key, oldRec) else store:remove(key) end
end)

SpireTest.add("houses: the portal can't reach labyrinths or Contested ground", function()
	SpireTest.eq((SpireHouses.portalTargetAllowed("contested", false, false, false, false)), false, "no Contested ground")
	local lab = WorldPoints.lab1_up
	SpireTest.eq(SpireHouses.inLabyrinth(Position(lab.x + 5, lab.y + 5, lab.z), { lab }), true, "a spot in the labyrinth is seen as one")
	SpireTest.eq((SpireHouses.portalTargetAllowed("open", false, false, false, true)), false, "no labyrinths")
	SpireTest.eq((SpireHouses.portalTargetAllowed("open", false, false, false, false)), true, "open ground is fine")
end)

SpireTest.add("houses: the Summoning Circle opens onto a private arena with a way home", function()
	SpireTest.eq(walkable(WorldPoints.summon_circle), true, "the circle arena is on the map")
	SpireTest.eq(walkable(WorldPoints.summon_circle_entry), true, "players arrive on a clear tile")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.summon_circle), "bossroom", "it is a boss room, not a safe house")
	SpireTest.eq(WorldPoints.summon_circle_exit ~= nil, true, "it has a way home")
end)
