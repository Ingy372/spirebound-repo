-- Roadmap 1.14: sword skill rules.
SpireTest.add("sword skills: 6 per weapon family, all with words and cooldowns", function()
	local count = {}
	for _, d in ipairs(SwordSkills.list) do
		count[d.family] = (count[d.family] or 0) + 1
		if not d.words or d.cd < 1000 then
			error(d.key .. " missing words or cooldown")
		end
	end
	for fam in pairs(SwordSkills.families) do
		SpireTest.eq(count[fam], 6, "skills for " .. fam)
	end
end)

SpireTest.add("sword skills: opener -> link -> finisher combo gives +30%", function()
	local O, L, F = SwordSkills.OPENER, SwordSkills.LINK, SwordSkills.FINISHER
	local s, m = SwordSkills.comboStep(nil, O, 100)
	s, m = SwordSkills.comboStep(s, L, 102)
	s, m = SwordSkills.comboStep(s, F, 104)
	SpireTest.eq(m, 1.30, "full combo in time")
	s, m = SwordSkills.comboStep(nil, O, 100)
	s, m = SwordSkills.comboStep(s, L, 105)
	s, m = SwordSkills.comboStep(s, F, 106)
	SpireTest.eq(m, 1.0, "link too late breaks the combo")
	s, m = SwordSkills.comboStep(nil, O, 100)
	s, m = SwordSkills.comboStep(s, F, 101)
	SpireTest.eq(m, 1.0, "skipping the link gives no bonus")
	s, m = SwordSkills.comboStep(nil, F, 100)
	SpireTest.eq(m, 1.0, "finisher alone still works, no bonus")
end)

SpireTest.add("sword skills: weapon family detection", function()
	local f = SwordSkills.familyFromFacts
	SpireTest.eq(f({ weaponType = WEAPON_SWORD }), "sword", "sword")
	SpireTest.eq(f({ weaponType = WEAPON_DISTANCE, ammoType = AMMO_ARROW }), "bow", "bow")
	SpireTest.eq(f({ weaponType = WEAPON_DISTANCE, ammoType = AMMO_BOLT }), "crossbow", "crossbow")
	SpireTest.eq(f({ weaponType = WEAPON_MISSILE, ammoType = AMMO_NONE }), "spear", "spear")
	SpireTest.eq(f({ weaponType = WEAPON_WAND, vocationBase = 1 }), "wand", "arcanist wand")
	SpireTest.eq(f({ weaponType = WEAPON_WAND, vocationBase = 2 }), "rod", "mystic rod")
	SpireTest.eq(f({ weaponType = WEAPON_SHIELD }), nil, "shield is not a weapon family")
end)

SpireTest.add("sword skills: every skill registered as a spell", function()
	for _, d in ipairs(SwordSkills.list) do
		if not Spell(d.name) then
			error(d.name .. " not registered")
		end
	end
end)
