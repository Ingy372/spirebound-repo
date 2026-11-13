-- Roadmap 5.7 / 5.7b / 5.7e: world events, weekend bonuses, derby, offline training, livestream.
SpireTest.add("events: weekend rotation and event picking", function()
	SpireTest.eq(SpireEvents.weekendBonus(3, 10), nil, "Tuesday: no bonus")
	SpireTest.eq(SpireEvents.weekendBonus(7, 0).id, "xp", "week 0 Saturday: double XP")
	SpireTest.eq(SpireEvents.weekendBonus(1, 1).id, "loot", "week 1 Sunday: double loot")
	SpireTest.eq(SpireEvents.weekendBonus(7, 4).id, "respawn", "week 4: Rapid Respawn (R20)")
	SpireTest.eq(SpireEvents.weekendBonus(7, 5).id, "xp", "rotation wraps")
	local k, f = SpireEvents.pick(0.0, 1)
	SpireTest.eq(f, 1, "only floor 1 open: events on floor 1")
	local seen = {}
	for i = 0, 99 do
		local kk = SpireEvents.pick(i / 100, 5)
		seen[kk.id] = true
	end
	SpireTest.eq(seen.frenzy and seen.incursion and seen.fishing and seen.champion, true, "all four event kinds come up")
end)

SpireTest.add("events: a GM-started event spawns and the fishing luck applies", function()
	SpireEvents.start(SpireEvents.KINDS[1], 1) -- frenzy on floor 1
	SpireTest.eq(SpireEvents.isActive("frenzy", 1), true, "frenzy running")
	SpireEvents.active = { kind = SpireEvents.KINDS[3], floor = 1, untilTime = os.time() + 60 }
	SpireTest.eq(SpireEvents.fishingLuck(1) >= 3, true, "fishing frenzy triples rare fish")
	local rare = 0
	for i = 0, 999 do
		local fish = SpireFishing.roll(1, false, i / 1000, 3)
		if fish.id == "golden_trout" then rare = rare + 1 end
	end
	if rare < 60 then error("golden trout should be much more common with luck x3, got " .. rare) end
	SpireEvents.active = nil
end)

SpireTest.add("offline training statues and livestream are available", function()
	-- the statues stand in the Training Yard (town redesign, 2026-11-11)
	local yard = WorldPoints.training_yard
	local found = false
	for dx = -12, 12 do
		for dy = -6, 0 do
			local tile = Tile(Position(yard.x + dx, yard.y + dy, yard.z))
			if tile and tile:getItemById(16198) then found = true end
		end
	end
	SpireTest.eq(found, true, "sword training statue in the Hearthgate Training Yard")
	SpireTest.eq(configManager.getFloat(configKeys.LIVESTREAM_EXPERIENCE_MULTIPLIER), 1.0, "no XP bonus for streaming")
end)
