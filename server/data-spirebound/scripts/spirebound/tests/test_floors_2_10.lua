-- Phases 4-5: floors 2-10 exist, link up and have their bosses, NPCs, secrets and quests.
SpireTest.add("floors 2-10: maps, stairs, bosses, towns", function()
	for n = 2, 10 do
		local P = "f" .. n .. "_"
		for _, k in ipairs({ "temple", "boss_spawn", "field_spawn", "gate_next", "gate_pass_1", "down_src", "lab1_up", "lab3_up", "lake" }) do
			if not WorldPoints[P .. k] then error("floor " .. n .. " missing point " .. k) end
		end
		if not WorldPoints["stair_floor" .. n] then error("no stair up into floor " .. n) end
		if not WorldPoints["floor" .. n .. "_landing"] then error("no landing on floor " .. n) end
		SpireTest.eq(Floors.at(WorldPoints[P .. "temple"]), n, "floor lookup for floor " .. n)
		local f = SpireFloorBosses[n]
		local function near(point, name)
			for _, c in ipairs(Game.getSpectators(WorldPoints[point], false, false, 3, 3, 3, 3)) do
				if c:getName() == name then return true end
			end
			return false
		end
		if not Floors.isLabyrinthOpen(n) and not near(P .. "field_spawn", f.field) then error(f.field .. " not spawned") end
		if not near(P .. "boss_spawn", f.boss) then error(f.boss .. " not spawned") end
		local npcs = 0
		for _, c in ipairs(Game.getSpectators(WorldPoints[P .. "temple"], false, false, 50, 50, 40, 40)) do
			if c:isNpc() then npcs = npcs + 1 end
		end
		if npcs < 7 then error("floor " .. n .. " town has only " .. npcs .. " NPCs") end
		local secrets = 0
		for _, s in ipairs(SpireSecrets.list) do
			if s.floor == n and WorldPoints[s.point] then secrets = secrets + 1 end
		end
		SpireTest.eq(secrets, 12, "secrets placed on floor " .. n)
		SpireTest.eq(SpireFishing.fishKinds(n), 7, "fish on floor " .. n)
	end
end)

SpireTest.add("floors 2-10: quests and perks generated", function()
	for n = 2, 10 do
		local q = 0
		for _, row in ipairs(SpireQuests.list) do
			if row.floor == n and not row.side then
				q = q + 1
				if not MonsterType(row.target) then error(row.id .. " targets unknown " .. row.target) end
			end
		end
		SpireTest.eq(q, 3, "story quests on floor " .. n)
		SpireTest.eq(#SpireQuests.PERKS[n], 2, "perk options on floor " .. n)
	end
end)
