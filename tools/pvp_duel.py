#!/usr/bin/env python3
"""Two test characters online at once for PvP spell checks (DESIGN 6.7): the Spell Ranger stands still and the
Spell Vanguard pulls it with Iron Reach and knocks it back with Shield Bash.

  python tools/pvp_duel.py          (needs the server running; prints the server trace)

tools/autopilot.py runs one client at a time, so this starts both clients itself; each keeps its own log
(autopilot_log_<route>.txt in the client's settings folder; the Ranger's has its position every 2 s).
"""
import json, subprocess, time, sys
from pathlib import Path
ROOT = Path(r"C:\Users\Muth3\Desktop\spirebound-repo")
CLIENT = ROOT / ".local" / "client"
RUN = CLIENT / "modules" / "game_autopilot" / "run.json"
LOG = ROOT / ".local" / "server.log"
def wait_for(text, secs):
    t = time.time() + secs
    while time.time() < t:
        if text in LOG.read_text(encoding="utf-8", errors="replace"):
            return True
        time.sleep(1)
    return False
import shutil
shutil.copytree(ROOT / "client/modules/game_autopilot", CLIENT / "modules/game_autopilot", dirs_exist_ok=True)

def start(route):
    r = json.loads((ROOT / "tools/autopilot_routes" / f"{route}.json").read_text())
    RUN.write_text(json.dumps({"name": route, "account": "autopilot@localhost", "password": "spirebound", "character": r["character"], "log": f"autopilot_log_{route}.txt", "exit": True, "steps": r["steps"]}))
    subprocess.Popen([str(CLIENT / "otclient.exe")], cwd=str(CLIENT))
    ok = wait_for(f"{r['character']} has logged in", 60)
    time.sleep(2)
    RUN.unlink(missing_ok=True)
    print(route, "logged in" if ok else "DID NOT LOG IN", flush=True)
start("pvp_duel_ranger")
time.sleep(6)
start("pvp_duel_vanguard")
time.sleep(40)
for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
    if "SPELLTRACE] Spell Vanguard" in line or "Spell Vanguard has" in line or "Spell Ranger has" in line:
        print(line.split("] ", 2)[-1])
