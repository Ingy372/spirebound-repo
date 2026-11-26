#!/usr/bin/env python3
"""Gear and weapon progression data (docs/superpowers/specs/2026-11-23-gear-progression-design.md).

One table for every Spirebound weapon, armour piece, shop starter piece, tier token (Hearth Shards) and style tree,
plus the numbers behind them. tools/balance.py --check enforces the ceiling rule, the shop rule and the pacing.

Weapon power is a damage multiplier on everything the holder deals (melee, arrows, spells, sword skills):
    power = (1 + base + tier * TIER_STEP + awakening) * (1 + FAM_BONUS * familiarity)
Familiarity (0-10) and style (3 stages x 10 levels) are counted in raw monster experience (before stages and bonuses).

Run: python tools/gen_gear.py   (writes server/data-spirebound/lib/spirebound/gear_data.lua and data/item_renames.json)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCANIST, MYSTIC, RANGER, VANGUARD = 1, 2, 3, 4

MAX_TIER = 5
FAM_BONUS = 0.015              # +1.5% damage per familiarity level (spec 4.3)
FAM_HOURS_PER_LEVEL = 0.35     # model hours of hunting at the weapon's floor per familiarity level (10 = 3.5 h)
F2_SHARE = 0.925               # a new weapon is 92.5% of a maxed weapon from the floor below (spec: 90-95%)

# per floor: the main weapon's base bonus, the bonus per tier, the awakening bonus (floor 1 is set; the rest follow
# the ceiling rule from the floor below)
FLOOR1 = dict(base=0.10, step=0.04, awaken=0.10)
STEP_GROWTH, AWAKEN_GROWTH = 1.5, 1.5
SHOP_BONUS = 0.08              # shop starter weapon (spec 4.9): better than NPC gear (0), below Floor 1 tier 2


def floor_numbers(n):
    """(base, step, awaken) for floor n's weapons."""
    base, step, awaken = FLOOR1["base"], FLOOR1["step"], FLOOR1["awaken"]
    for _ in range(1, n):
        top = (1 + base + MAX_TIER * step + awaken) * (1 + FAM_BONUS * 10)
        base = F2_SHARE * top - 1
        step, awaken = step * STEP_GROWTH, awaken * AWAKEN_GROWTH
    return base, step, awaken


def weapon_power(floor, tier, fam, awakened):
    base, step, awaken = floor_numbers(floor)
    return (1 + base + tier * step + (awaken if awakened else 0)) * (1 + FAM_BONUS * fam)


def shop_power():
    return 1 + SHOP_BONUS


