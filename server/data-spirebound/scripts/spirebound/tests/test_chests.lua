-- FLOOR1_REVIEW.md F1-20: a chest in every rebuilt ground, first-time reward then a daily one
SpireTest.add("chests: first time, then nothing for 20 hours, then the daily chest", function()
	SpireTest.eq(SpireChests.claim(nil, 1000), "first", "never opened")
	local kind, wait = SpireChests.claim({ first = 1000, last = 1000 }, 1000 + 3600)
	SpireTest.eq(kind, nil, "an hour later: empty")
	SpireTest.eq(wait, 19 * 3600, "19 hours to wait")
	SpireTest.eq(SpireChests.claim({ first = 1000, last = 1000 }, 1000 + 20 * 3600), "daily", "20 hours later: the daily chest")
	SpireTest.eq(SpireChests.reward(1, 4).gold, 300, "the Ratwarren's chest: 300 gold")
	SpireTest.eq(SpireChests.reward(14, 19).potions[1], 236, "from level 14: strong health potions")
end)

SpireTest.add("chests: every rebuilt ground has a chest on the map", function()
	local missing = {}
	for _, g in ipairs(SpireWilds.grounds) do
		local p = WorldPoints["chest_" .. g.id]
		local tile = p and Tile(p)
		if g.zs and not (tile and tile:getItemById(SpireChests.ITEM)) then -- designed grounds (several levels)
			table.insert(missing, g.id)
		end
	end
	SpireTest.eq(table.concat(missing, ","), "", "rebuilt grounds without a chest")
end)
