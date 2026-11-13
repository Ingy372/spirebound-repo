-- Roadmap R12: every perk works (one check per perk), the gear ladder exists with original names and real items,
-- and Floors 1-2 each have a quest line that rewards gear.
local never = function() return 1 end
local always = function() return 0 end

SpireTest.add("perks: every perk offered on any floor has a real effect", function()
	for floor = 1, 10 do
		for _, p in ipairs(SpireQuests.PERKS[floor] or {}) do
			SpireTest.eq(SpirePerks.EFFECTS[p.key] ~= nil, true, "floor " .. floor .. " perk " .. p.key .. " does something")
		end
	end
end)

SpireTest.add("perks: each combat and loot perk changes the numbers it promises", function()
	local E = SpirePerks.EFFECTS
	SpireTest.eq(SpirePerks.taken({ E.fog_sense }, COMBAT_PHYSICALDAMAGE, 100, always), 0, "Fog Sense: a dodged hit does nothing")
	SpireTest.eq(SpirePerks.taken({ E.fog_sense }, COMBAT_PHYSICALDAMAGE, 100, never), 100, "Fog Sense: otherwise full damage")
	SpireTest.eq(SpirePerks.taken({ E.iron_will }, COMBAT_PHYSICALDAMAGE, 100, never), 92, "Iron Will: -8% physical")
	SpireTest.eq(SpirePerks.taken({ E.bulwark }, COMBAT_FIREDAMAGE, 100, never), 95, "Bulwark: -5% of everything")
	SpireTest.eq(SpirePerks.taken({ E.ember_skin }, COMBAT_FIREDAMAGE, 100, never), 90, "Ember Skin: -10% fire")
	SpireTest.eq(SpirePerks.taken({ E.ember_skin }, COMBAT_ICEDAMAGE, 100, never), 100, "Ember Skin: not ice")
	SpireTest.eq(SpirePerks.taken({ E.toxin_ward }, COMBAT_EARTHDAMAGE, 100, never), 90, "Toxin Ward: -10% earth")
	SpireTest.eq(SpirePerks.taken({ E.frost_blood }, COMBAT_ICEDAMAGE, 100, never), 90, "Frost Blood: -10% ice")
	SpireTest.eq(SpirePerks.dealt({ E.executioner }, 100, 0.2, false, never), 110, "Executioner: +10% under 30% health")
	SpireTest.eq(SpirePerks.dealt({ E.executioner }, 100, 0.5, false, never), 100, "Executioner: not above")
	SpireTest.eq(SpirePerks.dealt({ E.hunters_eye }, 100, 1, false, always), 150, "Hunter's Eye: a critical hit")
	SpireTest.eq(SpirePerks.dealt({ E.ruinbreaker }, 100, 1, true, never), 105, "Ruinbreaker's Edge: +5% to bosses")
	SpireTest.eq(SpirePerks.potionHeal({ E.field_medic }, 200), 230, "Field Medic: +15% potion healing")
	SpireTest.eq(SpirePerks.secondWind({ E.second_wind_perk }, 200, 1000, nil, 100), 150, "Second Wind heals 15% below a quarter")
	SpireTest.eq(SpirePerks.secondWind({ E.second_wind_perk }, 200, 1000, 50, 100), 0, "Second Wind waits 5 minutes")
	SpireTest.eq(SpirePerks.coinBonus({ E.haggler }), 0.08, "Haggler: +8% coins")
	SpireTest.eq(SpirePerks.lootRoll({ E.lucky_find }), 0.03, "Lucky Find: +3% loot roll")
	for _, k in ipairs({ "thick_skin", "winter_vigor", "cobalt_heart" }) do
		SpireTest.eq(E[k].maxhp, 105, k .. ": +5% health")
	end
	SpireTest.eq(E.deep_reserves.maxmana, 110, "Deep Reserves: +10% mana")
	SpireTest.eq(E.forgehand.skills, 105, "Forgehand: +5% melee and distance skill")
	SpireTest.eq(E.light_step.speed, 10, "Light Step: +10 speed")
	SpireTest.eq(E.marsh_walker.speed, 15, "Marsh Walker: +15 speed")
end)

SpireTest.add("gear: every vocation has a drop, a quest piece and a boss piece on Floors 1 and 2", function()
	for floor = 1, 2 do
		for voc = 1, 4 do
			for _, src in ipairs({ "drop", "quest", "boss" }) do
				local g = SpireGear.find(voc, floor, src)
				SpireTest.eq(g ~= nil, true, string.format("vocation %d floor %d %s piece", voc, floor, src))
				SpireTest.eq(ItemType(g.base):getId() == g.base, true, g.name .. " is a real item")
			end
		end
		SpireTest.eq(MonsterType(SpireGear.bosses[floor]) ~= nil, true, "Floor " .. floor .. "'s boss drops its best piece")
	end
	local bag = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local item = SpireGear.make(bag, SpireGear.find(4, 1, "boss"))
	SpireTest.eq(item ~= nil and item:getName(), "Stairlord's Cleaver", "a made piece carries its own name")
	SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_ATTACK) > ItemType(3303):getAttack(), true, "and its bonus")
	bag:remove()
end)

SpireTest.add("quests: Floors 1 and 2 each have a quest line that rewards gear, not gold", function()
	for floor = 1, 2 do
		local found = false
		for _, q in ipairs(SpireQuests.list) do
			if q.floor == floor and q.reward.gear then
				found = true
				SpireTest.eq(q.requires ~= nil, true, q.id .. " is the second step of a line")
			end
		end
		SpireTest.eq(found, true, "Floor " .. floor .. " has a gear quest")
	end
end)
