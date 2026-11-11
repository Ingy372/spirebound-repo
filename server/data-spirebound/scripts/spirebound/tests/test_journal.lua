-- Roadmap 6.1: Journal window text
SpireTest.add("journal: secret rows hide names until found", function()
	local s = SpireSecrets.list[1]
	local hidden = SpireJournal.secretLine(s, false)
	SpireTest.eq(hidden:find(s.name, 1, true), nil, "name hidden")
	SpireTest.eq(hidden:find(s.hint, 1, true) ~= nil, true, "hint shown")
	SpireTest.eq(SpireJournal.secretLine(s, true):find(s.name, 1, true) ~= nil, true, "name shown when found")
end)

SpireTest.add("journal: fishing log and every tab build", function()
	local log = { hearth_minnow = { count = 3, best = 0.31 } }
	local lines = SpireJournal.fishingLines(SpireFishing.tables, function(id) return log[id] end)
	SpireTest.eq(lines[1]:find("1 of", 1, true) ~= nil, true, "one kind caught")
	local seen = false
	for _, l in ipairs(lines) do
		if l:find("Hearth Minnow", 1, true) and l:find("caught 3", 1, true) then seen = true end
	end
	SpireTest.eq(seen, true, "caught fish listed with count")
	SpireTest.eq(SpireJournal.tabFromRequest('{"t":"journal","tab":"quests"}'), "quests", "request parse")
	SpireTest.eq(SpireJournal.tabFromRequest('{"t":"bot","on":true}'), nil, "other messages ignored")
	SpireTest.eq(SpireJournal.build({}, "nonsense"), nil, "unknown tab")
	SpireTest.eq(type(SpireJournal.build({}, "top").lines), "table", "top builds")
	SpireTest.eq(type(SpireJournal.build({}, "memorial").lines), "table", "memorial builds")
end)
