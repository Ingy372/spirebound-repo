-- Roadmap 1.9: four vocations + four promotions, Spirebound names, no extras.
SpireTest.add("four vocations and promotions", function()
	local expected = {
		[0] = "None", [1] = "Arcanist", [2] = "Mystic", [3] = "Ranger", [4] = "Vanguard",
		[5] = "High Arcanist", [6] = "Elder Mystic", [7] = "Far Warden", [8] = "Blade Warden",
	}
	for id, name in pairs(expected) do
		local voc = Vocation(id)
		if not voc then error("vocation " .. id .. " missing") end
		SpireTest.eq(voc:getName(), name, "vocation " .. id)
	end
	for id = 1, 4 do
		SpireTest.eq(Vocation(id):getPromotion():getId(), id + 4, "promotion of " .. id)
	end
end)
