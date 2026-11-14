-- Spirebound spells. The design (why each spell exists, unlock curves, visuals) is docs/design/spells.md;
-- this file is the data. scripts/spirebound/spells.lua turns each row into a castable spell.
-- Spells unlock automatically at their level (no trainer, no gold; Jay, 2026-11-08).
--
-- Row fields
--   voc    "all" or a list of base vocation ids (1 Arcanist, 2 Mystic, 3 Ranger, 4 Vanguard); promotions inherit
--   level  a number, or for shared spells a table { [voc] = level } (each vocation learns them at its own pace)
--   cd     own cooldown in seconds; the group cooldown comes from the spell's group (see GROUP_COOLDOWN)
--   scale  what the numbers grow with: "magic" (default), "melee", "distance" or "level"
--   min/max/base  damage or healing = level/5 + scale*min + base  ..  level/5 + scale*max + base*2
--   cast / shoot / effect  the three visual layers: on the caster, the projectile, the impact on each tile/target
--   lostArt  floor whose story quests teach it (never level-unlocked)

SpireSpells = {}

-- Group cooldowns in milliseconds (Tibia's standard: attack 2 s, healing 1 s, support 2 s).
-- Sword skills share the "attack" group (with their own 1 s), so spells and sword skills weave, not stack.
SpireSpells.GROUP_COOLDOWN = { attack = 2000, healing = 1000, support = 2000 }

SpireSpells.BLANK_RUNE = 3147

local A, M, R, V = 1, 2, 3, 4

SpireSpells.list = {
	-- Shared utilities: every vocation gets them, each at its own level -----------------------------------------
	{ name = "Kindle", words = "kindle", voc = "all", level = { [A] = 8, [M] = 8, [R] = 9, [V] = 10 }, mana = 20, cd = 2, kind = "light", lightLevel = 7, duration = 600, effect = CONST_ME_FIRE_SPARKLES },
	{ name = "Wayfinder", words = "wayfinder", voc = "all", level = { [A] = 10, [M] = 10, [R] = 8, [V] = 8 }, mana = 20, cd = 2, kind = "find_person", effect = CONST_ME_MAGIC_BLUE },
	{ name = "Cleanse", words = "cleanse", voc = "all", level = { [A] = 12, [M] = 10, [R] = 11, [V] = 12 }, mana = 30, cd = 6, kind = "cleanse", effect = CONST_ME_WHITE_SMOKES },
	{ name = "Skystep", words = "skystep", voc = "all", level = { [A] = 12, [M] = 12, [R] = 12, [V] = 14 }, mana = 50, cd = 2, kind = "levitate", effect = CONST_ME_TELEPORT },
	{ name = "Hearth Ration", words = "hearth ration", voc = "all", level = { [A] = 14, [M] = 11, [R] = 14, [V] = 14 }, mana = 120, cd = 2, kind = "food", effect = CONST_ME_MAGIC_GREEN },
	{ name = "Quickstep", words = "quickstep", voc = "all", level = { [A] = 14, [M] = 14, [R] = 10, [V] = 16 }, mana = 60, cd = 2, kind = "haste", speed = 0.3, duration = 30, effect = CONST_ME_WHIRLWIND_BLOW_WHITE },

	-- Vanguard: crimson and gold, steel impacts. Slow burn: sparse early, defensive milestones, late power. ---------
	{ name = "Heavy Strike", words = "heavy strike", voc = { V }, level = 8, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.8, max = 1.5, range = 1, effect = CONST_ME_HITAREA_RED },
	{ name = "Second Wind", words = "second wind", voc = { V }, level = 9, mana = 30, cd = 1, kind = "heal_self", scale = "level", min = 1.0, max = 1.6, base = 20, effect = CONST_ME_OUTBURST_YELLOW },
	{ name = "Rending Blow", words = "rending blow", voc = { V }, level = 16, mana = 35, cd = 6, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.9, max = 1.6, range = 1, effect = CONST_ME_SLASH, impact2 = CONST_ME_DRAWBLOOD, dot = { type = CONDITION_BLEEDING, ticks = 5, interval = 2000, pct = 0.12 } },
	{ name = "Rally Cry", words = "rally cry", voc = { V }, level = 20, mana = 40, cd = 4, kind = "taunt", radius = 3, cast = CONST_ME_CHIVALRIOUS_CHALLENGE, effect = CONST_ME_SOUND_RED },
	{ name = "Charge", words = "charge", voc = { V }, level = 25, mana = 70, cd = 12, kind = "dash", tiles = 3, cast = CONST_ME_BLOODYSTEPS, effect = CONST_ME_GROUNDSHAKER },
	{ name = "Iron Hide", words = "iron hide", voc = { V }, level = 30, mana = 80, cd = 20, kind = "dr_self", pct = 30, duration = 6, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	-- the Vanguard's only damaging area spell: adjacent tiles only, about half the damage and half the rate of the others' (docs/design/spells.md)
	{ name = "Whirlwind", words = "whirlwind", voc = { V }, level = 33, mana = 60, cd = 8, kind = "attack_area", area = "ring1", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.4, max = 0.7, cast = CONST_ME_WHIRLWIND_BLOW_WHITE, effect = CONST_ME_HITAREA_RED },
	{ name = "Intimidate", words = "intimidate", voc = { V }, level = 40, mana = 90, cd = 16, kind = "slow_area", radius = 2, duration = 4, cast = CONST_ME_SOUND_RED, effect = CONST_ME_STUN },
	{ name = "Battle Hymn", words = "battle hymn", voc = { V }, level = 50, mana = 150, cd = 30, kind = "party_buff", buff = "melee", amount = 10, duration = 120, cast = CONST_ME_OUTBURST_YELLOW, effect = CONST_ME_MAGIC_RED },
	{ name = "Guardian Stance", words = "guardian stance", voc = { V }, level = 60, mana = 120, cd = 24, kind = "dr_adjacent", pct = 20, duration = 8, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	{ name = "Recovery", words = "recovery", voc = { V }, level = 70, mana = 120, cd = 2, kind = "heal_self", scale = "level", min = 2.0, max = 3.0, base = 60, cast = CONST_ME_MAGIC_RED, effect = CONST_ME_OUTBURST_YELLOW },
	{ name = "Skyrend", words = "skyrend", voc = { V }, level = 90, mana = 160, cd = 12, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 2.2, max = 3.4, base = 20, range = 1, cast = CONST_ME_HITAREA_ORANGE, effect = CONST_ME_EXPLOSIONHIT, impact2 = CONST_ME_CRITICAL_DAMAGE },
	{ name = "Iron Will", words = "iron will", voc = { V }, level = 110, mana = 80, cd = 12, kind = "break_free", effect = CONST_ME_MAGIC_RED },
	{ name = "Bulwark Aura", words = "bulwark aura", voc = { V }, level = 140, mana = 200, cd = 60, kind = "dr_party", pct = 8, duration = 120, radius = 4, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	{ name = "Undying Oath", words = "undying oath", voc = { V }, level = 200, mana = 250, cd = 120, kind = "undying", duration = 4, cast = CONST_ME_DIVINE_EMPOWERMENT, effect = CONST_ME_OUTBURST_YELLOW },
	{ name = "Last Bastion", words = "last bastion", voc = { V }, level = 120, mana = 250, cd = 60, kind = "heal_last_stand", scale = "level", min = 1.6, max = 2.4, base = 100, cast = CONST_ME_DIVINE_EMPOWERMENT, effect = CONST_ME_OUTBURST_YELLOW, lostArt = 5 },
	{ name = "Unbroken Line", words = "unbroken line", voc = { V }, level = 250, mana = 400, cd = 90, kind = "dr_party", pct = 15, duration = 10, radius = 4, cast = CONST_ME_CHIVALRIOUS_CHALLENGE, effect = CONST_ME_BLOCKHIT, lostArt = 8 },

	-- Ranger: daylight gold-white and forest green, arrows. Steady: something new every few levels, kiting tools early. -
	{ name = "Piercing Shot", words = "piercing shot", voc = { R }, level = 8, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.8, max = 1.5, shoot = CONST_ANI_SNIPERARROW, effect = CONST_ME_HITAREA_GREEN },
	{ name = "Field Dressing", words = "field dressing", voc = { R }, level = 10, mana = 40, cd = 1, kind = "heal_target", min = 1.2, max = 1.9, base = 15, shoot = CONST_ANI_SMALLHOLY, effect = CONST_ME_SPARKLING },
	{ name = "Keen Sight", words = "keen sight", voc = { R }, level = 13, mana = 40, cd = 10, kind = "reveal", radius = 6, cast = CONST_ME_OUTBURST_WHITE, effect = CONST_ME_MAGIC_BLUE },
	{ name = "Scatter Shot", words = "scatter shot", voc = { R }, level = 16, mana = 45, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.7, max = 1.3, cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_HITAREA_GREEN },
	{ name = "Snare", words = "snare", voc = { R }, level = 20, mana = 60, cd = 10, kind = "root", duration = 3, shoot = CONST_ANI_EARTHARROW, effect = CONST_ME_ROOTS },
	{ name = "Disengage", words = "disengage", voc = { R }, level = 24, mana = 60, cd = 12, kind = "leap_away", tiles = 2, cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_POFF },
	{ name = "Tracker's Mark", words = "trackers mark", voc = { R }, level = 28, mana = 60, cd = 15, kind = "mark", pct = 10, duration = 15, shoot = CONST_ANI_FLASHARROW, effect = CONST_ME_REDSMOKE },
	{ name = "Swift Foot", words = "swift foot", voc = { R }, level = 32, mana = 100, cd = 2, kind = "haste", speed = 0.7, duration = 22, effect = CONST_ME_WHIRLWIND_BLOW_GREEN },
	{ name = "Radiant Shot", words = "radiant shot", voc = { R }, level = 38, mana = 70, cd = 4, kind = "attack_target", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.1, max = 1.8, base = 10, shoot = CONST_ANI_SMALLHOLY, effect = CONST_ME_HOLYDAMAGE },
	{ name = "Sunburst Volley", words = "sunburst volley", voc = { R }, level = 45, mana = 110, cd = 6, kind = "attack_area", area = "target1", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 0.9, max = 1.5, shoot = CONST_ANI_HOLY, effect = CONST_ME_HOLYAREA },
	{ name = "Camouflage", words = "camouflage", voc = { R }, level = 50, mana = 120, cd = 30, kind = "invisible", duration = 10, effect = CONST_ME_GREENSMOKE },
	{ name = "Eagle Eye", words = "eagle eye", voc = { R }, level = 55, mana = 180, cd = 60, kind = "party_buff", buff = "crit", amount = 10, duration = 120, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_SPARKLING },
	{ name = "Sanctified Ground", words = "sanctified ground", voc = { R }, level = 65, mana = 220, cd = 30, kind = "heal_zone", min = 0.6, max = 1.0, base = 20, radius = 2, duration = 6, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_HOLYAREA },
	{ name = "Dawnpiercer", words = "dawnpiercer", voc = { R }, level = 80, mana = 160, cd = 10, kind = "attack_area", area = "beam7", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.5, max = 2.4, base = 10, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_HOLYDAMAGE },
	{ name = "Hunter's Focus", words = "hunters focus", voc = { R }, level = 100, mana = 150, cd = 60, kind = "party_buff", buff = "distance", amount = 15, duration = 20, radius = 0, cast = CONST_ME_DIVINE_EMPOWERMENT, effect = CONST_ME_SPARKLING },
	{ name = "Lightrain", words = "lightrain", voc = { R }, level = 160, mana = 300, cd = 15, kind = "attack_area", area = "target2", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.6, max = 2.6, base = 20, shoot = CONST_ANI_HOLY, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_HOLYAREA },
	{ name = "Hawk's Path", words = "hawks path", voc = { R }, level = 120, mana = 150, cd = 20, kind = "blink", tiles = 6, cast = CONST_ME_WHIRLWIND_BLOW_WHITE, effect = CONST_ME_OUTBURST_WHITE, lostArt = 5 },
	{ name = "Volley of Dawn", words = "volley of dawn", voc = { R }, level = 250, mana = 500, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 2.6, max = 4.0, base = 30, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_DIVINE_GRENADE, lostArt = 8 },

	-- Arcanist: ember orange and storm violet. Front-loaded glass cannon: most attacks by 30, big spikes at 55, 80, 100. --
	{ name = "Ember Strike", words = "ember strike", voc = { A }, level = 8, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_FIRE, effect = CONST_ME_FIREATTACK },
	{ name = "Mending Spark", words = "mending spark", voc = { A }, level = 9, mana = 25, cd = 1, kind = "heal_self", min = 1.0, max = 1.6, base = 10, effect = CONST_ME_PURPLEENERGY },
	{ name = "Volt Strike", words = "volt strike", voc = { A }, level = 12, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_ENERGYDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_ENERGY, effect = CONST_ME_PURPLE_ELECTRIC_SPARK },
	{ name = "Mana Ward", words = "mana ward", voc = { A }, level = 14, mana = 50, cd = 14, kind = "manashield", duration = 180, effect = CONST_ME_PURPLETELEPORT },
	{ name = "Fireburst Wave", words = "fireburst wave", voc = { A }, level = 18, mana = 80, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_FIREDAMAGE, min = 1.3, max = 2.1, cast = CONST_ME_ORANGE_ENERGY_SPARK, effect = CONST_ME_FIREAREA },
	{ name = "Arc Beam", words = "arc beam", voc = { A }, level = 23, mana = 110, cd = 4, kind = "attack_area", area = "beam", element = COMBAT_ENERGYDAMAGE, min = 1.6, max = 2.6, cast = CONST_ME_PURPLE_ELECTRIC_SPARK, effect = CONST_ME_ENERGYHIT },
	{ name = "Gale Step", words = "gale step", voc = { A }, level = 26, mana = 100, cd = 2, kind = "haste", speed = 0.7, duration = 22, effect = CONST_ME_PURPLESMOKE },
	{ name = "Conjure Fire Rune", words = "conjure fire rune", voc = { A }, level = 27, mana = 300, cd = 2, kind = "conjure", item = 3191, count = 4, effect = CONST_ME_FIRE_SPARKLES },
	{ name = "Blink", words = "blink", voc = { A }, level = 30, mana = 80, cd = 14, kind = "blink", tiles = 3, cast = CONST_ME_PURPLETELEPORT, effect = CONST_ME_PURPLETELEPORT },
	{ name = "Searing Brand", words = "searing brand", voc = { A }, level = 35, mana = 60, cd = 8, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 1.0, max = 1.6, shoot = CONST_ANI_FIRE, effect = CONST_ME_HITBYFIRE, dot = { type = CONDITION_FIRE, ticks = 6, interval = 2000, pct = 0.12 } },
	{ name = "Conjure Strike Rune", words = "conjure strike rune", voc = { A }, level = 45, mana = 600, cd = 2, kind = "conjure", item = 3155, count = 3, effect = CONST_ME_PURPLEENERGY },
	{ name = "Summon Ember Sprite", words = "summon ember sprite", voc = { A }, level = 50, mana = 300, cd = 30, kind = "summon", monster = "Ember Sprite", effect = CONST_ME_ORANGETELEPORT },
	{ name = "Stormcall", words = "stormcall", voc = { A }, level = 55, mana = 300, cd = 16, kind = "attack_area", area = "ring2", element = COMBAT_ENERGYDAMAGE, min = 2.2, max = 3.4, base = 10, cast = CONST_ME_STORM, effect = CONST_ME_ENERGYAREA },
	{ name = "Arcane Empower", words = "arcane empower", voc = { A }, level = 60, mana = 220, cd = 60, kind = "party_buff", buff = "magic", amount = 10, duration = 120, cast = CONST_ME_PURPLETELEPORT, effect = CONST_ME_PURPLEENERGY },
	{ name = "Inferno Core", words = "inferno core", voc = { A }, level = 80, mana = 400, cd = 20, kind = "attack_area", area = "ring2", element = COMBAT_FIREDAMAGE, min = 2.6, max = 4.0, base = 20, cast = CONST_ME_EXPLOSIONAREA, effect = CONST_ME_FIREAREA },
	{ name = "Cinder Lance", words = "cinder lance", voc = { A }, level = 100, mana = 250, cd = 30, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 3.2, max = 4.8, base = 30, shoot = CONST_ANI_EXPLOSION, effect = CONST_ME_EXPLOSIONHIT, impact2 = CONST_ME_FIRE_SPARKLES },
	{ name = "Arc Cataclysm", words = "arc cataclysm", voc = { A }, level = 130, mana = 500, cd = 12, kind = "attack_area", area = "bigbeam", element = COMBAT_ENERGYDAMAGE, min = 2.4, max = 3.6, base = 20, cast = CONST_ME_STORM, effect = CONST_ME_PURPLE_ELECTRIC_SPARK },
	{ name = "Meteor Rain", words = "meteor rain", voc = { A }, level = 120, mana = 600, cd = 40, kind = "attack_area", area = "target2", element = COMBAT_FIREDAMAGE, min = 3.2, max = 5.0, base = 30, shoot = CONST_ANI_FIRE, cast = CONST_ME_EXPLOSIONAREA, effect = CONST_ME_FIREAREA, lostArt = 5 },
	{ name = "Mirror Image", words = "mirror image", voc = { A }, level = 250, mana = 300, cd = 60, kind = "decoy", monster = "Mirror Image", duration = 5, effect = CONST_ME_PURPLETELEPORT, lostArt = 8 },

	-- Mystic: frost teal and living green. Healer's rhythm: heals first, party tools mid-game, damage a step behind the Arcanist. -
	{ name = "Frost Strike", words = "frost strike", voc = { M }, level = 8, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_ICEDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_ICE, effect = CONST_ME_ICEATTACK },
	{ name = "Dewfall", words = "dewfall", voc = { M }, level = 9, mana = 25, cd = 1, kind = "heal_self", min = 1.1, max = 1.8, base = 12, effect = CONST_ME_GREEN_RINGS },
	{ name = "Thorn Strike", words = "thorn strike", voc = { M }, level = 13, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_EARTHDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_EARTH, effect = CONST_ME_CARNIPHILA },
	{ name = "Mend Other", words = "mend other", voc = { M }, level = 16, mana = 70, cd = 1, kind = "heal_target", min = 1.6, max = 2.6, base = 20, shoot = CONST_ANI_GREENSTAR, effect = CONST_ME_MAGIC_GREEN },
	{ name = "Frost Wave", words = "frost wave", voc = { M }, level = 21, mana = 70, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_ICEDAMAGE, min = 1.0, max = 1.7, slow = true, cast = CONST_ME_ICETORNADO, effect = CONST_ME_ICEAREA },
	{ name = "Conjure Healing Rune", words = "conjure healing rune", voc = { M }, level = 24, mana = 400, cd = 2, kind = "conjure", item = 3160, count = 1, effect = CONST_ME_GREEN_RINGS },
	{ name = "Purify", words = "purify", voc = { M }, level = 28, mana = 90, cd = 6, kind = "purify", radius = 4, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_WHITE_SMOKES },
	{ name = "Barkskin", words = "barkskin", voc = { M }, level = 32, mana = 150, cd = 30, kind = "dr_party", pct = 10, duration = 120, radius = 4, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_SMALLPLANTS },
	{ name = "Mass Mend", words = "mass mend", voc = { M }, level = 36, mana = 160, cd = 2, kind = "heal_party", min = 1.0, max = 1.6, base = 20, radius = 4, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_MAGIC_GREEN },
	{ name = "Rejuvenate", words = "rejuvenate", voc = { M }, level = 42, mana = 100, cd = 6, kind = "hot_target", duration = 10, shoot = CONST_ANI_GREENSTAR, effect = CONST_ME_PULSE_GREEN },
	{ name = "Conjure Binding Rune", words = "conjure binding rune", voc = { M }, level = 48, mana = 500, cd = 2, kind = "conjure", item = 3165, count = 1, effect = CONST_ME_ROOTS },
	{ name = "Summon Wolf Companion", words = "summon wolf companion", voc = { M }, level = 50, mana = 300, cd = 30, kind = "summon", monster = "Wolf Companion", effect = CONST_ME_GREENSMOKE },
	{ name = "Thornfield", words = "thornfield", voc = { M }, level = 55, mana = 300, cd = 16, kind = "attack_area", area = "ring2", element = COMBAT_EARTHDAMAGE, min = 1.8, max = 2.9, base = 10, cast = CONST_ME_BIGPLANTS, effect = CONST_ME_PLANTATTACK },
	{ name = "Lifeward", words = "lifeward", voc = { M }, level = 65, mana = 120, cd = 12, kind = "dr_target", pct = 25, duration = 6, shoot = CONST_ANI_GREENSTAR, effect = CONST_ME_GREEN_RINGS },
	{ name = "Glacier Core", words = "glacier core", voc = { M }, level = 80, mana = 400, cd = 20, kind = "attack_area", area = "ring2", element = COMBAT_ICEDAMAGE, min = 2.2, max = 3.4, base = 20, cast = CONST_ME_GIANTICE, effect = CONST_ME_ICETORNADO },
	{ name = "Verdant Renewal", words = "verdant renewal", voc = { M }, level = 100, mana = 400, cd = 4, kind = "heal_party", min = 2.0, max = 3.0, base = 40, radius = 5, cast = CONST_ME_BIGPLANTS, effect = CONST_ME_PULSE_GREEN },
	{ name = "Mana Bloom", words = "mana bloom", voc = { M }, level = 130, mana = 200, cd = 60, kind = "mana_party", duration = 30, radius = 5, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_MAGIC_BLUE },
	{ name = "Wellspring", words = "wellspring", voc = { M }, level = 120, mana = 400, cd = 45, kind = "heal_zone", min = 1.0, max = 1.6, base = 40, radius = 3, duration = 8, cast = CONST_ME_WATERSPLASH, effect = CONST_ME_PULSE_GREEN, lostArt = 5 },
	{ name = "Winter's Breath", words = "winters breath", voc = { M }, level = 250, mana = 600, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_ICEDAMAGE, min = 3.2, max = 5.0, base = 30, cast = CONST_ME_GIANTICE, effect = CONST_ME_ICEAREA, lostArt = 8 },
}

-- Retired in the 2026-11-13 overhaul (docs/design/spells.md, "Retired"): First Aid (each vocation now has its own
-- first heal), Beacon (Kindle lasts longer instead), Entangle (renamed Conjure Binding Rune).

-- Pure: the level at which this base vocation learns the row
function SpireSpells.levelFor(row, baseVocation)
	if type(row.level) == "table" then
		return row.level[baseVocation] or math.huge
	end
	return row.level
end

-- Pure: lowest level any vocation learns the row (the engine's own level gate)
function SpireSpells.minLevel(row)
	if type(row.level) ~= "table" then
		return row.level
	end
	local low = math.huge
	for _, l in pairs(row.level) do
		low = math.min(low, l)
	end
	return low
end

-- Pure: the spell group for a row
function SpireSpells.group(row)
	if row.kind == "attack_target" or row.kind == "attack_area" then
		return "attack"
	end
	if row.kind:find("heal") then
		return "healing"
	end
	return "support"
end

-- Pure: Skystep needs a real gap. gapHasFloor = the tile you would pass through (above your head when going up,
-- in front of you when going down) has a floor.
function SpireSpells.levitateGapFree(gapHasFloor)
	return not gapHasFloor
end

-- Lost Arts: a player knows one once every story quest of its floor is done
function SpireSpells.knowsLostArt(row, floorStoryDone)
	return not row.lostArt or floorStoryDone(row.lostArt)
end

-- Pure: may this base vocation use this spell row?
function SpireSpells.allowed(row, baseVocation)
	if row.voc == "all" then
		return baseVocation >= 1 and baseVocation <= 4
	end
	for _, v in ipairs(row.voc) do
		if v == baseVocation then
			return true
		end
	end
	return false
end

-- Pure: spells that unlock exactly at `level` for this vocation (for the "you learned" message; Lost Arts excluded)
function SpireSpells.unlockedAt(level, baseVocation)
	local out = {}
	for _, row in ipairs(SpireSpells.list) do
		if not row.lostArt and SpireSpells.allowed(row, baseVocation) and SpireSpells.levelFor(row, baseVocation) == level then
			table.insert(out, row)
		end
	end
	return out
end

-- Pure: damage/heal range for a row. stat = the scaling value (magic level, weapon skill or character level).
function SpireSpells.range(row, level, stat)
	local base = row.base or 5
	if row.scale == "level" then
		return math.floor(level * row.min + base), math.floor(level * row.max + base * 2)
	end
	return math.floor(level / 5 + stat * row.min + base), math.floor(level / 5 + stat * row.max + base * 2)
end

-- Timed damage reduction / damage-taken marks / last-stand (Iron Hide, Guardian Stance, Barkskin, Lifeward,
-- Tracker's Mark, Undying Oath)
SpireBuffs = { reduce = {}, mark = {}, undying = {} } -- creatureId -> { pct, untilTime }

function SpireBuffs.addReduction(creatureId, pct, seconds)
	local cur = SpireBuffs.reduce[creatureId]
	if cur and cur.untilTime > os.time() and cur.pct > pct then
		return -- a stronger buff is already running; same buff never stacks
	end
	SpireBuffs.reduce[creatureId] = { pct = pct, untilTime = os.time() + seconds }
end

function SpireBuffs.addMark(creatureId, pct, seconds)
	SpireBuffs.mark[creatureId] = { pct = pct, untilTime = os.time() + seconds }
end

-- Pure: final damage after reduction and mark percentages
function SpireBuffs.apply(damage, reducePct, markPct)
	return math.floor(damage * (1 - (reducePct or 0) / 100) * (1 + (markPct or 0) / 100))
end

-- Pure: Undying Oath. Damage that would take health to 0 or below leaves 1 instead.
function SpireBuffs.undyingClamp(health, damage)
	if damage >= health then
		return math.max(0, health - 1)
	end
	return damage
end
