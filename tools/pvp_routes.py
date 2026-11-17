#!/usr/bin/env python3
"""Bot-vs-bot PvP spell test (DESIGN.md 6.7): writes the routes, then plays each scenario with two clients at once.

  python tools/pvp_routes.py            write tools/autopilot_routes/pvpt_*.json
  python tools/pvp_routes.py --run      also play every scenario (needs the server running) and print the trace

Scenarios (target bot first, attacker bot 6 s later):
  1-4  each class casts every attack spell at a player (damage should be about half a full hit; only the Vanguard's
       Iron Reach and Shield Bash may move a player; roots hold about a second, then 4 s of immunity)
  5    a target that casts Quickstep the moment it is held (haste breaks roots)
  6    Undying Oath, then 60 health for ~2.5 s while a player strikes every 2.2 s: survives on 1 health
  7    Lifeseed, the same: should die (Lifeseed only saves from monsters). The targets never turn the trace on,
       because the trace refills whoever casts.
  8    Wild PvP arena event: holds at full strength, no immunity, pushes move players
The barrier rune checks ride along: the Arcanist makes and uses one, the Ranger is refused.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "tools" / "autopilot_routes"
TGT, ATK = [1159, 1366, 7], [1159, 1368, 7]           # open road north of the spell-test spot, 2 tiles apart
NEXT = [1159, 1367, 7]                                 # right next to the target
ARENA_T, ARENA_A = [1030, 1022, 11], [1030, 1024, 11]


def cast(text, name, target=True, face=None, gap=3.0, shots=(0.0,), note=None):
    return {"do": "cast", "text": text, "target": "player" if target else False, "face": "target" if face else None,
            "shots": list(shots), "gap": gap, "name": "pvpt_" + name, "note": note or text}


def say(t):
    return {"do": "say", "text": t}


def jump(p, note=None):
    return {"do": "jump", "to": p, "note": note} if note else {"do": "jump", "to": p}


def wait(s):
    return {"do": "wait", "seconds": s}


def target_route(char, seconds, extra=()):
    steps = [jump(TGT, "target"), say("/pilot clear"), say("/pilot pardon"), {"do": "heal"}] + list(extra)
    t = 0
    while t < seconds:
        steps += [wait(10), {"do": "heal"}]
        t += 11
    return {"character": char, "steps": steps + [say("/pilot pardon"), say("/pilot logout")]}


def attacker(char, spells, extra_end=()):
    steps = [jump(ATK, "attacker"), wait(3), say("/pilot trace on"), say("/pilot pardon")]
    for sp in spells:
        if isinstance(sp, dict):
            steps.append(sp)
        else:
            text, face = (sp[1:], True) if sp.startswith(">") else (sp, False)
            steps.append(cast(text, text.replace(" ", "_"), face=face))
    steps += list(extra_end) + [wait(3), say("/pilot trace off"), say("/pilot pardon"), say("/pilot logout")]
    return {"character": char, "steps": steps}


ADJ = [jump(NEXT), wait(1.5)]
BACK = [jump(ATK), wait(1.5)]

SCENARIOS = {
 "1_arcanist": (target_route("Spell Vanguard", 120), attacker("Spell Arcanist", [
     "ember strike", "volt strike", "forked arc", ">fireburst wave", "ember barrage", ">arc beam", "emberfield",
     "searing brand", "gravity well", "stormcall", "skybrand", "inferno core", "cinder lance", "meteor rain",
     ">arc cataclysm", "storm lash", "worldfire", *ADJ, cast("repulse", "repulse", target=False, note="Repulse must not move a player"), *BACK],
     extra_end=[say("/pilot give 3147, 2"), cast("conjure barrier rune", "conjure_barrier", target=False),
                {"do": "cast", "text": "turn", "dir": "south", "shots": [], "gap": 0.5, "name": "turn", "note": "face south"},
                {"do": "rune", "id": 3180, "ahead": 2, "note": "Arcanist uses the barrier rune"}, {"do": "shot", "name": "pvpt_barrier_arcanist"}])),
 "2_ranger": (target_route("Spell Vanguard", 110), attacker("Spell Ranger", [
     "piercing shot", "double nock", ">scatter shot", "recoil shot", "snare", "ambush shot", "ricochet", "radiant shot",
     "mercy shot", "sunburst volley", "rapid volley", "falling star", ">dawnpiercer", ">pinning volley", "lightrain",
     "constellation", *ADJ, cast("scatterwind", "scatterwind", target=False, note="Scatterwind must not move a player"), *BACK],
     extra_end=[say("/pilot give 3180, 1"),
                {"do": "cast", "text": "turn", "dir": "south", "shots": [], "gap": 0.5, "name": "turn", "note": "face south"},
                {"do": "rune", "id": 3180, "ahead": 2, "note": "a Ranger may not use the barrier rune"}, {"do": "shot", "name": "pvpt_barrier_ranger"}])),
 "3_mystic": (target_route("Spell Vanguard", 100), attacker("Spell Mystic", [
     "frost strike", "sapdrain", "thorn strike", "hailshards", ">frost wave", "bramble patch",
     cast("rimebind", "rimebind", gap=2.3, note="Rimebind: root a player (about 1 s)"),
     cast("overgrowth", "overgrowth", target=False, note="Overgrowth right after: the player is immune"),
     ">tidecrash", "thornfield", "glacier core", "icefall", "winters breath"])),
 "4_vanguard": (target_route("Spell Ranger", 100), attacker("Spell Vanguard", [
     "iron reach", "heavy strike", "rending blow", "bloodoath strike", "sunder", "final verdict", "skyrend",
     cast("whirlwind", "whirlwind", target=False), ">faultline", "shield bash", "vault strike", "mountainbreaker"])),
 "5_haste_counter": ({"character": "Spell Vanguard", "steps": [jump(TGT, "target"), say("/pilot clear"), say("/pilot pardon"),
                      {"do": "heal"}, say("/pilot trace on"), {"do": "react", "text": "quickstep", "seconds": 60},
                      say("/pilot trace off"), say("/pilot logout")]},
                     attacker("Spell Ranger", [cast("snare", "snare_" + str(i), gap=10.5) for i in range(4)])),
 "6_undying": ({"character": "Spell Vanguard", "noPotions": True, "steps": [jump(TGT, "target"), say("/pilot clear"), say("/pilot pardon"), {"do": "heal"},
                wait(9), say("undying oath"), say("/pilot hp 60"), wait(1), {"do": "heal"},
                wait(4), say("/pilot logout")]},
               attacker("Spell Arcanist", [cast("ember strike", "undying_" + str(i), gap=2.2) for i in range(12)])),
 "7_lifeseed": ({"character": "Spell Mystic", "noPotions": True, "steps": [jump(TGT, "target"), say("/pilot clear"), say("/pilot pardon"), {"do": "heal"},
                 wait(9), say("lifeseed"), say("/pilot hp 60"), wait(1), {"do": "heal"}, wait(4), say("/pilot logout")]},
                attacker("Spell Arcanist", [cast("ember strike", "lifeseed_" + str(i), gap=2.2) for i in range(12)])),
 "8_wild_arena": ({"character": "Spell Vanguard", "steps": [jump(TGT, "target"), say("/pilot pardon"), {"do": "heal"}, say("/pilot arena join"),
                   wait(14), jump(ARENA_T), wait(40), say("/pilot logout")]},
                  {"character": "Spell Mystic", "steps": [jump(ATK), wait(2), say("/pilot arena join"), say("/pilot arena go"), wait(2),
                   jump(ARENA_A), wait(2), say("/pilot trace on"),
                   cast("rimebind", "wild_rimebind", gap=2.3, note="Wild PvP: Rimebind holds the full 3 s"),
                   cast("overgrowth", "wild_overgrowth", target=False, note="Wild PvP: no immunity, held again"),
                   cast("tidecrash", "wild_tidecrash", face=True, note="Wild PvP: the wave pushes a player"),
                   cast("bramble patch", "wild_bramble", note="Wild PvP: thorns slow a player"),
                   wait(3), say("/pilot trace off"), say("/pilot arena stop"), say("/pilot pardon"), say("/pilot logout")]}),
}


def write():
    for name, (tgt, atk) in SCENARIOS.items():
        for role, r in (("target", tgt), ("attacker", atk)):
            r = dict(r, name=f"pvpt_{name}_{role}", about="Bot-vs-bot PvP test (tools/pvp_routes.py)", timeout=300)
            (R / f"pvpt_{name}_{role}.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
    print(f"wrote {len(SCENARIOS) * 2} routes")


def run():
    for name in SCENARIOS:
        print(f"\n===== {name}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "pvp_duel.py"), f"pvpt_{name}_target", f"pvpt_{name}_attacker"])


if __name__ == "__main__":
    write()
    if "--run" in sys.argv:
        run()