# ---------------------------------------------------------------- weapons and armour
# (id, name, floor, vocation, family, source, base item id, awakened name)
# source: main = the floor's quest weapon (pick a family), drop = a rare alternative from the floor's harder monsters
WEAPONS = [
    ("f1_vanguard_sword", "Hearthguard Sword", 1, VANGUARD, "sword", "main", 3264, "Stairlord's Edge"),
    ("f1_vanguard_axe", "Hearthguard Axe", 1, VANGUARD, "axe", "main", 3274, "Stairlord's Cleaver"),
    ("f1_vanguard_club", "Hearthguard Mace", 1, VANGUARD, "club", "main", 3286, "Stairlord's Maul"),
    ("f1_ranger_bow", "Trailwarden Bow", 1, RANGER, "bow", "main", 3350, "Stair-Iron Longbow"),
    ("f1_ranger_crossbow", "Trailwarden Crossbow", 1, RANGER, "crossbow", "main", 3349, "Stair-Iron Crossbow"),
    ("f1_arcanist_wand", "Wand of Hearth Sparks", 1, ARCANIST, "wand", "main", 3074, "Wand of the Long Stair"),
    ("f1_mystic_rod", "Reedroot Rod", 1, MYSTIC, "rod", "main", 3066, "Rod of the Long Stair"),
    ("f1_vanguard_drop", "Briarguard Sabre", 1, VANGUARD, "sword", "drop", 3273, "Briarguard Sabre, Awakened"),
    ("f1_ranger_drop", "Copsewood Bow", 1, RANGER, "bow", "drop", 3350, "Copsewood Bow, Awakened"),
    ("f1_arcanist_drop", "Wand of Ember Script", 1, ARCANIST, "wand", "drop", 3074, "Wand of Ember Script, Awakened"),
    ("f1_mystic_drop", "Thornward Rod", 1, MYSTIC, "rod", "drop", 3066, "Thornward Rod, Awakened"),
    # Floor 2: two or three choices per class (spec 4.6)
    ("f2_vanguard_main", "Highland Edge", 2, VANGUARD, "sword", "main", 3271, "Aurochs-Crown Blade"),
    ("f2_vanguard_axe", "Hornbreaker Axe", 2, VANGUARD, "axe", "main", 3274, "Aurochs-Crown Axe"),
    ("f2_vanguard_drop", "Mesa Warhammer", 2, VANGUARD, "club", "drop", 3286, "Mesa Warhammer, Awakened"),
    ("f2_ranger_main", "Ridgecat Longbow", 2, RANGER, "bow", "main", 3350, "Crowned Longbow"),
    ("f2_ranger_cross", "Strider Arbalest", 2, RANGER, "crossbow", "main", 3349, "Crowned Arbalest"),
    ("f2_ranger_drop", "Mesa Recurve", 2, RANGER, "bow", "drop", 3350, "Mesa Recurve, Awakened"),
    ("f2_arcanist_main", "Wand of Dust Storms", 2, ARCANIST, "wand", "main", 3073, "Wand of the Crowned Herd"),
    ("f2_arcanist_drop", "Wand of Mesa Lightning", 2, ARCANIST, "wand", "drop", 3073, "Wand of Mesa Lightning, Awakened"),
    ("f2_mystic_main", "Highwind Rod", 2, MYSTIC, "rod", "main", 3067, "Rod of the Crowned Herd"),
    ("f2_mystic_drop", "Grazer-Bone Rod", 2, MYSTIC, "rod", "drop", 3067, "Grazer-Bone Rod, Awakened"),
]
# a rare drop starts like the main weapon, with a different small bonus (spec 4.5)
DROP_PERK = {VANGUARD: ("life_leech", 0.02), RANGER: ("crit", 0.03), ARCANIST: ("mana_leech", 0.02), MYSTIC: ("heal", 0.04)}
DROP_FROM = {1: ["Bandit Captain", "Grey Alpha", "Ruin Sentinel", "Stonehorn Ram"], 2: ["Herd Bull", "Stonehide Bull", "Mesa Wyrmling"]}
DROP_CHANCE = 0.03

# (id, name, floor, vocation, source, base item id, armour bonus)
ARMOUR = [
    ("f1_vanguard_armour", "Hearthward Mail", 1, VANGUARD, "quest", 3359, 2),
    ("f1_ranger_armour", "Trailwarden Greaves", 1, RANGER, "quest", 3372, 2),
    ("f1_arcanist_armour", "Millward Mantle", 1, ARCANIST, "quest", 3361, 3),
    ("f1_mystic_armour", "Thornward Robe", 1, MYSTIC, "quest", 3361, 3),
    ("f2_vanguard_armour", "Hornbreaker Plate", 2, VANGUARD, "quest", 3357, 2),
    ("f2_ranger_armour", "Strider Leggings", 2, RANGER, "quest", 3362, 2),
    ("f2_arcanist_armour", "Mesa-Weave Coat", 2, ARCANIST, "quest", 3378, 2),
    ("f2_mystic_armour", "Grazer-Hide Coat", 2, MYSTIC, "quest", 3378, 2),
]
TIER_ARMOR = {1: 1, 2: 2}     # armour points per tier

# shop starter set (spec 4.9): (vocation, weapon base, weapon name, armour base, armour name, armour bonus)
SHOP = [
    (VANGUARD, 3264, "Climber's Sword", 3359, "Climber's Mail", 1),
    (RANGER, 3350, "Climber's Bow", 3372, "Climber's Greaves", 1),
    (ARCANIST, 3074, "Climber's Wand", 3361, "Climber's Mantle", 1),
    (MYSTIC, 3066, "Climber's Rod", 3361, "Climber's Robe", 1),
]

