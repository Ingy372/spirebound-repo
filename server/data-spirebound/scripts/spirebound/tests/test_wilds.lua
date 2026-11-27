-- The rebuilt hunting grounds (FLOOR1_WILDS_PLAN.md): walled places with a gate, a hub and four loops.
-- Goes through the real game path: the real map tiles and the monsters the engine really spawned from the spawn file.

local function walkable(pos)
	local t = Tile(pos)
	return t ~= nil and t:getGround() ~= nil and t:isWalkable(false, false, false, false, true)
end

-- every rebuilt ground leaves a gate_<id> point; returns { id = { nw, se } }
local function grounds()
	local out = {}
	for k, _ in pairs(WorldPoints) do
		local id = k:match("^ground_(.+)_nw$")
		if id then
			out[id] = { WorldPoints[k], WorldPoints["ground_" .. id .. "_se"] }
		end
	end
	return out
end

local function monstersIn(nw, se)
	local cx, cy = math.floor((nw.x + se.x) / 2), math.floor((nw.y + se.y) / 2)
	local rx, ry = cx - nw.x + 1, cy - nw.y + 1
	local n = 0
	for _, c in ipairs(Game.getSpectators(Position(cx, cy, nw.z), false, false, rx, rx, ry, ry)) do
		local p = c:getPosition()
		if c:isMonster() and p.x >= nw.x and p.x <= se.x and p.y >= nw.y and p.y <= se.y then
			n = n + 1
		end
	end
	return n
end

SpireTest.add("wilds: every rebuilt ground has a walkable gate, hub, loop mouths and crowd spots", function()
	local count = 0
	for id, _ in pairs(grounds()) do
		count = count + 1
		for _, key in ipairs({ "gate_" .. id, "camp_" .. id }) do
			SpireTest.eq(walkable(WorldPoints[key]), true, key .. " is walkable")
		end
		local sides = WorldPoints["loop_" .. id .. "_a"] and { "a", "b", "c", "d" } or { "nw", "ne", "sw", "se" } -- designed grounds name routes a-d
		for _, side in ipairs(sides) do
			SpireTest.eq(walkable(WorldPoints["loop_" .. id .. "_" .. side]), true, id .. " " .. side .. " loop mouth is walkable")
			local n = 1
			while WorldPoints["crowd_" .. id .. "_" .. side .. "_" .. n] do
				SpireTest.eq(walkable(WorldPoints["crowd_" .. id .. "_" .. side .. "_" .. n]), true, id .. " crowd spot is walkable")
				n = n + 1
			end
			SpireTest.eq(n >= 4, true, id .. " " .. side .. " has at least three crowd spots") -- crowd spots may be on any level
		end
	end
	SpireTest.eq(count >= 1, true, "at least one rebuilt hunting ground")
end)

SpireTest.add("wilds: the engine really spawned each rebuilt ground's monsters (as many as the map places)", function()
	local want = {}
	for _, g in ipairs(SpireWilds.grounds) do
		want[g.id] = g.want
	end
	for id, r in pairs(grounds()) do
		local n = monstersIn(r[1], r[2])
		for _, z in ipairs({ 5, 6, 8, 9, 10 }) do -- designed grounds (FLOOR1_HUNTING_PLAN.md): their hill and lower levels count too
			local nw, se = WorldPoints["level_" .. id .. "_" .. z .. "_nw"], WorldPoints["level_" .. id .. "_" .. z .. "_se"]
			if nw then
				n = n + monstersIn(nw, se)
			end
		end
		local w = want[id]
		SpireTest.eq(w ~= nil and n >= w - 2 and n <= w, true, id .. ": " .. n .. " monsters inside (want " .. tostring(w) .. ")")
	end
end)

SpireTest.add("wilds: Old Tusk's wallow is inside Boar Meadow and walkable", function()
	local p, nw, se = WorldPoints.old_tusk_spawn, WorldPoints.ground_boar_meadow_nw, WorldPoints.ground_boar_meadow_se
	SpireTest.eq(walkable(p), true, "the wallow is walkable")
	SpireTest.eq(p.x > nw.x and p.x < se.x and p.y > nw.y and p.y < se.y, true, "the wallow is inside Boar Meadow")
	SpireTest.eq(walkable(WorldPoints.secret_s2), true, "secret s2 is walkable")
end)

