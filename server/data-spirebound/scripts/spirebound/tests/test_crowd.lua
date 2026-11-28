-- The crowd system (FLOOR1_WILDS_PLAN.md Part 7). Goes through the real update the 30-second tick runs, which really
-- creates the monsters on the map; only the player count and "is a player near this spot?" are handed in, since a
-- test boot has no players logged in.

local function reset(g)
	SpireCrowd.grounds[g.id] = nil
	for _, s in ipairs(g.spots) do
		local sr = SpireCrowd.spots[g.id .. ":" .. s.n]
		for _, cid in ipairs(sr and sr.alive or {}) do
			local c = Creature(cid)
			if c then
				c:remove()
			end
		end
		SpireCrowd.spots[g.id .. ":" .. s.n] = nil
	end
end

local function aliveAt(g)
	local n = 0
	for _, s in ipairs(g.spots) do
		local sr = SpireCrowd.spots[g.id .. ":" .. s.n]
		for _, cid in ipairs(sr and sr.alive or {}) do
			local c = Creature(cid)
			if c and c:getHealth() > 0 then
				n = n + 1
				local p = c:getPosition()
				SpireTest.eq(math.abs(p.x - s.x) <= 3 and math.abs(p.y - s.y) <= 3, true, "crowd monster stands at its spot")
			end
		end
	end
	return n
end

local far = function()
	return false
end

