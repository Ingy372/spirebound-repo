-- Roadmap 3.5: house fixtures
SpireTest.add("house fixtures: kits, trophies, pond, mannequins, Housewright", function()
	SpireTest.eq(SpireHouses.canBuild(23398, true, true, true), true, "owner builds the dummy on the house floor")
	SpireTest.eq(select(2, SpireHouses.canBuild(23398, false, true, true)), "Put the kit on the floor of your house first.", "not from a backpack")
	SpireTest.eq(select(2, SpireHouses.canBuild(23398, true, false, true)), "You can only build this inside a house.", "houses only")
	SpireTest.eq(select(2, SpireHouses.canBuild(23398, true, true, false)), "Only the owner or a subowner can build here.", "owner only")
	SpireTest.eq(SpireHouses.canBuild(3031, true, true, true), false, "gold is not a kit")
	for kit, built in pairs(SpireHouses.KITS) do
		local k, b = ItemType(kit), ItemType(built)
		if k:getId() == 0 or not k:isPickupable() then error("kit " .. kit .. " is not a takeable item") end
		if b:getId() == 0 or b:isPickupable() then error("kit " .. kit .. " builds " .. built .. ", which is not furniture") end
	end
	for _, r in ipairs(SpirePath.REWARDS) do
		local name = r.name or ""
		if name:find(" kit$") and not SpireHouses.FURNITURE_KITS[r.item] then
			error("Season Path kit " .. r.item .. " can't be built")
		end
	end
	SpireTest.eq(ItemType(28559):getId(), 28559, "house exercise dummy exists")
	local lines = SpireHouses.trophyLines({ ["Gate Hound"] = { first = 100, kills = 3 }, ["Axe-Lord"] = { first = 200, kills = 1 } })
	SpireTest.eq(lines[1]:sub(1, 10), "Gate Hound", "oldest trophy first")
	SpireTest.eq(lines[2]:sub(-6), "1 time", "singular")
	SpireTest.eq(SpireHouses.pondBait(4, nil, 10), 9, "5 worms + 1 per fish kind")
	SpireTest.eq(SpireHouses.pondBait(4, 10, 10), 0, "once a day")
	SpireTest.eq(SpireHouses.pondBait(40, 9, 10), 20, "capped at 20")
	SpireTest.eq(type(GUEST_LIST), "number", "house guest list constant")
	local found = Npc("Housewright Orla") ~= nil
	SpireTest.eq(found, true, "Housewright Orla stands in Hearthgate")
end)
