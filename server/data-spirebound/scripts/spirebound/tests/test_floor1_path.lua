-- Gear progression spec 4.5: the Floor 1 path (Captain Dorrow at level 10, the temper quest, the armour quest,
-- the Gate Hound's shards, the Axe-Lord's awakening).

SpireTest.add("path: Captain Dorrow gives the Floor 1 weapon from level 10, once", function()
	SpireTest.eq(SpireGear.dorrowOffer(9, 3, nil), "too_low", "level 9 is too low")
	SpireTest.eq(SpireGear.dorrowOffer(10, 3, nil), "offer", "level 10 gets the offer")
	SpireTest.eq(SpireGear.dorrowOffer(30, 3, "f1_ranger_bow"), "has", "only once")
	SpireTest.eq(SpireGear.dorrowOffer(10, 0, nil), "no_class", "pick a class first")
	SpireTest.eq(SpireGear.mainFor(3, 1, "crossbow").id, "f1_ranger_crossbow", "a Ranger's crossbow")
	SpireTest.eq(SpireGear.mainFor(4, 1, "axe").id, "f1_vanguard_axe", "a Vanguard's axe")
	SpireTest.eq(SpireGear.mainFor(3, 1, "axe"), nil, "not another class's family")
end)

SpireTest.add("path: tempering adds one tier and stops at the top", function()
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local w = SpireGear.make(b, "f1_mystic_rod")
	SpireTest.eq(SpireGear.temper(w), true, "tempered")
	SpireTest.eq(SpireGear.state(w).tier, 1, "tier 1")
	SpireGear.setState(w, { tier = 5 })
	SpireTest.eq(SpireGear.temper(w), false, "no tier past 5")
	b:remove()
end)

SpireTest.add("path: the Floor 1 story line runs weapon, temper, armour", function()
	local temper = SpireQuests.get("q1_temper")
	SpireTest.eq(temper ~= nil and temper.giver, "Captain Dorrow", "Dorrow gives the temper quest")
	SpireTest.eq(temper.reward.temper, true, "it tempers the weapon")
	SpireTest.eq(temper.side ~= true, true, "it is a story quest")
	SpireTest.eq(SpireQuests.available(temper, -1, {}, { level = 14, hasWeapon = false }), false, "not without the weapon")
	SpireTest.eq(SpireQuests.available(temper, -1, {}, { level = 14, hasWeapon = true }), true, "with the weapon")
	SpireTest.eq(SpireQuests.available(temper, -1, {}, { level = 9, hasWeapon = true }), false, "not below its level")
	local armour = SpireQuests.get("q1_iron2")
	SpireTest.eq(armour.reward.gear == true and armour.side ~= true, true, "the armour quest is part of the story")
end)

SpireTest.add("path: the Gate Hound gives cut shards once, the Axe-Lord awakens", function()
	local plan = SpireGear.bossReward("Gate Hound", false)
	SpireTest.eq(plan.shards, 3, "three cut shards")
	SpireTest.eq(SpireGear.bossReward("Gate Hound", true).shards, 0, "not twice")
	SpireTest.eq(SpireGear.bossReward("Axe-Lord of the Stair", false).awaken, 1, "the Axe-Lord awakens Floor 1 weapons")
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	for _, id in ipairs({ "f1_vanguard_axe", "f1_ranger_drop" }) do
		local w = SpireGear.make(b, id)
		SpireTest.eq(SpireGear.awaken(w), true, id .. " awakens")
		local d = SpireGear.def(id)
		SpireTest.eq(w:getName() .. "/" .. tostring(SpireGear.state(w).awakened), d.awakenedName .. "/true", "new name, awakened")
		SpireTest.eq(SpireGear.awaken(w), false, "only once")
	end
	b:remove()
end)

SpireTest.add("path: every Floor 1 step says where to go", function()
	SpireTest.eq(#SpireClimb.FLOOR1 >= 5, true, "at least five steps")
	for _, s in ipairs(SpireClimb.FLOOR1) do
		SpireTest.eq(type(s.where) == "string" and #s.where > 5, true, s.key .. " names a place")
		SpireTest.eq(type(s.done), "function", s.key .. " can be checked")
	end
end)

-- FLOOR1_REVIEW.md F1-46: the Floor 1 checklist asks every climber to defeat the Gate Hound, so it must come back
SpireTest.add("bosses: the Gate Hound and the Axe-Lord both return after a kill", function()
	SpireTest.eq(SpireBoss.defs["Gate Hound"].respawn, true, "the Gate Hound respawns (its shards are on everyone's path)")
	SpireTest.eq(SpireBoss.defs["Axe-Lord of the Stair"].respawn, true, "the Axe-Lord respawns")
end)
