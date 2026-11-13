-- Roadmap R18: one end-to-end check per headline rule, through the same code the game runs.

SpireTest.add("e2e: nobody reaches Floor 2 without the Axe-Lord's first kill", function()
	local rec = Floors.get(1)
	if rec.bossDeadAt then
		return -- this database already has a cleared Floor 1 (a playtest server); the rule is checked on fresh ones
	end
	SpireTest.eq(Floors.isOpen(2), false, "Floor 2 is closed on a fresh server")
	SpireTest.eq(Floors.mayStandOn(2, Floors.isOpen(2), false), false, "a player found on Floor 2 is sent back")
	SpireTest.eq(Floors.mayStandOn(2, Floors.isOpen(2), true), true, "staff may look around")
	local boulder = Tile(WorldPoints.gate_floor2)
	SpireTest.eq(boulder ~= nil and boulder:getItemById(1772) ~= nil, true, "the boulder still seals the stair")
end)

SpireTest.add("e2e: dying on each difficulty costs what DESIGN.md 5.4 says", function()
	local level, total = 60, 2000000
	local engine = 100000
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.NORMAL, engine, 30, 50000), 0, "Normal below level 50: nothing")
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.NORMAL, engine, level, total), engine, "Normal: the engine's loss")
	SpireTest.eq(Difficulty.finalDeathLoss(Difficulty.HARDCORE, engine, level, total) >= engine * 1.5, true, "Hardcore: half again")
	SpireTest.eq((SpireDeathGame.judge(9999, 1000, { monsterId = 1 }, 1000, function() return false end)), "retire",
		"Death Game: a monster's kill retires the character")
	SpireTest.eq((SpireDeathGame.judge(9999, 1000, { guid = 5, outside = true }, 1000, function() return true end)), "saved",
		"Death Game: another player's kill never does")
end)

SpireTest.add("e2e: a red skull wears off after its days", function()
	local now = 10000000
	local frags = {}
	for i = 1, SpirePvP.RED_DAY do
		table.insert(frags, { t = now - 60 * i, w = 1 })
	end
	SpireTest.eq(SpirePvP.skullFor(frags, now), SKULL_RED, "three unjust kills in a day: red")
	SpireTest.eq(SpirePvP.skullFor(frags, now + SpirePvP.RED_DAYS * 86400 + 3600) ~= SKULL_RED, true, "a week later the frags no longer make it red")
	SpireTest.eq(SpirePvP.skullSeconds(SKULL_RED), SpirePvP.RED_DAYS * 86400, "and the skull itself lasts 7 days")
end)

SpireTest.add("e2e: the Fortune Hall really destroys its cut", function()
	local total = 0
	for _, wins in ipairs({ true, false, true, false }) do
		local p, h, burned = SpireHouses.settleDice(5000, wins)
		total = total + p + h
		SpireTest.eq(burned, 500, "500 of every 10,000 gold pot destroyed")
	end
	SpireTest.eq(total, -2000, "four bets of 5,000: 2,000 gold left the game")
end)
