-- Floor 1 hunting ladder (BESTIARY.md) and the progression rules behind it.
SpireTest.add("hunting: the ladder sends each level to a sensible ground", function()
	local r1 = SpireHunt.recommend(1)
	SpireTest.eq(r1.xp.id, "starter_west", "level 1 starts with rats")
	local r12 = SpireHunt.recommend(12)
	SpireTest.eq(r12.xp.id, "wolf_copse", "level 12: the hardest ground whose range includes it")
	SpireTest.eq(r12.next.lo, 14, "the next step is level 14")
	local r20 = SpireHunt.recommend(20)
	SpireTest.eq(r20.xp.id, "shard_fields", "level 20 experience: shard fields")
	SpireTest.eq(r20.money.id, "bandit_road", "level 20 money: bandits")
	SpireTest.eq(SpireHunt.recommend(100).beyond, true, "level 100 has outgrown floor 1")
end)

SpireTest.add("hunting: every level from 1 to 40 has a place to hunt, and every ground's monsters exist", function()
	for level = 1, 40 do
		local r = SpireHunt.recommend(level)
		if not r.xp and not r.money then
			error("no hunting ground for level " .. level)
		end
	end
	for _, c in ipairs(SpireHunt.camps) do
		for _, name in ipairs(c.monsters) do
			if not MonsterType(name) then
				error(c.id .. " lists unknown monster " .. name)
			end
		end
		if not WorldPoints["camp_" .. c.id] and c.id ~= "apex_watchtower" then
			error(c.id .. " has no place on the map")
		end
	end
	SpireTest.eq(SpireHunt.advice(1):find("Ratwarren", 1, true) ~= nil, true, "level 1 advice names the Ratwarren")
end)

SpireTest.add("hunting: new characters start in the Arrival Yard", function()
	SpireTest.eq(Town(50) ~= nil, true, "the Arrival Yard is a town")
	SpireTest.eq(Town(1) ~= nil, true, "Hearthgate is town 1")
	SpireTest.eq(WorldPoints.tutorial_spawn ~= nil, true, "the yard has a spawn point")
end)

SpireTest.add("hunting: promotion vocations exist for all four paths", function()
	for id = 1, 4 do
		SpireTest.eq(Vocation(id + 4) ~= nil, true, "promoted vocation for " .. id)
		SpireTest.eq(Vocation(id + 4):getBaseId(), id, "promotion keeps its base path")
	end
end)
