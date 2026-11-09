-- Spirebound spells (DESIGN.md 5.3b). Spells unlock automatically at their level (no trainer, no gold).
-- This file holds the table; scripts/spirebound/spells.lua turns each row into a castable spell.
-- voc: "all" or a list of base vocation ids (1 Arcanist, 2 Mystic, 3 Ranger, 4 Vanguard); promotions inherit.
-- Lost Arts (★ in DESIGN) are added in task 4.6b and are never level-unlocked.

SpireSpells = {}

SpireSpells.list = {
	-- Shared by everyone
	{ name = "Kindle", words = "kindle", voc = "all", level = 8, mana = 20, cd = 2, kind = "light", lightLevel = 6, duration = 300 },
	{ name = "Wayfinder", words = "wayfinder", voc = "all", level = 8, mana = 20, cd = 2, kind = "find_person" },
	{ name = "First Aid", words = "first aid", voc = "all", level = 8, mana = 20, cd = 1, kind = "heal_self", min = 1.0, max = 1.6, base = 10 },
	{ name = "Cleanse", words = "cleanse", voc = "all", level = 10, mana = 30, cd = 6, kind = "cleanse" },
	{ name = "Skystep", words = "skystep", voc = "all", level = 12, mana = 50, cd = 2, kind = "levitate" },
	{ name = "Hearth Ration", words = "hearth ration", voc = "all", level = 14, mana = 120, cd = 2, kind = "food" },
	{ name = "Quickstep", words = "quickstep", voc = "all", level = 14, mana = 60, cd = 2, kind = "haste", speed = 0.3, duration = 30 },
	{ name = "Beacon", words = "beacon", voc = "all", level = 20, mana = 60, cd = 2, kind = "light", lightLevel = 9, duration = 1200 },

	-- Vanguard (4)
	{ name = "Second Wind", words = "second wind", voc = { 4 }, level = 10, mana = 40, cd = 2, kind = "heal_self", min = 1.4, max = 2.2, base = 20 },
	{ name = "Rally Cry", words = "rally cry", voc = { 4 }, level = 20, mana = 40, cd = 2, kind = "taunt", radius = 3 },
	{ name = "Charge", words = "charge", voc = { 4 }, level = 25, mana = 70, cd = 12, kind = "dash", tiles = 3 },
	{ name = "Iron Hide", words = "iron hide", voc = { 4 }, level = 30, mana = 80, cd = 20, kind = "dr_self", pct = 30, duration = 6 },
	{ name = "Intimidate", words = "intimidate", voc = { 4 }, level = 35, mana = 90, cd = 16, kind = "slow_area", radius = 2, duration = 4 },
	{ name = "Battle Hymn", words = "battle hymn", voc = { 4 }, level = 45, mana = 150, cd = 30, kind = "party_buff", buff = "melee", amount = 10, duration = 120 },
	{ name = "Guardian Stance", words = "guardian stance", voc = { 4 }, level = 50, mana = 120, cd = 24, kind = "dr_adjacent", pct = 20, duration = 8 },

	-- Ranger (3)
	{ name = "Keen Sight", words = "keen sight", voc = { 3 }, level = 13, mana = 40, cd = 10, kind = "reveal", radius = 6 },
	{ name = "Field Dressing", words = "field dressing", voc = { 3 }, level = 15, mana = 60, cd = 2, kind = "heal_target", min = 1.2, max = 1.9, base = 15 },
	{ name = "Tracker's Mark", words = "trackers mark", voc = { 3 }, level = 20, mana = 60, cd = 15, kind = "mark", pct = 10, duration = 15 },
	{ name = "Disengage", words = "disengage", voc = { 3 }, level = 25, mana = 60, cd = 12, kind = "leap_away", tiles = 2 },
	{ name = "Swift Foot", words = "swift foot", voc = { 3 }, level = 30, mana = 100, cd = 2, kind = "haste", speed = 0.7, duration = 22 },
	{ name = "Snare", words = "snare", voc = { 3 }, level = 35, mana = 80, cd = 12, kind = "root", duration = 3 },
	{ name = "Radiant Shot", words = "radiant shot", voc = { 3 }, level = 40, mana = 70, cd = 4, kind = "attack_target", element = COMBAT_HOLYDAMAGE, min = 1.4, max = 2.2, effect = CONST_ME_HOLYDAMAGE, shoot = CONST_ANI_HOLY },
	{ name = "Camouflage", words = "camouflage", voc = { 3 }, level = 45, mana = 120, cd = 30, kind = "invisible", duration = 10 },

	-- Arcanist (1)
	{ name = "Ember Strike", words = "ember strike", voc = { 1 }, level = 8, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 1.2, max = 2.0, effect = CONST_ME_FIREATTACK, shoot = CONST_ANI_FIRE },
	{ name = "Volt Strike", words = "volt strike", voc = { 1 }, level = 12, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_ENERGYDAMAGE, min = 1.2, max = 2.0, effect = CONST_ME_ENERGYAREA, shoot = CONST_ANI_ENERGY },
	{ name = "Mana Ward", words = "mana ward", voc = { 1 }, level = 14, mana = 50, cd = 14, kind = "manashield", duration = 180 },
	{ name = "Fireburst Wave", words = "fireburst wave", voc = { 1 }, level = 23, mana = 80, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_FIREDAMAGE, min = 1.3, max = 2.1, effect = CONST_ME_FIREAREA },
	{ name = "Conjure Fire Rune", words = "conjure fire rune", voc = { 1 }, level = 27, mana = 300, cd = 2, kind = "conjure", item = 3191, count = 4 },
	{ name = "Arc Beam", words = "arc beam", voc = { 1 }, level = 35, mana = 110, cd = 4, kind = "attack_area", area = "beam", element = COMBAT_ENERGYDAMAGE, min = 1.6, max = 2.6, effect = CONST_ME_ENERGYHIT },
	{ name = "Blink", words = "blink", voc = { 1 }, level = 40, mana = 80, cd = 14, kind = "blink", tiles = 3 },
	{ name = "Conjure Strike Rune", words = "conjure strike rune", voc = { 1 }, level = 45, mana = 600, cd = 2, kind = "conjure", item = 3155, count = 3 },
	{ name = "Summon Ember Sprite", words = "summon ember sprite", voc = { 1 }, level = 50, mana = 300, cd = 30, kind = "summon", monster = "Ember Sprite" },

	-- Mystic (2)
	{ name = "Frost Strike", words = "frost strike", voc = { 2 }, level = 8, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_ICEDAMAGE, min = 1.2, max = 2.0, effect = CONST_ME_ICEATTACK, shoot = CONST_ANI_ICE },
	{ name = "Thorn Strike", words = "thorn strike", voc = { 2 }, level = 14, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_EARTHDAMAGE, min = 1.2, max = 2.0, effect = CONST_ME_CARNIPHILA, shoot = CONST_ANI_EARTH },
	{ name = "Mend Other", words = "mend other", voc = { 2 }, level = 18, mana = 70, cd = 1, kind = "heal_target", min = 1.6, max = 2.6, base = 20 },
	{ name = "Purify", words = "purify", voc = { 2 }, level = 20, mana = 90, cd = 6, kind = "purify", radius = 4 },
	{ name = "Conjure Healing Rune", words = "conjure healing rune", voc = { 2 }, level = 24, mana = 400, cd = 2, kind = "conjure", item = 3160, count = 1 },
	{ name = "Barkskin", words = "barkskin", voc = { 2 }, level = 30, mana = 150, cd = 30, kind = "dr_party", pct = 10, duration = 120, radius = 4 },
	{ name = "Rejuvenate", words = "rejuvenate", voc = { 2 }, level = 35, mana = 100, cd = 6, kind = "hot_target", duration = 10 },
	{ name = "Mass Mend", words = "mass mend", voc = { 2 }, level = 36, mana = 160, cd = 2, kind = "heal_party", min = 1.0, max = 1.6, base = 20, radius = 4 },
	{ name = "Entangle", words = "entangle", voc = { 2 }, level = 40, mana = 500, cd = 2, kind = "conjure", item = 3165, count = 1 },
	{ name = "Summon Wolf Companion", words = "summon wolf companion", voc = { 2 }, level = 50, mana = 300, cd = 30, kind = "summon", monster = "Wolf Companion" },

	-- Above level 50 (roadmap 4.6b)
	{ name = "Bulwark Aura", words = "bulwark aura", voc = { 4 }, level = 60, mana = 200, cd = 60, kind = "dr_party", pct = 8, duration = 120, radius = 4 },
	{ name = "Recovery", words = "recovery", voc = { 4 }, level = 70, mana = 120, cd = 2, kind = "heal_self", min = 2.2, max = 3.4, base = 60 },
	{ name = "Iron Will", words = "iron will", voc = { 4 }, level = 80, mana = 80, cd = 12, kind = "break_free" },
	{ name = "Eagle Eye", words = "eagle eye", voc = { 3 }, level = 55, mana = 180, cd = 60, kind = "party_buff", buff = "crit", amount = 10, duration = 120 },
	{ name = "Sanctified Ground", words = "sanctified ground", voc = { 3 }, level = 70, mana = 220, cd = 30, kind = "heal_zone", min = 0.6, max = 1.0, base = 20, radius = 2, duration = 6 },
	{ name = "Arcane Empower", words = "arcane empower", voc = { 1 }, level = 60, mana = 220, cd = 60, kind = "party_buff", buff = "magic", amount = 10, duration = 120 },

	-- Lost Arts (DESIGN 5.3b): never unlocked by level alone; earned from Floor 5 and Floor 8 story quests (Claude's call)
	{ name = "Last Bastion", words = "last bastion", voc = { 4 }, level = 100, mana = 250, cd = 60, kind = "heal_last_stand", min = 2.0, max = 3.0, base = 100, lostArt = 5 },
	{ name = "Unbroken Line", words = "unbroken line", voc = { 4 }, level = 150, mana = 400, cd = 90, kind = "dr_party", pct = 15, duration = 10, radius = 4, lostArt = 8 },
	{ name = "Hawk's Path", words = "hawks path", voc = { 3 }, level = 100, mana = 150, cd = 20, kind = "blink", tiles = 6, lostArt = 5 },
	{ name = "Volley of Dawn", words = "volley of dawn", voc = { 3 }, level = 150, mana = 500, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_HOLYDAMAGE, min = 3.0, max = 4.6, effect = CONST_ME_HOLYAREA, lostArt = 8 },
	{ name = "Meteor Rain", words = "meteor rain", voc = { 1 }, level = 100, mana = 600, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_FIREDAMAGE, min = 3.2, max = 5.0, effect = CONST_ME_FIREAREA, lostArt = 5 },
	{ name = "Mirror Image", words = "mirror image", voc = { 1 }, level = 150, mana = 300, cd = 60, kind = "decoy", monster = "Mirror Image", duration = 5, lostArt = 8 },
	{ name = "Wellspring", words = "wellspring", voc = { 2 }, level = 100, mana = 400, cd = 45, kind = "heal_zone", min = 1.0, max = 1.6, base = 40, radius = 3, duration = 8, lostArt = 5 },
	{ name = "Winter's Breath", words = "winters breath", voc = { 2 }, level = 150, mana = 600, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_ICEDAMAGE, min = 3.2, max = 5.0, effect = CONST_ME_ICEAREA, lostArt = 8 },
}

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
		if row.level == level and not row.lostArt and SpireSpells.allowed(row, baseVocation) then
			table.insert(out, row)
		end
	end
	return out
end

-- Timed damage reduction / damage-taken marks (Iron Hide, Guardian Stance, Barkskin, Tracker's Mark)
SpireBuffs = { reduce = {}, mark = {} } -- creatureId -> { pct, untilTime }

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