SpireTest.add("crowd: quiet with 4 players, half the spots with 5, all with 8, and monsters really appear", function()
	local g = SpireCrowd.ground("boar_meadow")
	reset(g)
	local t = 1000000
	local state, n = SpireCrowd.update(g, t, 4, far)
	SpireTest.eq(state, "quiet", "4 players: quiet")
	SpireTest.eq(n, 0, "4 players: no extra groups")
	state, n = SpireCrowd.update(g, t + 30, 5, far)
	SpireTest.eq(state, "busy", "5 players: busy")
	SpireTest.eq(n, math.ceil(#g.spots / 2), "5 players: the odd-numbered spots switch on")
	local per = 0 -- monsters in one crowd group (the boars are loners since H7: one each)
	for _, e in ipairs(g.spots[1].group) do
		per = per + e[2]
	end
	SpireTest.eq(aliveAt(g), n * per, "their boars are really on the map")
	state, n = SpireCrowd.update(g, t + 60, 8, far)
	SpireTest.eq(state, "packed", "8 players: packed")
	SpireTest.eq(n, math.floor(#g.spots / 2), "8 players: the rest switch on too")
	SpireTest.eq(aliveAt(g), #g.spots * per, "every crowd spot holds a group")
	reset(g)
end)

SpireTest.add("crowd: 12 players is a Rush only on a Guarded ground", function()
	local open, guarded = SpireCrowd.ground("boar_meadow"), SpireCrowd.ground("starter_west")
	reset(open)
	reset(guarded)
	SpireTest.eq((SpireCrowd.update(open, 2000000, 12, far)), "packed", "Open ground with 12: packed")
	SpireTest.eq((SpireCrowd.update(guarded, 2000000, 12, far)), "rush", "Guarded ground with 12: rush")
	SpireTest.eq(SpireCrowd.respawn("rush", guarded.respawn), math.floor(guarded.respawn / 3), "rush: three times as fast")
	local spots = #guarded.spots
	reset(open)
	reset(guarded)
	-- the Ratwarren is a designed ground (FLOOR1_HUNTING_PLAN.md): 3 crowd pockets per route, spread over its levels
	SpireTest.eq(spots, guarded.zs and 12 or 16, "a starter ground's crowd spots (12 on a designed ground, 16 on a loop ground)")
end)

SpireTest.add("crowd: the Rapid Respawn weekend does not fill a ground for a lone player (H10)", function()
	local g = SpireCrowd.ground("boar_meadow")
	reset(g)
	SpireCrowd.forceRapid = true
	local ok, err = pcall(function()
		local state, n = SpireCrowd.update(g, 4000000, 1, far)
		SpireTest.eq(state, "quiet", "one player on the weekend: still quiet")
		SpireTest.eq(n, 0, "one player on the weekend: no extra groups")
		state, n = SpireCrowd.update(g, 4000030, 5, far)
		SpireTest.eq(state, "busy", "five players on the weekend: busy, as on any day")
	end)
	SpireCrowd.forceRapid = nil
	reset(g)
	if not ok then error(err, 0) end
end)

SpireTest.add("crowd: no group appears within 7 tiles of a player", function()
	local g = SpireCrowd.ground("wolf_copse")
	reset(g)
	local _, n = SpireCrowd.update(g, 3000000, 9, function()
		return true
	end)
	SpireTest.eq(n, 0, "a player beside every spot: nothing spawns")
	SpireTest.eq(SpireCrowd.playerNear(Position(g.spots[1].x, g.spots[1].y, g.spots[1].z)), false, "no real player near on a test boot")
	reset(g)
end)

SpireTest.add("crowd: five minutes after the players leave, the spots stop refilling", function()
	local g = SpireCrowd.ground("burrow_hills")
	reset(g)
	local t = 4000000
	SpireCrowd.update(g, t, 8, far)
	SpireTest.eq((SpireCrowd.update(g, t + 30, 0, far)), "packed", "just left: still packed")
	SpireTest.eq((SpireCrowd.update(g, t + 30 + 299, 0, far)), "packed", "4:59 later: still packed")
	-- the crowd monsters are killed off
	for _, s in ipairs(g.spots) do
		for _, cid in ipairs(SpireCrowd.spots[g.id .. ":" .. s.n].alive) do
			local c = Creature(cid)
			if c then
				c:remove()
			end
		end
	end
	SpireTest.eq((SpireCrowd.update(g, t + 30 + 300, 0, far)), "quiet", "5 minutes later: quiet")
	local _, n = SpireCrowd.update(g, t + 30 + 300 + 10000, 0, far)
	SpireTest.eq(n, 0, "quiet: dead crowd groups never come back")
	SpireTest.eq(aliveAt(g), 0, "no crowd monsters left")
	reset(g)
end)

SpireTest.add("crowd: the !hunt line and the cave rule", function()
	local g = SpireCrowd.ground("boar_meadow")
	reset(g)
	SpireCrowd.update(g, 5000000, 6, function()
		return true
	end)
	SpireTest.eq(SpireCrowd.statusLine("boar_meadow"), "Boar Meadow: busy (6 players, extra monsters are out)", "status line")
	reset(g)
	local s = WorldPoints.stairs_den_burrow_hills
	SpireTest.eq(SpireCrowd.caveAt(Position(s.x, s.y + 1, s.z)) ~= nil, true, "the Molework counts as a cave")
	SpireTest.eq(SpireCrowd.caveAt(Position(s.x, s.y, 7)), nil, "the ground above does not")
	local floor1 = 0
	for _, c in ipairs(SpireWilds.caves) do
		if c.x1 < 2000 then floor1 = floor1 + 1 end
	end
	SpireTest.eq(floor1, 8, "eight caves on Floor 1 (10.4 pass 3: the Ridge Tunnels and the Bastion Cellars)")
	SpireTest.eq(#SpireWilds.caves >= 6, true, "and the higher floors' caves are listed too")
end)

SpireTest.add("crowd QA15: in launch week a full harder ground puts out every crowd group twice (Q72)", function()
	SpireTest.eq(SpireCrowd.copies("packed", false, true), 2, "launch week, packed, harder ground: twice")
	SpireTest.eq(SpireCrowd.copies("packed", false, false), 1, "after launch week: once (1.5x)")
	SpireTest.eq(SpireCrowd.copies("busy", false, true), 1, "only when full")
	SpireTest.eq(SpireCrowd.copies("rush", true, true), 1, "starter grounds have their own rush")
	local g = SpireCrowd.ground("boar_meadow")
	reset(g)
	SpireSeason.forceLaunchWeek = true
	local ok, err = pcall(function()
		local state = SpireCrowd.update(g, 5000000, 8, far)
		SpireTest.eq(state, "packed", "8 players: packed")
		local per = 0
		for _, e in ipairs(g.spots[1].group) do
			per = per + e[2]
		end
		SpireTest.eq(aliveAt(g), #g.spots * per * 2, "twice the crowd monsters are really on the map")
	end)
	SpireSeason.forceLaunchWeek = nil
	reset(g)
	if not ok then
		error(err)
	end
end)
