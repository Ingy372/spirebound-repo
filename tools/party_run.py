#!/usr/bin/env python3
"""Several test characters in one party, in the real client (roadmap S4; rehearsal for N1, the real party clear).

  python tools/party_run.py [cellar|watchtower] [--level N]      (needs the server running)

Starts one client per Pilot character (tools/autopilot.py runs one at a time; this works like tools/pvp_duel.py).
They meet at the ground's hub, form a party the way players do (the leader invites from the client, the others accept,
shared experience on), go into the group ground together and hunt it. Each client keeps its own log
(autopilot_log_party_<name>.txt in the client's settings folder); the report at the end lists, per character, the
party state, kills, experience gained, lowest health and deaths.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIENT = ROOT / ".local" / "client"
RUN = CLIENT / "modules" / "game_autopilot" / "run.json"
LOG = ROOT / ".local" / "server.log"
LOGS = Path(os.environ.get("APPDATA", "")) / "otcr" / "otclient" / "otclient"
sys.path.insert(0, str(ROOT / "tools"))

LEADER = "Pilot Vanguard"
MEMBERS = ["Pilot Warden", "Pilot Scout", "Pilot Sage", "Pilot Healer"]
# the server lets 2 characters per account be online, so the party is spread over three test accounts (dev_accounts.sql)
ACCOUNT = {"Pilot Scout": "autopilot2@localhost", "Pilot Sage": "autopilot2@localhost", "Pilot Healer": "autopilot3@localhost"}

# where to meet, where to go in, and the spots to hunt round (world coordinates; from world_points.lua)
PLACES = {
    "cellar": dict(title="the Smugglers' Cellar", level=26, meet="camp_bandit_road", landing=[1353, 1207, 8],
                   spots=[[1342, 1212, 8], [1365, 1212, 8], [1353, 1185, 8]]),
    "watchtower": dict(title="the Old Watchtower", level=34, meet="apex_watchtower", landing=None, spots=[]),
    # P1 / N1 rehearsal (2026-11-26): the Floor 1 bosses. The Gate Hound is a field boss at the Pass; the Axe-Lord's hall
    # needs the Stair Key, which the test grants with /pilot stairkey (the real path is N1's job).
    "gatehound": dict(title="the Gate Hound", level=30, meet="gate_pass_1", landing=None, spots=[[1232, 1076, 7]], hunt=240),
    "axelord": dict(title="the Axe-Lord of the Stair", level=34, meet="boss_room_exit", landing=[1231, 1031, 4],
                    spots=[[1231, 1026, 4]], hunt=360, stairkey=True),
}


def points():
    txt = (ROOT / "server" / "data-spirebound" / "lib" / "spirebound" / "world_points.lua").read_text(encoding="utf-8")
    return {k: [int(x), int(y), int(z)] for k, x, y, z in re.findall(r'\["(\w+)"\] = Position\((\d+), (\d+), (\d+)\)', txt)}


def route(name, place, level):
    p = PLACES[place]
    pts = points()
    meet = pts[p["meet"]]
    off = ([LEADER] + MEMBERS).index(name)
    here = [meet[0] - 2 + off, meet[1] - 1, meet[2]]           # side by side at the hub, all in sight of each other
    steps = [{"do": "say", "text": "/pilot heal"}, {"do": "say", "text": f"/pilot level {level}"},
             {"do": "say", "text": "/pilot give 266, 40"}, {"do": "say", "text": "/pilot give 268, 40"}]
    if name == "Pilot Scout":
        steps.append({"do": "say", "text": "/pilot kit"})
    if p.get("stairkey"):
        steps.append({"do": "say", "text": "/pilot stairkey"})
    steps += [{"do": "jump", "to": here, "note": "meet at the hub"}, {"do": "wait", "seconds": 4}]
    if name == LEADER:
        steps += [{"do": "wait", "seconds": 25},
                  {"do": "party", "invite": MEMBERS, "share": True, "seconds": 60, "note": "form the party"}]
    else:
        steps += [{"do": "party", "join": LEADER, "seconds": 90, "note": "form the party"}]
    steps += [{"do": "shot", "name": f"party_{place}_formed_{name.split()[-1].lower()}"},
              {"do": "wait", "seconds": 8 if name == LEADER else 4}]
    if p["landing"]:
        land = list(p["landing"])
        land[0] += off - 2
        steps += [{"do": "jump", "to": land, "note": f"into {p['title']}"}, {"do": "wait", "seconds": 3}]
    for k, spot in enumerate(p["spots"]):
        steps += [{"do": "walk", "to": spot, "fight": True, "timeout": 90, "note": f"{p['title']}: spot {k + 1}"},
                  {"do": "hunt", "seconds": p.get("hunt", 90), "radius": 8},
                  {"do": "shot", "name": f"party_{place}_{k + 1}_{name.split()[-1].lower()}"}]
    steps += [{"do": "wait", "seconds": 5, "note": "done"}]
    return steps


def server_text():
    return LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""


def wait_for(text, secs, start=0):
    end = time.time() + secs
    while time.time() < end:
        if text in server_text()[start:]:
            return True
        time.sleep(1)
    return False


def logname(name):
    return f"autopilot_log_party_{name.split()[-1].lower()}.txt"


def start(name, steps, mark):
    (LOGS / logname(name)).unlink(missing_ok=True)
    RUN.write_text(json.dumps({"name": "party_" + name, "account": ACCOUNT.get(name, "autopilot@localhost"), "password": "spirebound",
                               "character": name, "log": logname(name), "exit": True, "steps": steps}))
    subprocess.Popen([str(CLIENT / "otclient.exe")], cwd=str(CLIENT))
    ok = wait_for(f"{name} has logged in", 60, mark)
    time.sleep(2)
    RUN.unlink(missing_ok=True)
    print(f"{name}: {'logged in' if ok else 'DID NOT LOG IN'}", flush=True)


def done(name):
    f = LOGS / logname(name)
    return f.exists() and " DONE " in f.read_text(encoding="utf-8", errors="replace")


def report(name):
    f = LOGS / logname(name)
    if not f.exists():
        return f"{name:15s} no log"
    t = f.read_text(encoding="utf-8", errors="replace")
    formed = "formed" if "party: formed" in t else "NOT formed"
    xp = sum(int(x) for x in re.findall(r"You gained (\d+) experience", t))
    whole = re.findall(r"WHOLE RUN: (.*)", t)
    died = "DIED" if " DEATH " in t else "alive"
    return f"{name:15s} party {formed:10s} {died:6s} xp +{xp:<7d} {whole[-1] if whole else ''}"


def main(argv):
    place = next((a for a in argv if a in PLACES), "cellar")
    level = next((int(a.split("=")[1]) for a in argv if a.startswith("--level=")), PLACES[place]["level"])
    shutil.copytree(ROOT / "client" / "modules" / "game_autopilot", CLIENT / "modules" / "game_autopilot", dirs_exist_ok=True)
    mark = len(server_text())
    names = [LEADER] + MEMBERS
    for n in names:
        start(n, route(n, place, level), mark)
        time.sleep(3)
    end = time.time() + 1200
    while time.time() < end and not all(done(n) for n in names):
        time.sleep(5)
    print(f"\nPARTY RUN at {PLACES[place]['title']} (level {level}):")
    for n in names:
        print("  " + report(n))
    for line in server_text()[mark:].splitlines():
        if "DIED" in line or "party" in line.lower():
            print("  server: " + line.split("] ", 2)[-1])


if __name__ == "__main__":
    main(sys.argv[1:])
