-- House doors follow the map, not the database.
-- Canary saves every house tile (doors included) and, on start, turns the map's door into the saved one.
-- After a map change that brings back old doors (Jay's playtest 2026-11-13: shops kept a level-locked
-- "gate of expertise"). This puts back the door the current map has (HouseDoors, written by tools/mapgen.py).
-- Furniture and other things players put in houses are not touched.

-- the closed version of each open door, so a door its owner closed stays closed
local closedOf = {}
for _, t in ipairs({ CustomDoorTable, KeyDoorTable }) do
	for _, d in ipairs(t or {}) do
		if d.openDoor and d.closedDoor then
			closedOf[d.openDoor] = d.closedDoor
		end
	end
end

function SpireFixHouseDoors()
	local fixed = 0
	for _, d in ipairs(HouseDoors or {}) do
		local tile = Tile(Position(d[1], d[2], d[3]))
		local door = tile and tile:getItemByType(ITEM_TYPE_DOOR)
		if door and door:getId() ~= d[4] and door:getId() ~= closedOf[d[4]] then
			door:transform(d[4])
			fixed = fixed + 1
		end
	end
	return fixed
end

local fix = GlobalEvent("SpireHouseDoors")
function fix.onStartup()
	local fixed = SpireFixHouseDoors()
	if fixed > 0 then
		logger.info("[Spirebound] {} house doors put back to the map's door", fixed)
	end
	return true
end
fix:register()
