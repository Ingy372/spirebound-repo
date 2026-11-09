-- Roadmap 1.10 / 1.11: difficulty rules (pure-logic checks; the full flow is in the Phase 1 playtest).
SpireTest.add("difficulty: choose once, then only step down", function()
	local N, H, D = Difficulty.NORMAL, Difficulty.HARDCORE, Difficulty.DEATHGAME
	SpireTest.eq(Difficulty.canChange(Difficulty.NONE, D), true, "first pick death game")
	SpireTest.eq(Difficulty.canChange(Difficulty.NONE, N), true, "first pick normal")
	SpireTest.eq(Difficulty.canChange(D, H), true, "death game -> hardcore")
	SpireTest.eq(Difficulty.canChange(H, N), true, "hardcore -> normal")
	SpireTest.eq(Difficulty.canChange(N, H), false, "normal -> hardcore refused")
	SpireTest.eq(Difficulty.canChange(H, D), false, "hardcore -> death game refused")
	SpireTest.eq(Difficulty.canChange(N, N), false, "same mode is not a change")
	SpireTest.eq(Difficulty.canChange(Difficulty.NONE, 7), false, "unknown mode refused")
end)

SpireTest.add("difficulty: xp and death-loss multipliers", function()
	SpireTest.eq(Difficulty.applyXp(Difficulty.NORMAL, 1000), 1000, "normal xp")
	SpireTest.eq(Difficulty.applyXp(Difficulty.HARDCORE, 1000), 1250, "hardcore xp +25%")
	SpireTest.eq(Difficulty.applyXp(Difficulty.DEATHGAME, 1000), 1500, "death game xp +50%")
	SpireTest.eq(Difficulty.applyDeathLoss(Difficulty.NORMAL, 1000), 1000, "normal loss")
	SpireTest.eq(Difficulty.applyDeathLoss(Difficulty.HARDCORE, 1000), 1500, "hardcore loss x1.5")
end)

SpireTest.add("death game: only outside players can save you from deletion", function()
	local victim = { guid = 1, ip = 111, guildId = 5, partyId = 9 }
	SpireTest.eq(Difficulty.countsAsOutsidePlayer(victim, { guid = 2, ip = 222, guildId = 6, partyId = nil }), true, "stranger counts")
	SpireTest.eq(Difficulty.countsAsOutsidePlayer(victim, { guid = 3, ip = 333, guildId = 7, partyId = 9 }), false, "party member does not count")
	SpireTest.eq(Difficulty.countsAsOutsidePlayer(victim, { guid = 4, ip = 444, guildId = 5 }), false, "guildmate does not count")
	SpireTest.eq(Difficulty.countsAsOutsidePlayer(victim, { guid = 5, ip = 111, guildId = 0 }), false, "same IP does not count")
	SpireTest.eq(Difficulty.countsAsOutsidePlayer(victim, nil), false, "monster does not count")
	local now = 100000
	SpireTest.eq(Difficulty.isPvPSavedDeath(now - 30, now), true, "outside hit 30 s ago saves")
	SpireTest.eq(Difficulty.isPvPSavedDeath(now - 61, now), false, "outside hit 61 s ago does not save")
	SpireTest.eq(Difficulty.isPvPSavedDeath(nil, now), false, "no outside hit: PvE death, retired")
end)
