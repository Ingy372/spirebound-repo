-- Gear progression spec 4.8: four hidden mini-bosses on Floor 1, each woken at a secret, each leaving a trophy once.

SpireTest.add("minibosses: six on Floor 1, each a real monster at a real secret", function()
	SpireTest.eq(#SpireTrophies.LIST, 6, "six hidden beasts (AD5 added Ironpurse and the Unfinished)")
	for _, t in ipairs(SpireTrophies.LIST) do
		SpireTest.eq(MonsterType(t.boss) ~= nil, true, t.boss .. " exists")
		local found = false
		for _, s in ipairs(SpireSecrets.list) do
			if s.id == t.secret and s.floor == 1 then
				found = true
			end
		end
		SpireTest.eq(found, true, t.boss .. " sits at a Floor 1 secret")
		SpireTest.eq(WorldPoints["secret_" .. t.secret] ~= nil, true, t.boss .. "'s secret is on the map")
	end
end)

SpireTest.add("minibosses: the respawn wait is always one to three hours", function()
	SpireTest.eq(SpireTrophies.respawnDelay(function() return 0 end), 3600, "shortest")
	SpireTest.eq(SpireTrophies.respawnDelay(function() return 1 end), 10800, "longest")
	SpireTest.eq(SpireTrophies.respawnDelay(function() return 0.5 end), 7200, "middle")
end)

SpireTest.add("minibosses: trophies are once per character and do what they promise", function()
	SpireTest.eq(SpireTrophies.newOnes({}, "hollowfang"), true, "a first kill gives the trophy")
	SpireTest.eq(SpireTrophies.newOnes({ hollowfang = 1 }, "hollowfang"), false, "a second kill does not")
	SpireTest.eq(SpireTrophies.damagePure({ briar_mother = 1 }), 0.02, "Briar Mother: +2% damage")
	SpireTest.eq(SpireTrophies.damagePure({}), 0, "no trophies, no bonus")
	SpireTest.eq(SpireTrophies.speedPure({ hollowfang = 1 }), 5, "Hollowfang: +5 speed")
	SpireTest.eq(SpireTrophies.healthPure({ old_tusk = 1 }), 0.03, "Old Tusk: +3% health")
	SpireTest.eq(SpireTrophies.stylePointsPure("drowned_warden"), SpireGearData.STYLE_POINTS[1], "Drowned Warden: one style level")
end)
