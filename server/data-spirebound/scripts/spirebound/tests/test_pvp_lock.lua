-- Roadmap M5: in a player fight the built-in helpers only heal (scripts/spirebound/pvp_lock.lua; the client side is
-- client/modules/game_spirebound/bot/spirebound_pvp_guard.lua, checked with tools/autopilot.py m5_heal_only).
SpireTest.add("pvp lock: a player hit starts a one-minute lock that ends on its own", function()
	SpireTest.eq(SpirePvPLock.LOCK, 60, "the lock lasts about a minute, like Tibia's fight lock")
	SpireTest.eq(SpirePvPLock.active(nil, 100), false, "no player hit: no lock")
	SpireTest.eq(SpirePvPLock.active(100, 100), true, "right after a player hit: locked")
	SpireTest.eq(SpirePvPLock.active(100, 159), true, "59 seconds later: still locked")
	SpireTest.eq(SpirePvPLock.active(100, 160), false, "a minute later: helpers are back")
	SpireTest.eq(type(SpirePvPLock.mark), "function", "the hit handler can start it")
end)