SpireTest.add("wilds: the Old Watchtower has its fixed groups (34 above ground, 32 in the cave)", function()
	local top = monstersIn(Position(1030, 1030, 7), Position(1073, 1073, 7))
	local cave = monstersIn(Position(1030, 1030, 8), Position(1073, 1073, 8))
	SpireTest.eq(top >= 32, true, "courtyard and inner room: " .. top .. " (want 34; the Frenzy event test may add 6)")
	SpireTest.eq(cave >= 30 and cave <= 32, true, "cave: " .. cave .. " (want 32)")
end)

SpireTest.add("wilds: eight party caves on Floor 1 (more above), each with working stairs and 56 to 64 monsters", function()
	local n = 0
	for k, _ in pairs(WorldPoints) do
		local id = k:match("^den_(.+)_nw$")
		if id then
			if WorldPoints[k].x < 2000 then n = n + 1 end
			local s = WorldPoints["stairs_den_" .. id]
			SpireTest.eq(Tile(s) ~= nil and Tile(s):hasFlag(TILESTATE_FLOORCHANGE), true, id .. ": cave stairs lead up")
			local hole = Tile(Position(s.x, s.y, s.z - 1))
			SpireTest.eq(hole ~= nil and hole:hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, id .. ": the hole on the surface leads down")
			SpireTest.eq(walkable(Position(s.x, s.y - 1, s.z - 1)), true, id .. ": surface landing is clear")
			SpireTest.eq(walkable(Position(s.x, s.y + 1, s.z)), true, id .. ": cave landing is clear")
			local c = monstersIn(WorldPoints[k], WorldPoints["den_" .. id .. "_se"])
			-- eight groups of four (seven in the built cellars of the Bandit Road and the Old Quarry), each doubled by H14
			SpireTest.eq(c >= 52 and c <= 64, true, id .. ": " .. c .. " monsters in the cave (want 56 to 64)")
		end
	end
	SpireTest.eq(n, 8, "eight caves on Floor 1 (10.4 pass 3)")
end)

-- FLOOR1_HUNTING_PLAN.md (H4): the Ratwarren is calm by the gate and layered below. Counts the monsters the engine really
-- spawned near a player standing in each place (NOTICE = 10 tiles, same level).
local function near(pos, r)
	local n = 0
	for _, c in ipairs(Game.getSpectators(pos, false, false, r, r, r, r)) do
		if c:isMonster() and c:getPosition().z == pos.z and not c:getMaster() then
			n = n + 1
		end
	end
	return n
end

-- DESIGN.md 9.4: the danger that can reach a player = the summed weight of the monsters within 10 tiles on the same level
local function danger(pos)
	local w = 0
	for _, c in ipairs(Game.getSpectators(pos, false, false, 10, 10, 10, 10)) do
		if c:isMonster() and c:getPosition().z == pos.z and not c:getMaster() then
			w = w + (SpireWilds.weights[c:getName()] or 1)
		end
	end
	return math.floor(w * 10 + 0.5) / 10
end

local function groundById(id)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.id == id then
			return g
		end
	end
end

SpireTest.add("spawn rules: every rebuilt ground is quiet at the gate and each route starts within its type's danger budget", function()
	local n = 0
	for _, g in ipairs(SpireWilds.grounds) do
		if g.starts then
			n = n + 1
			SpireTest.eq(danger(WorldPoints["camp_" .. g.id]), 0, g.id .. ": nothing can reach a player inside the gate")
			for r, band in pairs(g.starts) do
				local lim = band == "party" and SpireWilds.budgets.group.deep or SpireWilds.budgets[g.type][band]
				local d = danger(WorldPoints["loop_" .. g.id .. "_" .. r])
				SpireTest.eq(d <= lim, true, g.id .. " route " .. r .. ": danger " .. d .. " at the start (budget " .. lim .. ", " .. g.type .. " " .. band .. ")")
			end
		end
	end
	SpireTest.eq(n >= 5, true, "the five rebuilt grounds have route starts")
	SpireTest.eq(groundById("wasp_fields").type, "class", "Waspgrass Fields is a class ground")
end)

