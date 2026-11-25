-- Roadmap M3: the Spire Chronicle (lib/spirebound/chronicle.lua, scripts/spirebound/chronicle.lua).
local C = SpireChronicle

-- a stand-in for an online character: enough for SpireChronicle.add and its rewards
local function fakePlayer(accountId, guid, name)
	local titles = {}
	local items = {}
	return {
		titles = titles, items = items,
		getAccountId = function() return accountId end,
		getGuid = function() return guid end,
		getName = function() return name end,
		getPosition = function() return Position(1000, 1000, 7) end,
		sendTextMessage = function() end,
		addItem = function(_, id, n) items[id] = (items[id] or 0) + (n or 1) return true end,
		kv = function() return { scoped = function() return { set = function(_, k, v) titles[k] = v end, get = function(_, k) return titles[k] end } end } end,
	}
end

SpireTest.add("chronicle: chapters open in order, levels keep the best, counts add up", function()
	local rec = { counts = {}, chapter = 1 }
	local fin = C.step(rec, "level", 8, 0)
	SpireTest.eq(#fin, 0, "level 8 alone does not finish chapter 1")
	C.step(rec, "level", 5, 0)
	SpireTest.eq(rec.counts.level, 8, "a lower level never lowers the best")
	C.step(rec, "path", 1, 0)
	C.step(rec, "kill", 60, 0)
	C.step(rec, "kill", 40, 0)
	SpireTest.eq(rec.counts.kill, 100, "kills from two characters add up")
	fin = C.step(rec, "quest", 1, 0)
	SpireTest.eq(#fin == 1 and fin[1] == 1, true, "the last goal finishes chapter 1")
	SpireTest.eq(rec.chapter, 2, "chapter 2 is next")
	C.step(rec, "secret", 3, 0) -- secrets found early still count later
	C.step(rec, "fish", 5, 0)
	C.step(rec, "task", 1, 0)
	fin = C.step(rec, "level", 20, 0)
	SpireTest.eq(rec.chapter, 3, "chapter 2 done")
	local lines = C.lines(rec, 1, 0)
	local found = false
	for _, l in ipairs(lines) do
		if l:find("Defeat a field boss", 1, true) then found = true end
	end
	SpireTest.eq(found, true, "the Journal lists chapter 3's goals")
end)

SpireTest.add("chronicle: shared by the account, finishing gives seal, title, Monument line and cup; nothing else carries", function()
	local acc, season = 990001, 77
	local saved = SpireSeason.current
	SpireSeason.current = function() return season end
	C.put(acc, { counts = {}, chapter = 1 }, season)
	SpireSeason.accountKv(acc):set("chronicles", {})
	local a, b = fakePlayer(acc, 990101, "Chron Alpha"), fakePlayer(acc, 990102, "Chron Beta")
	local ok, err = pcall(function()
		-- chapters 1-4 by two characters on one account
		C.add(a, "level", 50) C.add(a, "path", 1) C.add(a, "kill", 100) C.add(a, "quest", 1)
		C.add(b, "task", 1) C.add(b, "fish", 5) C.add(b, "secret", 5)
		C.add(a, "fieldboss", 1) C.add(a, "floorboss", 1) C.add(b, "floor", 2) C.add(b, "beacon", 1)
		C.add(b, "underkeep", 1) C.add(a, "miniboss", 1)
		SpireTest.eq(C.get(acc, season).chapter, 5, "two characters together reach chapter 5")
		C.add(b, "floor", 4) C.add(a, "floorboss", 4) C.add(b, "secret", 7)
		SpireTest.eq(C.get(acc, season).finishedAt, nil, "not done before level 100")
		C.add(b, "level", 100)
		SpireTest.eq(C.get(acc, season).finishedAt ~= nil, true, "level 100 on the second character finishes it")
		SpireTest.eq(C.legacyCount(acc), 1, "the account's seal counts one season")
		SpireTest.eq((SpireSeason.accountKv(acc):get("titles") or {})["Chronicler"] ~= nil, true, "the title is account-wide")
		SpireTest.eq(b.titles["Chronicler"] ~= nil, true, "the finishing character wears it at once")
		SpireTest.eq(b.items[C.TROPHY], 1, "a Chronicle Cup for the house")
		local names = C.finishers(season)
		SpireTest.eq(names[#names], "Chron Beta", "the Monument names who finished")
		SpireTest.eq(SpireMonumentText():find("Chron Beta", 1, true) ~= nil, true, "and the Monument shows it")
		local before = C.legacyCount(acc)
		C.add(b, "kill", 1)
		SpireTest.eq(C.legacyCount(acc), before, "no second reward in the same season")
		local rec = SpireSeason.archivePlayer(990102, acc, "Chron Beta", 100, 4, season)
		SpireTest.eq(rec.chronicle, true, "the Hall of Seasons marks the finished Chronicle")
		-- a new season starts a fresh Chronicle; only the seal and title carry over
		SpireTest.eq(C.get(acc, season + 1).chapter, 1, "next season starts at chapter 1")
		SpireTest.eq(next(C.get(acc, season + 1).counts), nil, "with no progress carried over")
		SpireTest.eq(C.titleFor(2), "Seasoned Chronicler", "the seal grows with a second season")
		for _, stmt in ipairs(SpireSeason.wipeStatements()) do
			SpireTest.eq(stmt:find("account%.") == nil and stmt:find("chronicle") == nil, true, "the season wipe keeps account seals")
		end
		SpireTest.eq(ItemType(C.TROPHY):getName(), "Chronicle Cup", "the cup has its own name")
	end)
	SpireSeason.current = saved
	if not ok then error(err, 0) end
end)

SpireTest.add("chronicle: boss kinds and the Journal tab", function()
	SpireTest.eq(C.bossKind("Gate Hound"), "field", "the Gate Hound is a field boss")
	SpireTest.eq(C.bossKind("Axe-Lord of the Stair"), "floor", "the Axe-Lord is a floor boss")
	SpireTest.eq(C.bossKind("Old Tusk"), "mini", "Old Tusk is a hidden beast")
	SpireTest.eq(C.bossKind("Field Rat"), nil, "a rat is nothing special")
	local fake = { getAccountId = function() return 990002 end } -- no getGuid: the Journal skips translation
	local reply = SpireJournal.build(fake, "chronicle")
	SpireTest.eq(reply ~= nil and reply.tab == "chronicle", true, "the Journal builds a Chronicle tab")
	SpireTest.eq(reply.lines[2]:find("Chapter 1", 1, true) ~= nil, true, "a new account starts at chapter 1")
end)
