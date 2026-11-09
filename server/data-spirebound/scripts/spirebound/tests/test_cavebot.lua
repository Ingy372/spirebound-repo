-- Roadmap 2.12: cavebot penalty.
SpireTest.add("cavebot: penalty while on and for 10 minutes after", function()
	local now = 1000000
	SpireTest.eq(SpireCavebot.penaltyActive(nil, now), false, "never used")
	local st = SpireCavebot.setState(-1, true, now)
	SpireTest.eq(SpireCavebot.penaltyActive(st, now + 5000), true, "on")
	st = SpireCavebot.setState(-1, false, now + 6000)
	SpireTest.eq(SpireCavebot.penaltyActive(st, now + 6000 + 599), true, "just switched off")
	SpireTest.eq(SpireCavebot.penaltyActive(st, now + 6000 + 600), false, "10 minutes later")
	SpireCavebot.state[-1] = nil
	SpireTest.eq(SpireCavebot.XP, 0.45, "45% XP (Jay)")
	SpireTest.eq(SpireCavebot.LOOT, 0.5, "half loot")
end)
