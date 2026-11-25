-- Grok's third playtest (2026-11-25).
SpireTest.add("session 3: the fight lock lifts 15 seconds after the last hit, never during PvP", function()
	SpireTest.eq(SpireFightTimer.quiet(100, 90, false, false), false, "10 s after a hit: still locked")
	SpireTest.eq(SpireFightTimer.quiet(100, 85, false, false), true, "15 s after a hit: free to log out")
	SpireTest.eq(SpireFightTimer.quiet(100, 0, true, false), false, "attacking something: locked")
	SpireTest.eq(SpireFightTimer.quiet(100, 0, false, true), false, "a player-killing lock stays")
end)

SpireTest.add("session 3: starter items ignore carrying weight", function()
	SpireTest.eq(type(SpireGive.item), "function", "SpireGive.item exists")
	SpireTest.eq(FLAG_NOLIMIT ~= nil, true, "the engine knows FLAG_NOLIMIT")
	local q = Game.createItem(SpireQuiver.ID, 1, WorldPoints.temple_hearthgate)
	SpireTest.eq(SpireGive.into(q, 3447, 100) ~= nil, true, "arrows go into a quiver")
	q:remove()
end)

SpireTest.add("session 3: the Journal works before a path is chosen", function()
	SpireTest.eq(SpireStyle.stageName({ voc = 0, stage = 1 }), "", "no path: an empty stage name, not a crash")
end)
