-- Fixes for the blockers found in REVIEW.md (3.1 floor skipping, 3.2 Skystep, 3.3 skulls that never expire).

SpireTest.add("review: skulls last days, not decades", function()
	SpireTest.eq(SpirePvP.skullSeconds(SKULL_RED), 7 * 86400, "red skull = 7 days of seconds remaining")
	SpireTest.eq(SpirePvP.skullSeconds(SKULL_BLACK), 14 * 86400, "black skull = 14 days of seconds remaining")
	SpireTest.eq(SpirePvP.skullSeconds(SKULL_NONE), 0, "no skull, no time")
	-- a calendar time (seconds since 1970) would be over a billion: the old bug
	SpireTest.eq(SpirePvP.skullSeconds(SKULL_BLACK) < 100 * 86400, true, "a duration, not a calendar time")
end)

SpireTest.add("review: nobody stands on a sealed floor", function()
	SpireTest.eq(Floors.mayStandOn(1, false, false), true, "floor 1 is always open")
	SpireTest.eq(Floors.mayStandOn(0, false, false), true, "off-floor places (test areas) are fine")
	SpireTest.eq(Floors.mayStandOn(3, false, false), false, "a player on sealed floor 3 is sent back")
	SpireTest.eq(Floors.mayStandOn(3, true, false), true, "an open floor is fine")
	SpireTest.eq(Floors.mayStandOn(3, false, true), true, "staff may test sealed floors")
end)

SpireTest.add("review: the stair to the next floor can't be walked around", function()
	local gates = { "gate_floor2" }
	for n = 2, 10 do
		table.insert(gates, "f" .. n .. "_gate_next")
	end
	local checked = 0
	for _, key in ipairs(gates) do
		local g = WorldPoints[key]
		if g then
			-- the whole row of the boulder is wall, from one side of the boss room to the other
			for dx = -14, 13 do
				local tile = Tile(Position(g.x + dx, g.y, g.z))
				SpireTest.eq(tile ~= nil and tile:hasFlag(TILESTATE_BLOCKSOLID), true, string.format("%s: tile %d beside the boulder is blocked", key, dx))
			end
			-- and the stair itself is still there behind it
			SpireTest.eq(Tile(Position(g.x, g.y - 1, g.z)) ~= nil, true, key .. ": stair tile exists")
			checked = checked + 1
		end
	end
	SpireTest.eq(checked, 10, "all ten floors have a sealed stair")
end)

SpireTest.add("review: Skystep needs a real gap", function()
	SpireTest.eq(SpireSpells.levitateGapFree(true), false, "a floor in the way blocks Skystep")
	SpireTest.eq(SpireSpells.levitateGapFree(false), true, "an open gap allows it")
	-- the labyrinth's upper level has a floor right above the level below, so there is never a gap to climb through
	local stair = WorldPoints.stair_floor2_src or WorldPoints.gate_floor2
	local below = Tile(Position(stair.x, stair.y + 2, stair.z + 1))
	local above = Tile(Position(stair.x, stair.y + 2, stair.z))
	SpireTest.eq(below ~= nil and above ~= nil and above:getGround() ~= nil, true, "boss room floor lies over the maze")
	SpireTest.eq(SpireSpells.levitateGapFree(above:getGround() ~= nil), false, "so Skystep up from the maze is refused")
end)
