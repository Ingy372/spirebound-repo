-- Fishing (DESIGN.md 8.2). Roadmap 2.9.
-- Cast with a fishing rod on water (uses a worm when something bites). A few seconds later a fish may bite:
-- use the rod again within BITE_WINDOW seconds to land it. Unattended fishing catches nothing (anti-bot).
SpireFishing = {
	BITE_WINDOW = 3, -- seconds to react to a bite
	WORM = 3492,
	TITLES = { { 5, "Angler" }, { 7, "Master Angler of Floor 1" } },
}

-- Catch tables per floor. weight = relative chance; night = only 20:00-05:00; item = what lands in your backpack.
SpireFishing.tables = {
	[1] = {
		{ id = "hearth_minnow", name = "Hearth Minnow", item = 3578, weight = 50, kg = { 0.1, 0.4 } },
		{ id = "river_perch", name = "River Perch", item = 7159, weight = 25, kg = { 0.3, 1.2 } },
		{ id = "silver_carp", name = "Silver Carp", item = 3579, weight = 12, kg = { 1.0, 4.0 } },
		{ id = "mudskipper", name = "Mudskipper", item = 3581, weight = 6, kg = { 0.1, 0.3 } },
		{ id = "golden_trout", name = "Golden Trout", item = 7158, weight = 4, kg = { 0.8, 2.5 } },
		{ id = "moonscale_eel", name = "Moonscale Eel", item = 3580, weight = 4, kg = { 1.5, 5.0 }, night = true },
		{ id = "old_whiskers", name = "Old Whiskers", item = 3580, weight = 0.3, kg = { 12, 20 }, legendary = true },
		{ id = "sunken_purse", name = "a sunken purse", item = 3035, count = 5, weight = 2, treasure = true },
		{ id = "pearl", name = "a white pearl", item = 3026, weight = 1, treasure = true },
		{ id = "junk_boots", name = "old boots", item = 3123, weight = 8, junk = true },
	},
}

-- Pure: chance (percent) that a cast gets a bite at all, from fishing skill
function SpireFishing.biteChance(skill)
	return math.min(70, math.max(25, 20 + skill * 0.5))
end

-- Pure: pick a catch. r = random number in [0,1). Night-only entries are skipped by day.
function SpireFishing.roll(floor, isNight, r)
	local list = SpireFishing.tables[floor] or SpireFishing.tables[1]
	local total = 0
	for _, f in ipairs(list) do
		if isNight or not f.night then
			total = total + f.weight
		end
	end
	local x = r * total
	for _, f in ipairs(list) do
		if isNight or not f.night then
			x = x - f.weight
			if x < 0 then
				return f
			end
		end
	end
	return list[1]
end

function SpireFishing.fishKinds(floor)
	local n = 0
	for _, f in ipairs(SpireFishing.tables[floor] or {}) do
		if not f.treasure and not f.junk then
			n = n + 1
		end
	end
	return n
end

function SpireFishing.titleFor(kinds)
	local t = nil
	for _, row in ipairs(SpireFishing.TITLES) do
		if kinds >= row[1] then
			t = row[2]
		end
	end
	return t
end

function SpireFishing.log(player)
	return player:kv():scoped("spirebound-fishing")
end
