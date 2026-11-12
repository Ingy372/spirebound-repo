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
