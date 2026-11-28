-- 2026-11-26: a credited fighter who is not in the game when the boss dies (fell during the fight, logged out) gets the
-- reward on the next login instead of losing it (lib/spirebound/gear.lua SpireGear.grantBoss / collectPending).
SpireTest.add("boss rewards wait for a fighter who fell", function()
	local name = "Nobody Online Test"
	local store = kv.scoped("spirebound-gear-pending") -- its own store since 2026-11-28 (the boss titles' one is a list)
	store:remove(name)
	SpireGear.grantBoss("Gate Hound", { name })
	SpireTest.eq(store:get(name), "Gate Hound", "the Gate Hound's reward waits")
	SpireGear.grantBoss("Axe-Lord of the Stair", { name })
	SpireTest.eq(store:get(name), "Gate Hound;Axe-Lord of the Stair", "a second boss is added to the list")
	store:remove(name)
	SpireGear.grantBoss("Not A Boss", { name })
	SpireTest.eq(store:get(name), nil, "a monster without a boss reward leaves nothing waiting")
end)

SpireTest.add("a waiting boss reward never blocks a login (the two waiting lists stay apart)", function()
	local name = "Nobody Online Test 2"
	kv.scoped("spirebound-boss-pending"):set(name, "Axe-Lord of the Stair") -- an old reward saved in the titles' store
	local p = {}
	function p:getName() return name end
	function p:kv() return { scoped = function() return kv.scoped("spiretest-nobody2") end } end
	function p:sendTextMessage() end
	SpireTest.eq(SpireBoss.applyPending(p), 0, "the title reader ignores it instead of failing")
	kv.scoped("spirebound-boss-pending"):remove(name)
	SpireGear.grantBoss("Gate Hound", { name })
	SpireTest.eq(kv.scoped("spirebound-boss-pending"):get(name), nil, "boss rewards no longer go in the titles' store")
	kv.scoped("spirebound-gear-pending"):remove(name)
end)
