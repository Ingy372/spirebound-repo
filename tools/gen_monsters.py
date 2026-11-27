#!/usr/bin/env python3
"""Writes Spirebound monster files (Canary Lua) from the table below (roadmap 1.13).
One table, many files: never hand-edit server/data-spirebound/monster/*.lua; change the table and rerun.

Looks are PLACEHOLDERS (base Tibia outfits) until Jay's Grok art arrives (ART_REQUESTS.md).
Usage: python3 tools/gen_monsters.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "server" / "data-spirebound" / "monster"

GOLD, PLAT = 3031, 3035

# name: dict(desc, look=(type, head, body, legs, feet, addons), corpse, hp, xp, speed, race, attacks, armor, defense,
#            loot=[(id, chance per 100000, maxCount)], dist (keep-away distance), summons, heal, boss, voices, elements)
MONSTERS = {
    # ---------------------------------------------------------------- Floor 1, starter fields (Guarded)
    "Field Rat": dict(desc="a field rat", look=(56,), corpse=5964, hp=20, xp=6, speed=75, race="blood",
                      attacks=[("melee", 0, -8)], armor=1, defense=2, run=4,  # F1-10: bolts when nearly dead
                      loot=[(GOLD, 70000, 4), (3607, 30000, 1), (9668, 15000, 1)], voices=["Squeak!"],
                      events=["SpireRatSteal", "SpireRatStealDeath"]),  # F1-10: snatches coins and runs
    # the tutorial pen's rats: weak on purpose, so the very first fight can't kill a level 1 with a practice club
    # (2026-11-12 playthrough: three Field Rats killed a new character in the pen)
    # G7 (Q52, 2026-11-25): 1 experience. The engine adds +50% below level 50 and +50% for fresh stamina on top of the
    # 10x stage, so 6 took a new character from level 1 to 4 in three rats. Now the yard ends at level 2.
    "Pen Rat": dict(desc="a pen rat", look=(56,), corpse=5964, hp=12, xp=1, speed=70, race="blood",
                    attacks=[("melee", 0, -3)], armor=0, defense=0,
                    loot=[(3607, 100000, 1), (GOLD, 80000, 3)], voices=["Squeak?"]),  # cheese every time: the yard's loot gate needs something to take
    # The Proving's one-person boss (G2, Jay 2026-11-24): a new character's first fight with its new spells. Gentle on
    # purpose: a slow bite, and every few seconds a telegraphed stomp (red smoke first) that teaches stepping aside.
    # It can't kill you: the Proving pulls you out at 1 health (scripts/spirebound/proving.lua). Placeholder look.
    # G7: 6 experience (was 60 = about 1,350 with the engine's bonuses, level 3 to 5 in one fight); the Proving ends at level 3.
    "Bramblejaw": dict(desc="Bramblejaw", look=(119,), corpse=12321, hp=240, xp=6, speed=90, race="blood",
                       attacks=[("melee", 0, -12)], armor=2, defense=4, boss=True,
                       loot=[(GOLD, 100000, 40), (266, 100000, 2)], voices=["SNORT!", "Bramblejaw paws the ground."],
                       events=["SpireProvingThink", "SpireProvingDeath"]),
    "Hopper Toad": dict(desc="a hopper toad", look=(222,), corpse=6077, hp=28, xp=9, speed=80, race="blood",
                        attacks=[("melee", 0, -10), ("slow", -70, 1500, 3, "CONST_ME_GREEN_RINGS")], armor=2, defense=2,  # F1-10: a sticky spit
                        loot=[(GOLD, 70000, 6), (9640, 12000, 1)], voices=["Ribbit!"]),
    "Sproutling": dict(desc="a sproutling", look=(19,), corpse=17622, hp=35, xp=13, speed=70, race="venom",
                       attacks=[("melee", 0, -10), ("earth", 0, -12, 4)], armor=2, defense=3,
                       loot=[(GOLD, 75000, 7), (3577, 20000, 1), (3738, 14000, 1)],
                       events=["SpireSproutMend"]),  # F1-10: mends hurt sproutlings
    # ---------------------------------------------------------------- Floor 1 camps (Open)
    "Meadow Wasp": dict(desc="a meadow wasp", look=(44,), corpse=5989, hp=45, xp=17, speed=130, race="venom",
                        attacks=[("melee", 0, -16, None, "poison")], armor=2, defense=4, defenses=[("haste", 12, 200)],  # F1-10: darts
                        loot=[(GOLD, 70000, 8), (3577, 25000, 1), (5902, 16000, 1), (14083, 2500, 1)], voices=["Bzzzt!"]),
    "Burrow Mole": dict(desc="a burrow mole", look=(26,), corpse=27646, hp=130, xp=39, speed=85, race="blood",
                        attacks=[("melee", 0, -32)], armor=8, defense=8, defenses=[("invisible", 8)],  # F1-10: burrows out of sight
                        loot=[(GOLD, 90000, 26), (3577, 40000, 2), (266, 4000, 1), (5880, 12000, 1)]),  # more gold: an xp camp that must still pay for arrows
    "Reed Snapper": dict(desc="a reed snapper", look=(112,), corpse=6073, hp=150, xp=39, speed=90, race="blood",
                         attacks=[("melee", 0, -38), ("slow", -120, 2000, 1, "CONST_ME_WATERSPLASH")], armor=12, defense=12,  # F1-10: drags you down
                         loot=[(GOLD, 100000, 30), (PLAT, 1500, 1), (3582, 20000, 1), (266, 8000, 1), (5899, 10000, 1), (30975, 18000, 1)]),
    "Bristle Boar": dict(desc="a bristle boar", look=(119,), corpse=12321, hp=90, xp=28, speed=105, race="blood",
                         attacks=[("melee", 0, -30), ("charge", 0, -36, 4)], armor=6, defense=8,  # F1-10: charges
                         loot=[(GOLD, 85000, 15), (3577, 40000, 2), (3582, 15000, 1), (903, 12000, 1)], voices=["Hrrnk!"]),
    "Meadow Wolf": dict(desc="a meadow wolf", look=(27,), corpse=5968, hp=85, xp=36, speed=115, race="blood",
                        attacks=[("melee", 0, -25)], armor=4, defense=6, run=12, defenses=[("haste", 10, 250)],  # F1-10: darts in, flees hurt
                        loot=[(GOLD, 70000, 10), (5897, 10000, 1), (3577, 30000, 1)], voices=["Grrr!"],
                        events=["SpireWolfCall", "SpireWolfCallDeath", "SpirePack"]),  # F1-10: howls for the pack when hurt; S5: keeps to its pack
    "Grey Alpha": dict(desc="a grey alpha", look=(52,), corpse=5997, hp=260, xp=107, speed=125, race="blood",
                       attacks=[("melee", 0, -60)], armor=12, defense=14,
                       loot=[(GOLD, 100000, 40), (5897, 50000, 2), (266, 8000, 1), (3012, 6000, 1)], voices=["AWOOOO!"],
                       summons=[("Meadow Wolf", 2)], events=["SpirePack"]),  # S5: leads its pack
    "Field Shardling": dict(desc="a field shardling", look=(122,), corpse=16177, hp=120, xp=58, speed=90, race="undead",
                            attacks=[("melee", 0, -20), ("energy", 0, -35, 4)], armor=10, defense=10, events=["SpireShardBurst"],
                            loot=[(GOLD, 85000, 20), (268, 6000, 1), (3033, 6000, 1)], elements={"energy": 50, "earth": -10}),
    # Jay approved our own art for these four (2026-11-25): looks 2201-2204, no colour layer
    "Road Bandit": dict(desc="a road bandit", look=(2201, 0, 0, 0, 0, 0), corpse=18050, hp=160, xp=50, speed=100,
                        race="blood", attacks=[("melee", 0, -45), ("drunk", 0, 4000, 3)], armor=10, defense=12,  # F1-10: smoke bomb
                        loot=[(GOLD, 90000, 60), (PLAT, 6000, 1), (3294, 5000, 1), (3361, 4000, 1), (3286, 5000, 1), (11492, 13000, 1), (5913, 6000, 1)],
                        voices=["Your money or your life!"]),
    "Bandit Captain": dict(desc="a bandit captain", look=(2202, 0, 0, 0, 0, 0), corpse=18050, hp=450, xp=201, speed=110,
                           race="blood", attacks=[("melee", 0, -90), ("physical", 0, -60, 4)], armor=18, defense=20,
                           loot=[(GOLD, 100000, 80), (PLAT, 15000, 1), (3359, 4000, 1), (3352, 5000, 1), (266, 15000, 2), (5909, 12000, 1)],
                           voices=["Get them, boys!"], summons=[("Road Bandit", 2)]),
    "Thornsnap": dict(desc="a thornsnap", look=(28,), corpse=6047, hp=140, xp=56, speed=90, race="venom",
                      attacks=[("melee", 0, -35, None, "poison"), ("slow", -90, 2000, 2, "CONST_ME_CARNIPHILA")], armor=8, defense=8,  # F1-10: roots
                      loot=[(GOLD, 85000, 22), (266, 5000, 1), (5879, 13000, 1)], elements={"earth": 100, "fire": -15}),
    "Ruin Sentinel": dict(desc="a ruin sentinel", look=(2204, 0, 0, 0, 0, 0), corpse=13865, hp=300, xp=96, speed=85,
                          race="undead", attacks=[("melee", 0, -70), ("cleave", 0, -55, 1)], armor=25, defense=25,  # F1-10: shield bash
                          loot=[(GOLD, 100000, 85), (PLAT, 6000, 1), (3352, 6000, 1), (3274, 5000, 1), (5880, 8000, 1)], elements={"physical": 10, "holy": -15},
                          events=["SpireShieldWall", "SpireShieldWallHit", "SpireShieldWallDeath"]),  # F1-10: shield wall
    "Ruin Archer": dict(desc="a ruin archer", look=(2203, 0, 0, 0, 0, 0), corpse=5963, hp=220, xp=83, speed=95,
                        race="undead", attacks=[("melee", 0, -20), ("arrow", 0, -60, 6)], armor=12, defense=12, dist=4,
                        loot=[(GOLD, 100000, 75), (PLAT, 6000, 1), (3447, 30000, 15), (3350, 3000, 1), (11492, 8000, 1)], elements={"holy": -15}),
    # S4 (2026-11-25): the group grounds' mixed packs need a ranged one and a caster beside the front-liner (DESIGN.md 9.4).
    # Bandits in the Smugglers' Cellar and the Old Watchtower; they borrow the bandit outfit in new colours (ART_REQUESTS).
    "Bandit Crossbowman": dict(desc="a bandit crossbowman", look=(2208, 0, 0, 0, 0, 0), corpse=18050, hp=190, xp=72,
                               speed=95, race="blood", attacks=[("melee", 0, -15), ("bolt", 0, -60, 6)], armor=10,
                               defense=10, dist=4,
                               loot=[(GOLD, 90000, 55), (PLAT, 5000, 1), (3446, 30000, 10), (3349, 2500, 1), (11492, 10000, 1)],
                               voices=["Hold still!"]),
    "Hedge Hexer": dict(desc="a hedge hexer", look=(2209, 0, 0, 0, 0, 0), corpse=18050, hp=170, xp=78, speed=90,
                        race="blood", attacks=[("melee", 0, -10), ("earth", 0, -55, 4)], armor=8, defense=8, dist=3,
                        loot=[(GOLD, 90000, 55), (PLAT, 6000, 1), (236, 12000, 1), (5879, 8000, 1), (3738, 15000, 1)],
                        voices=["Mend, mend!"], elements={"earth": 30, "fire": -10},
                        events=["SpireHexMend"]),  # mends a hurt ally nearby now and then: kill her first
    # ---------------------------------------------------------------- Floor 1 elites (FLOOR1_REVIEW.md F1-11): one rare,
    # glowing elite per rebuilt ground, every 15 minutes (ELITE_RESPAWN); each has its own look since 2026-11-26
    "Old Bristleback": dict(desc="old bristleback", look=(2331, 0, 0, 0, 0, 0), corpse=12321, hp=600, xp=220, speed=115, race="blood",
                            attacks=[("melee", 0, -60), ("charge", 0, -80, 4)], armor=14, defense=14, light=(3, 198),
                            loot=[(GOLD, 100000, 60), (PLAT, 25000, 1), (3577, 60000, 3), (903, 50000, 2), (266, 30000, 2)],
                            voices=["HRRRNK!"]),
    "Moonhowl": dict(desc="moonhowl", look=(2330, 0, 0, 0, 0, 0), corpse=5968, hp=520, xp=240, speed=130, race="blood",
                     attacks=[("melee", 0, -55), ("howl", 0, -40, 2)], armor=10, defense=12, light=(3, 215),
                     loot=[(GOLD, 100000, 50), (PLAT, 25000, 1), (5897, 60000, 3), (266, 30000, 2)], voices=["AWOOOOOO!"],
                     events=["SpirePack"]),  # S5: leads its pack
    "Mossback Snapper": dict(desc="a mossback snapper", look=(2332, 0, 0, 0, 0, 0), corpse=6073, hp=900, xp=250, speed=95, race="blood",
                             attacks=[("melee", 0, -70), ("slow", -180, 2500, 1, "CONST_ME_WATERSPLASH")], armor=22,
                             defense=22, light=(3, 210),
                             loot=[(GOLD, 100000, 90), (PLAT, 40000, 2), (3582, 50000, 2), (5899, 40000, 2), (236, 25000, 1)]),
    "Blackthorn": dict(desc="blackthorn", look=(2333, 0, 0, 0, 0, 0), corpse=6047, hp=840, xp=330, speed=95, race="venom",
                       attacks=[("melee", 0, -65, None, "poison"), ("slow", -140, 2500, 3, "CONST_ME_CARNIPHILA")],
                       armor=16, defense=16, light=(3, 30), elements={"earth": 100, "fire": -15},
                       loot=[(GOLD, 100000, 80), (PLAT, 30000, 1), (5879, 60000, 3), (236, 25000, 1)]),
    "Prism Shardling": dict(desc="a prism shardling", look=(2334, 0, 0, 0, 0, 0), corpse=16177, hp=720, xp=340, speed=95, race="undead",
                            attacks=[("melee", 0, -40), ("energy", 0, -80, 4)], armor=18, defense=18, light=(4, 143),
                            events=["SpireShardBurst"],
                            elements={"energy": 50, "earth": -10},
                            loot=[(GOLD, 100000, 85), (PLAT, 40000, 2), (268, 30000, 2), (3033, 30000, 2)]),
    # H8 (2026-11-25): the Old Quarry's elite, on top of the Upper Cut. A grey-gold sentinel that keeps its shield wall.
    "Granite Warden": dict(desc="the granite warden", look=(2335, 0, 0, 0, 0, 0), corpse=13865, hp=1100, xp=380, speed=90,
                           race="undead", attacks=[("melee", 0, -95), ("cleave", 0, -80, 1)], armor=30, defense=30,
                           light=(3, 79), elements={"physical": 10, "holy": -15},
                           loot=[(GOLD, 100000, 95), (PLAT, 40000, 2), (3352, 20000, 1), (5880, 40000, 2), (236, 25000, 1)],
                           voices=["The works are closed."],
                           events=["SpireShieldWall", "SpireShieldWallHit", "SpireShieldWallDeath"]),
    # ---------------------------------------------------------------- Floor 1 rare roamers (AD4, adventure design 4.4)
    # One per level band; scripts/spirebound/roamers.lua brings one out every 25-45 minutes for 15 minutes, at a random
    # monster spot of its grounds. Tuned like an elite: one player at the top of the band, or two below it. Not in the
    # map's spawns. Own looks approved by Jay 2026-11-27 (the boar wears the approved red-crested boar); they keep a glow.
    # Goldback Toad: always hops away (runHealth = its health), so it must be cornered; spits from range while it flees.
    "Goldback Toad": dict(desc="the Goldback Toad", look=(2340, 0, 0, 0, 0, 0), corpse=6077, hp=420, xp=170, speed=135, race="blood",
                          attacks=[("melee", 0, -24), ("earth", -10, -30, 4), ("slow", -80, 1500, 3, "CONST_ME_GREEN_RINGS")],
                          armor=6, defense=8, run=420, light=(4, 210),
                          loot=[(9640, 100000, 3)], voices=["RIBBIT!", "The Goldback Toad puffs up its golden back."],
                          events=["SpireRoamerDeath"]),
    # Frenzied Boar: our red-crested boar (Q63), angrier. Charges, and speeds up as it is hurt (SpireRoamerHurt).
    "Frenzied Boar": dict(desc="the Frenzied Boar", look=(119,), corpse=12321, hp=900, xp=330, speed=120, race="blood",
                          attacks=[("melee", 0, -55), ("charge", -20, -75, 4)], armor=14, defense=14, light=(4, 194),
                          loot=[(3577, 100000, 4), (903, 60000, 2)], voices=["HRRRNNK!", "The Frenzied Boar's crest flares red."],
                          events=["SpireRoamerDeath", "SpireRoamerHurt"]),
    # Pale Stag: flees at speed (runHealth = its health) and gores with its antlers when you close in.
    "Pale Stag": dict(desc="the Pale Stag", look=(2341, 0, 0, 0, 0, 0), corpse=4016, hp=1100, xp=430, speed=190, race="blood",
                      attacks=[("melee", 0, -70), ("charge", -30, -95, 3)], armor=16, defense=18, run=1100, light=(4, 215),
                      loot=[(3577, 100000, 5)], voices=["The Pale Stag stamps and lowers its antlers."],
                      events=["SpireRoamerDeath"]),
    # The Paymaster: a bandit with the payroll chest; two Road Bandits guard him (roamers.lua), and he runs for the
    # ground's edge once badly hurt. A citizen outfit in bandit colours until his own art.
    "The Paymaster": dict(desc="the Paymaster", look=(2211, 0, 0, 0, 0, 0), corpse=18050, hp=1500, xp=600, speed=115,
                          race="blood", attacks=[("melee", 0, -85), ("physical", -40, -90, 4)], armor=20, defense=20,
                          run=450, light=(3, 206),
                          loot=[(3352, 15000, 1), (266, 50000, 2)], voices=["Hands off the payroll!", "Guards! GUARDS!"],
                          events=["SpireRoamerDeath"]),
    # ---------------------------------------------------------------- AD5 addon hunts (adventure design 4.5): each comes
    # out after 15 kills of its kind in its ground (scripts/spirebound/addon_hunts.lua), for the player on the quest.
    "Deadeye Sorrel": dict(desc="Deadeye Sorrel", look=(2208, 0, 0, 0, 0, 0), corpse=18050, hp=900, xp=380, speed=105,
                           race="blood", attacks=[("melee", 0, -25), ("bolt", -40, -95, 7)], armor=14, defense=14, dist=5,
                           light=(3, 30), loot=[(GOLD, 100000, 90), (PLAT, 60000, 2), (3446, 100000, 20)],
                           voices=["I never miss twice.", "Hold still, hunter."]),
    "The Page-Thief": dict(desc="the Page-Thief", look=(2209, 0, 0, 0, 0, 0), corpse=18050, hp=850, xp=380, speed=110,
                           race="blood", attacks=[("melee", 0, -20), ("earth", -40, -90, 4), ("drunk", 0, 3000, 3)],
                           armor=12, defense=12, dist=3, light=(3, 143), elements={"earth": 30, "fire": -10},
                           loot=[(GOLD, 100000, 90), (PLAT, 60000, 2), (3738, 100000, 2)],
                           voices=["Finders keepers!", "These pages are mine now."]),
    "Glasswing": dict(desc="Glasswing", look=(2334, 0, 0, 0, 0, 0), corpse=16177, hp=1000, xp=380, speed=90, race="undead",
                      attacks=[("melee", 0, -35), ("energy", -40, -85, 4)], armor=16, defense=16, light=(4, 71),
                      elements={"energy": 50, "earth": -10}, events=["SpireShardBurst"],
                      loot=[(GOLD, 100000, 90), (PLAT, 60000, 2), (268, 60000, 2)],
                      voices=["The old shardling chimes softly."]),
    # ---------------------------------------------------------------- AD5 hidden places (s14, s15): hidden beasts with
    # trophies (gear spec 4.8 rules: once per character, 1-3 hours' rest, solo at the top of the band or a small group).
    "Ironpurse": dict(desc="Ironpurse", look=(129, 94, 79, 79, 94, 0), corpse=18050, hp=2600, xp=1200, speed=110,
                      race="blood", attacks=[("melee", 0, -150), ("physical", -60, -140, 4)], armor=28, defense=28,
                      loot=[(GOLD, 100000, 100), (PLAT, 100000, 8), (3352, 30000, 1), (239, 50000, 2)],
                      voices=["Every coin is counted.", "You owe interest on that, climber."],
                      summons=[("Road Bandit", 2)], events=["SpireMiniBossDeath"]),
    "The Unfinished": dict(desc="the Unfinished", look=(2335, 0, 0, 0, 0, 0), corpse=13865, hp=3400, xp=1500, speed=80,
                           race="undead", attacks=[("melee", 0, -180), ("cleave", -80, -170, 1)], armor=34, defense=34,
                           elements={"physical": 10, "holy": -15},
                           loot=[(GOLD, 100000, 100), (PLAT, 100000, 10), (5880, 100000, 3), (239, 50000, 2)],
                           voices=["Chisel... and stone...", "FINISH... ME..."], events=["SpireMiniBossDeath"]),
    # ---------------------------------------------------------------- FD2 ground features (Floor 1 depth design 4.2):
    # each comes out of one ground's feature (scripts/spirebound/ground_features.lua), never from the map's spawns.
    # Elder Sproutling: a seedling left two minutes grows into one. Tougher, better loot (herbs, more coins).
    "Elder Sproutling": dict(desc="an elder sproutling", look=(19,), corpse=17622, hp=150, xp=55, speed=75, race="venom",
                             attacks=[("melee", 0, -22), ("earth", -8, -26, 4)], armor=6, defense=8, heal=(0.03, 4000),
                             loot=[(GOLD, 100000, 22), (3738, 60000, 2), (3577, 40000, 1)],
                             voices=["The elder sproutling creaks and spreads its leaves."]),
    # Nest Queen: comes out of a nest burnt with a torch in Waspgrass Fields, with her wasps.
    "Nest Queen": dict(desc="a nest queen", look=(44,), corpse=5989, hp=260, xp=90, speed=120, race="venom",
                       attacks=[("melee", 0, -30, None, "poison"), ("earth", -10, -30, 4)], armor=6, defense=8,
                       loot=[(GOLD, 100000, 30), (5902, 100000, 2), (14083, 15000, 1)], voices=["BZZZZZT!"],
                       summons=[("Meadow Wasp", 1)]),
    # Bandit Lieutenant: one named lieutenant walks the Bandit Road each hour; the wanted poster pays on his badge.
    "Bandit Lieutenant": dict(desc="a bandit lieutenant", look=(2202, 0, 0, 0, 0, 0), corpse=18050, hp=650, xp=260, speed=115,
                              race="blood", attacks=[("melee", 0, -75), ("physical", -30, -70, 4)], armor=18, defense=18,
                              loot=[(GOLD, 100000, 60), (9218, 100000, 1), (266, 30000, 1)],
                              voices=["You'll never collect on me!", "The poster's worth more than you are."],
                              summons=[("Road Bandit", 1)]),
    # ---------------------------------------------------------------- Floor 1 apex spawn (Contested)
    "Stonehorn Ram": dict(desc="a stonehorn ram", look=(607,), corpse=5994, hp=900, xp=480, speed=120, race="blood",
                          attacks=[("melee", 0, -120), ("charge", 0, -150, 4)], armor=30, defense=28, heal=(0.05, 6000),
                          loot=[(GOLD, 100000, 100), (PLAT, 30000, 2), (266, 20000, 3), (268, 20000, 3), (5880, 10000, 1)],
                          voices=["BAAAH!"], events=["SpireStairKeyRam"]),  # P9: a piece of the Stair Key
    # ---------------------------------------------------------------- Floor 1 bosses (behaviour scripts: tasks 1.18 / 1.19)
    "Gate Hound": dict(desc="the Gate Hound", look=(2205, 0, 0, 0, 0, 0), corpse=9001, hp=4000, xp=2500, speed=150, race="fire",
                       attacks=[("melee", 0, -180), ("howl", -80, -160, 2)], armor=35, defense=35, boss=True,
                       loot=[(GOLD, 100000, 100), (PLAT, 100000, 10), (266, 100000, 5)], voices=["GRRROOOAAARRR!"],
                       summons=[("Meadow Wolf", 3)], elements={"fire": 80, "ice": -10},
                       events=["SpireBossHealth", "SpireBossDeath", "SpireBossThink"]),
    "Axe-Lord of the Stair": dict(desc="the Axe-Lord of the Stair", look=(2206, 0, 0, 0, 0, 0), corpse=18074,
                                  # party playtest 2026-11-26 (P0-22, Q78: a party boss for 4-6 at level 30-35): a level-30
                                  # party of three did 19% of 12,000 health before wiping in 45 s; two hits together (melee
                                  # 260 + line 300) killed the tank from full, one line + one swing killed a caster. Smaller hits, more health (five level-30s in tier-3 gear killed 12,000 in 90 s, about 135 damage a second),
                                  # and he leaves the tank for the casters half as often.
                                  hp=20000, xp=8000, speed=130, race="blood", change_target=(6000, 10),
                                  attacks=[("melee", 0, -160), ("cleave", -80, -170, 1)], armor=40, defense=40, boss=True,
                                  # review A4-6: one body for the whole party, so most of his coins now go straight to each
                                  # credited fighter's bank (SpireBoss payEach, 10 platinum each); the body keeps a little
                                  loot=[(GOLD, 100000, 100), (PLAT, 100000, 5), (266, 100000, 10), (268, 100000, 10)],
                                  voices=["The stair is mine!", "None shall climb!"], summons=[("Ruin Sentinel", 2)],
                                  elements={"physical": 10},
                                  events=["SpireBossHealth", "SpireBossDeath", "SpireBossThink"]),
    # ---------------------------------------------------------------- the Underkeep, Wing 1 (tuned to Floor 2)
    "Mire Toad": dict(desc="a mire toad", look=(222, 0, 0, 0, 0, 0), corpse=6077, hp=420, xp=210, speed=95, race="venom",
                      attacks=[("melee", 0, -70, None, "poison"), ("earth", -30, -90, 4)], armor=18, defense=18,
                      loot=[(GOLD, 100000, 60), (236, 8000, 1), (3032, 2000, 1)], elements={"earth": 100, "fire": -10}),
    "Black Crawler": dict(desc="a black crawler", look=(2301, 0, 0, 0, 0, 0), corpse=10458, hp=520, xp=260, speed=130, race="blood",
                          attacks=[("melee", 0, -110)], armor=22, defense=20,
                          loot=[(GOLD, 100000, 70), (PLAT, 10000, 1), (3029, 2000, 1)], voices=["Skrrrk!"]),
    # ---------------------------------------------------------------- Underkeep Wings 2-6 (tuned to floors 2, 4, 6, 8, 10)
    "Vault Rat": dict(desc="a vault rat", look=(56,), corpse=5964, hp=600, xp=320, speed=140, race="blood",
                      attacks=[("melee", 0, -130)], armor=24, defense=22, loot=[(GOLD, 100000, 80), (PLAT, 20000, 1)]),
    "Chain Ghoul": dict(desc="a chain ghoul", look=(131, 79, 79, 79, 79, 0), corpse=18074, hp=900, xp=470, speed=110, race="undead",
                        attacks=[("melee", 0, -170), ("physical", -60, -150, 3)], armor=30, defense=28,
                        loot=[(GOLD, 100000, 100), (PLAT, 30000, 2), (3357, 1500, 1)], elements={"holy": -20}),
    # ---------------------------------------------------------------- small game in the open country (Jay, Q94,
    # 2026-11-26: "fill in the empty land with small game monsters"). Harmless, they run, and pay almost nothing, so they
    # never become a farm. Placed by maps/small_game.py on the empty lawns. Placeholder looks until their art.
    "Meadow Hare": dict(desc="a meadow hare", look=(74,), corpse=4173, hp=20, xp=3, speed=160, race="blood", hostile=False,
                        attacks=[], armor=1, defense=1, run=20, loot=[(3577, 25000, 1)]),
    "Dapple Fawn": dict(desc="a dapple fawn", look=(31,), corpse=4016, hp=35, xp=5, speed=170, race="blood", hostile=False,
                        attacks=[], armor=1, defense=2, run=35, loot=[(3577, 40000, 2)]),
    "Thistle Hen": dict(desc="a thistle hen", look=(111,), corpse=4330, hp=15, xp=2, speed=120, race="blood", hostile=False,
                        attacks=[], armor=1, defense=1, run=15, loot=[(3606, 20000, 1), (5890, 30000, 2)]),
    "Acorn Squirrel": dict(desc="an acorn squirrel", look=(274,), corpse=276, hp=12, xp=2, speed=180, race="blood", hostile=False,
                           attacks=[], armor=1, defense=1, run=12, loot=[]),
    # the Underkeep Wing 1 mini-boss (Q89, 2026-11-26): the keeper of the old sluices, in the den at the wing's heart.
    # Sized for one or two climbers around level 30-40 (Jay may test alone or as a pair). Placeholder look until its art.
    "Sluice Warden": dict(desc="the Sluice Warden", look=(222,), corpse=6077, hp=2600, xp=1500, speed=110, race="venom",
                          attacks=[("melee", 0, -150, None, "poison"), ("earth", -60, -160, 4)], armor=30, defense=30,
                          loot=[(GOLD, 100000, 100), (PLAT, 100000, 6), (3032, 25000, 1)], elements={"earth": 100},
                          voices=["The water remembers!"]),
    "Drain Matron": dict(desc="the Drain Matron", look=(222,), corpse=6077, hp=9000, xp=4200, speed=120, race="venom", boss=True,
                         attacks=[("melee", 0, -300, None, "poison"), ("earth", -150, -350, 5)], armor=40, defense=40,
                         loot=[(GOLD, 100000, 100), (PLAT, 100000, 15), (3370, 20000, 1)], elements={"earth": 100}),
    "Trap Mimic": dict(desc="a trap mimic", look=(197,), corpse=6072, hp=2200, xp=1100, speed=90, race="blood",
                       attacks=[("melee", 0, -320)], armor=45, defense=45, loot=[(GOLD, 100000, 100), (PLAT, 60000, 4), (3028, 4000, 1)]),
    "Iron Shade": dict(desc="an iron shade", look=(129, 0, 0, 0, 0, 0), corpse=18138, hp=1800, xp=950, speed=150, race="undead",
                       attacks=[("melee", 0, -200), ("energy", -120, -280, 5)], armor=35, defense=35, dist=3,
                       loot=[(GOLD, 100000, 100), (PLAT, 50000, 3), (3381, 1200, 1)], elements={"physical": 30, "holy": -25}),
    "Keep Warden": dict(desc="a keep warden", look=(131, 114, 114, 114, 114, 2), corpse=18074, hp=4200, xp=2300, speed=130,
                        race="blood", attacks=[("melee", 0, -480), ("physical", -250, -500, 4)], armor=55, defense=55,
                        loot=[(GOLD, 100000, 100), (PLAT, 80000, 6), (3364, 1500, 1)]),
    "Vault Warden": dict(desc="the Vault Warden", look=(131, 0, 94, 0, 94, 3), corpse=18074, hp=60000, xp=30000, speed=150,
                         race="blood", boss=True, attacks=[("melee", 0, -900), ("cleave", -500, -1000, 1)], armor=80, defense=80,
                         loot=[(GOLD, 100000, 100), (PLAT, 100000, 50), (3366, 8000, 1)]),
    "Deep Sentinel": dict(desc="a deep sentinel", look=(131, 86, 86, 86, 86, 3), corpse=18074, hp=8000, xp=4500, speed=140,
                          race="undead", attacks=[("melee", 0, -800), ("physical", -400, -800, 4)], armor=70, defense=70,
                          loot=[(GOLD, 100000, 100), (PLAT, 100000, 10), (3360, 1500, 1)]),
    "Vault Wraith": dict(desc="a vault wraith", look=(2324, 0, 0, 0, 0, 0), corpse=10430, hp=6500, xp=3800, speed=170, race="undead",
                         attacks=[("melee", 0, -400), ("energy", -400, -850, 5)], armor=50, defense=50, dist=3,
                         loot=[(GOLD, 100000, 100), (PLAT, 100000, 8), (3392, 1500, 1)], elements={"holy": -25}),
    "The Underkeeper": dict(desc="the Underkeeper", look=(2323, 0, 0, 0, 0, 0), corpse=12340, hp=180000, xp=90000, speed=160,
                            race="undead", boss=True, attacks=[("melee", 0, -1600), ("cleave", -900, -1800, 1), ("howl", -600, -1200, 2)],
                            armor=95, defense=95, loot=[(GOLD, 100000, 100), (PLAT, 100000, 100), (3366, 30000, 1)],
                            voices=["You dug too deep."]),
    # ---------------------------------------------------------------- secret bosses (DESIGN.md 8.1)
    "Old Tusk": dict(desc="Old Tusk", look=(2311, 0, 0, 0, 0, 0), corpse=12321, hp=1800, xp=900, speed=125, race="blood",
                     attacks=[("melee", 0, -140), ("charge", -60, -160, 4)], armor=25, defense=25,
                     loot=[(GOLD, 100000, 100), (PLAT, 100000, 5), (3582, 100000, 5), (236, 50000, 2)],
                     voices=["HRRROOONK!"], events=["SpireMiniBossDeath"]),
    # ---------------------------------------------------------------- spell summons (DESIGN.md 5.3b)
    "Ember Sprite": dict(desc="an ember sprite", look=(49,), corpse=0, hp=300, xp=0, speed=150, race="fire",
                         attacks=[("melee", 0, -40), ("fire", -20, -60, 4)], armor=10, defense=10, summon=True,
                         loot=[], elements={"fire": 100, "ice": -20}),
    # Hidden mini-bosses (gear progression spec 4.8): each woken at a Floor 1 secret, each leaves a trophy once.
    # Tuned for a solo player at the ground's top level or a small group below it.
    "Hollowfang": dict(desc="Hollowfang", look=(2312, 0, 0, 0, 0, 0), corpse=6009, hp=1500, xp=750, speed=150, race="blood",
                       attacks=[("melee", 0, -110), ("charge", -50, -140, 4)], armor=18, defense=20,
                       loot=[(GOLD, 100000, 100), (PLAT, 100000, 4), (5897, 100000, 3), (236, 40000, 2)],
                       voices=["The copse is mine.", "AWOOOOO!"], events=["SpireMiniBossDeath"]),
    "Briar Mother": dict(desc="the Briar Mother", look=(2313, 0, 0, 0, 0, 0), corpse=6047, hp=2200, xp=1000, speed=80, race="venom",
                         attacks=[("melee", 0, -120, None, "poison")], armor=22, defense=22,
                         loot=[(GOLD, 100000, 100), (PLAT, 100000, 6), (5879, 100000, 3), (236, 50000, 2)],
                         voices=["Sssssleep in the thorns."], elements={"earth": 100, "fire": -15}, events=["SpireMiniBossDeath"]),
    "Drowned Warden": dict(desc="the Drowned Warden", look=(131, 86, 86, 86, 86, 0), corpse=18074, hp=3200, xp=1500, speed=85,
                           race="undead", attacks=[("melee", 0, -190)], armor=35, defense=35,
                           loot=[(GOLD, 100000, 100), (PLAT, 100000, 10), (3352, 30000, 1), (239, 50000, 2)],
                           voices=["The well keeps what it takes."], elements={"physical": 10, "holy": -20}, events=["SpireMiniBossDeath"]),
    "Twin Fang Warden": dict(desc="the Twin Fang Warden", look=(131, 114, 94, 114, 94, 3), corpse=18074, hp=60000, xp=0, speed=220,
                             race="blood", attacks=[("melee", 0, -900), ("lance_", -500, -1100, 1)], armor=80, defense=80,
                             loot=[], boss=True, voices=["Show me two blades in one heart."], events=["SpireTwinFangDeath"]),
    "Mirror Image": dict(desc="a mirror image", look=(130,), corpse=0, hp=2000, xp=0, speed=0, race="undead",
                         attacks=[("melee", 0, 0)], armor=50, defense=50, summon=True, loot=[]),
    "Wolf Companion": dict(desc="a wolf companion", look=(27,), corpse=0, hp=400, xp=0, speed=160, race="blood",
                           attacks=[("melee", 0, -50)], armor=15, defense=15, summon=True, loot=[]),
    # P9b: the Lost Patrol's survivor while he walks home with you (scripts/spirebound/escort.lua); dressed like the watch
    "Patrolman Teodric": dict(desc="Patrolman Teodric", look=(134, 95, 94, 94, 95, 0), corpse=0, hp=900, xp=0, speed=230,
                              race="blood", attacks=[("melee", 0, -20)], armor=25, defense=25, summon=True, loot=[]),
}

ELEMENTS = ["physical", "energy", "earth", "fire", "lifedrain", "manadrain", "drown", "ice", "holy", "death"]
SPELL = {
    "earth": ('name = "combat", type = COMBAT_EARTHDAMAGE', "CONST_ANI_EARTH", "CONST_ME_CARNIPHILA"),
    "energy": ('name = "combat", type = COMBAT_ENERGYDAMAGE', "CONST_ANI_ENERGY", "CONST_ME_ENERGYHIT"),
    "physical": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', "CONST_ANI_THROWINGKNIFE", "CONST_ME_HITAREA"),
    "fire": ('name = "combat", type = COMBAT_FIREDAMAGE', "CONST_ANI_FIRE", "CONST_ME_FIREAREA"),
    "arrow": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', "CONST_ANI_ARROW", "CONST_ME_HITAREA"),
    "bolt": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', "CONST_ANI_BOLT", "CONST_ME_HITAREA"),
    "charge": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_GROUNDSHAKER"),
    "howl": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_SOUND_RED"),
    "cleave": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_HITAREA"),
    "lance_": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_HITAREA"),
}


def lua_name(name):
    return name.lower().replace("-", "_").replace(" ", "_").replace("'", "").replace(",", "")


def render(name, d):
    look = list(d["look"]) + [0] * (6 - len(d["look"]))
    boss = d.get("boss", False)
    L = [f'-- Generated by tools/gen_monsters.py: edit the table there, not this file.',
         f'local mType = Game.createMonsterType("{name}")', "local monster = {}", "",
         f'monster.description = "{d["desc"]}"', f"monster.experience = {d['xp']}",
         "monster.outfit = {",
         f"\tlookType = {look[0]}, lookHead = {look[1]}, lookBody = {look[2]}, lookLegs = {look[3]}, lookFeet = {look[4]}, lookAddons = {look[5]}, lookMount = 0,",
         "}", "",
         f"monster.health = {d['hp']}", f"monster.maxHealth = {d['hp']}", f'monster.race = "{d["race"]}"',
         f"monster.corpse = {d['corpse']}", f"monster.speed = {d['speed']}", "monster.manaCost = 0", "",
         "monster.changeTarget = { interval = %d, chance = %d }" % d.get("change_target", (4000, 20 if boss else 0)),
         "monster.strategiesTarget = { nearest = 100 }", "",
         "monster.flags = {",
         f"\tsummonable = {str(d.get('summon', False)).lower()}, attackable = true, hostile = {str(d.get('hostile', True)).lower()}, convinceable = false, pushable = false,",
         f"\trewardBoss = false, illusionable = false, canPushItems = {str(boss).lower()}, canPushCreatures = {str(boss).lower()},",
         f"\tstaticAttackChance = 90, targetDistance = {d.get('dist', 1)}, runHealth = {d.get('run', 0)}, healthHidden = false, isBlockable = false,",
         "\tcanWalkOnEnergy = false, canWalkOnFire = false, canWalkOnPoison = false,",
         "}", "", "monster.light = { level = %d, color = %d }" % d.get("light", (0, 0)), ""]
    v = d.get("voices", [])
    L.append("monster.voices = {")
    L.append(f"\tinterval = 5000, chance = {10 if v else 0},")
    for t in v:
        L.append(f'\t{{ text = "{t}", yell = {str(boss).lower()} }},')
    L.append("}")
    if d.get("summons"):
        total = sum(c for _, c in d["summons"])
        L.append(f"monster.summon = {{ maxSummons = {total}, summons = {{")
        for sname, c in d["summons"]:
            L.append(f'\t{{ name = "{sname}", chance = 10, interval = 2000, count = {c} }},')
        L.append("} }")
    events = ["SpireBuffDamage", "SpireTwinFangOffhand"] + d.get("events", [])
    L.append("monster.events = { " + ", ".join(f'"{e}"' for e in events) + " }")
    L.append("")
    L.append("monster.loot = {")
    for iid, chance, mx in d["loot"]:
        L.append(f"\t{{ id = {iid}, chance = {chance}, maxCount = {mx} }},")
    L.append("}")
    L.append("")
    L.append("monster.attacks = {")
    for a in d["attacks"]:
        kind, mn, mxd = a[0], a[1], a[2]
        rng = a[3] if len(a) > 3 else None
        cond = a[4] if len(a) > 4 else None
        # (kind, speedChange or 0, duration ms, range, effect): FLOOR1_REVIEW.md F1-10. The engine calls any slow
        # "paralyzed"; keep them small and short (2026-11-24 in-client check: -250 snappers plus toads were too harsh)
        if kind in ("slow", "drunk"):
            eff = a[4] if len(a) > 4 else ("CONST_ME_MAGIC_RED" if kind == "slow" else "CONST_ME_POFF")
            if kind == "slow":
                L.append(f'	{{ name = "speed", interval = 2000, chance = 10, speedChange = {mn}, range = {rng}, duration = {mxd}, effect = {eff}, target = true }},')
            else:
                L.append(f'	{{ name = "drunk", interval = 2000, chance = 12, range = {rng}, duration = {mxd}, shootEffect = CONST_ANI_SMOKE, effect = {eff}, target = true }},')
            continue
        if kind == "melee":
            extra = ""
            if cond == "poison":
                extra = ", condition = { type = CONDITION_POISON, totalDamage = 20, interval = 4000 }"
            L.append(f'\t{{ name = "melee", interval = 2000, chance = 100, minDamage = {mn}, maxDamage = {mxd}{extra} }},')
        else:
            base, shoot, eff = SPELL[kind]
            parts = [base, "interval = 2000", f"chance = {25 if boss else 15}", f"minDamage = {mn}", f"maxDamage = {mxd}"]
            if kind in ("howl",):
                parts.append(f"radius = {rng}")
                parts.append("target = false")
            elif kind in ("cleave", "lance_"):
                parts.append("length = 3, spread = 0")
                parts.append("target = false")
            elif kind == "charge":
                parts.append("range = 4, radius = 1, target = true")
            else:
                parts.append(f"range = {rng}")
                parts.append("target = true")
            if shoot:
                parts.append(f"shootEffect = {shoot}")
            parts.append(f"effect = {eff}")
            L.append("\t{ " + ", ".join(parts) + " },")
    L.append("}")
    L.append("")
    L.append("monster.defenses = {")
    L.append(f"\tdefense = {d['defense']},")
    L.append(f"\tarmor = {d['armor']},")
    for dk in d.get("defenses", []):  # ("invisible", chance) or ("haste", chance, speedChange)
        if dk[0] == "invisible":
            L.append(f'	{{ name = "invisible", interval = 2000, chance = {dk[1]}, effect = CONST_ME_POFF }},')
        elif dk[0] == "haste":
            L.append(f'	{{ name = "speed", interval = 2000, chance = {dk[1]}, speedChange = {dk[2]}, duration = 3000, effect = CONST_ME_MAGIC_GREEN, target = false }},')
    if d.get("heal"):
        pct, interval = d["heal"]
        amount = int(d["hp"] * pct)
        L.append(f'\t{{ name = "combat", interval = {interval}, chance = 100, type = COMBAT_HEALING, minDamage = {amount}, maxDamage = {amount}, effect = CONST_ME_MAGIC_BLUE, target = false }},')
    L.append("}")
    L.append("")
    el = d.get("elements", {})
    L.append("monster.elements = {")
    for e in ELEMENTS:
        const = f"COMBAT_{e.upper()}" if e in ("lifedrain", "manadrain") else f"COMBAT_{e.upper()}DAMAGE"
        L.append(f"\t{{ type = {const}, percent = {el.get(e, 0)} }},")
    L.append("}")
    L.append("")
    L.append("monster.immunities = {")
    L.append(f'\t{{ type = "paralyze", condition = {str(boss).lower()} }},')
    L.append('\t{ type = "outfit", condition = false },')
    L.append(f'\t{{ type = "invisible", condition = {str(boss).lower()} }},')
    L.append('\t{ type = "bleed", condition = false },')
    L.append("}")
    L.append("")
    L.append("mType:register(monster)")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- floors 2-10 (generated from maps/floors.py)
import sys as _sys
_sys.path.insert(0, str(ROOT / "maps"))
from floors import FLOORS  # noqa: E402

# placeholder looks (Tibia outfits) with matching corpses; looks redrawn as our own animals in the client (boar 119,
# shardling 122, thornsnap 28, sproutling 19, azhrakkar 61, ram 607) leave the corpse of the animal drawn (Jay: no boar
# leaving "an alligator body")
LOOKS = [(27, 5968), (52, 5997), (119, 12321), (122, 16177), (56, 5964), (222, 6077), (28, 6047), (129, 18050), (131, 18074),
         (15, 5960), (22, 5962), (61, 5995), (55, 5999), (240, 6331), (34, 4025), (121, 6048), (291, 8113), (197, 6072),
         (607, 5994), (19, 17622), (137, 18042), (152, 18046), (139, 18242), (53, 5998), (280, 771), (238, 6532)]
GEAR = {2: [3352, 3359, 3282], 3: [3357, 3351, 3279, 3065, 3068], 4: [3370, 3371, 3303, 3070, 3072],
        5: [3381, 3382, 3385, 3281, 3067, 3073], 6: [3364, 3392, 3415], 7: [3280, 3422, 3360], 8: [3392, 3364, 3360],
        9: [3366, 3360, 3422], 10: [3366, 3280, 3415]}
RANGED_WORDS = ("Archer", "Witch", "Wisp", "Imp", "Hag", "Wraith", "Shade", "Ghost", "Bat", "Wasp")


# Our own approved art (Jay, 2026-11-26: "nice. approved all art work"): replaces the placeholder look, keeps the corpse
OWN_LOOKS = {"Hill Cutthroat": 2210, "Blight Wasp": 2302, "Ridge Cat": 2303, "Herd Bull": 2304, "Stonehide Bull": 2305,
             "Horned Grazer": 2306, "Dust Strider": 2307}
# ...and the corpse of the animal it was drawn as (Tibia corpse items until our own corpse art is approved)
OWN_CORPSES = {"Hill Cutthroat": 18050, "Blight Wasp": 13983, "Ridge Cat": 5986, "Herd Bull": 17422, "Stonehide Bull": 17422,
               "Horned Grazer": 42230, "Dust Strider": 12329}


# Floor 2's camp monsters, one trick each (R13). Each returns an attack row from the floor's base damage.
TRICKS = {
    "Horned Grazer": lambda d: ("charge", -d // 2, -int(d * 1.1), 3),     # lowers its horns and charges the tiles around
    "Ridge Cat": lambda d: ("cleave", -d // 3, -d, 1),                   # pounces: a swipe that hits next to it
    "Dust Strider": lambda d: ("earth", -d // 4, -d // 2, 5),            # kicks up sand from range
    "Hill Cutthroat": lambda d: ("howl", -d // 3, -int(d * 0.8), 2),     # a war cry that hurts everyone near
    "Blight Wasp": lambda d: ("earth", -d // 3, -d, 4),                  # spits blight from range
}


def floor_monsters():
    out = {}
    look_i = 0
    for n, f in FLOORS.items():
        hp0 = int(150 * n ** 1.5)
        dmg0 = int(40 * n ** 1.3)
        gear = GEAR.get(n, [])
        def row(name, mult_hp, mult_xp, mult_dmg, role):
            nonlocal look_i
            lt, corpse = LOOKS[look_i % len(LOOKS)]
            look_i += 1
            lt = OWN_LOOKS.get(name, lt)
            corpse = OWN_CORPSES.get(name, corpse)
            hp = int(hp0 * mult_hp)
            dmg = int(dmg0 * mult_dmg * HUNT_DAMAGE.get(role, 1.0))
            ranged = any(w in name for w in RANGED_WORDS)
            attacks = [("melee", 0, -dmg if not ranged else -dmg // 3)]
            if ranged:
                attacks.append(("energy" if n % 2 else "earth", -dmg // 3, -dmg, 5))
            elif role in ("elite", "apex", "labyrinth"):
                attacks.append(("physical", -dmg // 2, -int(dmg * 1.2), 4))
            loot = [(GOLD, 100000, min(100, 20 * n)), (PLAT, 20000 + 5000 * n, max(1, n // 2)),
                    (239 if n >= 4 else 236, 8000, 1), (238 if n >= 4 else 237, 8000, 1)]
            for gi, g in enumerate(gear):
                loot.append((g, (1500 if role == "camp" else 4000) // (gi + 1), 1))
            d = dict(desc=("an " if name[0] in "AEIOU" else "a ") + name.lower(), look=(lt,), corpse=corpse,
                     hp=hp, xp=int(hp * mult_xp), speed=100 + 5 * n, race="blood", attacks=attacks,
                     armor=8 + 4 * n, defense=8 + 4 * n, loot=loot, dist=4 if ranged else 1, floor=n)
            if role == "apex":
                d["heal"] = (0.04, 6000)
            if role in ("field", "floor"):
                d["boss"] = True
                d["events"] = ["SpireBossHealth", "SpireBossDeath", "SpireBossThink"]
                d["desc"] = "the " + name if not name.startswith(("The ", "Azhrakkar")) else name
                d["loot"] = [(GOLD, 100000, 100), (PLAT, 100000, 10 * n), (239, 100000, 5), (238, 100000, 5)] + \
                            [(g, 30000, 1) for g in gear]
                d["summons"] = [(f["camp"][0], 2)]
            return d
        for i, name in enumerate(f["camp"]):
            out[name] = row(name, 0.8 + 0.12 * i, 0.5, 0.8 + 0.1 * i, "camp")
        out[f["elite"]] = row(f["elite"], 2.6, 0.6, 1.5, "elite")
        out[f["labyrinth"]] = row(f["labyrinth"], 1.7, 0.55, 1.3, "labyrinth")
        out[f["apex"]] = row(f["apex"], 4.5, 0.6, 1.8, "apex")
        out[f["field_boss"]] = row(f["field_boss"], 25 * n ** 0.3, 0.4, 2.2, "field")
        out[f["floor_boss"]] = row(f["floor_boss"], 70 * n ** 0.4, 0.35, 2.8, "floor")
        # roadmap R10: experience and coins come from the floor's targets in tools/balance.py
        import balance
        camp = [out[c] for c in f["camp"]]
        hp = sum(m["hp"] for m in camp) / len(camp)
        xp = sum(m["xp"] for m in camp) / len(camp)
        scale = balance.xp_scale(n, xp, hp, f["band"])
        coins = balance.floor_gold_per_kill(n, hp, f["band"])
        mult = {"camp": 1.0, "labyrinth": 1.5, "elite": balance.ELITE_GOLD, "apex": balance.APEX_GOLD}
        roles = [(c, "camp") for c in f["camp"]] + [(f["elite"], "elite"), (f["labyrinth"], "labyrinth"), (f["apex"], "apex"),
                                                   (f["field_boss"], "field"), (f["floor_boss"], "floor")]
        for name, role in roles:
            m = out[name]
            m["xp"] = max(1, int(round(m["xp"] * scale)))
            trick = TRICKS.get(name)
            if trick:                                        # R13: one trick each, so every hunt plays differently
                m["attacks"] = [a for a in m["attacks"] if a[0] == "melee"] + [trick(int(40 * n ** 1.3 * HUNT_DAMAGE.get(role, 1.0)))]
                m["voices"] = m.get("voices") or []
            if role in mult:
                m["loot"] = balance.coin_loot(coins * mult[role]) + [l for l in m["loot"] if l[0] not in (GOLD, PLAT)]
            for key, val in TWISTS.get(name, {}).items():   # S6: each floor's own twist (maps/floor<n>_plan.py)
                m[key] = val(m) if callable(val) else val
    return out


# R13b (2026-11-26): the hunting monsters of floors 2-10 hit at 60% of the old placeholder formula. Their grounds now
# wake a whole loop at once (6 to 12 monsters, like Floor 1's), and at full strength a level 60 test Vanguard died in
# Floor 2's training ground in seconds: one grazer hit took 11% of a level 40's health, where Floor 1's toughest
# ordinary monster takes about 8%. Bosses keep their numbers.
HUNT_DAMAGE = {"camp": 0.6, "elite": 0.6, "labyrinth": 0.6, "apex": 0.6}

# S6 (DESIGN.md 9.4 layer 3): each floor adds one behaviour the floors below don't have (Claude's call, Jay can veto).
#   Floor 2: the herd animals run when badly hurt and come back once recovered (the engine's runHealth).
#   Floor 3: the plant creatures regrow: they heal 3% of their health every 4 seconds.
#   Floor 4: the Reed Witches mend the hurt monsters around them, any kind (Floor 1's Hedge Hexer trick).
TWISTS = {
    "Horned Grazer": dict(run=lambda m: m["hp"] // 6), "Dust Strider": dict(run=lambda m: m["hp"] // 5),
    "Moss Crawler": dict(heal=(0.03, 4000)), "Rootbound Husk": dict(heal=(0.03, 4000)),
    "Reed Witch": dict(events=["SpireHexMend"]),          # Floor 4: witches mend the hurt monsters round them
}


def adventure_drops():
    """AD5 (tools/gen_adventure.py): Tattered maps from bandits and ruin guards, Vault Keys from Bandit Captains.
    The engine doubles every drop chance (rateLoot 2), so the rows hold half the chance the design names."""
    import gen_adventure as ga
    for drops, item in ((ga.MAP_DROPS, ga.MAP_ITEM[0]), (ga.VAULT_KEY_DROP, ga.VAULT_KEY[0])):
        for name, chance in drops.items():
            loot = MONSTERS[name]["loot"]
            if not any(row[0] == item for row in loot):
                loot.append((item, int(round(chance * 100000 / 2)), 1))


def main():
    _sys.path.insert(0, str(ROOT / "tools"))
    adventure_drops()
    floors_dir = OUT / "floors"
    floors_dir.mkdir(parents=True, exist_ok=True)
    for f in floors_dir.glob("*.lua"):
        f.unlink()
    extra = floor_monsters()
    for name, d in extra.items():
        (floors_dir / f"f{d['floor']}_{lua_name(name)}.lua").write_text(render(name, d))
    folder = OUT / "floor1"
    folder.mkdir(parents=True, exist_ok=True)
    for f in folder.glob("*.lua"):
        f.unlink()
    for name, d in MONSTERS.items():
        (folder / f"{lua_name(name)}.lua").write_text(render(name, d))
    print(f"wrote {len(MONSTERS)} floor 1 monsters and {len(extra)} floor 2-10 monsters")


if __name__ == "__main__":
    main()