# ---------------------------------------------------------------- tier tokens (spec 4.4)
TOKENS = {
    1: dict(rough=(16124, "rough Hearth Shard", "rough Hearth Shards", "Dropped by every monster on Floor 1's hunting grounds."),
            cut=(16119, "cut Hearth Shard", "cut Hearth Shards", "Dropped on Floor 1's harder grounds: Wolf Copse, Reedmarsh, Thornsnap Hollow, Shard Fields, the Bandit Road, the Old Quarry, and their caves."),
            flawless=(16120, "flawless Hearth Shard", "flawless Hearth Shards", "Dropped by Floor 1's elites (Grey Alpha, Bandit Captain), in the Old Watchtower and on group grounds.")),
    2: dict(rough=(16122, "rough Highland Shard", "rough Highland Shards", "Dropped by every monster on Floor 2's hunting grounds."),
            cut=(16121, "cut Highland Shard", "cut Highland Shards", "Dropped on Floor 2's harder grounds and caves."),
            flawless=(16127, "flawless Highland Shard", "flawless Highland Shards", "Dropped by Floor 2's elites and on its group grounds.")),
}
# tier t needs 3 shards of this grade plus gold (spec 4.4); gold per floor = fee * floor
TIER_COST = {1: ("rough", 500), 2: ("rough", 1000), 3: ("cut", 2000), 4: ("cut", 3500), 5: ("flawless", 6000)}
SHARDS_PER_TIER = 3
# Floor Beacons (DESIGN 3.6, roadmap M1): the token that lights a town Beacon's fire bowl (server: lib/spirebound/beacons.lua)
BEACON_EMBER = (9636, "Beacon Ember", "Beacon Embers",
                "Light a fire bowl of a town's Beacon with it: +5% experience and loot for everyone on that floor for an hour. "
                "Dropped by field bosses, hidden beasts, and sometimes elites and apex monsters.")
# Spire Chronicle (DESIGN 4, roadmap M3): the house trophy for finishing a season's Chronicle (lib/spirebound/chronicle.lua)
CHRONICLE_CUP = (5805, "Chronicle Cup", "Chronicle Cups",
                 "Awarded for finishing a season's Spire Chronicle. It looks best on a shelf in your house.")
RESPEC_ITEM = (28650, "Mastery Respec Scroll", "Mastery Respec Scrolls",
               "Use it to choose your style again: your Mastery points stay. Sold only in the shop; one use.")
CUT_FROM_LEVEL = 12            # Floor 1 grounds whose lowest level is 12 or more drop cut shards
FLAWLESS_MONSTERS = {1: ["Grey Alpha", "Bandit Captain", "Stonehorn Ram", "Old Bristleback", "Moonhowl", "Mossback Snapper",
                         "Blackthorn", "Prism Shardling", "Granite Warden"]}
NO_SHARDS = {"Pen Rat"}       # the Arrival Yard's tutorial rats
REFORGE_FEE = 1000             # change family at the Weaponsmith (per floor of the weapon); tier kept, familiarity 0
REISSUE_FEE = 2000             # a lost main weapon replaced by its quest giver (per floor), tier 0


def shard_monsters():
    """{monster: [grades]} on Floor 1: rough everywhere, cut where a monster only lives on grounds from level 12 up,
    flawless on elites and the apex (spec 4.4)."""
    sys.path[:0] = [str(ROOT / "maps")]
    from floor1_plan import CAMPS
    lowest = {}
    for c in CAMPS:
        for name in {m[0] for m in c.get("mix", [])}:
            lowest[name] = min(lowest.get(name, 99), c["levels"][0])
    for name in FLAWLESS_MONSTERS[1]:
        lowest.setdefault(name, 99)
    out = {}
    for name, lo in lowest.items():
        if name in NO_SHARDS:
            continue
        grades = ["rough"]
        if lo >= CUT_FROM_LEVEL:
            grades.append("cut")
        if name in FLAWLESS_MONSTERS[1]:
            grades.append("flawless")
        out[name] = grades
    return out

