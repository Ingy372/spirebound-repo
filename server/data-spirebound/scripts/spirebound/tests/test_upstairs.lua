-- Upper storeys, stairs, ladders and roofs (map task: "add the stairs and roofs").
-- Goes through the real game path: the real map tiles, the server's own floor-change flags, the ladder action's own
-- "climb up" rule, and a creature actually stepping onto the stairs.

local function walkable(pos)
	local t = Tile(pos)
	return t ~= nil and t:getGround() ~= nil and t:isWalkable(false, false, false, false, true)
end

local function checkStairs(name)
	local s = WorldPoints["stairs_" .. name]
	if not s then error("no stairs point " .. name) end
	local up = Tile(s)
	SpireTest.eq(up ~= nil and up:hasFlag(TILESTATE_FLOORCHANGE), true, name .. ": stairs tile changes floor")
	local hole = Tile(Position(s.x, s.y, s.z - 1))
	SpireTest.eq(hole ~= nil and hole:hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, name .. ": the tile above leads back down")
	SpireTest.eq(walkable(Position(s.x, s.y - 1, s.z - 1)), true, name .. ": landing upstairs is clear")
	SpireTest.eq(walkable(Position(s.x, s.y + 1, s.z)), true, name .. ": landing downstairs is clear")
end

SpireTest.add("map: stairs in the Guild Hall, the Millcross inn and two-storey houses work both ways", function()
	checkStairs("guild_hall")
	checkStairs("millcross_inn")
	local houses = 0
	for k, _ in pairs(WorldPoints) do
		local n = k:match("^stairs_(house_%d+)$")
		if n then
			checkStairs(n)
			houses = houses + 1
		end
	end
	SpireTest.eq(houses >= 4, true, "at least four two-storey houses")
end)

SpireTest.add("map: a creature walking onto stairs arrives upstairs", function()
	local s = WorldPoints.stairs_guild_hall
	local start = Position(s.x, s.y + 1, s.z)
	local npc = Game.createNpc("Guildwarden Sela", start, false, true)
	if not npc then error("could not place a test walker") end
	npc:teleportTo(start)
	local ret = npc:move(DIRECTION_NORTH)
	local p = npc:getPosition()
	npc:remove()
	SpireTest.eq(p.z, s.z - 1, "went up one level (move returned " .. tostring(ret) .. ")")
	SpireTest.eq(p.y, s.y - 1, "arrived on the landing north of the stairs")
end)

SpireTest.add("map: the Hunters' Hall ladder climbs to the loft and the trapdoor leads back", function()
	local l = WorldPoints.ladder_hunters_hall
	local t = Tile(l)
	local found = false
	for _, item in ipairs(t:getItems() or {}) do
		if table.contains(Game.getLadderIds(), item:getId()) then found = true end
	end
	SpireTest.eq(found, true, "a ladder the server's ladder action knows")
	local top = Position(l):moveUpstairs()
	SpireTest.eq(top.z, l.z - 1, "climbing goes up one level")
	SpireTest.eq(walkable(top), true, "and lands on the loft floor")
	local trap = Tile(Position(l.x, l.y, l.z - 1))
	SpireTest.eq(trap ~= nil and trap:hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, "the trapdoor leads back down")
end)

SpireTest.add("map: upstairs of a two-storey house belongs to the house; buildings have roofs", function()
	for k, s in pairs(WorldPoints) do
		if k:match("^stairs_house_") then
			local below = Tile(Position(s.x - 1, s.y, s.z)):getHouse()
			local above = Tile(Position(s.x - 1, s.y, s.z - 1)):getHouse()
			SpireTest.eq(below ~= nil and above ~= nil and below:getId() == above:getId(), true, k .. ": upstairs is part of the same house")
		end
	end
	local g = WorldPoints.stairs_guild_hall
	SpireTest.eq(SpirePvP.zoneAt(Position(g.x, g.y - 1, g.z - 1)), "town", "upstairs in town is still the town zone")
	local temple = WorldPoints.temple_hearthgate
	local roof = Tile(Position(temple.x, temple.y, temple.z - 1))
	SpireTest.eq(roof ~= nil and roof:getGround() ~= nil, true, "the temple has a roof over it")
end)
