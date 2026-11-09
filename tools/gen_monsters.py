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
                      attacks=[("melee", 0, -8)], armor=1, defense=2,
                      loot=[(GOLD, 70000, 4), (3607, 30000, 1)], voices=["Squeak!"]),
    "Hopper Toad": dict(desc="a hopper toad", look=(222,), corpse=6077, hp=28, xp=9, speed=80, race="blood",
                        attacks=[("melee", 0, -10)], armor=2, defense=2,
                        loot=[(GOLD, 70000, 6)], voices=["Ribbit!"]),
    "Sproutling": dict(desc="a sproutling", look=(19,), corpse=2127, hp=35, xp=12, speed=70, race="venom",
                       attacks=[("melee", 0, -10), ("earth", 0, -12, 4)], armor=2, defense=3,
                       loot=[(GOLD, 75000, 7), (3577, 20000, 1)]),
    # ---------------------------------------------------------------- Floor 1 camps (Open)
    "Bristle Boar": dict(desc="a bristle boar", look=(119,), corpse=6046, hp=90, xp=40, speed=105, race="blood",
                         attacks=[("melee", 0, -30)], armor=6, defense=8,
                         loot=[(GOLD, 85000, 15), (3577, 40000, 2), (3582, 15000, 1)], voices=["Hrrnk!"]),
    "Meadow Wolf": dict(desc="a meadow wolf", look=(27,), corpse=5968, hp=70, xp=30, speed=115, race="blood",
                        attacks=[("melee", 0, -25)], armor=4, defense=6,
                        loot=[(GOLD, 70000, 10), (5897, 10000, 1), (3577, 30000, 1)], voices=["Grrr!"]),
    "Grey Alpha": dict(desc="a grey alpha", look=(52,), corpse=5997, hp=260, xp=150, speed=125, race="blood",
                       attacks=[("melee", 0, -60)], armor=12, defense=14,
                       loot=[(GOLD, 100000, 40), (5897, 50000, 2), (266, 8000, 1)], voices=["AWOOOO!"],
                       summons=[("Meadow Wolf", 2)]),
    "Field Shardling": dict(desc="a field shardling", look=(122,), corpse=6053, hp=120, xp=55, speed=90, race="undead",
                            attacks=[("melee", 0, -20), ("energy", 0, -35, 4)], armor=10, defense=10,
                            loot=[(GOLD, 85000, 20), (268, 6000, 1)], elements={"energy": 50, "earth": -10}),
    "Road Bandit": dict(desc="a road bandit", look=(129, 58, 59, 45, 114, 0), corpse=18050, hp=160, xp=70, speed=100,
                        race="blood", attacks=[("melee", 0, -45)], armor=10, defense=12,
                        loot=[(GOLD, 90000, 30), (3294, 5000, 1), (3361, 4000, 1), (3286, 5000, 1)],
                        voices=["Your money or your life!"]),
    "Bandit Captain": dict(desc="a bandit captain", look=(129, 94, 94, 94, 95, 1), corpse=18050, hp=450, xp=280, speed=110,
                           race="blood", attacks=[("melee", 0, -90), ("physical", 0, -60, 4)], armor=18, defense=20,
                           loot=[(GOLD, 100000, 80), (PLAT, 15000, 1), (3359, 4000, 1), (3352, 5000, 1), (266, 15000, 2)],
                           voices=["Get them, boys!"], summons=[("Road Bandit", 2)]),
    "Thornsnap": dict(desc="a thornsnap", look=(28,), corpse=3998, hp=140, xp=60, speed=90, race="venom",
                      attacks=[("melee", 0, -35, None, "poison")], armor=8, defense=8,
                      loot=[(GOLD, 85000, 22), (266, 5000, 1)], elements={"earth": 100, "fire": -15}),
    "Ruin Sentinel": dict(desc="a ruin sentinel", look=(131, 79, 79, 79, 79, 0), corpse=18074, hp=300, xp=140, speed=85,
                          race="undead", attacks=[("melee", 0, -70)], armor=25, defense=25,
                          loot=[(GOLD, 100000, 45), (3352, 6000, 1), (3274, 5000, 1)], elements={"physical": 10, "holy": -15}),
    "Ruin Archer": dict(desc="a ruin archer", look=(129, 79, 79, 79, 79, 0), corpse=18138, hp=220, xp=120, speed=95,
                        race="undead", attacks=[("melee", 0, -20), ("arrow", 0, -60, 6)], armor=12, defense=12, dist=4,
                        loot=[(GOLD, 100000, 40), (3447, 30000, 15), (3350, 3000, 1)], elements={"holy": -15}),
    # ---------------------------------------------------------------- Floor 1 apex spawn (Contested)
    "Stonehorn Ram": dict(desc="a stonehorn ram", look=(607,), corpse=20996, hp=900, xp=480, speed=120, race="blood",
                          attacks=[("melee", 0, -120), ("charge", 0, -150, 4)], armor=30, defense=28, heal=(0.05, 6000),
                          loot=[(GOLD, 100000, 100), (PLAT, 30000, 2), (266, 20000, 3), (268, 20000, 3)],
                          voices=["BAAAH!"]),
    # ---------------------------------------------------------------- Floor 1 bosses (behaviour scripts: tasks 1.18 / 1.19)
    "Gate Hound": dict(desc="the Gate Hound", look=(240,), corpse=6331, hp=4000, xp=2500, speed=150, race="fire",
                       attacks=[("melee", 0, -180), ("howl", -80, -160, 2)], armor=35, defense=35, boss=True,
                       loot=[(GOLD, 100000, 100), (PLAT, 100000, 10), (266, 100000, 5)], voices=["GRRROOOAAARRR!"],
                       summons=[("Meadow Wolf", 3)], elements={"fire": 80, "ice": -10},
                       events=["SpireBossHealth", "SpireBossDeath", "SpireBossThink"]),
    "Axe-Lord of the Stair": dict(desc="the Axe-Lord of the Stair", look=(131, 94, 114, 94, 114, 3), corpse=18074,
                                  hp=12000, xp=8000, speed=130, race="blood",
                                  attacks=[("melee", 0, -260), ("cleave", -150, -300, 1)], armor=45, defense=45, boss=True,
                                  loot=[(GOLD, 100000, 100), (PLAT, 100000, 40), (266, 100000, 10), (268, 100000, 10)],
                                  voices=["The stair is mine!", "None shall climb!"], summons=[("Ruin Sentinel", 2)],
                                  elements={"physical": 10},
                                  events=["SpireBossHealth", "SpireBossDeath", "SpireBossThink"]),
    # ---------------------------------------------------------------- secret bosses (DESIGN.md 8.1)
    "Old Tusk": dict(desc="Old Tusk", look=(119,), corpse=6046, hp=1800, xp=900, speed=125, race="blood",
                     attacks=[("melee", 0, -140), ("charge", -60, -160, 4)], armor=25, defense=25,
                     loot=[(GOLD, 100000, 100), (PLAT, 100000, 5), (3582, 100000, 5), (236, 50000, 2)],
                     voices=["HRRROOONK!"]),
    # ---------------------------------------------------------------- spell summons (DESIGN.md 5.3b)
    "Ember Sprite": dict(desc="an ember sprite", look=(49,), corpse=0, hp=300, xp=0, speed=150, race="fire",
                         attacks=[("melee", 0, -40), ("fire", -20, -60, 4)], armor=10, defense=10, summon=True,
                         loot=[], elements={"fire": 100, "ice": -20}),
    "Wolf Companion": dict(desc="a wolf companion", look=(27,), corpse=0, hp=400, xp=0, speed=160, race="blood",
                           attacks=[("melee", 0, -50)], armor=15, defense=15, summon=True, loot=[]),
}

