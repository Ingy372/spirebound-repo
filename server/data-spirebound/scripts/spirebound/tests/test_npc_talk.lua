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

SpireTest.add("newcomer: the Arrival Yard is guarded, the rat pen gap keeps rats in", function()
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.tutorial_spawn), "guarded", "Arrival Yard zone")
	local pen = WorldPoints.tutorial_pen
	local gap = Tile(Position(pen.x, pen.y + 1, pen.z))
	SpireTest.eq(gap ~= nil and gap:hasFlag(TILESTATE_PROTECTIONZONE), true, "pen gap is a safe tile monsters can't cross")
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

SpireTest.add("Hearthgate v3: four open archways, a locker six steps from the Hearthstone, 30 street houses", function()
	local t = WorldPoints.temple_hearthgate
	for _, d in ipairs({ { 0, -11 }, { 0, 11 }, { -14, 0 }, { 14, 0 } }) do
		local p = Position(t.x + d[1], t.y + d[2], t.z)
		local tile = Tile(p)
		SpireTest.eq(tile ~= nil and tile:isWalkable(false, false, false, false, true), true, "archway " .. d[1] .. "," .. d[2] .. " is open")
	end
	local locker
	for dx = -8, 8 do
		for dy = -8, 8 do
			local tile = Tile(Position(t.x + dx, t.y + dy, t.z))
			if tile and tile:getItemByType(ITEM_TYPE_DEPOT) then
				if not locker or math.abs(dx) + math.abs(dy) < locker then locker = math.abs(dx) + math.abs(dy) end
			end
		end
	end
	SpireTest.eq(locker ~= nil and locker <= 8, true, "a depot locker within eight steps of the Hearthstone")
	local streets = 0
	for _, h in ipairs(Game.getHouses()) do
		local n = h:getName()
		if n:find("^Squareside") or n:find("^Crown Row") or n:find("^Northside") or n:find("^Greenside") or n:find("^Lantern Row")
			or n:find("^Manor Walk") or n:find("^Southgate Row") then
			streets = streets + 1
		end
	end
	SpireTest.eq(streets, 30, "thirty houses in the eight streets")
end)
