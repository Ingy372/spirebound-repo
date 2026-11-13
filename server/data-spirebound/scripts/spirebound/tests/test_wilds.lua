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
		for _, side in ipairs({ "nw", "ne", "sw", "se" }) do
			SpireTest.eq(walkable(WorldPoints["loop_" .. id .. "_" .. side]), true, id .. " " .. side .. " loop mouth is walkable")
			local n = 1
			while WorldPoints["crowd_" .. id .. "_" .. side .. "_" .. n] do
				SpireTest.eq(walkable(WorldPoints["crowd_" .. id .. "_" .. side .. "_" .. n]), true, id .. " crowd spot is walkable")
				n = n + 1
			end
			SpireTest.eq(n >= 4, true, id .. " " .. side .. " has at least three crowd spots")
		end
	end
	SpireTest.eq(count >= 1, true, "at least one rebuilt hunting ground")
end)

SpireTest.add("wilds: the engine really spawned each rebuilt ground's monsters (48 small, 72 standard)", function()
	local want = { starter_west = 48, starter_east = 48, starter_south = 48, wasp_fields = 48 }
	for id, r in pairs(grounds()) do
		local n = monstersIn(r[1], r[2])
		local w = want[id] or 72
		SpireTest.eq(n >= w - 2 and n <= w, true, id .. ": " .. n .. " monsters inside (want " .. w .. ")")
	end
end)

SpireTest.add("wilds: Old Tusk's wallow is inside Boar Meadow and walkable", function()
	local p, nw, se = WorldPoints.old_tusk_spawn, WorldPoints.ground_boar_meadow_nw, WorldPoints.ground_boar_meadow_se
	SpireTest.eq(walkable(p), true, "the wallow is walkable")
	SpireTest.eq(p.x > nw.x and p.x < se.x and p.y > nw.y and p.y < se.y, true, "the wallow is inside Boar Meadow")
	SpireTest.eq(walkable(WorldPoints.secret_s2), true, "secret s2 is walkable")
end)