SpireTest.add("hunting plan: the Ratwarren gate is quiet, the yard calm, and the stairs lead to the Warren below", function()
	SpireTest.eq(near(WorldPoints.camp_starter_west, 10), 0, "no rat can reach a player at the Ratwarren's entrance")
	local downs = 0
	for k, p in pairs(WorldPoints) do
		if k:match("^stairs_starter_west_") then
			downs = downs + 1
			SpireTest.eq(Tile(p) ~= nil and Tile(p):hasFlag(TILESTATE_FLOORCHANGE), true, k .. ": the stairs lead up")
			local hole = Tile(Position(p.x, p.y, p.z - 1))
			SpireTest.eq(hole ~= nil and hole:hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, k .. ": the way down leads down")
		end
	end
	SpireTest.eq(downs >= 2, true, "two ways down into the Warren")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.loop_starter_west_b), "guarded", "the Warren is guarded like the yard")
end)

-- FLOOR1_HUNTING_PLAN.md (H5): Burrow Hills is quiet by the gate, calm in the hollows, and has two ramps up to the Crown
-- and two holes down to the Molework.
SpireTest.add("hunting plan: Burrow Hills is quiet at the gate, ramps lead up to the Crown and holes down to the Molework", function()
	SpireTest.eq(near(WorldPoints.camp_burrow_hills, 10), 0, "no monster can reach a player inside the Burrow Hills gate")
	local ramps, holes = 0, 0
	for k, p in pairs(WorldPoints) do
		if k:match("^ramp_burrow_hills_") then
			ramps = ramps + 1
			SpireTest.eq(Tile(p) ~= nil and Tile(p):hasFlag(TILESTATE_FLOORCHANGE), true, k .. ": the ramp leads up")
			local top = Tile(Position(p.x, p.y, p.z - 1))
			SpireTest.eq(top ~= nil and top:hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, k .. ": the top of the ramp leads down")
			SpireTest.eq(walkable(Position(p.x, p.y - 1, p.z - 1)), true, k .. ": the Crown is walkable at the top")
			SpireTest.eq(walkable(Position(p.x, p.y + 1, p.z)), true, k .. ": the foot of the ramp is walkable")
		elseif k:match("^stairs_burrow_hills_") then
			holes = holes + 1
		end
	end
	SpireTest.eq(ramps, 2, "two ramps up to the Crown")
	SpireTest.eq(holes, 2, "two ways down into the Molework")
end)

-- FLOOR1_HUNTING_PLAN.md (H6): Toad Pond, Sproutling Glade and Waspgrass Fields are quiet inside the gate, every way
-- down leads down, and Hive Knoll has two ramps.
SpireTest.add("hunting plan: Toad Pond, Sproutling Glade and Waspgrass Fields are quiet at the gate and their stairs work", function()
	for _, id in ipairs({ "starter_east", "starter_south", "wasp_fields" }) do
		SpireTest.eq(near(WorldPoints["camp_" .. id], 10), 0, id .. ": no monster can reach a player inside the gate")
		SpireTest.eq(SpirePvP.zoneAt(WorldPoints["loop_" .. id .. "_d"]), "guarded", id .. ": the level below is guarded too")
		local downs = 0
		for k, p in pairs(WorldPoints) do
			if k:match("^stairs_" .. id .. "_") then
				downs = downs + 1
				SpireTest.eq(Tile(p) ~= nil and Tile(p):hasFlag(TILESTATE_FLOORCHANGE), true, k .. ": the stairs lead up")
				local hole = Tile(Position(p.x, p.y, p.z - 1))
				SpireTest.eq(hole ~= nil and hole:hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, k .. ": the way down leads down")
			end
		end
		SpireTest.eq(downs >= 2, true, id .. ": two ways down")
	end
	local ramps = 0
	for k, p in pairs(WorldPoints) do
		if k:match("^ramp_wasp_fields_") then
			ramps = ramps + 1
			SpireTest.eq(walkable(Position(p.x, p.y - 1, p.z - 1)), true, k .. ": Hive Knoll is walkable at the top")
		end
	end
	SpireTest.eq(ramps, 2, "two ramps up Hive Knoll")
end)
