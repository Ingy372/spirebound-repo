#!/usr/bin/env python3
"""Four Pilots clear the Oathroom through the real door (roadmap FD3).  python tools/oath_run.py   (server running)

Starts one client per Pilot (as tools/party_run.py does). They form a party, stand on the four oath stones in the Old
Quarry, the leader pulls the lever, and inside they hold the Captain's line, split into pairs for the Scout's levers,
walk the Keeper's rune floor (the test fixes the safe path to the middle stone with /story oathsafe, and one Pilot
steps on a wrong stone first to see it hurt), break the Oathkeeper while two of them put out braziers, and each takes
a different chest. The report lists, per Pilot, deaths, the server lines about the hall, and the chest taken.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import party_run as PR  # noqa: E402  (client start-up, logs and waiting are the same as the party runs)

TEAM = ["Pilot Vanguard", "Pilot Warden", "Pilot Scout", "Pilot Healer"]
CHEST = {"Pilot Vanguard": "captain", "Pilot Warden": "scout", "Pilot Scout": "keeper", "Pilot Healer": "healer"}


def P():
    return PR.points()


def say(t, w=1.0):
    return [{"do": "say", "text": t}, {"do": "wait", "seconds": w}]


def walk(to, note, t=60, fight=True, tries=1):
    """a walk; through a gate that may still be shut, try again a few times (the gates open as the team goes on)"""
    out = []
    for k in range(tries):
        out += [{"do": "walk", "to": to, "fight": fight, "timeout": t, "note": note + ("" if k == 0 else " (again)")}]
        if k < tries - 1:
            out += [{"do": "hunt", "seconds": 8, "radius": 4}]
    return out


def use(at, n=1, gap=6):
    out = []
    for _ in range(n):
        out += [{"do": "use", "at": at}, {"do": "wait", "seconds": gap}]
    return out


def route(name):
    p = P()
    i = TEAM.index(name)
    tile = p[f"oath_tile_{i + 1}"]
    lever = p["oath_lever"]
    arrival = p["oath_arrival"]
    ax, ay, z = arrival
    steps = say("/pilot emptybag") + say("/pilot heal") + say("/pilot level 30") + say("/story reset") \
        + say("/pilot gear 3") + say("/pilot give 266, 40") + say("/pilot give 268, 40")
    if name == "Pilot Scout":
        steps += say("/pilot kit")
    steps += [{"do": "jump", "to": [tile[0], tile[1] - 1, 7], "note": "meet at the oath stones"}, {"do": "wait", "seconds": 4}]
    if i == 0:
        steps += [{"do": "wait", "seconds": 30}, {"do": "party", "invite": TEAM[1:], "share": True, "seconds": 60, "note": "form the party"}]
    else:
        steps += [{"do": "party", "join": TEAM[0], "seconds": 100, "note": "form the party"}]
    steps += walk(tile, "onto oath stone %d" % (i + 1), 10, False, 2)
    # stay on the stone until the team is inside (quarry monsters wander past and pull fighters off it); the last one
    # pulls the lever every 9 seconds until all four stand (the door says "3 of 4 are standing" until then)
    hold = {"do": "until", "text": "inside the First Climb's oath hall", "seconds": 240, "every": 9, "hold": list(tile),
            "note": "on the stone until the lever takes us in"}
    if i == 3:
        hold["use"] = list(lever)
        steps += [{"do": "shot", "name": "oath_door"}]
    steps += [hold]
    if i == 3:
        steps += say("/story oathsafe", 1)
    # the Captain's hall: hold in front of the line (the line is 5 tiles in from the west end)
    line = p["oath_line"]
    steps += walk([line[0] + 3 + (i % 2), ay - 1 + i, z], "hold the line", 15, True, 5) + [{"do": "hunt", "seconds": 240, "radius": 9}]
    if i == 0:
        steps += [{"do": "shot", "name": "oath_captain"}]
    steps += say("/pilot heal")
    # the Scout's hall: Vanguard + Warden north, Scout + Healer south; levers SUN (N1), MOON (S1), STAR (N2), FLAME (S2)
    north = i in (0, 1)
    l1, l2, l3, l4 = (p[f"oath_lever_l{k}"] for k in (1, 2, 3, 4))
    gx = p["oath_gate_g1"][0]
    steps += walk([gx + 3, ay - 3 if north else ay + 3, z], "into the Scout's hall", 25, True, 5)
    if i == 0:      # SUN
        steps += walk([l1[0] - 1, l1[1] + 1, z], "to the SUN lever", 20, True, 5) + use(l1, 3, 5) + [{"do": "hunt", "seconds": 15, "radius": 4}]
        steps += walk([l3[0] - 1, l3[1] + 1, z], "to the STAR lever", 20, True, 5) + use(l3, 5, 5)
    elif i == 2:    # MOON
        steps += walk([l2[0] - 1, l2[1] - 1, z], "to the MOON lever", 20, True, 5) + [{"do": "wait", "seconds": 8}] + use(l2, 6, 5)
        steps += [{"do": "hunt", "seconds": 10, "radius": 4}]
        steps += walk([l4[0] - 1, l4[1] - 1, z], "to the FLAME lever", 20, True, 5) + use(l4, 8, 5)
    else:           # the partners fight beside them
        lv = l1 if north else l2
        steps += walk([lv[0] - 2, lv[1] + (1 if north else -1), z], "beside the partner", 20, True, 5) + [{"do": "hunt", "seconds": 25, "radius": 4}]
        lv = l3 if north else l4
        steps += walk([lv[0] - 2, lv[1] + (1 if north else -1), z], "beside the partner (second room)", 20, True, 5) + [{"do": "hunt", "seconds": 35, "radius": 4}]
    # the Keeper's hall: read the lectern, then the middle lane (one Pilot first steps on a wrong stone)
    lec = p["oath_lectern"]
    runes = p["oath_runes"]
    steps += walk([lec[0], lec[1] + 1, z], "to the Keeper's lectern", 20, True, 6) + use(lec, 1, 3)
    if i == 0:
        steps += [{"do": "shot", "name": "oath_lectern"}]
    if i == 1:
        steps += walk([runes[0], runes[1], z], "a wrong rune (top lane)", 10, False) + [{"do": "wait", "seconds": 3}]
    for r in range(9):
        steps += walk([runes[0] + r, runes[1] + 2, z], f"rune row {r + 1}", 10, False)
    steps += [{"do": "wait", "seconds": 4 + 2 * i}]
    # the Healer's hall
    boss = p["oath_boss"]
    steps += walk([boss[0] - 3, boss[1] + (i - 1), z], "into the Healer's hall", 20, True, 3)
    if i in (1, 3):     # Warden puts out braziers 1 and 2 (north), the Healer 3 and 4 (south)
        b = [p["oath_brazier_1"], p["oath_brazier_2"]] if i == 1 else [p["oath_brazier_3"], p["oath_brazier_4"]]
        for k, br in enumerate(b):
            stand = [br[0], br[1] + (1 if i == 1 else -1), z]
            steps += walk(stand, f"put out a brazier ({k + 1})", 20, False) + [{"do": "wait", "seconds": 8}]
    steps += [{"do": "hunt", "seconds": 240, "radius": 10}]
    if i == 0:
        steps += [{"do": "shot", "name": "oath_boss"}]
    # the reward room: one chest each, then out through the light
    chest = p["oath_chest_" + CHEST[name]]
    steps += walk([chest[0], chest[1] + 1, z], "to " + CHEST[name] + "'s chest", 20, False, 6) + use(chest, 1, 3)
    steps += [{"do": "shot", "name": "oath_chest_" + CHEST[name]}]
    steps += walk(list(p["oath_exit_reward"]), "out through the light", 20, False) + [{"do": "wait", "seconds": 4}]
    steps += [{"do": "wait", "seconds": 3, "note": "done"}]
    return steps


def main():
    import shutil
    shutil.copytree(PR.ROOT / "client" / "modules" / "game_autopilot", PR.CLIENT / "modules" / "game_autopilot", dirs_exist_ok=True)
    PR.MEMBERS[:] = TEAM[1:]
    PR.LEADER = TEAM[0]
    mark = len(PR.server_text())
    for n in TEAM:
        PR.start(n, route(n), mark)
        time.sleep(3)
    end = time.time() + 1800
    while time.time() < end and not all(PR.done(n) for n in TEAM):
        time.sleep(5)
    print("\nOATHROOM RUN:")
    for n in TEAM:
        print("  " + PR.report(n))
        f = PR.LOGS / PR.logname(n)
        t = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
        for line in re.findall(r"[^\n]*(?:oath|Oath|line|lever|rune|brazier|chest|Keeper|Captain|Scout|Healer)[^\n]*", t):
            if "msg" in line or "message" in line.lower() or ":" in line:
                print("     " + line.strip()[:160])
    for line in PR.server_text()[mark:].splitlines():
        if "DIED" in line or "oath" in line.lower():
            print("  server: " + line.split("] ", 2)[-1])


if __name__ == "__main__":
    main()
