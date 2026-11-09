-- Roadmap 1.18 / 1.19: boss credit, resets and enrage (pure rules) + map points exist.
SpireTest.add("bosses: credit needs a hit in the last 90 s, top contributors first", function()
	local s = SpireBoss.newState()
	SpireBoss.recordHit(s, "Early", 5000, 100) -- hit long ago only
	SpireBoss.recordHit(s, "Tank", 800, 920)
	SpireBoss.recordHit(s, "Mage", 3000, 950)
	SpireBoss.recordHit(s, "Healer", 10, 990)
	local credit = SpireBoss.credited(s, 1000)
	SpireTest.eq(#credit, 3, "three credited")
	SpireTest.eq(credit[1], "Mage", "biggest damage first")
	for _, n in ipairs(credit) do
		if n == "Early" then
			error("Early should not be credited (last hit 900 s before the kill)")
		end
	end
end)

SpireTest.add("bosses: reset after 60 s without damage or 30 s empty", function()
	local s = SpireBoss.newState()
	SpireTest.eq(SpireBoss.shouldReset(s, 100, 0), false, "never reset before the fight starts")
	s.started = 100
	SpireBoss.recordHit(s, "A", 10, 100)
	SpireTest.eq(SpireBoss.shouldReset(s, 150, 2), false, "50 s without damage is fine")
	SpireTest.eq(SpireBoss.shouldReset(s, 161, 2), true, "61 s without damage resets")
	local e = SpireBoss.newState()
	e.started = 100
	SpireBoss.recordHit(e, "A", 10, 100)
	SpireTest.eq(SpireBoss.shouldReset(e, 105, 0), false, "room just emptied")
	SpireTest.eq(SpireBoss.shouldReset(e, 136, 0), true, "empty for 31 s resets")
end)

SpireTest.add("bosses: enrage steps", function()
	local s = SpireBoss.newState()
	s.started = 0
	s.headcount = 8 -- 8 min enrage
	SpireTest.eq(SpireBoss.enrageMultiplier(s, 479), 1, "before enrage")
	SpireTest.eq(SpireBoss.enrageMultiplier(s, 480), 1.5, "first step")
	SpireTest.eq(SpireBoss.enrageMultiplier(s, 540), 2.5, "three steps after 60 s")
	s.headcount = 1
	SpireTest.eq(SpireBoss.enrageMultiplier(s, 3599), 1, "solo has 60 minutes")
end)

SpireTest.add("map: floor 1 has every named point the scripts need", function()
	for _, n in ipairs({ "temple_hearthgate", "gate_hound_spawn", "axe_lord_spawn", "gate_pass_1", "gate_pass_2", "gate_floor2",
		"boss_room_floor1_nw", "boss_room_floor1_se", "stair_floor2", "floor2_landing", "lab1_up", "lab2_up", "lab3_up" }) do
		if not WorldPoints[n] then
			error("missing world point " .. n)
		end
	end
	if not Tile(WorldPoints.temple_hearthgate) then
		error("temple tile missing from the map")
	end
end)

SpireTest.add("bosses: both floor 1 bosses exist and are scripted", function()
	for _, n in ipairs({ "Gate Hound", "Axe-Lord of the Stair" }) do
		if not MonsterType(n) then
			error(n .. " monster type missing")
		end
		if not SpireBoss.defs[n] then
			error(n .. " has no boss script")
		end
	end
end)

SpireTest.add("map: monsters, NPCs and the floor 1 bosses are in the world", function()
	local count = Game.getMonsterCount()
	if count < 80 then
		error("only " .. count .. " monsters spawned")
	end
	if Game.getNpcCount() < 1 then
		error("no NPCs spawned")
	end
	local function near(pointName, monsterName)
		for _, c in ipairs(Game.getSpectators(WorldPoints[pointName], false, false, 3, 3, 3, 3)) do
			if c:getName() == monsterName then
				return true
			end
		end
		return false
	end
	if not Floors.isLabyrinthOpen(1) and not near("gate_hound_spawn", "Gate Hound") then
		error("Gate Hound not at the Pass")
	end
	if not near("axe_lord_spawn", "Axe-Lord of the Stair") then
		error("Axe-Lord not in the boss room")
	end
	logger.info("[SPIRETEST] note: {} monsters and {} NPCs in the world", count, Game.getNpcCount())
end)

-- Full first-kill effects, then everything is put back so the real world state is untouched.
SpireTest.add("bosses: first kills open the labyrinth and the stair to floor 2", function()
	local function boulderAt(name)
		local t = Tile(WorldPoints[name])
		return t and t:getItemById(1772) ~= nil
	end
	local passWasOpen, floor2WasOpen = Floors.isLabyrinthOpen(1), Floors.isOpen(2)
	if passWasOpen or floor2WasOpen then
		logger.info("[SPIRETEST] note: floor 1 already progressed on this database, first-kill test skipped")
		return
	end
	SpireTest.eq(boulderAt("gate_pass_1"), true, "pass sealed before the Gate Hound dies")
	SpireBoss.defs["Gate Hound"].onFirstKill({ "Tester" }, "Tester", 100)
	SpireTest.eq(Floors.isLabyrinthOpen(1), true, "pass open in the saved state")
	SpireTest.eq(boulderAt("gate_pass_1") or boulderAt("gate_pass_2"), false, "pass boulders removed")
	SpireTest.eq(boulderAt("gate_floor2"), true, "stair sealed before the Axe-Lord dies")
	SpireBoss.defs["Axe-Lord of the Stair"].onFirstKill({ "Tester", "Helper" }, "Helper", 300)
	SpireTest.eq(Floors.isOpen(2), true, "floor 2 open in the saved state")
	SpireTest.eq(boulderAt("gate_floor2"), false, "stair boulder removed")
	SpireTest.eq(Floors.get(1).lastHit, "Helper", "last hit recorded")
	-- a second kill must not redo first-clear actions
	SpireTest.eq(Floors.recordClear(1, { "Late" }, "Late", 10), false, "second clear ignored")
	-- put the world back
	Floors.reset(1)
	Floors.reset(2)
	for _, n in ipairs({ "gate_pass_1", "gate_pass_2", "gate_floor2" }) do
		Game.createItem(1772, 1, WorldPoints[n])
	end
	SpireTest.eq(Floors.isOpen(2), false, "state restored")
end)
