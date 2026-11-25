-- The Proving (G2), first spells on the bar (G1) and the "you need a target" hint (G4). Grok playtest, 2026-11-24.
SpireTest.add("proving: the hall, the stone, three pits and Bramblejaw exist", function()
	for _, name in ipairs({ "proving_arrival", "proving_entry", "proving_skip" }) do
		if not WorldPoints[name] then
			error("missing map point " .. name)
		end
	end
	for i = 1, SpireProving.PITS do
		for _, part in ipairs({ "player", "boss", "nw", "se" }) do
			if not WorldPoints["proving_pit_" .. i .. "_" .. part] then
				error("pit " .. i .. " has no " .. part .. " point")
			end
		end
		local p = WorldPoints["proving_pit_" .. i .. "_player"]
		SpireTest.eq(SpireProving.pitAt(p), i, "the climber's spot is inside pit " .. i)
		SpireTest.eq(SpireProving.pitAt(WorldPoints["proving_pit_" .. i .. "_boss"]), i, "Bramblejaw's spot is inside pit " .. i)
	end
	SpireTest.eq(SpireProving.pitAt(WorldPoints.proving_arrival), nil, "the hall is not a pit")
	if not MonsterType("Bramblejaw") then
		error("Bramblejaw is not a monster")
	end
end)

SpireTest.add("proving: pits are handed out one climber each", function()
	SpireTest.eq(SpireProving.freePit({}, 3), 1, "empty: the first pit")
	SpireTest.eq(SpireProving.freePit({ [1] = {} }, 3), 2, "first taken: the second")
	SpireTest.eq(SpireProving.freePit({ [1] = {}, [3] = {} }, 3), 2, "a gap is reused")
	SpireTest.eq(SpireProving.freePit({ {}, {}, {} }, 3), nil, "all taken: wait")
end)

SpireTest.add("first spells: every path has an attack spell and a heal that exist", function()
	for voc, list in pairs(SpireClient.FIRST_SPELLS) do
		SpireTest.eq(#list, 2, "two first spells for vocation " .. voc)
		for _, words in ipairs(list) do
			local found = false
			for _, row in ipairs(SpireSpells.list or {}) do
				if row.words == words then
					found = true
				end
			end
			if not found then
				error("first spell '" .. words .. "' is not a Spirebound spell")
			end
		end
	end
end)

SpireTest.add("need a target: target spells are hinted, other words are not", function()
	SpireTest.eq(SpireSpells.isHinted(SpireSpells.hinted.frost, "frost strike"), true, "frost strike is a target spell")
	SpireTest.eq(SpireSpells.isHinted(SpireSpells.hinted.frost, "frost is cold"), false, "ordinary chat passes")
	SpireTest.eq(SpireSpells.isHinted(SpireSpells.hinted.dewfall, "dewfall"), false, "a heal needs no target")
end)
