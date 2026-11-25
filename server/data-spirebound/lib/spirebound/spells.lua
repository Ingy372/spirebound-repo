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
-- Extra mechanics (2026-11-16 pass, docs/design/spells.md section 3.5):
--   anim     how an area spell plays out: "burst" (rings outward), "sweep" (rows away from you), "spiral" (around you),
--            "rain" (random tiles over a second); step = milliseconds between stages
--   delay / warn   the spell lands `delay` ms after the cast; `warn` is the marker shown on the tiles meanwhile
--   hits / hitGap  several projectiles in a row at one target
--   chain    { jumps, range, falloff }: the hit jumps on to nearby monsters
--   push / root / leech / vuln / execute / opener   riders on a hit (knock back, pin, heal the caster, armour break,
--            more damage on wounded / untouched targets)
--   dashTo   leap next to the target first
--   evolve   { { level, ...visual fields } }: the spell looks bigger once the caster reaches that level

SpireSpells = {}

-- Group cooldowns in milliseconds (Tibia's standard: attack 2 s, healing 1 s, support 2 s).
-- Sword skills share the "attack" group (with their own 1 s), so spells and sword skills weave, not stack.
SpireSpells.GROUP_COOLDOWN = { attack = 2000, healing = 1000, support = 2000 }

SpireSpells.BLANK_RUNE = 3147

local A, M, R, V = 1, 2, 3, 4

-- Spirebound's own spell effects, made with the Blender pipeline (art/effects, installed by tools/install_effects.py).
-- Ids start above the engine's own (which end at 309).
SpireFx = {
	STEEL_ARC = 401, -- crimson-edged steel slash
	SKYREND = 402, -- tall golden sword falling from above
	OATH_HALO = 403, -- golden ring around a character
	GROUND_CRACK = 404, -- stone bursting out of the ground
	WAR_BANNER = 405, -- a planted crimson banner
	LIGHT_NEEDLES = 406, -- needles of light falling
	SUN_SIGIL = 407, -- golden circle on the ground
	VIOLET_BOLT = 408, -- lightning striking from above
	METEOR = 409, -- a meteor landing
	EMBER_PILLAR = 410, -- a column of fire
	THORN_BURST = 411, -- thorns bursting out of the ground
	LEAF_WARD = 412, -- a leaf-green bubble around a character
	ICE_SPIRES = 413, -- ice crystals erupting
	BLOOM = 414, -- a flower of light opening
	CLASH = 415, -- the starburst of an elemental clash
	VOID_PULL = 416, -- violet swirl pulling inward
	EMBER_SIGIL = 417, -- orange warning circle
	FROST_SIGIL = 418, -- teal warning circle
}

SpireSpells.list = {
	-- Shared utilities: every vocation gets them, each at its own level -----------------------------------------
	{ name = "Kindle", words = "kindle", voc = "all", level = { [A] = 8, [M] = 8, [R] = 9, [V] = 10 }, mana = 20, cd = 2, kind = "light", lightLevel = 7, duration = 600, effect = CONST_ME_FIRE_SPARKLES },
	{ name = "Wayfinder", words = "wayfinder", voc = "all", level = { [A] = 10, [M] = 10, [R] = 8, [V] = 8 }, mana = 20, cd = 2, kind = "find_person", effect = CONST_ME_MAGIC_BLUE },
	{ name = "Cleanse", words = "cleanse", voc = "all", level = { [A] = 12, [M] = 10, [R] = 11, [V] = 12 }, mana = 30, cd = 6, kind = "cleanse", effect = CONST_ME_WHITE_SMOKES },
	{ name = "Skystep", words = "skystep", voc = "all", level = { [A] = 12, [M] = 12, [R] = 12, [V] = 14 }, mana = 50, cd = 2, kind = "levitate", effect = CONST_ME_TELEPORT },
	{ name = "Hearth Ration", words = "hearth ration", voc = "all", level = { [A] = 14, [M] = 11, [R] = 14, [V] = 14 }, mana = 120, cd = 2, kind = "food", effect = CONST_ME_MAGIC_GREEN },
	{ name = "Quickstep", words = "quickstep", voc = "all", level = { [A] = 14, [M] = 14, [R] = 10, [V] = 16 }, mana = 60, cd = 2, kind = "haste", speed = 0.3, duration = 30, effect = CONST_ME_WHIRLWIND_BLOW_WHITE },

	-- Vanguard: crimson and gold, steel impacts. Slow burn: sparse early, defensive milestones, late power. ---------
	{ name = "Heavy Strike", words = "heavy strike", voc = { V }, level = 1, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.8, max = 1.5, range = 1, effect = CONST_ME_HITAREA_RED, evolve = { { level = 50, impact2 = CONST_ME_GROUNDSHAKER }, { level = 120, effect = SpireFx.STEEL_ARC, impact2 = CONST_ME_GROUNDSHAKER } } },
	{ name = "Second Wind", words = "second wind", voc = { V }, level = 4, mana = 30, cd = 1, kind = "heal_self", scale = "level", min = 1.0, max = 1.6, base = 20, effect = CONST_ME_OUTBURST_YELLOW },
	{ name = "Shield Bash", words = "shield bash", voc = { V }, level = 12, mana = 25, cd = 8, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.5, max = 0.9, range = 1, push = 1, root = 2, pvpMove = true, effect = CONST_ME_BLOCKHIT, impact2 = CONST_ME_STUN },
	{ name = "Rending Blow", words = "rending blow", voc = { V }, level = 16, mana = 35, cd = 6, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.9, max = 1.6, range = 1, effect = CONST_ME_SLASH, impact2 = CONST_ME_DRAWBLOOD, dot = { type = CONDITION_BLEEDING, ticks = 5, interval = 2000, pct = 0.12 } },
	{ name = "Rally Cry", words = "rally cry", voc = { V }, level = 20, mana = 40, cd = 4, kind = "taunt", radius = 3, cast = CONST_ME_CHIVALRIOUS_CHALLENGE, effect = CONST_ME_SOUND_RED },
	-- PvP (DESIGN 6.7, Jay 2026-11-17): the Vanguard is the one class whose spells move players (pvpMove)
	{ name = "Iron Reach", words = "iron reach", voc = { V }, level = 22, mana = 50, cd = 14, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.2, max = 0.4, range = 5, pull = true, pvpMove = true, shoot = CONST_ANI_WHIRLWINDCLUB, effect = CONST_ME_GROUNDSHAKER },
	{ name = "Charge", words = "charge", voc = { V }, level = 25, mana = 70, cd = 12, kind = "dash", tiles = 3, cast = CONST_ME_BLOODYSTEPS, effect = CONST_ME_GROUNDSHAKER },
	{ name = "Bloodoath Strike", words = "bloodoath strike", voc = { V }, level = 28, mana = 45, cd = 8, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.9, max = 1.5, range = 1, leech = 0.4, effect = CONST_ME_BIG_SCRATCH, impact2 = CONST_ME_DRAWBLOOD },
	{ name = "Iron Hide", words = "iron hide", voc = { V }, level = 30, mana = 80, cd = 20, kind = "dr_self", pct = 30, duration = 6, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	-- the Vanguard's only damaging area spell: adjacent tiles only, about half the damage and half the rate of the others' (docs/design/spells.md)
	{ name = "Whirlwind", words = "whirlwind", voc = { V }, level = 33, mana = 60, cd = 8, kind = "attack_area", area = "ring1", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.4, max = 0.7, cast = CONST_ME_WHIRLWIND_BLOW_WHITE, effect = SpireFx.STEEL_ARC, anim = "spiral", step = 45 },
	{ name = "Counterguard", words = "counterguard", voc = { V }, level = 36, mana = 70, cd = 20, kind = "reflect", pct = 35, duration = 6, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	{ name = "Intimidate", words = "intimidate", voc = { V }, level = 40, mana = 90, cd = 16, kind = "slow_area", radius = 2, duration = 4, cast = CONST_ME_SOUND_RED, effect = CONST_ME_STUN },
	{ name = "Sunder", words = "sunder", voc = { V }, level = 45, mana = 60, cd = 15, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.8, max = 1.3, range = 1, vuln = { pct = 10, duration = 10 }, effect = CONST_ME_HITAREA_ORANGE, impact2 = CONST_ME_STONES },
	{ name = "Battle Hymn", words = "battle hymn", voc = { V }, level = 50, mana = 150, cd = 30, kind = "party_buff", buff = "melee", amount = 10, duration = 120, cast = CONST_ME_OUTBURST_YELLOW, effect = CONST_ME_MAGIC_RED },
	{ name = "Standard of Defiance", words = "standard of defiance", voc = { V }, level = 55, mana = 110, cd = 30, kind = "banner", duration = 8, radius = 4, cast = CONST_ME_CHIVALRIOUS_CHALLENGE, effect = SpireFx.WAR_BANNER },
	{ name = "Guardian Stance", words = "guardian stance", voc = { V }, level = 60, mana = 120, cd = 24, kind = "dr_adjacent", pct = 20, duration = 8, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	{ name = "Recovery", words = "recovery", voc = { V }, level = 70, mana = 120, cd = 2, kind = "heal_self", scale = "level", min = 2.0, max = 3.0, base = 60, cast = CONST_ME_MAGIC_RED, effect = CONST_ME_OUTBURST_YELLOW },
	{ name = "Vault Strike", words = "vault strike", voc = { V }, level = 80, mana = 100, cd = 14, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 1.2, max = 2.0, base = 10, range = 4, dashTo = true, effect = SpireFx.GROUND_CRACK, impact2 = CONST_ME_HITAREA_RED },
	{ name = "Skyrend", words = "skyrend", voc = { V }, level = 90, mana = 160, cd = 12, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 2.2, max = 3.4, base = 20, range = 1, cast = CONST_ME_HITAREA_ORANGE, effect = SpireFx.SKYREND, impact2 = CONST_ME_CRITICAL_DAMAGE },
	{ name = "Iron Will", words = "iron will", voc = { V }, level = 110, mana = 80, cd = 12, kind = "break_free", effect = CONST_ME_MAGIC_RED },
	{ name = "Final Verdict", words = "final verdict", voc = { V }, level = 125, mana = 150, cd = 16, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 1.6, max = 2.4, base = 15, range = 1, execute = { below = 0.3, bonus = 0.6 }, cast = CONST_ME_HITAREA_ORANGE, effect = CONST_ME_FATAL, impact2 = CONST_ME_CRITICAL_DAMAGE },
	{ name = "Bulwark Aura", words = "bulwark aura", voc = { V }, level = 140, mana = 200, cd = 60, kind = "dr_party", pct = 8, duration = 120, radius = 4, cast = CONST_ME_YELLOW_RINGS, effect = CONST_ME_BLOCKHIT },
	-- a second, late area attack (a line, still weak for its level), like the old knights' late sweep
	{ name = "Faultline", words = "faultline", voc = { V }, level = 170, mana = 180, cd = 14, kind = "attack_area", area = "beam", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 0.9, max = 1.4, base = 10, root = 1, anim = "sweep", step = 90, cast = CONST_ME_GROUNDSHAKER, effect = SpireFx.GROUND_CRACK },
	{ name = "Undying Oath", words = "undying oath", voc = { V }, level = 200, mana = 250, cd = 120, kind = "undying", duration = 4, cast = SpireFx.OATH_HALO, effect = CONST_ME_OUTBURST_YELLOW },
	{ name = "Aegis Ascendant", words = "aegis ascendant", voc = { V }, level = 230, mana = 300, cd = 180, kind = "form", duration = 15, dr = 25, buff = "melee", amount = 15, aura = SpireFx.OATH_HALO, pulse = { kind = "taunt", radius = 3, effect = CONST_ME_SOUND_RED }, cast = CONST_ME_DIVINE_EMPOWERMENT },
	{ name = "Mountainbreaker", words = "mountainbreaker", voc = { V }, level = 300, mana = 350, cd = 45, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 3.0, max = 4.6, base = 30, range = 5, dashTo = true, root = 3, effect = SpireFx.SKYREND, impact2 = SpireFx.GROUND_CRACK, ringFx = CONST_ME_GROUNDSHAKER },
	{ name = "Last Bastion", words = "last bastion", voc = { V }, level = 120, mana = 250, cd = 60, kind = "heal_last_stand", scale = "level", min = 1.6, max = 2.4, base = 100, cast = CONST_ME_DIVINE_EMPOWERMENT, effect = CONST_ME_OUTBURST_YELLOW, lostArt = 5 },
	{ name = "Unbroken Line", words = "unbroken line", voc = { V }, level = 250, mana = 400, cd = 90, kind = "dr_party", pct = 15, duration = 10, radius = 4, cast = CONST_ME_CHIVALRIOUS_CHALLENGE, effect = CONST_ME_BLOCKHIT, lostArt = 8 },

	-- Ranger: daylight gold-white and forest green, arrows. Steady: something new every few levels, kiting tools early. -
	{ name = "Piercing Shot", words = "piercing shot", voc = { R }, level = 1, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.8, max = 1.5, shoot = CONST_ANI_SNIPERARROW, effect = CONST_ME_HITAREA_GREEN, evolve = { { level = 50, shoot = CONST_ANI_CRYSTALLINEARROW }, { level = 120, shoot = CONST_ANI_DIAMONDARROW, impact2 = CONST_ME_HOLYDAMAGE } } },
	{ name = "Field Dressing", words = "field dressing", voc = { R }, level = 4, mana = 40, cd = 1, kind = "heal_target", min = 1.2, max = 1.9, base = 15, shoot = CONST_ANI_SMALLHOLY, effect = CONST_ME_SPARKLING },
	{ name = "Double Nock", words = "double nock", voc = { R }, level = 12, mana = 25, cd = 4, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.5, max = 0.9, hits = 2, hitGap = 180, shoot = CONST_ANI_SIMPLEARROW, effect = CONST_ME_HITAREA_GREEN },
	{ name = "Keen Sight", words = "keen sight", voc = { R }, level = 13, mana = 40, cd = 10, kind = "reveal", radius = 6, cast = CONST_ME_OUTBURST_WHITE, effect = CONST_ME_MAGIC_BLUE },
	{ name = "Scatter Shot", words = "scatter shot", voc = { R }, level = 16, mana = 45, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.7, max = 1.3, cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_HITAREA_GREEN, anim = "sweep", step = 70 },
	{ name = "Recoil Shot", words = "recoil shot", voc = { R }, level = 18, mana = 40, cd = 10, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.7, max = 1.2, push = 2, shoot = CONST_ANI_BURSTARROW, effect = CONST_ME_BLOW_GREEN },
	{ name = "Snare", words = "snare", voc = { R }, level = 20, mana = 60, cd = 10, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.2, max = 0.3, range = 7, root = 3, shoot = CONST_ANI_EARTHARROW, effect = CONST_ME_ROOTS },
	{ name = "Ambush Shot", words = "ambush shot", voc = { R }, level = 22, mana = 40, cd = 8, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 1.0, max = 1.6, opener = { bonus = 0.6 }, shoot = CONST_ANI_ONYXARROW, effect = CONST_ME_CLAW_GREEN },
	{ name = "Disengage", words = "disengage", voc = { R }, level = 24, mana = 60, cd = 12, kind = "leap_away", tiles = 2, cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_POFF },
	{ name = "Tracker's Mark", words = "trackers mark", voc = { R }, level = 28, mana = 60, cd = 15, kind = "mark", pct = 10, duration = 15, shoot = CONST_ANI_FLASHARROW, effect = CONST_ME_REDSMOKE },
	{ name = "Caltrops", words = "caltrops", voc = { R }, level = 30, mana = 60, cd = 16, kind = "zone", at = "self", area = "square1", duration = 8, slowZone = true, cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_WOODEN_STAKES },
	{ name = "Swift Foot", words = "swift foot", voc = { R }, level = 32, mana = 100, cd = 2, kind = "haste", speed = 0.7, duration = 22, effect = CONST_ME_WHIRLWIND_BLOW_GREEN },
	{ name = "Breach Arrow", words = "breach arrow", voc = { R }, level = 34, mana = 50, cd = 8, kind = "breach", tiles = 6, shoot = CONST_ANI_SNIPERARROW, effect = CONST_ME_HOLYDAMAGE },
	{ name = "Ricochet", words = "ricochet", voc = { R }, level = 35, mana = 60, cd = 6, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.9, max = 1.4, chain = { jumps = 3, range = 3, falloff = 0.8 }, shoot = CONST_ANI_CRYSTALLINEARROW, effect = CONST_ME_HITAREA_GREEN },
	{ name = "Radiant Shot", words = "radiant shot", voc = { R }, level = 38, mana = 70, cd = 4, kind = "attack_target", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.1, max = 1.8, base = 10, shoot = CONST_ANI_SMALLHOLY, effect = CONST_ME_HOLYDAMAGE },
	{ name = "Mercy Shot", words = "mercy shot", voc = { R }, level = 42, mana = 60, cd = 8, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 1.0, max = 1.6, execute = { below = 0.3, bonus = 0.75 }, shoot = CONST_ANI_TARSALARROW, effect = CONST_ME_FATAL },
	{ name = "Sunburst Volley", words = "sunburst volley", voc = { R }, level = 45, mana = 110, cd = 6, kind = "attack_area", area = "target1", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 0.9, max = 1.5, shoot = CONST_ANI_HOLY, effect = CONST_ME_HOLYAREA, anim = "burst", step = 110 },
	{ name = "Camouflage", words = "camouflage", voc = { R }, level = 50, mana = 120, cd = 30, kind = "invisible", duration = 10, effect = CONST_ME_GREENSMOKE },
	{ name = "Eagle Eye", words = "eagle eye", voc = { R }, level = 55, mana = 180, cd = 60, kind = "party_buff", buff = "crit", amount = 10, duration = 120, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_SPARKLING },
	{ name = "Rapid Volley", words = "rapid volley", voc = { R }, level = 60, mana = 110, cd = 10, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.45, max = 0.7, hits = 5, hitGap = 140, shoot = CONST_ANI_SIMPLEARROW, effect = CONST_ME_HITAREA_GREEN },
	{ name = "Sanctified Ground", words = "sanctified ground", voc = { R }, level = 65, mana = 220, cd = 30, kind = "heal_zone", min = 0.6, max = 1.0, base = 20, radius = 2, duration = 6, cast = CONST_ME_DIVINE_DAZZLE, effect = SpireFx.SUN_SIGIL },
	{ name = "Falling Star", words = "falling star", voc = { R }, level = 72, mana = 150, cd = 14, kind = "attack_area", area = "target1", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.6, max = 2.5, base = 10, delay = 1200, warn = SpireFx.SUN_SIGIL, skyshot = CONST_ANI_HOLY, anim = "burst", step = 90, cast = CONST_ME_DIVINE_DAZZLE, effect = SpireFx.LIGHT_NEEDLES },
	{ name = "Dawnpiercer", words = "dawnpiercer", voc = { R }, level = 80, mana = 160, cd = 10, kind = "attack_area", area = "beam7", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.5, max = 2.4, base = 10, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_HOLYDAMAGE, anim = "sweep", step = 40 },
	{ name = "Scatterwind", words = "scatterwind", voc = { R }, level = 90, mana = 100, cd = 20, kind = "attack_area", area = "ring1", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 0.3, max = 0.5, push = 3, anim = "burst", cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_BLOW_GREEN },
	{ name = "Hunter's Focus", words = "hunters focus", voc = { R }, level = 100, mana = 150, cd = 60, kind = "party_buff", buff = "distance", amount = 15, duration = 20, radius = 0, cast = CONST_ME_DIVINE_EMPOWERMENT, effect = CONST_ME_SPARKLING },
	{ name = "Pinning Volley", words = "pinning volley", voc = { R }, level = 130, mana = 200, cd = 14, kind = "attack_area", area = "wave", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 1.2, max = 1.9, base = 10, root = 2, anim = "sweep", step = 70, cast = CONST_ME_WHIRLWIND_BLOW_GREEN, effect = CONST_ME_WOODEN_STAKES },
	{ name = "Lightrain", words = "lightrain", voc = { R }, level = 160, mana = 300, cd = 15, kind = "attack_area", area = "target2", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 1.6, max = 2.6, base = 20, shoot = CONST_ANI_HOLY, cast = CONST_ME_DIVINE_DAZZLE, effect = SpireFx.LIGHT_NEEDLES, anim = "rain" },
	{ name = "Dawnstrider", words = "dawnstrider", voc = { R }, level = 230, mana = 300, cd = 180, kind = "form", duration = 15, buff = "distance", amount = 15, speed = 0.5, aura = SpireFx.SUN_SIGIL, pulse = { kind = "strike", count = 1, radius = 5, element = COMBAT_HOLYDAMAGE, min = 0.8, max = 1.2, shoot = CONST_ANI_HOLY, effect = SpireFx.LIGHT_NEEDLES }, scale = "distance", cast = CONST_ME_DIVINE_EMPOWERMENT },
	{ name = "Constellation", words = "constellation", voc = { R }, level = 300, mana = 600, cd = 45, kind = "attack_area", area = "target3", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 2.4, max = 3.6, base = 30, delay = 800, warn = SpireFx.SUN_SIGIL, anim = "rain", cast = CONST_ME_DIVINE_DAZZLE, effect = SpireFx.LIGHT_NEEDLES },
	{ name = "Hawk's Path", words = "hawks path", voc = { R }, level = 120, mana = 150, cd = 20, kind = "blink", tiles = 6, cast = CONST_ME_WHIRLWIND_BLOW_WHITE, effect = CONST_ME_OUTBURST_WHITE, lostArt = 5 },
	{ name = "Volley of Dawn", words = "volley of dawn", voc = { R }, level = 250, mana = 500, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_HOLYDAMAGE, scale = "distance", min = 2.6, max = 4.0, base = 30, cast = CONST_ME_DIVINE_DAZZLE, effect = CONST_ME_DIVINE_GRENADE, lostArt = 8, anim = "burst", step = 130 },

	-- Arcanist: ember orange and storm violet. Front-loaded glass cannon: most attacks by 30, big spikes at 55, 80, 100. --
	{ name = "Ember Strike", words = "ember strike", voc = { A }, level = 1, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_FIRE, effect = CONST_ME_FIREATTACK, evolve = { { level = 50, impact2 = CONST_ME_EXPLOSIONHIT }, { level = 120, effect = SpireFx.EMBER_PILLAR, impact2 = CONST_ME_EXPLOSIONHIT } } },
	{ name = "Mending Spark", words = "mending spark", voc = { A }, level = 4, mana = 25, cd = 1, kind = "heal_self", min = 1.0, max = 1.6, base = 10, effect = CONST_ME_PURPLEENERGY },
	{ name = "Volt Strike", words = "volt strike", voc = { A }, level = 12, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_ENERGYDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_ENERGY, effect = CONST_ME_PURPLE_ELECTRIC_SPARK, evolve = { { level = 50, impact2 = CONST_ME_ENERGYHIT }, { level = 120, effect = SpireFx.VIOLET_BOLT, impact2 = CONST_ME_ENERGYHIT } } },
	{ name = "Mana Ward", words = "mana ward", voc = { A }, level = 14, mana = 50, cd = 14, kind = "manashield", duration = 180, effect = CONST_ME_PURPLETELEPORT },
	{ name = "Forked Arc", words = "forked arc", voc = { A }, level = 16, mana = 45, cd = 6, kind = "attack_target", element = COMBAT_ENERGYDAMAGE, min = 0.9, max = 1.5, chain = { jumps = 3, range = 3, falloff = 0.75 }, shoot = CONST_ANI_ENERGY, effect = CONST_ME_PURPLE_ELECTRIC_SPARK },
	{ name = "Fireburst Wave", words = "fireburst wave", voc = { A }, level = 18, mana = 80, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_FIREDAMAGE, min = 1.3, max = 2.1, cast = CONST_ME_ORANGE_ENERGY_SPARK, effect = CONST_ME_FIREAREA, anim = "sweep", step = 80 },
	{ name = "Ember Barrage", words = "ember barrage", voc = { A }, level = 20, mana = 50, cd = 6, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 0.5, max = 0.8, hits = 4, hitGap = 150, shoot = CONST_ANI_FIRE, effect = CONST_ME_FIREATTACK },
	{ name = "Arc Beam", words = "arc beam", voc = { A }, level = 23, mana = 110, cd = 4, kind = "attack_area", area = "beam", element = COMBAT_ENERGYDAMAGE, min = 1.6, max = 2.6, cast = CONST_ME_PURPLE_ELECTRIC_SPARK, effect = CONST_ME_ENERGYHIT, anim = "sweep", step = 45 },
	{ name = "Gale Step", words = "gale step", voc = { A }, level = 26, mana = 100, cd = 2, kind = "haste", speed = 0.7, duration = 22, effect = CONST_ME_PURPLESMOKE },
	{ name = "Conjure Fire Rune", words = "conjure fire rune", voc = { A }, level = 27, mana = 300, cd = 2, kind = "conjure", item = 3191, count = 4, effect = CONST_ME_FIRE_SPARKLES },
	{ name = "Blink", words = "blink", voc = { A }, level = 30, mana = 80, cd = 14, kind = "blink", tiles = 3, cast = CONST_ME_PURPLETELEPORT, effect = CONST_ME_PURPLETELEPORT },
	{ name = "Emberfield", words = "emberfield", voc = { A }, level = 32, mana = 120, cd = 14, kind = "zone", at = "target", area = "target1", duration = 6, element = COMBAT_FIREDAMAGE, min = 0.35, max = 0.6, base = 2, shoot = CONST_ANI_FIRE, effect = SpireFx.EMBER_PILLAR },
	{ name = "Searing Brand", words = "searing brand", voc = { A }, level = 35, mana = 60, cd = 8, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 1.0, max = 1.6, shoot = CONST_ANI_FIRE, effect = CONST_ME_HITBYFIRE, dot = { type = CONDITION_FIRE, ticks = 6, interval = 2000, pct = 0.12 } },
	{ name = "Conjure Barrier Rune", words = "conjure barrier rune", voc = { A }, level = 34, mana = 500, cd = 2, kind = "conjure", item = 3180, count = 3, effect = CONST_ME_PURPLEENERGY },
	{ name = "Repulse", words = "repulse", voc = { A }, level = 38, mana = 90, cd = 12, kind = "attack_area", area = "ring1", element = COMBAT_ENERGYDAMAGE, min = 0.8, max = 1.3, push = 2, anim = "burst", cast = CONST_ME_PURPLEENERGY, effect = CONST_ME_ENERGYHIT },
	{ name = "Gravity Well", words = "gravity well", voc = { A }, level = 42, mana = 120, cd = 20, kind = "gravity", radius = 3, tiles = 2, duration = 2, shoot = CONST_ANI_ENERGYBALL, effect = SpireFx.VOID_PULL },
	{ name = "Tailwind", words = "tailwind", voc = { A }, level = 40, mana = 150, cd = 20, kind = "party_haste", speed = 0.4, duration = 10, radius = 5, cast = CONST_ME_WHIRLWIND_BLOW_WHITE, effect = CONST_ME_PURPLESMOKE },
	{ name = "Conjure Strike Rune", words = "conjure strike rune", voc = { A }, level = 45, mana = 600, cd = 2, kind = "conjure", item = 3155, count = 3, effect = CONST_ME_PURPLEENERGY },
	{ name = "Summon Ember Sprite", words = "summon ember sprite", voc = { A }, level = 50, mana = 300, cd = 30, kind = "summon", monster = "Ember Sprite", effect = CONST_ME_ORANGETELEPORT },
	{ name = "Stormcall", words = "stormcall", voc = { A }, level = 55, mana = 300, cd = 16, kind = "attack_area", area = "ring2", element = COMBAT_ENERGYDAMAGE, min = 2.2, max = 3.4, base = 10, cast = CONST_ME_STORM, effect = SpireFx.VIOLET_BOLT, anim = "rain" },
	{ name = "Arcane Empower", words = "arcane empower", voc = { A }, level = 60, mana = 220, cd = 60, kind = "party_buff", buff = "magic", amount = 10, duration = 120, cast = CONST_ME_PURPLETELEPORT, effect = CONST_ME_PURPLEENERGY },
	{ name = "Skybrand", words = "skybrand", voc = { A }, level = 70, mana = 220, cd = 14, kind = "attack_area", area = "target1", element = COMBAT_FIREDAMAGE, min = 2.4, max = 3.6, base = 15, delay = 1200, warn = SpireFx.EMBER_SIGIL, anim = "burst", step = 90, cast = CONST_ME_ORANGE_ENERGY_SPARK, effect = SpireFx.METEOR },
	{ name = "Inferno Core", words = "inferno core", voc = { A }, level = 80, mana = 400, cd = 20, kind = "attack_area", area = "ring2", element = COMBAT_FIREDAMAGE, min = 2.6, max = 4.0, base = 20, cast = CONST_ME_EXPLOSIONAREA, effect = SpireFx.EMBER_PILLAR, anim = "burst", step = 130 },
	{ name = "Firewake", words = "firewake", voc = { A }, level = 90, mana = 150, cd = 16, kind = "trail_dash", tiles = 4, duration = 4, element = COMBAT_FIREDAMAGE, min = 0.4, max = 0.7, base = 2, cast = CONST_ME_ORANGETELEPORT, effect = SpireFx.EMBER_PILLAR },
	{ name = "Cinder Lance", words = "cinder lance", voc = { A }, level = 100, mana = 250, cd = 30, kind = "attack_target", element = COMBAT_FIREDAMAGE, min = 3.2, max = 4.8, base = 30, shoot = CONST_ANI_EXPLOSION, effect = CONST_ME_EXPLOSIONHIT, impact2 = CONST_ME_FIRE_SPARKLES },
	{ name = "Arc Cataclysm", words = "arc cataclysm", voc = { A }, level = 130, mana = 500, cd = 12, kind = "attack_area", area = "bigbeam", element = COMBAT_ENERGYDAMAGE, min = 2.4, max = 3.6, base = 20, cast = CONST_ME_STORM, effect = SpireFx.VIOLET_BOLT, anim = "sweep", step = 60 },
	{ name = "Storm Lash", words = "storm lash", voc = { A }, level = 160, mana = 350, cd = 16, kind = "attack_target", element = COMBAT_ENERGYDAMAGE, min = 2.0, max = 3.0, base = 20, chain = { jumps = 6, range = 4, falloff = 1.0 }, shoot = CONST_ANI_ENERGYBALL, effect = SpireFx.VIOLET_BOLT },
	{ name = "Stormheart", words = "stormheart", voc = { A }, level = 230, mana = 400, cd = 180, kind = "form", duration = 15, buff = "magic", amount = 15, aura = CONST_ME_PURPLEENERGY, pulse = { kind = "strike", count = 2, radius = 4, element = COMBAT_ENERGYDAMAGE, min = 0.9, max = 1.4, effect = SpireFx.VIOLET_BOLT }, cast = CONST_ME_STORM },
	{ name = "Worldfire", words = "worldfire", voc = { A }, level = 300, mana = 800, cd = 45, kind = "attack_area", area = "target3", element = COMBAT_FIREDAMAGE, min = 3.4, max = 5.2, base = 40, delay = 1000, warn = SpireFx.EMBER_SIGIL, anim = "rain", cast = CONST_ME_EXPLOSIONAREA, effect = SpireFx.METEOR },
	{ name = "Meteor Rain", words = "meteor rain", voc = { A }, level = 120, mana = 600, cd = 40, kind = "attack_area", area = "target2", element = COMBAT_FIREDAMAGE, min = 3.2, max = 5.0, base = 30, shoot = CONST_ANI_FIRE, cast = CONST_ME_EXPLOSIONAREA, effect = SpireFx.METEOR, lostArt = 5, anim = "rain", delay = 900, warn = SpireFx.EMBER_SIGIL },
	{ name = "Mirror Image", words = "mirror image", voc = { A }, level = 250, mana = 300, cd = 60, kind = "decoy", monster = "Mirror Image", duration = 5, effect = CONST_ME_PURPLETELEPORT, lostArt = 8 },

	-- Mystic: frost teal and living green. Healer's rhythm: heals first, party tools mid-game, damage a step behind the Arcanist. -
	{ name = "Frost Strike", words = "frost strike", voc = { M }, level = 1, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_ICEDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_ICE, effect = CONST_ME_ICEATTACK, evolve = { { level = 50, impact2 = CONST_ME_ICEAREA }, { level = 120, effect = SpireFx.ICE_SPIRES, impact2 = CONST_ME_ICEAREA } } },
	{ name = "Dewfall", words = "dewfall", voc = { M }, level = 4, mana = 25, cd = 1, kind = "heal_self", min = 1.1, max = 1.8, base = 12, effect = CONST_ME_GREEN_RINGS },
	{ name = "Sapdrain", words = "sapdrain", voc = { M }, level = 11, mana = 25, cd = 6, kind = "attack_target", element = COMBAT_EARTHDAMAGE, min = 0.7, max = 1.2, leech = 0.5, shoot = CONST_ANI_SMALLEARTH, effect = CONST_ME_SMALLPLANTS },
	{ name = "Thorn Strike", words = "thorn strike", voc = { M }, level = 13, mana = 20, cd = 2, kind = "attack_target", element = COMBAT_EARTHDAMAGE, min = 1.2, max = 2.0, shoot = CONST_ANI_EARTH, effect = CONST_ME_CARNIPHILA, evolve = { { level = 50, impact2 = CONST_ME_PLANTATTACK }, { level = 120, effect = SpireFx.THORN_BURST } } },
	{ name = "Mend Other", words = "mend other", voc = { M }, level = 16, mana = 70, cd = 1, kind = "heal_target", min = 1.6, max = 2.6, base = 20, shoot = CONST_ANI_GREENSTAR, effect = CONST_ME_MAGIC_GREEN },
	{ name = "Hailshards", words = "hailshards", voc = { M }, level = 18, mana = 45, cd = 6, kind = "attack_target", element = COMBAT_ICEDAMAGE, min = 0.55, max = 0.9, hits = 3, hitGap = 160, shoot = CONST_ANI_SMALLICE, effect = CONST_ME_ICEATTACK },
	{ name = "Frost Wave", words = "frost wave", voc = { M }, level = 21, mana = 70, cd = 4, kind = "attack_area", area = "wave", element = COMBAT_ICEDAMAGE, min = 1.0, max = 1.7, slow = true, cast = CONST_ME_ICETORNADO, effect = CONST_ME_ICEAREA, anim = "sweep", step = 80 },
	{ name = "Conjure Healing Rune", words = "conjure healing rune", voc = { M }, level = 24, mana = 400, cd = 2, kind = "conjure", item = 3160, count = 1, effect = CONST_ME_GREEN_RINGS },
	{ name = "Bramble Patch", words = "bramble patch", voc = { M }, level = 26, mana = 100, cd = 14, kind = "zone", at = "target", area = "target1", duration = 8, element = COMBAT_EARTHDAMAGE, min = 0.3, max = 0.5, base = 2, slowZone = true, shoot = CONST_ANI_EARTH, effect = SpireFx.THORN_BURST },
	{ name = "Purify", words = "purify", voc = { M }, level = 28, mana = 90, cd = 6, kind = "purify", radius = 4, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_WHITE_SMOKES },
	{ name = "Bloomburst", words = "bloomburst", voc = { M }, level = 30, mana = 90, cd = 8, kind = "heal_burst", min = 1.2, max = 2.0, base = 15, element = COMBAT_EARTHDAMAGE, burst = 0.5, shoot = CONST_ANI_GREENSTAR, effect = SpireFx.BLOOM, burstEffect = CONST_ME_PLANTATTACK },
	{ name = "Vinewall", words = "vinewall", voc = { M }, level = 34, mana = 120, cd = 16, kind = "vine_wall", width = 3, ahead = 2, effect = SpireFx.THORN_BURST },
	{ name = "Barkskin", words = "barkskin", voc = { M }, level = 32, mana = 150, cd = 30, kind = "dr_party", pct = 10, duration = 120, radius = 4, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_SMALLPLANTS },
	{ name = "Mass Mend", words = "mass mend", voc = { M }, level = 36, mana = 160, cd = 2, kind = "heal_party", min = 1.0, max = 1.6, base = 20, radius = 4, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_MAGIC_GREEN },
	{ name = "Rimebind", words = "rimebind", voc = { M }, level = 38, mana = 80, cd = 12, kind = "attack_target", element = COMBAT_ICEDAMAGE, min = 0.6, max = 1.0, root = 3, shoot = CONST_ANI_ICE, effect = CONST_ME_ICEATTACK, impact2 = CONST_ME_GIANTICE },
	{ name = "Rejuvenate", words = "rejuvenate", voc = { M }, level = 42, mana = 100, cd = 6, kind = "hot_target", duration = 10, shoot = CONST_ANI_GREENSTAR, effect = CONST_ME_PULSE_GREEN },
	{ name = "Tidecrash", words = "tidecrash", voc = { M }, level = 45, mana = 110, cd = 14, kind = "attack_area", area = "wave", element = COMBAT_ICEDAMAGE, min = 0.8, max = 1.3, push = 2, anim = "sweep", step = 90, cast = CONST_ME_WATERSPLASH, effect = CONST_ME_WATERSPLASH },
	{ name = "Conjure Binding Rune", words = "conjure binding rune", voc = { M }, level = 48, mana = 500, cd = 2, kind = "conjure", item = 3165, count = 1, effect = CONST_ME_ROOTS },
	{ name = "Summon Wolf Companion", words = "summon wolf companion", voc = { M }, level = 50, mana = 300, cd = 30, kind = "summon", monster = "Wolf Companion", effect = CONST_ME_GREENSMOKE },
	{ name = "Thornfield", words = "thornfield", voc = { M }, level = 55, mana = 300, cd = 16, kind = "attack_area", area = "ring2", element = COMBAT_EARTHDAMAGE, min = 1.8, max = 2.9, base = 10, cast = CONST_ME_BIGPLANTS, effect = SpireFx.THORN_BURST, anim = "burst", step = 130 },
	{ name = "Linked Mend", words = "linked mend", voc = { M }, level = 60, mana = 140, cd = 4, kind = "heal_chain", min = 1.4, max = 2.2, base = 20, jumps = 3, range = 4, falloff = 0.8, shoot = CONST_ANI_GREENSTAR, effect = SpireFx.BLOOM },
	{ name = "Lifeward", words = "lifeward", voc = { M }, level = 65, mana = 120, cd = 12, kind = "dr_target", pct = 25, duration = 6, shoot = CONST_ANI_GREENSTAR, effect = SpireFx.LEAF_WARD },
	{ name = "Lifeseed", words = "lifeseed", voc = { M }, level = 75, mana = 250, cd = 120, kind = "seed", duration = 20, pct = 35, shoot = CONST_ANI_GREENSTAR, effect = SpireFx.LEAF_WARD },
	{ name = "Glacier Core", words = "glacier core", voc = { M }, level = 80, mana = 400, cd = 20, kind = "attack_area", area = "ring2", element = COMBAT_ICEDAMAGE, min = 2.2, max = 3.4, base = 20, cast = CONST_ME_GIANTICE, effect = SpireFx.ICE_SPIRES, anim = "burst", step = 130 },
	{ name = "Icefall", words = "icefall", voc = { M }, level = 90, mana = 280, cd = 16, kind = "attack_area", area = "target2", element = COMBAT_ICEDAMAGE, min = 2.0, max = 3.2, base = 15, delay = 900, warn = SpireFx.FROST_SIGIL, anim = "rain", cast = CONST_ME_ICETORNADO, effect = SpireFx.ICE_SPIRES },
	{ name = "Verdant Renewal", words = "verdant renewal", voc = { M }, level = 100, mana = 400, cd = 4, kind = "heal_party", min = 2.0, max = 3.0, base = 40, radius = 5, cast = CONST_ME_BIGPLANTS, effect = SpireFx.BLOOM },
	{ name = "Mana Bloom", words = "mana bloom", voc = { M }, level = 130, mana = 200, cd = 60, kind = "mana_party", duration = 30, radius = 5, cast = CONST_ME_GREEN_RINGS, effect = CONST_ME_MAGIC_BLUE },
	{ name = "Overgrowth", words = "overgrowth", voc = { M }, level = 160, mana = 450, cd = 30, kind = "attack_area", area = "ring3", element = COMBAT_EARTHDAMAGE, min = 2.4, max = 3.6, base = 20, root = 2, anim = "burst", step = 120, cast = CONST_ME_BIGPLANTS, effect = SpireFx.THORN_BURST },
	{ name = "Wildheart", words = "wildheart", voc = { M }, level = 230, mana = 400, cd = 180, kind = "form", duration = 16, dr = 10, aura = SpireFx.BLOOM, pulse = { kind = "heal", every = 2, radius = 4, min = 0.8, max = 1.2, base = 20, effect = CONST_ME_MAGIC_GREEN }, cast = CONST_ME_BIGPLANTS },
	{ name = "Worldroot", words = "worldroot", voc = { M }, level = 300, mana = 700, cd = 90, kind = "heal_party", min = 3.0, max = 4.4, base = 60, radius = 6, ward = { pct = 30, duration = 6 }, purify = true, cast = CONST_ME_BIGPLANTS, effect = SpireFx.BLOOM },
	{ name = "Wellspring", words = "wellspring", voc = { M }, level = 120, mana = 400, cd = 45, kind = "heal_zone", min = 1.0, max = 1.6, base = 40, radius = 3, duration = 8, cast = CONST_ME_WATERSPLASH, effect = CONST_ME_PULSE_GREEN, lostArt = 5 },
	{ name = "Winter's Breath", words = "winters breath", voc = { M }, level = 250, mana = 600, cd = 40, kind = "attack_area", area = "ring2", element = COMBAT_ICEDAMAGE, min = 3.2, max = 5.0, base = 30, cast = CONST_ME_GIANTICE, effect = SpireFx.ICE_SPIRES, lostArt = 8, anim = "burst", step = 150 },
	-- Style abilities (gear progression spec 4.2): learned when the class's Mastery reaches 10, never by level alone.
	{ name = "Hearthbreaker", words = "hearthbreaker", voc = { V }, level = 10, style = 1, mana = 60, cd = 12, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "melee", min = 1.8, max = 2.6, range = 1, vuln = { pct = 10, duration = 6 }, cast = CONST_ME_GROUNDSHAKER, effect = SpireFx.GROUND_CRACK },
	{ name = "Truesight Arrow", words = "truesight arrow", voc = { R }, level = 10, style = 1, mana = 50, cd = 10, kind = "attack_target", element = COMBAT_PHYSICALDAMAGE, scale = "distance", min = 2.0, max = 3.0, shoot = CONST_ANI_SNIPERARROW, effect = CONST_ME_HITAREA_GREEN, execute = { below = 0.3, bonus = 0.5 } },
	{ name = "Ember Crown", words = "ember crown", voc = { A }, level = 10, style = 1, mana = 120, cd = 12, kind = "attack_area", area = "ring2", element = COMBAT_FIREDAMAGE, min = 1.4, max = 2.2, cast = CONST_ME_ORANGE_ENERGY_SPARK, effect = CONST_ME_FIREAREA, anim = "burst", step = 90 },
	{ name = "Verdant Surge", words = "verdant surge", voc = { M }, level = 10, style = 1, mana = 140, cd = 12, kind = "heal_party", min = 1.4, max = 2.2, base = 30, radius = 4, cast = CONST_ME_BIGPLANTS, effect = CONST_ME_MAGIC_GREEN },
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
	if row.kind == "attack_target" or row.kind == "attack_area" or row.kind == "trail_dash" or (row.kind == "zone" and row.element) then
		return "attack"
	end
	if row.kind:find("heal") then
		return "healing"
	end
	return "support"
end

-- Pure: is this an attack that needs the engine's "aggressive" rules (no casting in safe zones, PvP checks)?
function SpireSpells.aggressive(row)
	local k = row.kind
	return SpireSpells.group(row) == "attack" or k == "root" or k == "mark" or k == "pull_target" or k == "gravity" or k == "vine_wall" or k == "breach"
end

-- Area shapes, drawn facing north with the caster at the bottom (2 or 3 marks the centre; 3 = the centre is hit too).
SpireSpells.AREAS = {
	wave = { { 1, 1, 1 }, { 1, 1, 1 }, { 0, 1, 0 }, { 0, 2, 0 } },
	beam = { { 1 }, { 1 }, { 1 }, { 1 }, { 1 }, { 2 } },
	beam7 = { { 1 }, { 1 }, { 1 }, { 1 }, { 1 }, { 1 }, { 1 }, { 2 } },
	bigbeam = { { 1, 1, 1 }, { 1, 1, 1 }, { 1, 1, 1 }, { 1, 1, 1 }, { 0, 1, 0 }, { 0, 1, 0 }, { 0, 2, 0 } },
	ring1 = { { 1, 1, 1 }, { 1, 2, 1 }, { 1, 1, 1 } },
	ring2 = { { 0, 1, 1, 1, 0 }, { 1, 1, 1, 1, 1 }, { 1, 1, 2, 1, 1 }, { 1, 1, 1, 1, 1 }, { 0, 1, 1, 1, 0 } },
	ring3 = { { 0, 0, 1, 1, 1, 0, 0 }, { 0, 1, 1, 1, 1, 1, 0 }, { 1, 1, 1, 1, 1, 1, 1 }, { 1, 1, 1, 2, 1, 1, 1 }, { 1, 1, 1, 1, 1, 1, 1 }, { 0, 1, 1, 1, 1, 1, 0 }, { 0, 0, 1, 1, 1, 0, 0 } },
	square1 = { { 1, 1, 1 }, { 1, 3, 1 }, { 1, 1, 1 } },
	-- centred on the target (needs a target)
	target1 = { { 1, 1, 1 }, { 1, 3, 1 }, { 1, 1, 1 } },
	target2 = { { 0, 1, 1, 1, 0 }, { 1, 1, 1, 1, 1 }, { 1, 1, 3, 1, 1 }, { 1, 1, 1, 1, 1 }, { 0, 1, 1, 1, 0 } },
	target3 = { { 0, 0, 1, 1, 1, 0, 0 }, { 0, 1, 1, 1, 1, 1, 0 }, { 1, 1, 1, 1, 1, 1, 1 }, { 1, 1, 1, 3, 1, 1, 1 }, { 1, 1, 1, 1, 1, 1, 1 }, { 0, 1, 1, 1, 1, 1, 0 }, { 0, 0, 1, 1, 1, 0, 0 } },
}
SpireSpells.DIRECTIONAL = { wave = true, beam = true, beam7 = true, bigbeam = true }
SpireSpells.ON_TARGET = { target1 = true, target2 = true, target3 = true }

-- Pure: the tiles of an area as offsets from its centre, turned to face `dir` (0 north, 1 east, 2 south, 3 west).
-- Each entry: { dx, dy, ring = distance from the centre, row = distance in front of the caster }.
function SpireSpells.areaOffsets(areaName, dir)
	local grid = SpireSpells.AREAS[areaName]
	local cx, cy
	for y, line in ipairs(grid) do
		for x, v in ipairs(line) do
			if v >= 2 then
				cx, cy = x, y
			end
		end
	end
	local out = {}
	for y, line in ipairs(grid) do
		for x, v in ipairs(line) do
			if v == 1 or v == 3 then
				local dx, dy = x - cx, y - cy
				local rx, ry = dx, dy
				if dir == 1 then
					rx, ry = -dy, dx
				elseif dir == 2 then
					rx, ry = -dx, -dy
				elseif dir == 3 then
					rx, ry = dy, -dx
				end
				table.insert(out, { dx = rx, dy = ry, ring = math.max(math.abs(dx), math.abs(dy)), row = -dy })
			end
		end
	end
	return out
end

-- Pure: split an area's tiles into the stages of its animation. Returns a list of stages (each a list of offsets)
-- and the milliseconds between stages. rnd(n) returns 1..n (math.random in the game, fixed in tests).
function SpireSpells.stages(row, dir, rnd)
	local tiles = SpireSpells.areaOffsets(row.area, dir or 0)
	local anim = row.anim
	if not anim then
		return { tiles }, 0
	end
	local stages = {}
	local function put(i, t)
		stages[i] = stages[i] or {}
		table.insert(stages[i], t)
	end
	if anim == "burst" then
		for _, t in ipairs(tiles) do
			put(t.ring + 1, t)
		end
	elseif anim == "sweep" then
		for _, t in ipairs(tiles) do
			put(math.max(1, t.row), t)
		end
	elseif anim == "spiral" then
		table.sort(tiles, function(a, b)
			return math.atan2(a.dx, -a.dy) % (2 * math.pi) < math.atan2(b.dx, -b.dy) % (2 * math.pi)
		end)
		for i, t in ipairs(tiles) do
			put(i, t)
		end
	elseif anim == "rain" then
		for i = #tiles, 2, -1 do
			local j = rnd(i)
			tiles[i], tiles[j] = tiles[j], tiles[i]
		end
		local per = math.max(1, math.ceil(#tiles / 8))
		for i, t in ipairs(tiles) do
			put(math.ceil(i / per), t)
		end
	end
	-- close gaps (a shape may have no tile on some ring or row)
	local packed = {}
	local last = 0
	for i in pairs(stages) do
		last = math.max(last, i)
	end
	for i = 1, last do
		if stages[i] then
			table.insert(packed, stages[i])
		end
	end
	return packed, row.step or (anim == "rain" and 110 or 100)
end

-- Pure: how many tiles an area covers (used by the balance test)
function SpireSpells.areaSize(areaName)
	return #SpireSpells.areaOffsets(areaName, 0)
end

-- Pure: the look of a spell for a caster of this level (row.evolve upgrades the cast/shoot/effect/impact2 fields)
function SpireSpells.visuals(row, level)
	local v = { cast = row.cast, shoot = row.shoot, effect = row.effect, impact2 = row.impact2 }
	for _, step in ipairs(row.evolve or {}) do
		if level >= step.level then
			for _, k in ipairs({ "cast", "shoot", "effect", "impact2" }) do
				if step[k] then
					v[k] = step[k]
				end
			end
		end
	end
	return v
end

-- Pure: extra damage share from a row's execute / opener riders, for a target at this health share (0..1)
function SpireSpells.riderBonus(row, healthShare)
	local bonus = 0
	if row.execute and healthShare <= row.execute.below then
		bonus = bonus + row.execute.bonus
	end
	if row.opener and healthShare >= 1 then
		bonus = bonus + row.opener.bonus
	end
	return bonus
end

-- Elemental Clash (docs/design/spells.md 3.5): a spell leaves its element on a monster for a few seconds; the next
-- spell of a DIFFERENT element (from anyone) clashes with it for extra damage and uses the mark up.
-- Physical spells and weapon arts never leave a mark, but they do set off a clash.
SpireClash = { BONUS_PCT = 25, SECONDS = 8, state = {} } -- creatureId -> { el, untilTime }
SpireClash.NAMES = {
	["energy+fire"] = "Flashfire", ["fire+ice"] = "Steamburst", ["earth+fire"] = "Wildfire", ["fire+holy"] = "Sunflare",
	["energy+ice"] = "Shatterstorm", ["earth+energy"] = "Groundstrike", ["energy+holy"] = "Skyfire",
	["earth+ice"] = "Rimethorn", ["holy+ice"] = "Prism", ["earth+holy"] = "Blossom",
}

-- Pure: what happens when damage of element `el` ("fire", "energy", "ice", "earth", "holy", "physical" or nil for
-- anything else) lands on a creature whose current mark is `mark` (or nil).
-- Returns bonusPct, newMark (false = clear it, nil = leave it), clashName.
function SpireClash.resolve(mark, el)
	if not el then
		return 0, nil, nil
	end
	if mark and mark ~= el then
		local a, b = mark, el
		if a > b then
			a, b = b, a
		end
		return SpireClash.BONUS_PCT, false, SpireClash.NAMES[a .. "+" .. b] or "Breaker"
	end
	if el == "physical" then
		return 0, nil, nil
	end
	return 0, el, nil
end

-- Speed changes (haste, slows, roots). Canary's speed formula gives the NEW speed, not the change:
--   new speed = a * (base speed - 40) + b,   and the engine never lets a creature go below speed 40.
-- So "pct faster" (0.3 = 30% faster, -0.4 = 40% slower) is a = b / 40 = 1 + pct. Writing the change instead
-- (a = 0.3) made Quickstep leave you at a third of your speed and every slow freeze its target (fixed 2026-11-17).
function SpireSpells.speedFormula(pct)
	local m = 1 + pct
	return m, 40 * m, m, 40 * m
end

-- Pure: the speed a creature with this base speed ends up with (what the engine will compute), for tests
function SpireSpells.speedAfter(base, pct)
	local m = 1 + pct
	return math.max(40, math.floor(m * (base - 40) + 40 * m))
end

-- set a speed condition (CONDITION_HASTE or CONDITION_PARALYZE) to pct faster or slower
function SpireSpells.setSpeed(condition, pct)
	condition:setFormula(SpireSpells.speedFormula(pct))
	return condition
end

-- PvP rules for spells (DESIGN 6.7, Jay 2026-11-17: the proven Tibia core plus terrain and counters) ------------
SpireSpells.PVP = {
	ROOT_IMMUNE = 4, -- seconds after a root or slow ends before the same player can be held again
	RIDER_SHARE = 0.5, -- finishers and openers give half their bonus against players
}

-- Pure: how long a root or slow holds. Monsters: the full time. Players: half (at least 1 s), never again within
-- ROOT_IMMUNE seconds after the last one ended; in a Wild PvP arena event, the full time with no immunity.
-- Returns seconds (0 = immune) and the new immunity end (nil = unchanged).
function SpireSpells.holdSeconds(isPlayer, seconds, heldUntil, now, wild)
	if not isPlayer or wild then
		return seconds, nil
	end
	if heldUntil and heldUntil > now then
		return 0, nil
	end
	local secs = math.max(1, math.floor(seconds / 2))
	return secs, now + secs + SpireSpells.PVP.ROOT_IMMUNE
end

-- Pure: a finisher or opener bonus, weaker against players
function SpireSpells.pvpBonus(bonus, targetIsPlayer)
	return targetIsPlayer and bonus * SpireSpells.PVP.RIDER_SHARE or bonus
end

-- Is a Wild PvP arena event (every push, pull, slow and root at full strength on players) running at this spot?
function SpireSpells.wildAt(pos)
	local cur = SpireArena and SpireArena.current
	return cur ~= nil and cur.phase == "running" and SpireArena.KINDS[cur.kind].wild == true and SpirePvP ~= nil and SpirePvP.zoneAt(pos) == "arena"
end

-- Walls: the Mystic's vines (fire burns them) and the Arcanist's barrier (Breach Arrow breaks either early)
SpireSpells.VINES = { ITEM_WILDGROWTH, ITEM_WILDGROWTH_SAFE }
SpireSpells.BARRIERS = { ITEM_MAGICWALL, ITEM_MAGICWALL_SAFE }

-- remove the first item with one of these ids from a tile; true if one was there
function SpireSpells.removeFrom(pos, ids)
	local tile = Tile(pos)
	if not tile then
		return false
	end
	for _, id in ipairs(ids) do
		local it = tile:getItemById(id)
		if it then
			it:remove()
			return true
		end
	end
	return false
end

function SpireSpells.burnVines(pos)
	if SpireSpells.removeFrom(pos, SpireSpells.VINES) then
		pos:sendMagicEffect(CONST_ME_FIREAREA)
		return true
	end
	return false
end

-- Breach Arrow: the first vine or barrier within `tiles` straight ahead breaks. Returns where, or nil.
function SpireSpells.breakFirstWall(from, dir, tiles)
	local pos = Position(from)
	for _ = 1, tiles do
		pos:getNextPosition(dir)
		local tile = Tile(pos)
		if not tile then
			return nil
		end
		if SpireSpells.removeFrom(pos, SpireSpells.VINES) or SpireSpells.removeFrom(pos, SpireSpells.BARRIERS) then
			return pos
		end
		if tile:hasProperty(CONST_PROP_BLOCKPROJECTILE) then
			return nil
		end
	end
	return nil
end

-- Pure: the tiles of a Vinewall: `width` tiles across, `ahead` tiles in front of you (dir 0 N, 1 E, 2 S, 3 W)
function SpireSpells.wallTiles(x, y, dir, width, ahead)
	local fx, fy = ({ [0] = 0, 1, 0, -1 })[dir], ({ [0] = -1, 0, 1, 0 })[dir]
	local sx, sy = -fy, fx
	local half = math.floor(width / 2)
	local out = {}
	for i = -half, width - 1 - half do
		table.insert(out, { x = x + fx * ahead + sx * i, y = y + fy * ahead + sy * i })
	end
	return out
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
		if not row.lostArt and not row.style and SpireSpells.allowed(row, baseVocation) and SpireSpells.levelFor(row, baseVocation) == level then
			table.insert(out, row)
		end
	end
	return out
end

-- Pure: the next level above `level` at which this vocation learns something, and the names it learns then
function SpireSpells.nextUnlock(level, baseVocation)
	local best, names = nil, {}
	for _, row in ipairs(SpireSpells.list) do
		if not row.lostArt and not row.style and SpireSpells.allowed(row, baseVocation) then
			local l = SpireSpells.levelFor(row, baseVocation)
			if l > level and (not best or l < best) then
				best, names = l, { row.name }
			elseif l == best then
				table.insert(names, row.name)
			end
		end
	end
	return best, names
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
SpireBuffs = { reduce = {}, mark = {}, undying = {}, reflect = {}, seed = {}, held = {} } -- creatureId -> { pct, untilTime }; held: time until a player can be rooted again

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

-- G4 (Grok playtest, 2026-11-24): saying a target spell with nothing targeted did nothing at all, not even a message.
-- Talk actions are checked before spells, so each target spell gets one: no target -> a clear line and no cast;
-- a target -> carry on to the spell (return true). Called from the spell registration scripts.
SpireSpells.hinted = SpireSpells.hinted or {} -- first word -> { full spell words = true }

-- Pure: is `said` (lower case, spaces squeezed) one of the target spells in `set`?
function SpireSpells.isHinted(set, said)
	return set ~= nil and set[said] == true
end

function SpireSpells.needTargetHint(words)
	words = words:lower()
	local first = words:match("^(%S+)")
	if SpireSpells.hinted[first] then
		SpireSpells.hinted[first][words] = true
		return
	end
	SpireSpells.hinted[first] = { [words] = true }
	-- the engine matches a talk action by the first word said; the rest arrives as `param`
	local ta = TalkAction(first)
	function ta.onSay(player, w, param)
		local said = (first .. " " .. (param or "")):lower():gsub("%s+", " "):gsub("%s$", "")
		if not SpireSpells.isHinted(SpireSpells.hinted[first], said) or player:getTarget() then
			return true -- not a target spell, or a target is set: carry on (chat or the spell)
		end
		player:sendTextMessage(MESSAGE_STATUS, "You need a target: click a monster first (or pick it in the Battle List), then use " .. said .. ".")
		return false
	end
	ta:separator(" ")
	ta:groupType("normal")
	ta:register()
end
