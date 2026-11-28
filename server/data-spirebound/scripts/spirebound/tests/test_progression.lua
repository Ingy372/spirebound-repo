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
	SpireTest.eq(v.choiceReady, false, "ST1: the path is chosen on Floor 2, not at Mastery 10")
	SpireTest.eq(SpireStyle.view(1, P[15], nil, nil, nil, { arrived = true }).choiceReady, true, "on Floor 2 the first choice is ready")
	SpireTest.eq(SpireStyle.view(1, P[3], nil, nil, nil, { arrived = true }).choiceReady, true, "even before Mastery 10 (spec 8.1)")
	v = SpireStyle.view(1, P[15], "emberwright", nil)
	SpireTest.eq(v.stage .. "/" .. v.level, "2/5", "with a path the banked points count")
	v = SpireStyle.view(1, P[25], "emberwright", nil)
	SpireTest.eq(v.stage .. "/" .. v.level .. tostring(v.choiceReady), "2/10true", "the final choice is ready")
end)

SpireTest.add("style: choices are checked and permanent", function()
	local f2 = { arrived = true, trials = { marksman = true, trapper = true } }
	SpireTest.eq((SpireStyle.canChoose(3, P[10], nil, nil, "marksman")), false, "not before Floor 2")
	SpireTest.eq((SpireStyle.canChoose(3, P[10], nil, nil, "emberwright", f2)), false, "not another class's path")
	SpireTest.eq((SpireStyle.canChoose(3, P[10], nil, nil, "marksman", f2)), true, "Marksman on Floor 2, both trials done")
	SpireTest.eq((SpireStyle.canChoose(3, P[10], nil, nil, "marksman", { arrived = true, trials = { marksman = true } })), false,
		"ST1 9.2: only after the Path Trial for both options")
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
	SpireTest.eq(SpireStyle.takenFactor(SpireStyle.view(4, P[12], "bulwark", nil), { shield = true }), 1 - 2 * 0.006, "Bulwark level 2 takes less with a shield")
	SpireTest.eq(SpireStyle.takenFactor(SpireStyle.view(4, P[12], "bulwark", nil), { shield = false }), 1, "and nothing without one (ST1)")
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

-- Task 8: each class's first style ability (spec 4.2: finishing a stage unlocks a signature ability)
SpireTest.add("style: each class has one stage-1 ability, learned only from its mastery", function()
	for voc = 1, 4 do
		local rows = {}
		for _, row in ipairs(SpireSpells.list) do
			if row.style == 1 and SpireSpells.allowed(row, voc) then
				table.insert(rows, row)
			end
		end
		SpireTest.eq(#rows, 1, "vocation " .. voc .. " has one stage-1 ability")
		for _, r in ipairs(SpireSpells.unlockedAt(rows[1].level, voc)) do
			SpireTest.eq(r.style == nil, true, "a style ability never unlocks by level alone")
		end
	end
	SpireTest.eq(SpireStyle.hasAbilityPure(SpireStyle.view(3, P[9], nil, nil), 1), false, "not at mastery 9")
	SpireTest.eq(SpireStyle.hasAbilityPure(SpireStyle.view(3, P[10], nil, nil), 1), true, "at mastery 10")
	SpireTest.eq(SpireStyle.hasAbilityPure(SpireStyle.view(3, P[12], "marksman", nil), 1), true, "and after")
end)

-- Task 9: the Mastery Respec (Jay, 2026-11-23: sold only in the shop)
SpireTest.add("style: a respec clears the choices, keeps the points, and waits 7 days", function()
	local now = 1000000
	SpireTest.eq((SpireStyle.respecCheck(nil, nil, now)), false, "nothing to undo without a choice")
	SpireTest.eq((SpireStyle.respecCheck("marksman", nil, now)), true, "a first respec")
	SpireTest.eq((SpireStyle.respecCheck("marksman", now - 6 * 86400, now)), false, "not within 7 days")
	SpireTest.eq((SpireStyle.respecCheck("marksman", now - 7 * 86400, now)), true, "after 7 days")
	local v = SpireStyle.view(3, P[15], nil, nil, nil, { arrived = true })
	SpireTest.eq(v.stage .. "/" .. v.level .. "/" .. tostring(v.choiceReady), "1/10/true", "after a respec at Marksman 5: the choice again, points kept")
end)

-- Final review: the damage hook must run on a real monster without errors
SpireTest.add("progress: the damage hook runs on a real monster", function()
	local m = Game.createMonster("Meadow Wolf", WorldPoints.temple_hearthgate, true, true)
	SpireTest.eq(m ~= nil, true, "a wolf to hit")
	SpireTest.eq(SpireProgress.onDealt(m, m, 100), 100, "a monster's own damage is left alone")
	SpireTest.eq(SpireProgress.onDealt(nil, m, 100), 100, "no attacker, no change")
	m:remove()
end)

-- ST1 (style trees v2): the stance is gone, the extreme finals pay with a minus, the new passive kinds work
SpireTest.add("style ST1: no stance; minuses, shield-only and the new kinds", function()
	local P = SpireGearData.STYLE_POINTS
	SpireTest.eq((SpireStyle.canStance(3, P[6], nil, "marksman")), false, "the free stance is gone (Path Trial instead)")
	local iron = SpireStyle.view(4, P[30], "bulwark", "ironwall")
	SpireTest.eq(SpireStyle.damageBonus(iron, {}) < 0, true, "Ironwall deals less damage than no style")
	SpireTest.eq(math.abs(SpireStyle.maxHealthBonus(iron) - 0.15) < 1e-9, true, "+15% health")
	local blood = SpireStyle.view(4, P[30], "reaver", "bloodedge")
	SpireTest.eq(SpireStyle.takenFactor(blood, {}) > 1, true, "Bloodedge takes more damage")
	SpireTest.eq(math.abs(SpireStyle.offhandShare(blood) - 0.5) < 1e-9, true, "off-hand strike 20% + 10 + 20 = 50% (spec 7.3)")
	SpireTest.eq(SpireStyle.offhandShare(iron), 0, "no off-hand strike for a Bulwark")
	local cinder = SpireStyle.view(1, P[30], "emberwright", "cinderheart")
	SpireTest.eq(SpireStyle.damageBonus(cinder, { area = true }) < SpireStyle.damageBonus(cinder, { area = false }), true, "Cinderheart: area hits weaker")
	local frost = SpireStyle.view(2, P[30], "wildcaller", "frostwarden")
	SpireTest.eq(math.abs(SpireStyle.ccFactor(frost) - 1.25) < 1e-9, true, "Frostwarden: holds up to 25% longer")
	local wild = SpireStyle.view(2, P[20], "wildcaller", nil)
	SpireTest.eq(math.abs(SpireStyle.ccFactor(wild) - 1.2) < 1e-9, true, "Wildcaller: up to 20%")
	local path = SpireStyle.view(3, P[30], "trapper", "pathfinder")
	SpireTest.eq(math.abs(SpireStyle.partyDodge(path) - 0.05) < 1e-9, true, "Pathfinder: 5% party dodge")
	local spell = SpireStyle.view(1, P[30], "stormbinder", "spellbreaker")
	SpireTest.eq(SpireStyle.damageBonus(spell, { unmarked = true }) < SpireStyle.damageBonus(spell, { unmarked = false }), true, "Spellbreaker: weaker on unmarked targets")
	SpireTest.eq(SpireGearData.RETIRED_STYLE.aegis_warden, "bladeward", "retired keys are listed")
end)

-- P1b: one signature ability per path, castable only on that path
SpireTest.add("style: every path has its own signature ability", function()
	for voc, tree in pairs(SpireGearData.style) do
		for _, p in ipairs(tree.paths) do
			local found = 0
			for _, row in ipairs(SpireSpells.list) do
				if row.style == 2 and row.path == p.key then
					found = found + 1
					SpireTest.eq(SpireSpells.allowed(row, voc), true, row.name .. " is for " .. tree.name)
				end
			end
			SpireTest.eq(found, 1, p.name .. " has one ability")
		end
	end
	local v = SpireStyle.view(3, SpireGearData.STYLE_POINTS[20], "marksman", nil)
	SpireTest.eq(SpireStyle.hasAbilityPure(v, 2), true, "a finished path has its ability")
	local early = SpireStyle.view(3, SpireGearData.STYLE_POINTS[15], "marksman", nil)
	SpireTest.eq(SpireStyle.hasAbilityPure(early, 2), false, "not before the path's Mastery 10")
end)

-- P1c: one ability per final style
SpireTest.add("style: every final style has its own ability", function()
	local names = {}
	for voc, tree in pairs(SpireGearData.style) do
		for _, p in ipairs(tree.paths) do
			for _, f in ipairs(p.finals) do
				local found = 0
				for _, row in ipairs(SpireSpells.list) do
					if row.style == 3 and row.final == f.key then
						found = found + 1
						SpireTest.eq(SpireSpells.allowed(row, voc), true, row.name .. " is for " .. tree.name)
						SpireTest.eq(names[row.words], nil, row.name .. " has words of its own")
						names[row.words] = true
					end
				end
				SpireTest.eq(found, 1, f.name .. " has one ability")
			end
		end
	end
end)
