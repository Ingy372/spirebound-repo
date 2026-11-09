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
}

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
