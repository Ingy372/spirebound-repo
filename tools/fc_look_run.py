#!/usr/bin/env python3
"""FD1b check: Pilot Scout plays chapter 4 of the First Climb with the wreath (Agna's wreath laid on Brother Tam's
grave), and Pilot Sage looks at Pilot Scout: the look line should show chapter 4's choice and the Oathroom chest
(Pilot Scout took a chest in tools/oath_run.py; run that first).  python tools/fc_look_run.py   (server running)

Chapters 1-3 are marked done with /pilot quest (they were played through on 2026-11-27, route fc_story); chapter 4
itself goes through Maren, the grave and the wreath for real.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import party_run as PR  # noqa: E402

MAREN = [1229, 1278, 7]
GRAVE = [1047, 1338, 7]


def say(t, w=1.5):
    return [{"do": "say", "text": t}, {"do": "wait", "seconds": w}]


def npc(*words):
    out = [{"do": "jump", "to": MAREN, "note": "Archivist Maren"}, {"do": "wait", "seconds": 1}] + say("hi", 2)
    for w in words:
        out += [{"do": "npc", "text": w}, {"do": "wait", "seconds": 2}]
    return out + [{"do": "npc", "text": "bye"}]


def scout():
    s = say("/pilot level 15") + say("/pilot quest fc1 3") + say("/pilot quest fc2 3") + say("/pilot quest fc3 3")
    s += say("/pilot quest fc4 -1") + say("/pilot emptybag")
    s += npc("quest", "yes")
    s += [{"do": "jump", "to": [GRAVE[0], GRAVE[1] + 1, 7], "note": "Brother Tam's grave"}, {"do": "wait", "seconds": 2},
          {"do": "use", "at": GRAVE}, {"do": "wait", "seconds": 3}, {"do": "inventory"},
          {"do": "useitem", "id": 2981, "on": GRAVE, "note": "lay Agna's wreath on the grave"}, {"do": "wait", "seconds": 3},
          {"do": "shot", "name": "fc_wreath"}]
    s += npc("report")
    s += [{"do": "jump", "to": [MAREN[0] + 1, MAREN[1] + 1, 7], "note": "stand still to be looked at"},
          {"do": "wait", "seconds": 100, "note": "done"}]
    return s


def sage():
    return [{"do": "wait", "seconds": 70}, {"do": "jump", "to": [MAREN[0] + 2, MAREN[1] + 2, 7], "note": "beside Pilot Scout"},
            {"do": "wait", "seconds": 4}, {"do": "look", "name": "Pilot Scout"}, {"do": "wait", "seconds": 3},
            {"do": "shot", "name": "fc_look"}, {"do": "look", "name": "Pilot Scout", "note": "again"},
            {"do": "wait", "seconds": 3, "note": "done"}]


def main():
    import shutil
    shutil.copytree(PR.ROOT / "client" / "modules" / "game_autopilot", PR.CLIENT / "modules" / "game_autopilot", dirs_exist_ok=True)
    mark = len(PR.server_text())
    PR.start("Pilot Scout", scout(), mark)
    time.sleep(3)
    PR.start("Pilot Sage", sage(), mark)
    end = time.time() + 600
    while time.time() < end and not all(PR.done(n) for n in ("Pilot Scout", "Pilot Sage")):
        time.sleep(5)
    for n in ("Pilot Scout", "Pilot Sage"):
        f = PR.LOGS / PR.logname(n)
        t = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
        print(f"--- {n}")
        for line in t.splitlines():
            if any(k in line for k in ("First Climb", "wreath", "Tam", "You see", "record:", "Keepsake", "title", "looked", "look:")):
                print("   " + line.strip()[:220])


if __name__ == "__main__":
    main()
