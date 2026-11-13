-- Roadmap R10: the Fortune Hall cut is really destroyed, halls have an hourly limit, every floor has hunting tasks
-- with sane payouts, and task points buy something.
SpireTest.add("balance: the Fortune Hall's 5% leaves the game whoever wins", function()
	local p, h, burned = SpireHouses.settleDice(1000, true)
	SpireTest.eq(p, 900, "a winning bettor gains the bet less the cut")
	SpireTest.eq(h, -1000, "the host loses the bet")
	SpireTest.eq(burned, 100, "100 gold destroyed")
	p, h, burned = SpireHouses.settleDice(1000, false)
	SpireTest.eq(p + h + burned, 0, "nothing is created: what the players lose is what was destroyed")
	SpireTest.eq(h, 900, "a winning host also pays the cut")
	local now = 5000
	SpireTest.eq((SpireHouses.hallHasRoom({ { now - 100, 400000 } }, 100000, now)), true, "within the hourly limit")
	SpireTest.eq((SpireHouses.hallHasRoom({ { now - 100, 450000 } }, 100000, now)), false, "past the hall's hourly limit")
	SpireTest.eq((SpireHouses.hallHasRoom({ { now - 4000, 450000 } }, 100000, now)), true, "older bets no longer count")
end)

SpireTest.add("balance: every floor has hunting tasks, and task points buy something", function()
	local floors = {}
	for _, t in ipairs(SpireTasks.list) do
		floors[t.floor] = (floors[t.floor] or 0) + 1
		SpireTest.eq(MonsterType(t.monster) ~= nil, true, "task " .. t.id .. " hunts a real monster")
	end
	for n = 1, 10 do
		SpireTest.eq((floors[n] or 0) >= 4, true, "Floor " .. n .. " has tasks")
	end
	SpireTest.eq((SpireTasks.canBuy(1, 2)), false, "3 points needed for the scroll")
	SpireTest.eq((SpireTasks.canBuy(1, 3)), true, "3 points buy it")
	SpireTest.eq((SpireTasks.canBuy(99, 100)), false, "no such item")
	SpireTest.eq(SpireTasks.shop[3].points, 5, "Hunting Focus costs 5 points")
end)