ELEMENTS = ["physical", "energy", "earth", "fire", "lifedrain", "manadrain", "drown", "ice", "holy", "death"]
SPELL = {
    "earth": ('name = "combat", type = COMBAT_EARTHDAMAGE', "CONST_ANI_EARTH", "CONST_ME_CARNIPHILA"),
    "energy": ('name = "combat", type = COMBAT_ENERGYDAMAGE', "CONST_ANI_ENERGY", "CONST_ME_ENERGYHIT"),
    "physical": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', "CONST_ANI_THROWINGKNIFE", "CONST_ME_HITAREA"),
    "fire": ('name = "combat", type = COMBAT_FIREDAMAGE', "CONST_ANI_FIRE", "CONST_ME_FIREAREA"),
    "arrow": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', "CONST_ANI_ARROW", "CONST_ME_HITAREA"),
    "charge": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_GROUNDSHAKER"),
    "howl": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_SOUND_RED"),
    "cleave": ('name = "combat", type = COMBAT_PHYSICALDAMAGE', None, "CONST_ME_HITAREA"),
}


def lua_name(name):
    return name.lower().replace("-", "_").replace(" ", "_").replace("'", "")


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
         "monster.changeTarget = { interval = 4000, chance = %d }" % (20 if boss else 0),
         "monster.strategiesTarget = { nearest = 100 }", "",
         "monster.flags = {",
         f"\tsummonable = {str(d.get('summon', False)).lower()}, attackable = true, hostile = true, convinceable = false, pushable = false,",
         f"\trewardBoss = false, illusionable = false, canPushItems = {str(boss).lower()}, canPushCreatures = {str(boss).lower()},",
         f"\tstaticAttackChance = 90, targetDistance = {d.get('dist', 1)}, runHealth = 0, healthHidden = false, isBlockable = false,",
         "\tcanWalkOnEnergy = false, canWalkOnFire = false, canWalkOnPoison = false,",
         "}", "", "monster.light = { level = 0, color = 0 }", ""]
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
    events = ["SpireBuffDamage"] + d.get("events", [])
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
            elif kind == "cleave":
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


def main():
    folder = OUT / "floor1"
    folder.mkdir(parents=True, exist_ok=True)
    for f in folder.glob("*.lua"):
        f.unlink()
    for name, d in MONSTERS.items():
        (folder / f"{lua_name(name)}.lua").write_text(render(name, d))
    print(f"wrote {len(MONSTERS)} monsters to {folder}")


if __name__ == "__main__":
    main()
