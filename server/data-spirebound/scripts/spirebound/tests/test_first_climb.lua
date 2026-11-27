-- FD1: The First Climb (lib/spirebound/first_climb.lua)
SpireTest.add("first climb: eight chapters in order, each with a log line for every step and state", function()
	local FC = SpireFirstClimb
	SpireTest.eq(#FC.CHAPTERS, 8, "eight chapters")
	local last = 0
	for i, q in ipairs(FC.CHAPTERS) do
		SpireTest.eq(q.giver, "Archivist Maren", q.id .. " from Maren")
		SpireTest.eq(q.minLevel >= last, true, q.id .. " level never goes down")
		last = q.minLevel
		if i > 1 then
			SpireTest.eq(q.requires, FC.CHAPTERS[i - 1].id, q.id .. " needs the chapter before")
		end
		for n = 0, #q.steps - 1 do
			local line = SpireQuests.logText(q, 1, FC.encode(n, 1))
			SpireTest.eq(type(line) == "string" and #line > 20 and not line:find("%%"), true, q.id .. " step " .. n .. " log line")
		end
		for _, st in ipairs({ -1, 2, 3 }) do
			local line = SpireQuests.logText(q, st, 0)
			SpireTest.eq(line ~= nil and line ~= "", true, q.id .. " state " .. st)
		end
		SpireTest.eq(SpireQuests.get(q.id) == q, true, q.id .. " is in the quest list (so the quest log shows it)")
	end
	SpireTest.eq(FC.CHAPTERS[8].reward.title, "Heir to the First Climb", "the title at the end")
	SpireTest.eq(SpireQuests.logText(FC.get("fc2"), 1, FC.encode(0, 2)):find("2 of 3", 1, true) ~= nil, true, "a counted step shows its count")
end)

SpireTest.add("first climb: records, choices and the Monument", function()
	local FC = SpireFirstClimb
	local chain, loose = 0, 0
	for _, r in ipairs(FC.RECORDS) do
		if r.chain then chain = chain + 1 end
		if r.loose then loose = loose + 1 end
		SpireTest.eq(#r.text > 40, true, r.id .. " has text")
	end
	SpireTest.eq(chain, 9, "nine records in the chain")
	SpireTest.eq(loose, 3, "three loose records")
	SpireTest.eq(FC.CHOICES.pendant.title ~= FC.CHOICES.wreath.title, true, "two different titles for chapter 4")
	SpireTest.eq(FC.monumentHeader(false, "Ana"):find("chiselled", 1, true) ~= nil, true, "scraped for most")
	SpireTest.eq(FC.monumentHeader(true, "Ana"):find("Aldric Vane", 1, true) ~= nil, true, "restored for an heir")
	local q, st = FC.current(function(x) return x.id == "fc1" and 3 or -1 end)
	SpireTest.eq(q and q.id, "fc2", "the next chapter after chapter 1")
	SpireTest.eq(FC.decode(FC.encode(3, 2)), 3, "step decodes")
end)

SpireTest.add("first climb: the perk waits at chapter 8, the old story quests are jobs", function()
	for _, id in ipairs({ "q1_1", "q1_2", "q1_temper", "q1_iron2", "q1_6" }) do
		SpireTest.eq(SpireQuests.get(id).side, true, id .. " is a job")
	end
	local fake = { getStorageValue = function(self, k) return k == SpireFirstClimb.CHAPTERS[8].storage and 3 or -1 end }
	SpireTest.eq(SpireQuests.floorStoryDone(fake, 1), true, "chapter 8 done: perk")
	local fake2 = { getStorageValue = function(self, k) return 3 end }
	fake2.getStorageValue = function(self, k) return k == SpireFirstClimb.CHAPTERS[8].storage and 1 or 3 end
	SpireTest.eq(SpireQuests.floorStoryDone(fake2, 1), false, "every old quest done but not chapter 8: no perk")
end)

SpireTest.add("first climb: Archivist Maren stands where the quest log says", function()
	local pos = SpireQuests.giverPos("Archivist Maren")
	SpireTest.eq(WorldPoints.archivist_maren ~= nil and pos == WorldPoints.archivist_maren, true, "WHERE matches the map")
end)