# ---------------------------------------------------------------- style trees (spec 4.2; names are Claude's call)
STYLE = {
    VANGUARD: ("vanguard", "Vanguard Mastery", [
        ("bulwark", "Bulwark", "tank, protects the party", [("aegis_warden", "Aegis Warden"), ("ironwall", "Ironwall")]),
        ("reaver", "Reaver", "melee damage", [("bloodedge", "Bloodedge"), ("stormbreaker", "Stormbreaker")])]),
    RANGER: ("ranger", "Ranger Mastery", [
        ("marksman", "Marksman", "long-range single target", [("deadeye", "Deadeye"), ("volley_captain", "Volley Captain")]),
        ("trapper", "Trapper", "slows and ground control", [("snareweaver", "Snareweaver"), ("pathfinder", "Pathfinder")])]),
    ARCANIST: ("arcanist", "Arcanist Mastery", [
        ("emberwright", "Emberwright", "fire, burst", [("cinderheart", "Cinderheart"), ("ashwalker", "Ashwalker")]),
        ("stormbinder", "Stormbinder", "lightning, chains", [("tempest", "Tempest"), ("spellbreaker", "Spellbreaker")])]),
    MYSTIC: ("mystic", "Mystic Mastery", [
        ("lifebinder", "Lifebinder", "healing", [("dawnmender", "Dawnmender"), ("wardkeeper", "Wardkeeper")]),
        ("wildcaller", "Wildcaller", "nature damage", [("rootcaller", "Rootcaller"), ("frostwarden", "Frostwarden")])]),
}
# passive per style level: (kind, value per level). kinds are read by lib/spirebound/style.lua
PASSIVES = {
    "vanguard": ("damage", 0.005), "ranger": ("damage", 0.005), "arcanist": ("damage", 0.005), "mystic": ("damage", 0.005),
    "bulwark": ("taken", 0.006), "reaver": ("damage", 0.008),
    "marksman": ("far_damage", 0.01), "trapper": ("damage", 0.006),
    "emberwright": ("damage", 0.008), "stormbinder": ("damage", 0.007),
    "lifebinder": ("heal", 0.01), "wildcaller": ("damage", 0.008),
    "aegis_warden": ("taken", 0.008), "ironwall": ("taken", 0.01), "bloodedge": ("damage", 0.01), "stormbreaker": ("damage", 0.01),
    "deadeye": ("far_damage", 0.012), "volley_captain": ("damage", 0.01), "snareweaver": ("damage", 0.008), "pathfinder": ("speed", 2),
    "cinderheart": ("damage", 0.012), "ashwalker": ("damage", 0.01), "tempest": ("damage", 0.01), "spellbreaker": ("damage", 0.008),
    "dawnmender": ("heal", 0.012), "wardkeeper": ("taken", 0.008), "rootcaller": ("damage", 0.01), "frostwarden": ("damage", 0.009),
}
STAGE_END_LEVEL = {1: 37, 2: 110, 3: 275}   # character level at which each style stage finishes (spec pacing)


# ---------------------------------------------------------------- the hunting model (shared with tools/balance.py)
def _model():
    sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "maps")]
    import balance
    return balance


def raw_xp_to(level):
    """Raw monster experience (before stages) a character earns climbing from level 1 to `level`."""
    b = _model()
    return sum((b.xp_for(l + 1) - b.xp_for(l)) / b.stage(l) for l in range(1, level))


def style_thresholds():
    """30 cumulative raw-experience thresholds: style stage s level k needs STYLE_POINTS[(s-1)*10+k-1]."""
    out, prev = [], 0
    for s in (1, 2, 3):
        end = raw_xp_to(STAGE_END_LEVEL[s])
        out += [round(prev + (end - prev) * k / 10) for k in range(1, 11)]
        prev = end
    return out


def style_stage_level(stage):
    """The character level at which style stage `stage` finishes (inverse of raw_xp_to)."""
    goal, lvl = style_thresholds()[stage * 10 - 1], 1
    while raw_xp_to(lvl) < goal:
        lvl += 1
    return lvl


def floor_raw_xp_per_hour(n):
    """Raw monster experience per hour at floor n's middle level (balance.py's own model)."""
    b = _model()
    monsters, floors, *_ = b.load_game()
    lo, hi = floors[n]["band"]
    mid = (lo + hi) // 2
    rates = []
    for name in floors[n]["camp"]:
        m = monsters[name]
        rates.append(m["xp"] * b.kills_per_hour(m["hp"], mid))
    return sum(rates) / len(rates)


def fam_thresholds(n):
    per_hour = floor_raw_xp_per_hour(n)
    return [round(per_hour * FAM_HOURS_PER_LEVEL * k) for k in range(1, 11)]


def hours_to_pass(n):
    """Hours of hunting on floor n until a new floor-n weapon (familiarity only) beats a maxed floor n-1 weapon."""
    old = weapon_power(n - 1, MAX_TIER, 10, True)
    for k in range(0, 11):
        if weapon_power(n, 0, k, False) > old:
            return k * FAM_HOURS_PER_LEVEL
    return 99


def floor1_kills(lo, hi):
    """Expected kills while levelling from lo to hi on Floor 1 (the economy model's grounds, by level)."""
    b = _model()
    camps = b.floor1_camps()   # monster -> (kills/h, gold/h, low level)
    monsters, *_ = b.load_game()
    total = 0.0
    for l in range(lo, hi):
        name = max((m for m, c in camps.items() if c[2] <= l), key=lambda m: camps[m][2])
        kph = camps[name][0]
        total += (b.xp_for(l + 1) - b.xp_for(l)) / (monsters[name]["xp"] * b.stage(l))
    return total


