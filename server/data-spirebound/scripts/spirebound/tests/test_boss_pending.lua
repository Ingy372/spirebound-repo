-- 2026-11-26: a credited fighter who is not in the game when the boss dies (fell during the fight, logged out) gets the
-- reward on the next login instead of losing it (lib/spirebound/gear.lua SpireGear.grantBoss / collectPending).
SpireTest.add("boss rewards wait for a fighter who fell", function()
	local name = "Nobody Online Test"
	local store = kv.scoped("spirebound-boss-pending")
	store:remove(name)
	SpireGear.grantBoss("Gate Hound", { name })
	SpireTest.eq(store:get(name), "Gate Hound", "the Gate Hound's reward waits")
	SpireGear.grantBoss("Axe-Lord of the Stair", { name })
	SpireTest.eq(store:get(name), "Gate Hound;Axe-Lord of the Stair", "a second boss is added to the list")
	store:remove(name)
	SpireGear.grantBoss("Not A Boss", { name })
	SpireTest.eq(store:get(name), nil, "a monster without a boss reward leaves nothing waiting")
end)
