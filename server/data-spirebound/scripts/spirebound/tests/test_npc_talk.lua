-- Found in the level-10 playthrough (2026-11-12): Guide Pell said nothing to "quest". Talks to the quest code the way an
-- NPC does, with a stand-in player, and checks that every quest giver answers a newcomer.
local function fakePlayer()
	local st = {}
	return {
		getId = function() return 424242 end,
		getStorageValue = function(_, k) return st[k] or -1 end,
		setStorageValue = function(_, k, v) st[k] = v end,
		addMoney = function() end,
		getLevel = function() return 1 end,
		kv = function() return { scoped = function() return { set = function() end, get = function() end } end } end,
		sendTextMessage = function() end,
	}
end

SpireTest.add("npc talk: quest givers answer 'quest' (Guide Pell first)", function()
	local said
	local handler = { say = function(_, text) said = text end }
	local p = fakePlayer()
	local ok, err = pcall(SpireQuests.talk, nil, handler, p, "quest", "Guide Pell")
	SpireTest.eq(ok, true, "quest talk runs without an error: " .. tostring(err))
	SpireTest.eq(type(said), "string", "Guide Pell says something to 'quest'")
	said = nil
	ok, err = pcall(SpireQuests.talk, nil, handler, p, "yes", "Guide Pell")
	SpireTest.eq(ok, true, "accepting runs without an error: " .. tostring(err))
	SpireTest.eq(p:getStorageValue(50121), 1, "First Blood is in the quest log")
end)

SpireTest.add("newcomer: the Arrival Yard is guarded, the granary cellar's doorway keeps rats in", function()
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.tutorial_spawn), "guarded", "Arrival Yard zone")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.tutorial_pen), "guarded", "the rat cellar is guarded too")
	local door = Tile(WorldPoints.tutorial_cellar_door)
	SpireTest.eq(door ~= nil and door:hasFlag(TILESTATE_PROTECTIONZONE), true, "cellar doorway is a safe tile monsters can't cross")
	SpireTest.eq(SpireTutorial.inYard(WorldPoints.tutorial_pen), true, "the cellar counts as the yard (no bounce to the spawn)")
	local stairs = WorldPoints.stairs_granary
	SpireTest.eq(Tile(Position(stairs.x, stairs.y, stairs.z - 1)) ~= nil, true, "the granary's stairs lead up into the house")
end)

