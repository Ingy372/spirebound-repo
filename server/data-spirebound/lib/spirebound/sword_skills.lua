-- Sword skills (DESIGN.md 5.3): combo-style abilities with cooldowns, tied to the weapon type in hand.
-- This file holds the data and the pure rules. scripts/spirebound/sword_skills.lua turns each entry into a spell.

SwordSkills = {
	COMBO_WINDOW = 4, -- seconds between steps of Opener -> Link -> Finisher
	COMBO_BONUS = 1.30, -- finisher damage multiplier when the combo is complete
	SHARED_COOLDOWN = 1000, -- ms, shared by all sword skills
	OPENER = "opener",
	LINK = "link",
	FINISHER = "finisher",
}

-- Weapon families. "melee" families scale with the weapon skill; "magic" families with magic level.
SwordSkills.families = {
	sword = { kind = "melee", skill = SKILL_SWORD },
	axe = { kind = "melee", skill = SKILL_AXE },
	club = { kind = "melee", skill = SKILL_CLUB },
	bow = { kind = "melee", skill = SKILL_DISTANCE },
	crossbow = { kind = "melee", skill = SKILL_DISTANCE },
	spear = { kind = "melee", skill = SKILL_DISTANCE },
	wand = { kind = "magic" },
	rod = { kind = "magic" },
}

