-- Roadmap 1.12: experience stages match DESIGN.md 5.5.
SpireTest.add("xp stages match DESIGN 5.5", function()
	local expected = { [10] = 25, [50] = 25, [75] = 15, [120] = 10, [175] = 7, [250] = 5, [350] = 3, [999] = 2 }
	for level, rate in pairs(expected) do
		SpireTest.eq(getRateFromTable(experienceStages, level, 1), rate, "xp rate at level " .. level)
	end
	SpireTest.eq(getRateFromTable(skillsStages, 80, 1), 10, "skill rate")
	SpireTest.eq(getRateFromTable(magicLevelStages, 40, 1), 5, "magic rate")
end)
