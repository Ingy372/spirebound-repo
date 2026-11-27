-- Waycrystals (DESIGN.md 3.7): the rules in lib/spirebound/crystals.lua. The real use (buy, menu, cast, arrive, the
-- locks) is checked on real characters by tools/loadtest.py review (TC1 cases).

SpireTest.add("waycrystals: ten floors, ten colours, prices rise with the floors, Floor 1's is sold", function()
	local floors, colours, last = {}, {}, 0
	local byFloor = {}
	for itemId, d in pairs(SpireCrystalData.byItem) do
		floors[d.floor] = true
		colours[d.colour] = true
		byFloor[d.floor] = d
		SpireTest.eq(ItemType(itemId):getId() ~= 0, true, d.name .. " has an item")
	end
	local n, c = 0, 0
	for _ in pairs(floors) do n = n + 1 end
	for _ in pairs(colours) do c = c + 1 end
	SpireTest.eq(n, 10, "one crystal per floor")
	SpireTest.eq(c, 10, "ten colours")
	for f = 1, 10 do
		SpireTest.eq(byFloor[f].price >= last, true, "Floor " .. f .. " costs at least Floor " .. (f - 1) .. "'s")
		last = byFloor[f].price
	end
	SpireTest.eq(WorldPoints[byFloor[1].town] ~= nil, true, "Floor 1's town is on the map")
end)

SpireTest.add("waycrystals: refused in tutorials, boss rooms, party caves, fights and sealed floors", function()
	local ok = { zone = "open", tutorial = false, cave = false, fight = false, floorOpen = true }
	local function with(k, v)
		local s = {}
		for a, b in pairs(ok) do s[a] = b end
		s[k] = v
		return SpireCrystals.refusal(s)
	end
	SpireTest.eq(SpireCrystals.refusal(ok), nil, "an open meadow, no fight: allowed")
	SpireTest.eq(with("tutorial", true) ~= nil, true, "not before choosing a path")
	SpireTest.eq(with("zone", "bossroom") ~= nil, true, "not in a boss room")
	SpireTest.eq(with("zone", "arena") ~= nil, true, "not in an arena")
	SpireTest.eq(with("cave", true) ~= nil, true, "not in a party cave")
	SpireTest.eq(with("fight", true) ~= nil, true, "not in a fight")
	SpireTest.eq(with("floorOpen", false) ~= nil, true, "not to a sealed floor")
	SpireTest.eq(with("zone", "guarded"), nil, "a guarded road is fine")
end)

SpireTest.add("waycrystals: the menu shows the town and only the grounds the level has reached", function()
	local low = SpireCrystals.choices(1, 3, "Hearthgate")
	local high = SpireCrystals.choices(1, 40, "Hearthgate")
	SpireTest.eq(low[1].id, "town", "the town comes first")
	SpireTest.eq(#high > #low, true, "a level 40 sees more grounds than a level 3")
	for _, c in ipairs(low) do
		if c.pos then
			local g
			for _, x in ipairs(SpireCrystalData.grounds[1]) do
				if x.id == c.id then g = x end
			end
			SpireTest.eq(g.lo <= 3, true, c.id .. " is open to a level 3")
			SpireTest.eq(Tile(Position(c.pos[1], c.pos[2], c.pos[3])) ~= nil, true, c.id .. "'s gate is on the map")
		end
	end
end)
