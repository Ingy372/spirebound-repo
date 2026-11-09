-- Roadmap 5.7d: Spire Siege with two test guilds
SpireTest.add("siege: two test guilds fight, the throne picks a holder", function()
	local st = SpireSiege.new(0)
	SpireTest.eq(select(2, SpireSiege.join(st, 1, "Loner", 60, 0)), "Only guild members can join the Siege.", "guild needed")
	SpireSiege.join(st, 11, "Red1", 60, 100)
	SpireSiege.join(st, 12, "Red2", 60, 100)
	SpireSiege.join(st, 21, "Blue1", 60, 200)
	SpireSiege.join(st, 22, "Blue2", 60, 200)
	SpireSiege.join(st, 31, "Solo", 60, 300) -- a guild with one fighter is sent home
	SpireTest.eq(SpireSiege.start(st, 1000), true, "two guilds: the Siege starts")
	SpireTest.eq(st.players[31].alive, false, "one-member guild dropped")
	SpireTest.eq(st.gates[100] ~= st.gates[200], true, "guilds get different gates")
	SpireTest.eq(SpireSiege.canHit(st, 11, 21), true, "rival guilds fight")
	SpireTest.eq(SpireSiege.canHit(st, 11, 12), false, "no friendly fire")
	for _ = 1, 30 do
		SpireSiege.tick(st, { 11, 12 }) -- Red holds the throne
	end
	SpireTest.eq(SpireSiege.tick(st, { 11, 21 }), nil, "contested throne scores nothing")
	for _ = 1, 10 do
		SpireSiege.tick(st, { 22 })
	end
	SpireTest.eq(SpireSiege.result(st, 1000 + 60, nil), nil, "still running")
	SpireTest.eq(SpireSiege.result(st, 1000 + SpireSiege.DURATION, nil), 100, "Red holds the keep")
	-- tie keeps the old holder
	local t = SpireSiege.new(0)
	for _, row in ipairs({ { 1, 100 }, { 2, 100 }, { 3, 200 }, { 4, 200 } }) do
		SpireSiege.join(t, row[1], "P" .. row[1], 50, row[2])
	end
	SpireSiege.start(t, 0)
	SpireSiege.tick(t, { 1 })
	SpireSiege.tick(t, { 3 })
	SpireTest.eq(SpireSiege.result(t, SpireSiege.DURATION, 200), 200, "tie: the holder keeps it")
	SpireTest.eq(SpireSiege.result(t, SpireSiege.DURATION, nil), 0, "tie, no holder: nobody")
	-- a guild whose fighters all leave loses
	local u = SpireSiege.new(0)
	for _, row in ipairs({ { 1, 100 }, { 2, 100 }, { 3, 200 }, { 4, 200 } }) do
		SpireSiege.join(u, row[1], "P" .. row[1], 50, row[2])
	end
	SpireSiege.start(u, 0)
	SpireSiege.leave(u, 3)
	SpireSiege.leave(u, 4)
	SpireTest.eq(SpireSiege.result(u, 10, nil), 100, "the guild left standing wins")
end)

SpireTest.add("siege: holder buff and the keep on the map", function()
	local h = { guild = 100, untilTime = 5000 }
	SpireTest.eq(SpireSiege.buffFor(100, h, 1000), 1.05, "holders +5%")
	SpireTest.eq(SpireSiege.buffFor(200, h, 1000), 1, "others nothing")
	SpireTest.eq(SpireSiege.buffFor(100, h, 6000), 1, "expires after a week")
	SpireTest.eq(SpireSiege.buffFor(0, h, 1000), 1, "no guild")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints["siege_throne"]), "siege", "siege zone on the map")
	local tile = Tile(WorldPoints["siege_gate_1"])
	SpireTest.eq(tile and tile:hasFlag(TILESTATE_PVPZONE), true, "keep is an engine PvP zone")
end)
