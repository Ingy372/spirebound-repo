-- Roadmap 2.14 - 2.17: Hardcore extras, autoloot, tasks, catch-up.
SpireTest.add("death: catch-up and Hardcore blessing cap", function()
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.NORMAL, 5000, 40, 100000), 0, "normal below 50 loses nothing")
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.NORMAL, 5000, 60, 100000), 5000, "normal from 50 loses as usual")
	-- level 40: Tibia's unblessed loss is 63,360 experience
	SpireTest.eq(Difficulty.baseDeathLoss(40, 917800), 63360, "base loss at level 40")
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.HARDCORE, 1000, 40, 917800), 31680, "hardcore: blessings can't remove more than half")
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.HARDCORE, 63360, 40, 917800), 95040, "hardcore unblessed: x1.5")
end)

SpireTest.add("tasks: list, one at a time, daily repeat", function()
	for _, t in ipairs(SpireTasks.list) do
		if not MonsterType(t.monster) then error(t.id .. " targets unknown " .. t.monster) end
	end
	SpireTest.eq((SpireTasks.canTake(nil, nil, 1000000)), true, "free to take")
	SpireTest.eq((SpireTasks.canTake("t_wolves", nil, 1000000)), false, "one task at a time")
	SpireTest.eq((SpireTasks.canTake(nil, 1000000 - 3600, 1000000)), false, "done an hour ago")
	SpireTest.eq((SpireTasks.canTake(nil, 1000000 - 21 * 3600, 1000000)), true, "done yesterday")
	SpireTest.eq(configManager.getBoolean(configKeys.AUTOLOOT), true, "autoloot on")
end)
