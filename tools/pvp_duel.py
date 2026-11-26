#!/usr/bin/env python3
"""Two test characters online at once for PvP spell checks (DESIGN 6.7).

  python tools/pvp_duel.py <target_route> <attacker_route>      (needs the server running)
  python tools/pvp_duel.py                                       the first check: Iron Reach and Shield Bash

tools/autopilot.py runs one client at a time, so this starts both clients itself; each keeps its own log
(autopilot_log_<route>.txt in the client's settings folder). Prints the server's spell trace for the fight.
"""
from __future__ import annotations

import json
import os
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


def server_text():
    return LOG.read_text(encoding="utf-8", errors="replace")


def wait_for(text, secs, start=0):
    end = time.time() + secs
    while time.time() < end:
        if text in server_text()[start:]:
            return True
        time.sleep(1)
    return False


def start(route, mark):
    r = json.loads((ROOT / "tools" / "autopilot_routes" / f"{route}.json").read_text())
    (LOGS / f"autopilot_log_{route}.txt").unlink(missing_ok=True)
    RUN.write_text(json.dumps({"name": route, "account": "autopilot@localhost", "password": "spirebound",
                               "character": r["character"], "log": f"autopilot_log_{route}.txt", "exit": True, "noPotions": r.get("noPotions", False), "noSpells": True,
                               "steps": r["steps"]}))
    subprocess.Popen([str(CLIENT / "otclient.exe")], cwd=str(CLIENT))
    ok = wait_for(f"{r['character']} has logged in", 60, mark)
    time.sleep(2)
    RUN.unlink(missing_ok=True)
    print(f"{route}: {r['character']} {'logged in' if ok else 'DID NOT LOG IN'}", flush=True)
    return r


def done(route):
    f = LOGS / f"autopilot_log_{route}.txt"
    return f.exists() and " DONE " in f.read_text(encoding="utf-8", errors="replace")


def main(argv):
    target, attacker = (argv + ["pvp_duel_ranger", "pvp_duel_vanguard"])[:2] if len(argv) >= 2 else ("pvp_duel_ranger", "pvp_duel_vanguard")
    shutil.copytree(ROOT / "client" / "modules" / "game_autopilot", CLIENT / "modules" / "game_autopilot", dirs_exist_ok=True)
    mark = len(server_text())
    start(target, mark)
    time.sleep(6)
    start(attacker, mark)
    end = time.time() + 400
    while time.time() < end and not (done(target) and done(attacker)):
        time.sleep(3)
    time.sleep(3)
    for line in server_text()[mark:].splitlines():
        if "SPELLTRACE" in line or " has logged" in line or "DIED" in line:
            print("  " + line.split("] ", 2)[-1].replace("[SPELLTRACE] ", ""))
    for route in (target, attacker):
        f = LOGS / f"autopilot_log_{route}.txt"
        if f.exists():
            for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if ("message:" in ln and "pilot:" not in ln and "loses" not in ln and "healed" not in ln and "restored" not in ln) \
                        or "held:" in ln or "rune" in ln or "DONE" in ln or "dead" in ln.lower():
                    print(f"  [{route}] {ln.strip()}")


if __name__ == "__main__":
    main(sys.argv[1:])
