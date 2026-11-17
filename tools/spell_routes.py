#!/usr/bin/env python3
"""Write one autopilot route per vocation that casts EVERY spell it has in the real client (task J13b).

  python tools/spell_routes.py                  write tools/autopilot_routes/spells_<vocation>.json
  python tools/autopilot.py spells_arcanist     play one (needs the server running)
  python tools/spell_routes.py --report         after a run: one line per spell from the server's [SPELLTRACE] log

The route jumps a level 300 "Spell <Vocation>" tester (server/sql/dev_accounts.sql) to open ground, turns on the
spell trace (/pilot trace on: the server logs what every cast did and refills the caster; Lost Arts allowed),
surrounds it with sturdy monsters and casts each spell in unlock order. Screenshots are timed to each spell's
style: staged areas get three, delayed strikes wait for the landing, forms and banners get a late one too.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPELLS = ROOT / "server" / "data-spirebound" / "lib" / "spirebound" / "spells.lua"
ROUTES = ROOT / "tools" / "autopilot_routes"
VOCS = {"A": ("arcanist", 1), "M": ("mystic", 2), "R": ("ranger", 3), "V": ("vanguard", 4)}
SPOT = "centre_boar_meadow"
TARGET_MONSTER, TARGETS, TARGET_HP = "Bristle Boar", 6, 60000
NEEDS_TARGET = {"attack_target", "root", "mark", "pull_target", "gravity"}
ON_TARGET = {"target1", "target2", "target3"}
DIRECTIONAL = {"wave", "beam", "beam7", "bigbeam"}


def rows():
    out = []
    for line in SPELLS.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\s*\{ name = "([^"]+)", words = "([^"]+)", voc = (\{ [^}]* \}|"all"), level = (\{[^}]*\}|\d+)', line)
        if not m:
            continue
        name, words, voc, level = m.groups()
        get = lambda k: (re.search(r'\b%s = "?([\w.]+)"?' % k, line) or [None, None])[1]
        lv = {v: int(n) for v, n in re.findall(r"\[(\w)\] = (\d+)", level)} if level.startswith("{") else int(level)
        vocs = list(VOCS) if voc == '"all"' else re.findall(r"\b([AMRV])\b", voc)
        out.append({"name": name, "words": words, "vocs": vocs, "level": lv, "kind": get("kind"), "area": get("area"),
                    "anim": get("anim"), "delay": get("delay"), "at": get("at"), "lost": "lostArt" in line})
    return out


def cast_step(r, char):
    words = r["words"]
    if r["kind"] == "find_person":
        words += ' "%s"' % char
    elif r["kind"] == "levitate":
        words += " up"
    target = r["kind"] in NEEDS_TARGET or r["area"] in ON_TARGET or r["at"] == "target"
    if r["delay"]:
        shots = [0.25, 1.2, 1.6]
    elif r["anim"]:
        shots = [0.0, 0.3, 0.7]
    elif r["kind"] in ("form", "banner", "zone", "trail_dash", "heal_zone"):
        shots = [0.25, 1.5, 3.0]
    else:
        shots = [0.0, 0.35]
    gap = max(2.4, shots[-1] + 0.4)
    face = "target" if r["area"] in DIRECTIONAL else ("away" if r["kind"] in ("trail_dash", "blink") else None)
    return {"do": "cast", "text": words, "target": target, "face": face, "shots": shots, "gap": gap,
            "name": "spell_" + re.sub(r"\W+", "_", r["name"].lower()).strip("_"), "note": r["name"]}


def route(code):
    voc, vid = VOCS[code]
    char = "Spell " + voc.title()
    mine = [r for r in rows() if code in r["vocs"]]
    lvl = lambda r: r["level"][code] if isinstance(r["level"], dict) else r["level"]
    mine.sort(key=lambda r: (lvl(r), r["name"]))
    spawn = {"do": "say", "text": f"/pilot spawn {TARGET_MONSTER}, {TARGETS}, {TARGET_HP}"}
    steps = [{"do": "jump", "to": SPOT, "note": "setup"}, {"do": "say", "text": "/pilot trace on"},
             {"do": "say", "text": "/pilot clear"}, {"do": "say", "text": "/pilot give 3147, 10"}, spawn,
             {"do": "wait", "seconds": 2}, {"do": "shot", "name": f"spells_{voc}_start"}]
    for i, r in enumerate(mine):
        if i and i % 5 == 0:
            steps.append(dict(spawn, note=r["name"]))
        steps.append(cast_step(r, char))
        if r["kind"] in ("summon", "decoy"):           # never let the test target its own companion
            steps.append({"do": "wait", "seconds": 1.5})
            steps.append({"do": "say", "text": "/pilot unsummon"})
    steps += [{"do": "wait", "seconds": 3, "note": "end"}, {"do": "say", "text": "/pilot clear"}, {"do": "say", "text": "/pilot trace off"}, {"do": "say", "text": "/pilot logout"}]
    seconds = sum(s.get("gap", 2) for s in steps) + 120
    return {"name": f"spells_{voc}", "about": f"Casts every {voc} spell ({len(mine)}) in the real client with screenshots; "
            "read the result with: python tools/spell_routes.py --report", "character": char,
            "timeout": int(seconds), "steps": steps}, len(mine)


def report():
    log = ROOT / ".local" / "server.log"
    if not log.exists():
        sys.exit("no .local/server.log (the server writes it while it runs)")
    lines = [ln.split("[SPELLTRACE] ", 1)[1] for ln in log.read_text(encoding="utf-8", errors="replace").splitlines()
             if "[SPELLTRACE]" in ln]
    for ln in lines:
        print(ln)
    refused = [ln for ln in lines if "REFUSED" in ln]
    print(f"\n{len(lines)} casts traced, {len(refused)} refused")


def main(argv):
    if "--report" in argv:
        return report()
    ROUTES.mkdir(exist_ok=True)
    for code in VOCS:
        r, n = route(code)
        (ROUTES / f"{r['name']}.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
        print(f"{r['name']}: {n} spells, {len(r['steps'])} steps, up to {r['timeout']} s")


if __name__ == "__main__":
    main(sys.argv[1:])
