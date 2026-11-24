#!/usr/bin/env python3
"""Writes tools/autopilot_routes/playthrough_<class>.json: a whole Floor 1 run for one class.

A fresh level 2 Pilot arrives, talks to Guide Pell, does the tutorial pen, then hunts every Floor 1 ground at that
ground's middle level (set with /pilot level, so the run tests each place rather than the hours of walking between
them), gets Captain Dorrow's weapon at level 10, and tries the Gate Hound and the Axe-Lord. The autopilot logs
experience, kills, damage taken and loot per step, so each ground gets an experience-per-hour and a danger number.
Run:  python tools/autopilot.py playthrough_ranger
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "autopilot_routes"

CLASSES = {  # route name: (character, Dorrow's weapon word, Dorrow's weapon item id)
    "ranger": ("Pilot Ranger", "bow", 3350),
    "vanguard": ("Pilot Vanguard", "sword", 3264),
    "arcanist": ("Pilot Arcanist", "wand", 3074),
    "mystic": ("Pilot Mystic", "rod", 3066),
}
# The Registrar's starter kit (npc/registrar.lua): the Pilots already have a vocation, so they never meet him
KIT = {
    "ranger": [(3350, 1, "left"), (3447, 200, "ammo")],
    "vanguard": [(3264, 1, "left"), (3412, 1, "right")],
    "arcanist": [(3074, 1, "left")],
    "mystic": [(3066, 1, "left")],
}
COMMON = [(3361, 1, "body"), (3355, 1, "head"), (3559, 1, "legs"), (3552, 1, "feet"), (266, 10, None), (268, 10, None)]

# ground id, title, level to test it at (the middle of its band in maps/floor1_plan.py)
GROUNDS = [
    ("starter_west", "Ratwarren", 3),
    ("starter_east", "Toad Pond", 5),
    ("starter_south", "Sproutling Glade", 7),
    ("wasp_fields", "Waspgrass Fields", 9),
    ("boar_meadow", "Boar Meadow", 12),
    ("burrow_hills", "Burrow Hills", 13),
    ("wolf_copse", "Wolf Copse", 15),
    ("reed_marsh", "Reedmarsh", 16),
    ("thornsnap_hollow", "Thornsnap Hollow", 17),
    ("shard_fields", "Shard Fields", 20),
    ("bandit_road", "Bandit Road", 23),
    ("old_quarry", "Old Quarry", 26),
]


# Arcanist and Mystic (2026-11-23): Boar Meadow skipped (two Pilots died at its gate on the old map), the bosses before
# the old loop grounds, which are 3-5x over the danger budget and likely to end the run
# (Wolf Copse and Reedmarsh were rebuilt the same night: the autopilot plans on the repo's map, so they are left out
# until the server runs the new map.)
_SAFE_FIRST = ["starter_west", "starter_east", "starter_south", "wasp_fields", "burrow_hills", "BOSSES",
               "thornsnap_hollow", "shard_fields", "bandit_road", "old_quarry"]
ORDERS = {"arcanist": _SAFE_FIRST, "mystic": _SAFE_FIRST}
REBUILT = {"starter_west", "starter_east", "starter_south", "wasp_fields", "burrow_hills"}  # the rest still name corners


def hunt_ground(gid, title, level):
    a, b = ("a", "b") if gid in REBUILT else ("nw", "se")
    return [
        {"do": "say", "text": f"/pilot level {level}"},
        {"do": "jump", "to": f"gate_{gid}", "note": f"{title} (level {level}): gate"},
        {"do": "heal"},
        {"do": "shot", "name": f"{gid}_gate"},
        {"do": "walk", "to": f"loop_{gid}_{a}", "fight": True, "timeout": 60, "note": f"{title} (level {level}): route A"},
        {"do": "hunt", "seconds": 75, "radius": 7},
        {"do": "shot", "name": f"{gid}_a"},
        {"do": "walk", "to": f"loop_{gid}_{b}", "fight": True, "timeout": 60, "note": f"{title} (level {level}): route B"},
        {"do": "hunt", "seconds": 75, "radius": 7},
    ]


def route(key, char, word, wid, order=None):
    kit = []
    for iid, n, slot in KIT[key] + COMMON:
        kit.append({"do": "say", "text": f"/pilot give {iid}, {n}", "note": "Arrival"})
        if slot:
            kit.append({"do": "equip", "id": iid, "slot": slot})
    s = [
        {"do": "say", "text": "/pilot gearreset", "note": "Arrival"},
    ] + kit + [
        {"do": "jump", "to": "tutorial_spawn", "note": "Arrival"},
        {"do": "shot", "name": "arrival"},
        {"do": "say", "text": "hi"},
        {"do": "wait", "seconds": 2},
        {"do": "npc", "text": "quest"},
        {"do": "wait", "seconds": 2},
        {"do": "npc", "text": "yes"},
        {"do": "wait", "seconds": 2},
        {"do": "npc", "text": "hunt"},
        {"do": "wait", "seconds": 2},
        {"do": "shot", "name": "pell"},
        {"do": "npc", "text": "bye"},
        {"do": "walk", "to": "tutorial_pen", "fight": True, "timeout": 40, "note": "Tutorial pen (level 2)"},
        {"do": "hunt", "seconds": 40, "radius": 6},
        {"do": "jump", "to": "tutorial_spawn", "note": "Tutorial pen (level 2)"},
        {"do": "say", "text": "hi"},
        {"do": "wait", "seconds": 2},
        {"do": "npc", "text": "report"},
        {"do": "wait", "seconds": 2},
        {"do": "npc", "text": "bye"},
    ]
    grounds = GROUNDS if order is None else [g for k in order for g in GROUNDS if g[0] == k]
    boss_steps = boss_part()
    for i, (gid, title, level) in enumerate(grounds):
        if gid == "BOSSES":
            continue
        if level >= 10 and (i == 0 or grounds[i - 1][2] < 10):  # Captain Dorrow's weapon at level 10, before the first level 10+ ground
            s += [
                {"do": "say", "text": "/pilot level 10", "note": "Captain Dorrow (level 10)"},
                {"do": "jump", "to": [1235, 1246, 7], "note": "Captain Dorrow (level 10)"},
                {"do": "say", "text": "hi"},
                {"do": "wait", "seconds": 2},
                {"do": "npc", "text": "weapon"},
                {"do": "wait", "seconds": 2},
                {"do": "npc", "text": word},
                {"do": "wait", "seconds": 2},
                {"do": "equip", "id": wid, "slot": "left"},
                {"do": "npc", "text": "quest"},
                {"do": "wait", "seconds": 2},
                {"do": "npc", "text": "bye"},
                {"do": "say", "text": "!upgrade"},
                {"do": "wait", "seconds": 2},
                {"do": "shot", "name": "upgrade_tab_l10"},
            ]
        s += hunt_ground(gid, title, level)
        if order is not None and gid == order[order.index("BOSSES") - 1]:
            s += boss_steps                       # the bosses before the risky old grounds (a death ends a run)
    if order is None:
        s += boss_steps
    s += [
        {"do": "say", "text": "!upgrade", "note": "End"},
        {"do": "wait", "seconds": 2},
        {"do": "shot", "name": "upgrade_tab_end"},
        {"do": "say", "text": "/pilot logout", "note": "End"},
    ]
    return {"name": f"playthrough_{key}", "character": char, "timeout": 3300,
            "about": f"A whole Floor 1 run as {char} (tools/make_playthrough_routes.py).", "steps": s}


def boss_part():
    return [
        {"do": "say", "text": "/pilot level 24", "note": "Gate Hound (level 24)"},
        {"do": "jump", "to": [1232, 1084, 7], "note": "Gate Hound (level 24)"},
        {"do": "heal"},
        {"do": "hunt", "seconds": 90, "radius": 9},
        {"do": "shot", "name": "gate_hound"},
        {"do": "say", "text": "/pilot level 32", "note": "Old Watchtower (level 32)"},
        {"do": "jump", "to": "apex_watchtower", "note": "Old Watchtower (level 32)"},
        {"do": "heal"},
        {"do": "shot", "name": "watchtower"},
        {"do": "hunt", "seconds": 90, "radius": 7},
        {"do": "say", "text": "/pilot level 30", "note": "Axe-Lord (level 30)"},
        {"do": "jump", "to": "boss_room_floor1", "note": "Axe-Lord (level 30)"},
        {"do": "heal"},
        {"do": "shot", "name": "axe_lord_room"},
        {"do": "hunt", "seconds": 90, "radius": 9},
        {"do": "shot", "name": "axe_lord_after"},
    ]


if __name__ == "__main__":
    for key, (char, word, wid) in CLASSES.items():
        (OUT / f"playthrough_{key}.json").write_text(json.dumps(route(key, char, word, wid, ORDERS.get(key)), indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(CLASSES)} playthrough routes")
