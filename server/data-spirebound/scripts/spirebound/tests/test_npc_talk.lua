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
