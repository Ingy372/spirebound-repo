-- Roadmap 2.11: story quests, quest log lines, perks.
SpireTest.add("quests: floor 1 story quests with a next step for every state", function()
	local n = 0
	for _, q in ipairs(SpireQuests.list) do
		if q.floor == 1 then
			n = n + 1
			for _, st in ipairs({ -1, 1, 2, 3 }) do
				local line = SpireQuests.logText(q, st, 3)
				if not line or line == "" then error(q.id .. " has no log line for state " .. st) end
			end
			if not MonsterType(q.target) then error(q.id .. " targets unknown monster " .. q.target) end
		end
	end
	SpireTest.eq(n, 13, "thirteen floor 1 quests: six story, six side (two of them the gear line) and the tutorial quest")
	local story = 0
	for _, q in ipairs(SpireQuests.list) do
		if q.floor == 1 and not q.side then story = story + 1 end
	end
	SpireTest.eq(story, 6, "six story quests (the perk needs only these)")
	local q3 = SpireQuests.get("q1_3")
	SpireTest.eq(SpireQuests.available(q3, -1, {}), false, "Millstone needs Bread for the Road first")
	SpireTest.eq(SpireQuests.available(q3, -1, { q1_1 = true }), true, "then it opens")
	SpireTest.eq(SpireQuests.logText(SpireQuests.get("q1_1"), 1, 4), "Hunt Bristle Boars in the boar meadow (south-west of Hearthgate): 4 of 15.", "progress line")
	SpireTest.eq(#SpireQuests.PERKS[1], 2, "pick 1 of 2 perks")
end)

SpireTest.add("quests: quest log catalog loaded", function()
	local found = 0
	for _, quest in pairs(Quests or {}) do
		if quest.name == "Bread for the Road" or quest.name == "The Lost Patrol" or quest.name == "Millstone" then
			found = found + 1
		end
	end
	SpireTest.eq(found, 3, "quests in the client quest log")
end)
