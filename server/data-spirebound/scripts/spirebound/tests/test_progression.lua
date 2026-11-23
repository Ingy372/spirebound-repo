-- Gear progression spec 4.2-4.3: kills fill weapon familiarity and the style tree; both add damage.
local P = SpireGearData.STYLE_POINTS

SpireTest.add("style: levels and stages follow the thresholds", function()
	local s, l = SpireStyle.levelOf(0)
	SpireTest.eq(s .. "/" .. l, "1/0", "nothing yet")
	s, l = SpireStyle.levelOf(P[1])
	SpireTest.eq(s .. "/" .. l, "1/1", "first level")
	s, l = SpireStyle.levelOf(P[10])
	SpireTest.eq(s .. "/" .. l, "1/10", "stage 1 complete")
	s, l = SpireStyle.levelOf(P[11])
	SpireTest.eq(s .. "/" .. l, "2/1", "into stage 2")
	s, l = SpireStyle.levelOf(P[30] * 2)
	SpireTest.eq(s .. "/" .. l, "3/10", "capped at the end")
end)

SpireTest.add("style: a stage waits for its choice before the next one starts", function()
	local v = SpireStyle.view(1, P[15], nil, nil)
	SpireTest.eq(v.stage .. "/" .. v.level, "1/10", "no path chosen: held at stage 1 level 10")
	SpireTest.eq(v.choiceReady, true, "the first choice is ready")
	v = SpireStyle.view(1, P[15], "emberwright", nil)
	SpireTest.eq(v.stage .. "/" .. v.level, "2/5", "with a path the banked points count")
	v = SpireStyle.view(1, P[25], "emberwright", nil)
	SpireTest.eq(v.stage .. "/" .. v.level .. tostring(v.choiceReady), "2/10true", "the final choice is ready")
end)

SpireTest.add("style: choices are checked and permanent", function()
	SpireTest.eq((SpireStyle.canChoose(3, P[5], nil, nil, "marksman")), false, "not before stage 1 level 10")
	SpireTest.eq((SpireStyle.canChoose(3, P[10], nil, nil, "emberwright")), false, "not another class's path")
	SpireTest.eq((SpireStyle.canChoose(3, P[10], nil, nil, "marksman")), true, "Marksman at level 10")
	SpireTest.eq((SpireStyle.canChoose(3, P[20], "marksman", nil, "trapper")), false, "the other path once chosen")
	SpireTest.eq((SpireStyle.canChoose(3, P[20], "marksman", nil, "snareweaver")), false, "not a final of the other path")
	SpireTest.eq((SpireStyle.canChoose(3, P[20], "marksman", nil, "deadeye")), true, "a final of your path")
	SpireTest.eq((SpireStyle.canChoose(3, P[30], "marksman", "deadeye", "volley_captain")), false, "nothing after the final")
end)

SpireTest.add("style: passives add up per level of each stage", function()
	local v = SpireStyle.view(3, P[15], "marksman", nil)
	local near = math.abs(SpireStyle.damageBonus(v, { distance = 1 }) - 10 * 0.005) < 1e-9
	SpireTest.eq(near, true, "stage 1 complete: +5% damage, Marksman needs range")
	near = math.abs(SpireStyle.damageBonus(v, { distance = 5 }) - (10 * 0.005 + 5 * 0.01)) < 1e-9
	SpireTest.eq(near, true, "Marksman level 5 at range: +5% more")
	SpireTest.eq(SpireStyle.takenFactor(SpireStyle.view(4, P[12], "bulwark", nil)), 1 - 2 * 0.006, "Bulwark level 2 takes less")
end)

SpireTest.add("progress: party kills are shared, never copied", function()
	SpireTest.eq(SpireProgress.killShare(100, 1), 100, "alone")
	SpireTest.eq(SpireProgress.killShare(100, 4), 25, "a party of four")
	SpireTest.eq(SpireProgress.killShare(100, 0), 100, "never divides by zero")
end)

SpireTest.add("progress: only real monster kills with your class weapon count", function()
	local ok = SpireProgress.countsPure
	SpireTest.eq(ok({ isPlayer = false, summoned = false, name = "Meadow Wolf" }, 3, 3), true, "a wolf with a Ranger weapon")
	SpireTest.eq(ok({ isPlayer = true, summoned = false, name = "Someone" }, 3, 3), false, "a player")
	SpireTest.eq(ok({ isPlayer = false, summoned = true, name = "Meadow Wolf" }, 3, 3), false, "a summon")
	SpireTest.eq(ok({ isPlayer = false, summoned = false, name = "Pen Rat" }, 3, 3), false, "an Arrival Yard rat")
	SpireTest.eq(ok({ isPlayer = false, summoned = false, name = "Meadow Wolf" }, 3, 4), false, "another class's weapon")
	SpireTest.eq(ok({ isPlayer = false, summoned = false, name = "Meadow Wolf" }, 3, nil), false, "no Spirebound weapon")
end)

SpireTest.add("progress: weapon power and style multiply the damage dealt", function()
	local w = { floor = 1, tier = 0, fam = 6 }
	local expected = math.floor(100 * SpireGear.power(w) + 0.5)
	SpireTest.eq(SpireProgress.dealtPure(100, w, SpireStyle.view(3, 0, nil, nil), { distance = 1 }, 0), expected, "familiarity 6, no style")
	local v = SpireStyle.view(3, P[10], nil, nil)
	SpireTest.eq(SpireProgress.dealtPure(100, nil, v, { distance = 1 }, 0), 105, "no weapon, stage 1 complete: +5%")
	SpireTest.eq(SpireProgress.dealtPure(100, nil, v, { distance = 1 }, 0.02), 107, "a trophy adds 2%")
end)
