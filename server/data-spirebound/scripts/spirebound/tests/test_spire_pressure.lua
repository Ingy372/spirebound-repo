-- Roadmap M4: Spire Pressure in arena events (lib/spirebound/arena.lua, scripts/spirebound/arena.lua).
local A = SpireArena

local function fill(st, n)
	for i = 1, n do
		A.join(st, 2000 + i, "Presser" .. i, 50)
	end
end

SpireTest.add("pressure: every 30 seconds more damage and less health, up to a limit", function()
	SpireTest.eq(A.pressureStep(100, 129), 0, "first 30 seconds: no pressure")
	SpireTest.eq(A.pressureStep(100, 130), 1, "30 seconds in: step 1")
	SpireTest.eq(A.pressureStep(100, 100 + 95), 3, "95 seconds in: step 3")
	SpireTest.eq(A.pressureStep(100, 100 + 3600), A.PRESSURE_MAX, "it stops rising at the limit")
	SpireTest.eq(math.abs(A.pressureDamage(1) - 1.15) < 1e-9, true, "+15% damage a step")
	SpireTest.eq(A.pressureHp(0), A.HP, "full event health at the start")
	SpireTest.eq(A.pressureHp(1), math.floor(A.HP * 0.9 + 0.5), "-10% health a step")
	SpireTest.eq(A.pressureHp(A.PRESSURE_MAX) > 0, true, "never down to nothing")
end)

SpireTest.add("pressure: idle fighters are moved, then deserters lose everything", function()
	SpireTest.eq(A.idleAction(0, false, 59), nil, "59 seconds idle: nothing yet")
	SpireTest.eq(A.idleAction(0, false, 60), "move", "60 seconds idle: moved")
	SpireTest.eq(A.idleAction(0, true, 90), nil, "moved once already: no second move")
	SpireTest.eq(A.idleAction(0, true, 120), "desert", "2 minutes idle: deserter")
	SpireTest.eq(A.banned(os.time() + 3600, os.time()), true, "a deserter can't join for a while")
	SpireTest.eq(A.banned(os.time() - 1, os.time()), false, "the ban ends")
	SpireTest.eq(A.DESERTER_BAN, 7 * 86400, "the ban lasts 7 days")
	-- a deserter on the winning team gets nothing
	local st = A.new("rush", 0)
	fill(st, 4)
	A.start(st, 0)
	A.leave(st, 2003)
	st.players[2003].deserter = true
	st.score.a = A.RUSH_KILLS
	local w = A.result(st, 50)
	SpireTest.eq(#w, 1, "only the West fighter who stayed wins")
	SpireTest.eq(w[1], 2001, "the deserter is left out")
end)

SpireTest.add("pressure: the week has two banner days and one Wild PvP day", function()
	local banner, wild = 0, 0
	for d = 0, 6 do
		local k = A.kindForDay(d)
		if k == "banner" then banner = banner + 1 end
		if k == "wild" then wild = wild + 1 end
	end
	SpireTest.eq(banner, 2, "Capture the Banner twice a week")
	SpireTest.eq(wild, 1, "Wild PvP once a week")
end)

SpireTest.add("pressure: the MVP gets the statue in the Hearth Square", function()
	local st = A.new("lms", 0)
	fill(st, 4)
	A.start(st, 0)
	SpireTest.eq(A.mvp(st), nil, "no takedowns: no MVP")
	A.down(st, 2002, 2001)
	A.down(st, 2003, 2004)
	A.down(st, 2004, 2001)
	SpireTest.eq(A.mvp(st), 2001, "most takedowns is MVP")
	local saved = kv.scoped("spirebound-arena"):get("mvp")
	A.current = st
	A.finish(st, A.result(st, 10))
	local rec = kv.scoped("spirebound-arena"):get("mvp")
	SpireTest.eq(rec and rec.name, "Presser1", "the MVP's name is kept")
	local item = Tile(WorldPoints.arena_mvp_statue):getItemById(2025)
	SpireTest.eq(item ~= nil, true, "the statue stands in the Hearth Square")
	SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_DESCRIPTION):find("Presser1", 1, true) ~= nil, true, "and carries the MVP's name")
	SpireTest.eq(SpireArena.current, nil, "the event is over")
	A.raiseStatue(saved and saved.name and saved or nil) -- put back what was there
end)
