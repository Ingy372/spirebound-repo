-- Roadmap 5.7c: equal-footing arena events (scripted with test players)
local function fill(st, n)
	for i = 1, n do
		SpireArena.join(st, 1000 + i, "Tester" .. i, 50)
	end
end

SpireTest.add("arena: Last Man Standing starts, scores and ends", function()
	local st = SpireArena.new("lms", 0)
	SpireTest.eq(select(2, SpireArena.join(st, 1, "Low", 5)), "You need level 20 to fight in the Arena.", "level rule")
	fill(st, 3)
	SpireTest.eq(SpireArena.start(st, 10), false, "3 fighters is too few")
	st = SpireArena.new("lms", 0)
	fill(st, 4)
	SpireTest.eq(SpireArena.start(st, 10), true, "4 fighters start")
	SpireTest.eq(SpireArena.canHit(st, 1001, 1002), true, "free for all")
	SpireTest.eq(SpireArena.result(st, 20), nil, "still running")
	SpireTest.eq(SpireArena.down(st, 1002, 1001), "out", "one life")
	SpireTest.eq(SpireArena.canHit(st, 1001, 1002), false, "can't hit someone who is out")
	SpireArena.down(st, 1003, 1001)
	SpireArena.leave(st, 1004) -- logged out
	local w = SpireArena.result(st, 30)
	SpireTest.eq(#w, 1, "one winner")
	SpireTest.eq(w[1], 1001, "last one standing wins")
	SpireTest.eq(st.players[1001].kills, 2, "kills counted")
end)

SpireTest.add("arena: Team Rush and Capture the Banner", function()
	local st = SpireArena.new("rush", 0)
	fill(st, 4)
	SpireArena.start(st, 0)
	SpireTest.eq(st.players[1001].team, "a", "teams alternate")
	SpireTest.eq(st.players[1002].team, "b", "teams alternate")
	SpireTest.eq(SpireArena.canHit(st, 1001, 1003), false, "no friendly fire")
	for _ = 1, SpireArena.RUSH_KILLS - 1 do
		SpireTest.eq(SpireArena.down(st, 1002, 1001), "respawn", "teams respawn")
	end
	SpireTest.eq(SpireArena.result(st, 60), nil, "19 kills: not yet")
	SpireArena.down(st, 1004, 1003)
	local w = SpireArena.result(st, 61)
	SpireTest.eq(#w, 2, "the whole West team wins")
	local b = SpireArena.new("banner", 0)
	fill(b, 4)
	SpireArena.start(b, 0)
	SpireTest.eq(SpireArena.bannerTick(b, { 1001, 1003 }), "a", "West alone on the banner scores")
	SpireTest.eq(SpireArena.bannerTick(b, { 1001, 1002 }), nil, "contested banner: nobody scores")
	b.score.b = SpireArena.BANNER_POINTS
	local wb = SpireArena.result(b, 100)
	SpireTest.eq(wb[1], 1002, "East reaches the target")
	local empty = SpireArena.new("rush", 0)
	empty.phase, empty.started = "running", 0
	SpireTest.eq(#SpireArena.result(empty, 700), 0, "nobody left on either team: draw")
end)

SpireTest.add("arena: equal numbers and the map", function()
	for i = 0, 9 do
		local h = SpireArena.amount("hit", i / 10)
		if h < SpireArena.HIT[1] or h > SpireArena.HIT[2] then error("hit out of range") end
	end
	SpireTest.eq(SpireArena.amount("spell", 0), SpireArena.SPELL[1], "spell floor")
	SpireTest.eq(SpireArena.kindForDay(0), "lms", "rotation")
	SpireTest.eq(SpireArena.kindForDay(4), "rush", "rotation wraps")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints["arena_center"]), "arena", "arena zone on the map")
	local tile = Tile(WorldPoints["arena_center"])
	SpireTest.eq(tile and tile:hasFlag(TILESTATE_PVPZONE), true, "arena floor is an engine PvP zone (no death loss)")
	SpireTest.eq(type(ORIGIN_SPELL), "number", "spell origin constant")
	SpireTest.eq(type(CONST_PROP_BLOCKSOLID), "number", "block-solid constant")
	SpireTest.eq(type(CONST_ME_FIREWORK_YELLOW), "number", "firework effect")
	SpireTest.eq(tile:getCreatureCount(), 0, "tile API works")
end)