# shard chances per kill (spec 4.4): solve so a solo player who saves every shard gets enough for tier 5 by ~level 32
SHARD_TARGET = {"rough": (10, 28, 2 * SHARDS_PER_TIER), "cut": (14, 31, 2 * SHARDS_PER_TIER), "flawless": (22, 33, SHARDS_PER_TIER)}
FLAWLESS_SHARE = 0.08          # in the model, about 1 kill in 12 on the harder grounds is an elite or a group-ground monster


def shard_chances():
    out = {}
    for grade, (lo, hi, need) in SHARD_TARGET.items():
        kills = floor1_kills(lo, hi) * (FLAWLESS_SHARE if grade == "flawless" else 1)
        out[grade] = min(1.0, need * 1.25 / kills)   # 25% spare: armour tiers and some to sell
    return out


def shard_tier5_level():
    """Level at which the expected shards cover a weapon's tier 1-5 for a solo player who keeps them all."""
    ch = shard_chances()
    for lvl in range(12, 60):
        got = {g: floor1_kills(SHARD_TARGET[g][0], lvl) * ch[g] * (FLAWLESS_SHARE if g == "flawless" else 1) for g in ch}
        if all(got[g] >= (2 if g != "flawless" else 1) * SHARDS_PER_TIER for g in got):
            return lvl
    return 99


