-- Roadmap 1.17: world floor state. Uses test floors 90-92 so real floor records are never touched.
SpireTest.add("floors: first clear opens the next floor once", function()
	for i = 90, 92 do
		Floors.reset(i)
	end
	SpireTest.eq(Floors.isOpen(1), true, "floor 1 open at launch")
	SpireTest.eq(Floors.isOpen(91), false, "test floor 91 sealed before clear")
	SpireTest.eq(Floors.isLabyrinthOpen(90), false, "pass sealed before field boss")
	SpireTest.eq(Floors.markFieldBoss(90, { "A" }), true, "field boss first kill")
	SpireTest.eq(Floors.markFieldBoss(90, { "B" }), false, "field boss second kill does nothing")
	SpireTest.eq(Floors.isLabyrinthOpen(90), true, "pass open after field boss")
	SpireTest.eq(Floors.recordClear(90, { "A", "B", "C" }, "C", 600), true, "first clear")
	SpireTest.eq(Floors.isOpen(91), true, "next floor open")
	SpireTest.eq(Floors.recordClear(90, { "D" }, "D", 100), false, "second clear is not a first clear")
	local rec = Floors.get(90)
	SpireTest.eq(#rec.credit, 3, "credit kept from first clear")
	SpireTest.eq(rec.lastHit, "C", "last hit kept")
	for i = 90, 92 do
		Floors.reset(i)
	end
end)

SpireTest.add("floors: credit top 20 and enrage scaling", function()
	local c = {}
	for i = 1, 25 do
		table.insert(c, { name = string.format("P%02d", i), amount = i * 10 })
	end
	local names = Floors.rankCredit(c)
	SpireTest.eq(#names, 20, "credit capped at 20")
	SpireTest.eq(names[1], "P25", "biggest contributor first")
	SpireTest.eq(Floors.enrageSeconds(1), 3600, "solo: 60 min")
	SpireTest.eq(Floors.enrageSeconds(4), 960, "4 players: 16 min")
	SpireTest.eq(Floors.enrageSeconds(8), 480, "8 players: 8 min")
	SpireTest.eq(Floors.enrageSeconds(20), 480, "20 players: still 8 min")
end)

-- State must survive a restart: each boot checks the value the previous boot wrote.
SpireTest.add("floors: saved state survives a restart", function()
	local probe = kv.scoped("spirebound-test")
	local previous = probe:get("restart-probe")
	local token = os.time()
	probe:set("restart-probe", token)
	if previous == nil then
		logger.info("[SPIRETEST] note: first boot on this database, restart check runs next boot")
		return
	end
	if type(previous) ~= "number" then
		error("probe value corrupted: " .. tostring(previous))
	end
end)
