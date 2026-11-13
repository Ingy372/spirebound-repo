-- Roadmap R8: the server saves at the big moments. Goes through the real floor-state calls the boss deaths use.
SpireTest.add("save: a field boss kill and a floor clear save the server at once", function()
	local realSave, saves = saveServer, 0
	saveServer = function()
		saves = saves + 1
	end
	local ok, err = pcall(function()
		Floors.reset(97)
		Floors.reset(98)
		SpireSave.lastTime = nil
		SpireTest.eq(Floors.markFieldBoss(97, { "Tester" }), true, "first field boss kill")
		SpireTest.eq(saves, 1, "the field boss kill saved the server")
		SpireTest.eq(SpireSave.last, "floor 97 field boss", "and says why")
		SpireSave.lastTime = nil
		SpireTest.eq(Floors.recordClear(97, { "Tester" }, "Tester", 60), true, "first clear")
		SpireTest.eq(saves, 2, "the floor clear saved the server")
		SpireTest.eq(SpireSave.now("again at once"), false, "two big moments in the same few seconds share one save")
		SpireTest.eq(saves, 2, "no extra save")
	end)
	saveServer = realSave
	Floors.reset(97)
	Floors.reset(98)
	SpireSave.lastTime = nil
	if not ok then
		error(err)
	end
	SpireTest.eq(SpireSave.INTERVAL_MINUTES, 10, "the regular save is every 10 minutes")
end)