-- area names are defined in scripts/spirebound/sword_skills.lua
-- coef: damage strength relative to a basic hit; cd: cooldown in ms
SwordSkills.list = {
	-- Sword
	{ key = "arc_slash", name = "Arc Slash", words = "arc slash", family = "sword", tag = "opener", area = "front3", coef = 1.2, cd = 4000, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "riposte_line", name = "Riposte Line", words = "riposte line", family = "sword", tag = "link", area = "line3", coef = 1.3, cd = 6000, effect = CONST_ME_BLOCKHIT, element = COMBAT_PHYSICALDAMAGE },
	{ key = "fourfold_rend", name = "Fourfold Rend", words = "fourfold rend", family = "sword", tag = "finisher", area = "target", coef = 2.0, cd = 10000, effect = CONST_ME_DRAWBLOOD, element = COMBAT_PHYSICALDAMAGE },
	-- Axe
	{ key = "split_earth", name = "Split Earth", words = "split earth", family = "axe", tag = "opener", area = "around1", coef = 1.1, cd = 5000, effect = CONST_ME_GROUNDSHAKER, element = COMBAT_PHYSICALDAMAGE },
	{ key = "hewing_turn", name = "Hewing Turn", words = "hewing turn", family = "axe", tag = "link", area = "front3", coef = 1.3, cd = 6000, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "executioners_drop", name = "Executioner's Drop", words = "executioners drop", family = "axe", tag = "finisher", area = "target", coef = 2.0, cd = 10000, effect = CONST_ME_EXPLOSIONHIT, element = COMBAT_PHYSICALDAMAGE },
	-- Club
	{ key = "bell_ringer", name = "Bell Ringer", words = "bell ringer", family = "club", tag = "opener", area = "target", coef = 1.2, cd = 5000, effect = CONST_ME_STUN, element = COMBAT_PHYSICALDAMAGE },
	{ key = "crushing_arc", name = "Crushing Arc", words = "crushing arc", family = "club", tag = "link", area = "front3", coef = 1.3, cd = 6000, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "tremor_blow", name = "Tremor Blow", words = "tremor blow", family = "club", tag = "finisher", area = "around1", coef = 1.7, cd = 10000, effect = CONST_ME_GROUNDSHAKER, element = COMBAT_PHYSICALDAMAGE },
	-- Bow
	{ key = "quickdraw", name = "Quickdraw", words = "quickdraw", family = "bow", tag = "opener", area = "target", coef = 1.2, cd = 3000, effect = CONST_ME_HITAREA, distance = CONST_ANI_ARROW, element = COMBAT_PHYSICALDAMAGE },
	{ key = "pinning_shot", name = "Pinning Shot", words = "pinning shot", family = "bow", tag = "link", area = "target", coef = 1.3, cd = 6000, effect = CONST_ME_HITAREA, distance = CONST_ANI_ARROW, element = COMBAT_PHYSICALDAMAGE, slow = true },
	{ key = "arrow_storm", name = "Arrow Storm", words = "arrow storm", family = "bow", tag = "finisher", area = "targetaround1", coef = 1.6, cd = 10000, effect = CONST_ME_HITAREA, distance = CONST_ANI_ARROW, element = COMBAT_PHYSICALDAMAGE },
	-- Crossbow
	{ key = "bolt_lance", name = "Bolt Lance", words = "bolt lance", family = "crossbow", tag = "opener", area = "line4", coef = 1.1, cd = 4000, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "ratchet_shot", name = "Ratchet Shot", words = "ratchet shot", family = "crossbow", tag = "link", area = "target", coef = 1.4, cd = 6000, effect = CONST_ME_HITAREA, distance = CONST_ANI_BOLT, element = COMBAT_PHYSICALDAMAGE },
	{ key = "siege_bolt", name = "Siege Bolt", words = "siege bolt", family = "crossbow", tag = "finisher", area = "target", coef = 2.1, cd = 10000, effect = CONST_ME_EXPLOSIONHIT, distance = CONST_ANI_POWERBOLT, element = COMBAT_PHYSICALDAMAGE },
	-- Spear
	{ key = "skewer", name = "Skewer", words = "skewer", family = "spear", tag = "opener", area = "target", coef = 1.2, cd = 3000, effect = CONST_ME_DRAWBLOOD, distance = CONST_ANI_SPEAR, element = COMBAT_PHYSICALDAMAGE },
	{ key = "javelin_arc", name = "Javelin Arc", words = "javelin arc", family = "spear", tag = "link", area = "targetaround1", coef = 1.1, cd = 6000, effect = CONST_ME_HITAREA, distance = CONST_ANI_SPEAR, element = COMBAT_PHYSICALDAMAGE },
	{ key = "comet_spear", name = "Comet Spear", words = "comet spear", family = "spear", tag = "finisher", area = "target", coef = 2.0, cd = 10000, effect = CONST_ME_FIREAREA, distance = CONST_ANI_SPEAR, element = COMBAT_PHYSICALDAMAGE },
	-- Wand (Arcanist)
	{ key = "spark_edge", name = "Spark Edge", words = "spark edge", family = "wand", tag = "opener", area = "target", coef = 1.2, cd = 3000, effect = CONST_ME_ENERGYHIT, distance = CONST_ANI_ENERGY, element = COMBAT_ENERGYDAMAGE },
	{ key = "flame_script", name = "Flame Script", words = "flame script", family = "wand", tag = "link", area = "targetaround1", coef = 1.1, cd = 6000, effect = CONST_ME_FIREAREA, distance = CONST_ANI_FIRE, element = COMBAT_FIREDAMAGE },
	{ key = "starfall_rite", name = "Starfall Rite", words = "starfall rite", family = "wand", tag = "finisher", area = "around2", coef = 1.6, cd = 12000, effect = CONST_ME_ENERGYAREA, element = COMBAT_ENERGYDAMAGE },
	-- Rod (Mystic)
	{ key = "thorn_edge", name = "Thorn Edge", words = "thorn edge", family = "rod", tag = "opener", area = "target", coef = 1.2, cd = 3000, effect = CONST_ME_SMALLPLANTS, distance = CONST_ANI_EARTH, element = COMBAT_EARTHDAMAGE },
	{ key = "frost_script", name = "Frost Script", words = "frost script", family = "rod", tag = "link", area = "target", coef = 1.2, cd = 6000, effect = CONST_ME_ICEATTACK, distance = CONST_ANI_ICE, element = COMBAT_ICEDAMAGE, slow = true },
	{ key = "verdant_burst", name = "Verdant Burst", words = "verdant burst", family = "rod", tag = "finisher", area = "around2", coef = 1.4, cd = 12000, effect = CONST_ME_PLANTATTACK, element = COMBAT_EARTHDAMAGE, partyHeal = 0.05 },

	-- Skills 4-6 per family (roadmap 4.6), unlocked by level 60 / 100 / 150 (Claude's call)
	{ key = "crescent_guard", name = "Crescent Guard", words = "crescent guard", family = "sword", tag = "opener", area = "front3", coef = 1.6, cd = 5000, level = 60, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "blade_tempest", name = "Blade Tempest", words = "blade tempest", family = "sword", tag = "link", area = "around1", coef = 1.7, cd = 8000, level = 100, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "thousandfold_strike", name = "Thousandfold Strike", words = "thousandfold strike", family = "sword", tag = "finisher", area = "target", coef = 3.2, cd = 14000, level = 150, effect = CONST_ME_DRAWBLOOD, element = COMBAT_PHYSICALDAMAGE },
	{ key = "cleaving_gale", name = "Cleaving Gale", words = "cleaving gale", family = "axe", tag = "opener", area = "front3", coef = 1.6, cd = 5000, level = 60, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "ravagers_spin", name = "Ravager's Spin", words = "ravagers spin", family = "axe", tag = "link", area = "around1", coef = 1.8, cd = 8000, level = 100, effect = CONST_ME_GROUNDSHAKER, element = COMBAT_PHYSICALDAMAGE },
	{ key = "worldsplitter", name = "Worldsplitter", words = "worldsplitter", family = "axe", tag = "finisher", area = "line4", coef = 2.8, cd = 14000, level = 150, effect = CONST_ME_EXPLOSIONHIT, element = COMBAT_PHYSICALDAMAGE },
	{ key = "shatter_guard", name = "Shatter Guard", words = "shatter guard", family = "club", tag = "opener", area = "target", coef = 1.7, cd = 5000, level = 60, effect = CONST_ME_STUN, element = COMBAT_PHYSICALDAMAGE },
	{ key = "quake_line", name = "Quake Line", words = "quake line", family = "club", tag = "link", area = "line4", coef = 1.8, cd = 8000, level = 100, effect = CONST_ME_GROUNDSHAKER, element = COMBAT_PHYSICALDAMAGE },
	{ key = "titans_fall", name = "Titan's Fall", words = "titans fall", family = "club", tag = "finisher", area = "around2", coef = 2.4, cd = 14000, level = 150, effect = CONST_ME_GROUNDSHAKER, element = COMBAT_PHYSICALDAMAGE },
	{ key = "twin_shot", name = "Twin Shot", words = "twin shot", family = "bow", tag = "opener", area = "target", coef = 1.7, cd = 4000, level = 60, effect = CONST_ME_HITAREA, distance = CONST_ANI_ARROW, element = COMBAT_PHYSICALDAMAGE },
	{ key = "hail_of_arrows", name = "Hail of Arrows", words = "hail of arrows", family = "bow", tag = "link", area = "targetaround1", coef = 1.6, cd = 8000, level = 100, effect = CONST_ME_HITAREA, distance = CONST_ANI_ARROW, element = COMBAT_PHYSICALDAMAGE },
	{ key = "heartseeker", name = "Heartseeker", words = "heartseeker", family = "bow", tag = "finisher", area = "target", coef = 3.2, cd = 14000, level = 150, effect = CONST_ME_DRAWBLOOD, distance = CONST_ANI_ARROW, element = COMBAT_PHYSICALDAMAGE },
	{ key = "piercing_bolt", name = "Piercing Bolt", words = "piercing bolt", family = "crossbow", tag = "opener", area = "line4", coef = 1.6, cd = 5000, level = 60, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "scatter_bolts", name = "Scatter Bolts", words = "scatter bolts", family = "crossbow", tag = "link", area = "targetaround1", coef = 1.6, cd = 8000, level = 100, effect = CONST_ME_HITAREA, distance = CONST_ANI_BOLT, element = COMBAT_PHYSICALDAMAGE },
	{ key = "ballista_shot", name = "Ballista Shot", words = "ballista shot", family = "crossbow", tag = "finisher", area = "target", coef = 3.3, cd = 14000, level = 150, effect = CONST_ME_EXPLOSIONHIT, distance = CONST_ANI_POWERBOLT, element = COMBAT_PHYSICALDAMAGE },
	{ key = "lunging_thrust", name = "Lunging Thrust", words = "lunging thrust", family = "spear", tag = "opener", area = "target", coef = 1.7, cd = 4000, level = 60, effect = CONST_ME_DRAWBLOOD, distance = CONST_ANI_SPEAR, element = COMBAT_PHYSICALDAMAGE },
	{ key = "whirling_spear", name = "Whirling Spear", words = "whirling spear", family = "spear", tag = "link", area = "around1", coef = 1.6, cd = 8000, level = 100, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "skyfall_lance", name = "Skyfall Lance", words = "skyfall lance", family = "spear", tag = "finisher", area = "targetaround1", coef = 2.6, cd = 14000, level = 150, effect = CONST_ME_FIREAREA, distance = CONST_ANI_SPEAR, element = COMBAT_PHYSICALDAMAGE },
	{ key = "arc_script", name = "Arc Script", words = "arc script", family = "wand", tag = "opener", area = "target", coef = 1.7, cd = 4000, level = 60, effect = CONST_ME_ENERGYHIT, distance = CONST_ANI_ENERGY, element = COMBAT_ENERGYDAMAGE },
	{ key = "inferno_script", name = "Inferno Script", words = "inferno script", family = "wand", tag = "link", area = "targetaround1", coef = 1.6, cd = 8000, level = 100, effect = CONST_ME_FIREAREA, distance = CONST_ANI_FIRE, element = COMBAT_FIREDAMAGE },
	{ key = "cataclysm_rite", name = "Cataclysm Rite", words = "cataclysm rite", family = "wand", tag = "finisher", area = "around2", coef = 2.4, cd = 16000, level = 150, effect = CONST_ME_FIREAREA, element = COMBAT_FIREDAMAGE },
	{ key = "glacial_edge", name = "Glacial Edge", words = "glacial edge", family = "rod", tag = "opener", area = "target", coef = 1.7, cd = 4000, level = 60, effect = CONST_ME_ICEATTACK, distance = CONST_ANI_ICE, element = COMBAT_ICEDAMAGE },
	{ key = "bramble_script", name = "Bramble Script", words = "bramble script", family = "rod", tag = "link", area = "targetaround1", coef = 1.5, cd = 8000, level = 100, effect = CONST_ME_SMALLPLANTS, distance = CONST_ANI_EARTH, element = COMBAT_EARTHDAMAGE, slow = true },
	{ key = "lifebloom_rite", name = "Lifebloom Rite", words = "lifebloom rite", family = "rod", tag = "finisher", area = "around2", coef = 2.0, cd = 16000, level = 150, effect = CONST_ME_PLANTATTACK, element = COMBAT_EARTHDAMAGE, partyHeal = 0.08 },
	-- Twin Fang (DESIGN.md 5.6): only for holders of the rare unique skill
	{ key = "twin_fang_rush", name = "Twin Fang Rush", words = "twin fang rush", family = "sword", tag = "opener", area = "line4", coef = 2.0, cd = 6000, level = 1, twinFang = true, effect = CONST_ME_HITAREA, element = COMBAT_PHYSICALDAMAGE },
	{ key = "crossed_fangs", name = "Crossed Fangs", words = "crossed fangs", family = "sword", tag = "link", area = "around1", coef = 2.2, cd = 9000, level = 1, twinFang = true, effect = CONST_ME_DRAWBLOOD, element = COMBAT_PHYSICALDAMAGE },
	{ key = "fang_storm", name = "Fang Storm", words = "fang storm", family = "sword", tag = "finisher", area = "target", coef = 4.0, cd = 18000, level = 1, twinFang = true, effect = CONST_ME_EXPLOSIONHIT, element = COMBAT_PHYSICALDAMAGE },
}

-- Twin Fang -----------------------------------------------------------------
SwordSkills.TWIN_FANG = { MAX_HOLDERS = 3, SWORD_SKILL = 80, COMBOS = 1000, OFFHAND = 0.5 }

function SwordSkills.hasTwinFang(player)
	return player:kv():scoped("spirebound-twinfang"):get("holder") == true
end

-- Pure: may this character take the trial?
function SwordSkills.twinFangEligible(baseVocation, swordSkill, combos, holders)
	if holders >= SwordSkills.TWIN_FANG.MAX_HOLDERS then
		return false, "The trial is sealed until next season. Three already hold the Twin Fang."
	end
	if baseVocation ~= 4 then
		return false, "Only a Vanguard can hold two fangs."
	end
	if swordSkill < SwordSkills.TWIN_FANG.SWORD_SKILL then
		return false, "Your sword skill must reach " .. SwordSkills.TWIN_FANG.SWORD_SKILL .. "."
	end
	if combos < SwordSkills.TWIN_FANG.COMBOS then
		return false, string.format("Finish %d sword-skill combos first (%d so far).", SwordSkills.TWIN_FANG.COMBOS, combos)
	end
	return true
end

-- Pure combo rule. state = { stage = 0|1|2, t = seconds }. Returns newState, multiplier.
function SwordSkills.comboStep(state, tag, now)
	state = state or { stage = 0, t = 0 }
	local inTime = (now - (state.t or 0)) <= SwordSkills.COMBO_WINDOW
	if tag == SwordSkills.OPENER then
		return { stage = 1, t = now }, 1.0
	elseif tag == SwordSkills.LINK and state.stage == 1 and inTime then
		return { stage = 2, t = now }, 1.0
	elseif tag == SwordSkills.FINISHER and state.stage == 2 and inTime then
		return { stage = 0, t = now }, SwordSkills.COMBO_BONUS
	end
	return { stage = 0, t = now }, 1.0
end

-- Which family is the player holding? Pure part: decide from item facts.
-- facts = { weaponType = WEAPON_*, ammoType = AMMO_*, vocationBase = 1..4 }
function SwordSkills.familyFromFacts(facts)
	local w = facts.weaponType
	if w == WEAPON_SWORD then
		return "sword"
	elseif w == WEAPON_AXE then
		return "axe"
	elseif w == WEAPON_CLUB then
		return "club"
	elseif w == WEAPON_DISTANCE or w == WEAPON_MISSILE then
		if facts.ammoType == AMMO_BOLT then
			return "crossbow"
		elseif facts.ammoType == AMMO_ARROW then
			return "bow"
		end
		return "spear"
	elseif w == WEAPON_WAND then
		return facts.vocationBase == 2 and "rod" or "wand"
	end
	return nil
end

function SwordSkills.heldFamily(player)
	for _, slot in ipairs({ CONST_SLOT_LEFT, CONST_SLOT_RIGHT }) do
		local item = player:getSlotItem(slot)
		if item then
			local it = item:getType()
			local fam = SwordSkills.familyFromFacts({
				weaponType = it:getWeaponType(),
				ammoType = it:getAmmoType(),
				vocationBase = player:getVocation():getBaseId(),
			})
			if fam then
				return fam
			end
		end
	end
	return nil
end