# ---------------------------------------------------------------- output
def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    L = ["-- GENERATED by tools/gen_gear.py (gear progression, docs/superpowers/specs/2026-11-23-gear-progression-design.md).",
         "-- Do not edit by hand.", "SpireGearData = {}", f"SpireGearData.MAX_TIER = {MAX_TIER}",
         f"SpireGearData.FAM_BONUS = {FAM_BONUS}", f"SpireGearData.SHARDS_PER_TIER = {SHARDS_PER_TIER}",
         f"SpireGearData.DROP_CHANCE = {DROP_CHANCE}"]
    L.append("SpireGearData.floor = {")
    for n in (1, 2):
        base, step, awaken = floor_numbers(n)
        L.append(f"\t[{n}] = {{ base = {base:.4f}, step = {step:.4f}, awaken = {awaken:.4f}, armorStep = {TIER_ARMOR[n]} }},")
    L.append("}")
    L.append("SpireGearData.weapons = {")
    for wid, name, fl, voc, fam, src, base, awake in WEAPONS:
        perk = DROP_PERK[voc] if src == "drop" else None
        p = f', perk = "{perk[0]}", perkValue = {perk[1]}' if perk else ""
        L.append(f'\t{{ id = "{wid}", name = {lua_str(name)}, floor = {fl}, vocation = {voc}, family = "{fam}", source = "{src}", base = {base}, awakenedName = {lua_str(awake)}{p} }},')
    L.append("}")
    L.append("SpireGearData.armour = {")
    for aid, name, fl, voc, src, base, bonus in ARMOUR:
        L.append(f'\t{{ id = "{aid}", name = {lua_str(name)}, floor = {fl}, vocation = {voc}, source = "{src}", base = {base}, bonus = {bonus} }},')
    L.append("}")
    L.append("SpireGearData.shop = {")
    for voc, wb, wn, ab, an, abon in SHOP:
        L.append(f'\t[{voc}] = {{ weapon = {{ id = "shop_weapon_{voc}", base = {wb}, name = {lua_str(wn)}, bonus = {SHOP_BONUS} }}, '
                 f'armour = {{ id = "shop_armour_{voc}", base = {ab}, name = {lua_str(an)}, bonus = {abon} }} }},')
    L.append("}")
    L.append("SpireGearData.dropFrom = {")
    for fl, names in DROP_FROM.items():
        L.append(f"\t[{fl}] = {{ " + ", ".join(lua_str(n) for n in names) + " },")
    L.append("}")
    L.append("SpireGearData.FAMILIARITY_POINTS = {")
    for n in (1, 2):
        L.append(f"\t[{n}] = {{ " + ", ".join(str(v) for v in fam_thresholds(n)) + " },")
    L.append("}")
    L.append("SpireGearData.tokens = {")
    for fl, grades in TOKENS.items():
        L.append(f"\t[{fl}] = {{ " + ", ".join(f"{g} = {v[0]}" for g, v in grades.items()) + " },")
    L.append("}")
    L.append("SpireGearData.tokenWhere = {")
    for fl, grades in TOKENS.items():
        for g, v in grades.items():
            L.append(f"\t[{v[0]}] = {lua_str(v[3])},")
    L.append("}")
    L.append("SpireGearData.TIER_COST = {")
    for t, (grade, gold) in TIER_COST.items():
        L.append(f'\t[{t}] = {{ grade = "{grade}", gold = {gold} }},')
    L.append("}")
    L.append("SpireGearData.style = {")
    for voc, (key, name, paths) in STYLE.items():
        ps = []
        for pk, pn, role, finals in paths:
            fs = ", ".join(f'{{ key = "{fk}", name = {lua_str(fn)} }}' for fk, fn in finals)
            ps.append(f'{{ key = "{pk}", name = {lua_str(pn)}, role = {lua_str(role)}, finals = {{ {fs} }} }}')
        L.append(f'\t[{voc}] = {{ key = "{key}", name = {lua_str(name)}, paths = {{ {", ".join(ps)} }} }},')
    L.append("}")
    L.append("SpireGearData.PASSIVES = {")
    for k, (kind, v) in PASSIVES.items():
        L.append(f'\t{k} = {{ kind = "{kind}", per = {v} }},')
    L.append("}")
    L.append("SpireGearData.STYLE_POINTS = { " + ", ".join(str(v) for v in style_thresholds()) + " }")
    L.append(f"SpireGearData.REFORGE_FEE = {REFORGE_FEE}")
    L.append(f"SpireGearData.REISSUE_FEE = {REISSUE_FEE}")
    L.append("SpireGearData.tokenNames = {")
    for fl, grades in TOKENS.items():
        for g, v in grades.items():
            L.append(f"	[{v[0]}] = {{ {lua_str(v[1])}, {lua_str(v[2])} }},")
    L.append("}")
    L.append("SpireGearData.shardMonsters = {")
    for name, grades in sorted(shard_monsters().items()):
        L.append(f"	[{lua_str(name)}] = {{ " + ", ".join(f"{g} = true" for g in grades) + " },")
    L.append("}")
    ch = shard_chances()
    L.append("SpireGearData.SHARD_CHANCE = { " + ", ".join(f"{g} = {v:.5f}" for g, v in ch.items()) + " }")
    out = ROOT / "server/data-spirebound/lib/spirebound/gear_data.lua"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    renames = {str(v[0]): dict(name=v[1], plural=v[2], description=v[3]) for g in TOKENS.values() for v in g.values()}
    renames[str(RESPEC_ITEM[0])] = dict(name=RESPEC_ITEM[1], plural=RESPEC_ITEM[2], description=RESPEC_ITEM[3])
    renames[str(CHRONICLE_CUP[0])] = dict(name=CHRONICLE_CUP[1], plural=CHRONICLE_CUP[2], description=CHRONICLE_CUP[3])
    renames[str(BEACON_EMBER[0])] = dict(name=BEACON_EMBER[1], plural=BEACON_EMBER[2], description=BEACON_EMBER[3])
    # our own corpses (art/CORPSE_RULES.md, Jay approved 2026-11-26): spare Tibia corpse chains drawn with our art
    # (CORPSE_ITEMS in tools/make_creature_sheets.py), renamed for the monsters that leave them
    corpses = [([13865, 13866, 13867, 13868], "broken stone guardian", "broken stone guardians",
                "Carved stone and a cracked spear, all that is left of a guardian of the old ruins."),
               ([12340, 12337, 12338, 12339], "fallen underkeeper", "fallen underkeepers",
                "Old bones, a cage-helm and a cold lantern, tangled in the chain he dragged."),
               ([10430, 10431, 10432, 10433], "faded vault wraith", "faded vault wraiths",
                "An empty purple shroud beside the strongbox it guarded."),
               ([9001, 9002, 9003, 9004], "slain gate hound", "slain gate hounds",
                "Three heads on the ground, each still in its spiked iron collar.")]
    for ids, name, plural, desc in corpses:
        for i in ids:
            renames[str(i)] = dict(name=name, plural=plural, description=desc)
    (ROOT / "data/item_renames.json").write_text(json.dumps(renames, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out.name}: {len(WEAPONS)} weapons, {len(ARMOUR)} armour, {len(SHOP)} shop sets; data/item_renames.json")
    print("shard chances per kill: " + ", ".join(f"{g} {v:.2%}" for g, v in ch.items()))


if __name__ == "__main__":
    main()