SpireTest.add("economy: crafting recipes are real, need materials and gold, and the crafters know them", function()
	SpireTest.eq(#SpireCraft.recipes >= 7, true, "recipes loaded")
	for _, r in ipairs(SpireCraft.recipes) do
		if not r.addon then
			SpireTest.eq(ItemType(r.item):getId() ~= 0, true, r.name .. " is a real item")
		end
		for _, need in ipairs(r.needs) do
			SpireTest.eq(ItemType(need[1]):getId() ~= 0, true, r.name .. ": material " .. need[1] .. " is a real item")
		end
	end
	local r = SpireCraft.forNpc("Fletcher Tamsin")[1]
	local none = function() return 0 end
	local plenty = function() return 99 end
	SpireTest.eq(#SpireCraft.missing(r, none, 0) > 0, true, "nothing in the bag: something is missing")
	SpireTest.eq(#SpireCraft.missing(r, plenty, 10000), 0, "materials and gold: nothing missing")
	SpireTest.eq(#SpireCraft.missing(r, plenty, 0), 1, "only the fee is missing")
	local said
	local handler = { say = function(_, text) said = text end }
	SpireTest.eq(SpireCraft.talk(nil, handler, nil, "craft", "Fletcher Tamsin"), true, "the Fletcher answers 'craft'")
	SpireTest.eq(said:find("sniper arrows", 1, true) ~= nil, true, "and lists sniper arrows")
	SpireTest.eq(SpireCraft.talk(nil, handler, nil, "craft", "Priest Odran"), false, "the priest crafts nothing")
end)

SpireTest.add("boosted creature: a real hunting-ground monster each day, no repeats within 13 days", function()
	local seen = {}
	for d = 100, 112 do
		local n = SpireBoost.pick(d)
		SpireTest.eq(MonsterType(n) ~= nil, true, n .. " is a real monster")
		SpireTest.eq(seen[n] == nil, true, n .. " not boosted twice in 13 days")
		seen[n] = true
	end
	SpireTest.eq(type(SpireBoost.today()), "string", "today has a boosted creature")
end)

SpireTest.add("temple scroll: a real item the Runewright sells", function()
	SpireTest.eq(ItemType(25718):getId(), 25718, "temple teleport scroll exists")
	local npc = NpcType("Runewright Mael")
	SpireTest.eq(npc ~= nil, true, "Runewright Mael is loaded")
end)

SpireTest.add("the Hearth: spawn point, three levels by stairs, lockers, junk buyer, vault", function()
	local t = WorldPoints.temple_hearthgate
	SpireTest.eq(Town(1):getTemplePosition() == t, true, "Hearthgate's temple position is the Hearth's nave")
	SpireTest.eq(Tile(t):hasFlag(TILESTATE_PROTECTIONZONE), true, "the respawn point is a safe tile")
	for _, n in ipairs({ "hearth_west", "hearth_east", "hearth_hall" }) do
		local s = WorldPoints["stairs_" .. n]
		SpireTest.eq(Tile(s):hasFlag(TILESTATE_FLOORCHANGE), true, n .. " stairs go up")
		SpireTest.eq(Tile(Position(s.x, s.y, s.z - 1)):hasFlag(TILESTATE_FLOORCHANGE_DOWN), true, n .. " stairs come back down")
	end
	SpireTest.eq(NpcType("Trader Osric") ~= nil, true, "the junk buyer is loaded")
	SpireTest.eq(NpcType("Banker Tolliver") ~= nil and NpcType("Banker Ansel") ~= nil, true, "two bankers")
	local action, n = SpireVault.parse("vault deposit 500")
	SpireTest.eq(action, "deposit", "parses a vault deposit")
	SpireTest.eq(n, 500, "parses the amount")
	local bank, vault = SpireVault.move("deposit", 500, 800, 100)
	SpireTest.eq(bank, 300, "bank goes down")
	SpireTest.eq(vault, 600, "vault goes up")
	bank, vault = SpireVault.move("withdraw", -1, 0, 600)
	SpireTest.eq(bank, 600, "withdraw all moves everything back")
	local b2 = SpireVault.move("deposit", 900, 800, 0)
	SpireTest.eq(b2, 800, "can't deposit more than the bank holds")
	SpireTest.eq(SpireVault.parse("hello"), nil, "ordinary words aren't vault commands")
end)

SpireTest.add("Hearthgate v4: the Hearthstone under open sky, the Hearth's archways, a locker close by, 30 street houses", function()
	local t = WorldPoints.temple_hearthgate
	local function open(x, y)
		local tile = Tile(Position(x, y, t.z))
		return tile ~= nil and tile:isWalkable(false, false, false, false, true)
	end
	-- the Hearthstone stands in the middle of Hearth Plaza: it and its eight neighbours are clear, with sky above
	for dx = -1, 1 do
		for dy = -1, 1 do
			SpireTest.eq(open(t.x + dx, t.y + dy), true, "the Hearthstone square is clear at " .. dx .. "," .. dy)
		end
	end
	SpireTest.eq(Tile(Position(t.x, t.y, t.z - 1)) == nil, true, "nothing over the Hearthstone: it is in the open plaza")
	-- the Hearth (maps/hearthgate_plan.py: 42, 12, 30, 23; the Hearthstone is 56, 49): front archway faces the Hearthstone
	for _, d in ipairs({ { -1, -15 }, { 0, -15 }, { 1, -15 }, { 2, -15 }, { 0, -37 }, { 1, -37 }, { -14, -26 }, { 15, -26 } }) do
		SpireTest.eq(open(t.x + d[1], t.y + d[2]), true, "the Hearth's archway " .. d[1] .. "," .. d[2] .. " is open")
	end
	-- the nearest locker, counted in real steps (no diagonals) from the Hearthstone; the v4 plan promises 26
	local seen, todo, steps, near = { [t.x .. ":" .. t.y] = true }, { { t.x, t.y } }, 0, nil
	while #todo > 0 and steps <= 30 and not near do
		local nxt = {}
		for _, p in ipairs(todo) do
			local tile = Tile(Position(p[1], p[2], t.z))
			if tile and tile:getGround() and tile:getGround():getId() == 10145 then near = steps break end
			for _, d in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }) do
				local x, y = p[1] + d[1], p[2] + d[2]
				if not seen[x .. ":" .. y] and open(x, y) then
					seen[x .. ":" .. y] = true
					nxt[#nxt + 1] = { x, y }
				end
			end
		end
		todo, steps = nxt, steps + 1
	end
	SpireTest.eq(near ~= nil and near <= 26, true, "a depot locker within 26 steps of the Hearthstone (" .. tostring(near) .. ")")
	-- the Hearth's depot booths: a switch tile in front of every locker, walled in two tiles deep on both sides
	local function blocked(x, y)
		return not open(x, y)
	end
	local booths, good = 0, 0
	for dx = -13, 14 do
		for dy = -36, -16 do
			local x, y = t.x + dx, t.y + dy
			local tile = Tile(Position(x, y, t.z))
			if tile and tile:getItemByType(ITEM_TYPE_DEPOT) then
				booths = booths + 1
				for _, f in ipairs({ { 0, 1 }, { 0, -1 } }) do
					local st = Tile(Position(x, y + f[2], t.z))
					if st and st:getGround() and st:getGround():getId() == 10145 then
						local s1, s2 = y + f[2], y + 2 * f[2]
						if blocked(x - 1, s1) and blocked(x + 1, s1) and blocked(x - 1, s2) and blocked(x + 1, s2) then good = good + 1 end
					end
				end
			end
		end
	end
	SpireTest.eq(booths, 20, "twenty lockers in the Hearth's depot wings")
	SpireTest.eq(good, 20, "every booth has a depot switch and two-deep dividers")
	local streets = 0
	for _, h in ipairs(Game.getHouses()) do
		local n = h:getName()
		if n:find("^Squareside") or n:find("^Crown Row") or n:find("^Northside") or n:find("^Greenside") or n:find("^Lantern Row")
			or n:find("^Manor Walk") or n:find("^Southgate Row") then
			streets = streets + 1
		end
	end
	SpireTest.eq(streets, 30, "thirty houses in the town's streets")
end)

-- P3: Hearthgate's townsfolk are out in the square
SpireTest.add("town: the townsfolk walk about Hearthgate", function()
	SpireTest.eq(#SpireTownsfolk, 6, "six townsfolk")
	for _, f in ipairs(SpireTownsfolk) do
		local spot = SpireTownlife.placed[f.name]
		SpireTest.eq(spot ~= nil, true, f.name .. " has a spot")
		local seen = false
		for _, c in ipairs(spot and Game.getSpectators(spot, false, false, 3, 3, 3, 3) or {}) do
			if c:isNpc() and c:getName() == f.name then
				seen = true
			end
		end
		SpireTest.eq(seen, true, f.name .. " is in town")
		SpireTest.eq(math.max(math.abs(spot.x - f.near.x), math.abs(spot.y - f.near.y)) <= 6, true, f.name .. " is near where they belong")
	end
	local t = Tile(SpireTownlife.FOUNTAIN)
	SpireTest.eq(t ~= nil and t:getItemById(1922) ~= nil, true, "the fountain is where the spray goes")
end)
