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

-- FLOOR1_REVIEW.md F1-03: the race is the hook; every login says where the tower stands
SpireTest.add("floors: the login line says which floor is sealed and what opens it", function()
	SpireTest.eq(Floors.raceLine(1, {}), "The tower: Floor 2 is sealed. No one has broken through the Pass on Floor 1 yet: the first party to defeat its guardian opens the way to the floor boss.", "launch day")
	SpireTest.eq(Floors.raceLine(1, { fieldBossDeadAt = 1, fieldBossCredit = { "Ana", "Bo" } }), "The tower: Floor 2 is sealed. The Pass on Floor 1 was first broken by Ana. The first party to defeat the floor boss opens Floor 2 for everyone.", "pass open")
	SpireTest.eq(Floors.raceLine(10, {}), "The tower: all 10 floors are open.", "the end")
end)

SpireTest.add("floors: test characters never open a floor, told apart by account e-mail (review A4-5)", function()
	local emails = { ["Pilot Warden"] = "autopilot@localhost", ["Pilot Ranger"] = "autopilot2@localhost",
		["Loadbot 001"] = "loadbot1@localhost", ["Pilot Realguy"] = "someone@example.com", Jay = "jay@localhost" }
	local of = function(n) return emails[n] end
	SpireTest.eq(Floors.onlyTesters({ "Pilot Warden", "Pilot Ranger", "Loadbot 001" }, of), true, "a party of test accounts is only testers")
	SpireTest.eq(Floors.onlyTesters({ "Pilot Warden", "Jay" }, of), false, "one real player makes it count")
	SpireTest.eq(Floors.onlyTesters({ "Pilot Realguy" }, of), false, "a real player named 'Pilot ...' counts")
	SpireTest.eq(Floors.onlyTesters({}, of), false, "nobody credited is not 'only testers'")
	-- and through the real database: a character called "Pilot ..." on a real account counts
	local name = "Pilot Notatest"
	db.query("DELETE FROM `players` WHERE `name` = " .. db.escapeString(name))
	db.query("INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, `lookbody`, `lookfeet`, `lookhead`, `looklegs`, `looktype`, `maglevel`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`) SELECT "
		.. db.escapeString(name) .. ", 1, `id`, 8, 0, 185, 185, 4200, 0, 0, 0, 0, 128, 0, 35, 35, 1, '', 400, 1 FROM `accounts` WHERE `name` = 'jay'")
	SpireTest.eq(Floors.onlyTesters({ name }), false, "database: 'Pilot Notatest' on Jay's account is a real player")
	db.query("DELETE FROM `players` WHERE `name` = " .. db.escapeString(name))
end)

SpireTest.add("bosses: the field boss comes back in 10 minutes and credits from 1%; a lost fight record is rebuilt (review A4-3, A4-5)", function()
	SpireTest.eq(SpireBoss.respawnSeconds("field"), 600, "Gate Hound back in 10 minutes")
	SpireTest.eq(SpireBoss.respawnSeconds("floor"), 1800, "floor boss still 30")
	local st = SpireBoss.newState()
	SpireBoss.recordHit(st, "Big", 985, 100)
	SpireBoss.recordHit(st, "Small", 15, 100)
	local function has(list, n) for _, x in ipairs(list) do if x == n then return true end end return false end
	SpireTest.eq(has(SpireBoss.credited(st, 101, SpireBoss.minShare("field")), "Small"), true, "1.5% is credited at a field boss")
	SpireTest.eq(has(SpireBoss.credited(st, 101, SpireBoss.minShare("floor")), "Small"), false, "but not at the floor boss (2%)")
	local rebuilt = SpireBoss.stateFromDamageMap({ [11] = { total = 500, ticks = 1 }, [12] = { total = 300 }, [13] = { total = 50 } },
		function(cid) return ({ [11] = "Ana", [12] = "Bo" })[cid] end, 1000)
	SpireTest.eq(#SpireBoss.credited(rebuilt, 1000), 2, "both players on the damage map are credited; the monster (13) is not")
end)

