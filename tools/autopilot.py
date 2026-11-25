#!/usr/bin/env python3
"""Test autopilot: plays a test route in the real game client by itself and prints what happened.

    python tools/autopilot.py ratwarren                 run tools/autopilot_routes/ratwarren.json
    python tools/autopilot.py ratwarren --char "Pilot Ranger"
    python tools/autopilot.py ratwarren --plan-only     only print the planned steps

How it works:
  1. Reads the route (places may be world point names from world_points.lua, or [x, y, z]).
  2. Builds the Floor 1 map in memory and plans every walk as a chain of short hops along walkable tiles, so the
     character never needs to find a long path through map it has not seen yet ("down"/"up" use the stairs).
  3. Writes the run file into the installed client (.local/client/modules/game_autopilot/run.json), starts the client,
     and waits. The client module (client/modules/game_autopilot) logs in a Pilot test character on the local
     autopilot account, plays the steps, writes autopilot_log.txt and closes itself. The run file is deleted right after the
     client has read it, so Jay's own client never starts the autopilot.
  4. Prints the per-step summaries (monsters in sight, monsters next to you, damage, kills, potions) and where the full
     log and the screenshots are.

Needs the server running (windows\\Start-Spirebound.bat). Local testing only: the account is the public dev account.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))

CLIENT = ROOT / ".local" / "client"
MODULE_SRC = ROOT / "client" / "modules" / "game_autopilot"
MODULE_DST = CLIENT / "modules" / "game_autopilot"
ROUTES = ROOT / "tools" / "autopilot_routes"
ACCOUNT, PASSWORD = "autopilot@localhost", "spirebound"  # the public LOCAL test account (server/sql/dev_accounts.sql)
HOP = 6                                                 # tiles per walking hop
D8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


def world_points():
    text = (ROOT / "server/data-spirebound/lib/spirebound/world_points.lua").read_text(encoding="utf-8")
    return {k: (int(x), int(y), int(z)) for k, x, y, z in
            re.findall(r'\["([^"]+)"\]\s*=\s*Position\((\d+),\s*(\d+),\s*(\d+)\)', text)}


def place(v, wp):
    if isinstance(v, str):
        if v not in wp:
            sys.exit(f"autopilot: no world point called {v!r}")
        return wp[v]
    return tuple(v)


class Planner:
    """Walkable tiles of the real Floor 1 map, and shortest paths across them."""

    def __init__(self, wp):
        import hunt_check
        import wilds
        print("autopilot: building the map to plan the walks...", flush=True)
        self.m = hunt_check.build_map()
        self.block = wilds.blockers()
        self.walkable = wilds.walkable
        # never path across stairs or holes by accident
        self.avoid = set()
        for k, (x, y, z) in wp.items():
            if k.startswith(("stairs_", "ramp_")):     # a ramp is two tiles wide
                self.avoid |= {(x + 1, y, z), (x + 1, y, z - 1)} if k.startswith("ramp_") else set()
                self.avoid |= {(x, y, z), (x, y, z - 1)}

    def ok(self, p):
        return p not in self.avoid and self.walkable(self.m, p, self.block)

    def path(self, a, b, allow_end=False, lim=90):
        if a[2] != b[2]:
            return None
        prev, q = {a: None}, deque([a])
        while q:
            p = q.popleft()
            if p == b:
                break
            for dx, dy in D8:
                n = (p[0] + dx, p[1] + dy, p[2])
                if n in prev or abs(n[0] - a[0]) > lim or abs(n[1] - a[1]) > lim:
                    continue
                if self.ok(n) or (allow_end and n == b):
                    prev[n] = p
                    q.append(n)
        if b not in prev:
            return None
        out, p = [], b
        while p is not None:
            out.append(p)
            p = prev[p]
        return out[::-1]


def hops(path):
    pts = path[HOP::HOP]
    if not pts or pts[-1] != path[-1]:
        pts.append(path[-1])
    return pts


def plan_steps(route, wp, planner):
    """Expands walks into short hops and down/up into walking onto the stairs."""
    out, here, sec = [], None, "start"
    for s in route["steps"]:
        s = dict(s)
        d = s["do"]
        if s.get("note"):
            sec = s["note"]
        first = len(out)
        if d == "jump":
            here = place(s["to"], wp)
            out.append({"do": "jump", "to": list(here), "note": s.get("note")})
        elif d in ("walk", "down", "up"):
            if d == "walk":
                goal, end_z, arrive = place(s["to"], wp), None, None
            else:
                st = place(s["at"], wp)                 # the stairs-up (or ramp) tile on the lower level; ramps facing
                if isinstance(s["at"], str) and s["at"].endswith("_s"):   # south work the other way round
                    sys.exit("autopilot: south-facing ramps are not planned yet")
                if d == "down":
                    goal, end_z, arrive = (st[0], st[1], st[2] - 1), st[2], (st[0], st[1] + 1, st[2])
                else:
                    goal, end_z, arrive = st, st[2] - 1, (st[0], st[1] - 1, st[2] - 1)
            path = planner.path(here, goal, allow_end=end_z is not None) if here else None
            if path is None:
                print(f"autopilot: WARNING no walkable path from {here} to {goal}; the client will try directly")
                path = [goal]
            pts = hops(path)
            for i, p in enumerate(pts):
                last = i == len(pts) - 1
                step = {"do": "walk", "to": list(p), "fight": s.get("fight", True), "timeout": s.get("timeout", 60)}
                if last and end_z is not None:
                    step["arrive_z"] = end_z
                if last and s.get("note"):
                    step["note"] = s["note"]
                out.append(step)
            here = arrive or goal
        else:
            out.append({k: v for k, v in s.items()})
        for o in out[first:]:
            o["sec"] = sec
    return [{k: v for k, v in s.items() if v is not None} for s in out]


SUM = re.compile(r"step (\d+): in sight max (\d+) \(avg ([\d.]+)\), next to you max (\d+) \(avg ([\d.]+)\), damage taken (\d+), "
                 r"kills (\d+), potions (\d+), lowest health (\d+)%")
DONE = re.compile(r"== step (\d+) done in (\d+)s")


def report(lines, steps):
    """One line per place: the steps of a route that share a note."""
    took = {int(m.group(1)): int(m.group(2)) for m in map(DONE.search, lines) if m}
    order, by = [], {}
    for m in map(SUM.search, lines):
        if not m:
            continue
        i = int(m.group(1))
        sec = steps[i - 1].get("sec", "?") if i <= len(steps) else "?"
        if sec not in by:
            order.append(sec)
            by[sec] = dict(t=0, seen=0, avg=0.0, nxt=0, navg=0.0, dmg=0, kills=0, pots=0, hp=100)
        r, t = by[sec], max(1, took.get(i, 1))
        r["avg"] += float(m.group(3)) * t
        r["navg"] += float(m.group(5)) * t
        r["t"] += t
        r["seen"], r["nxt"] = max(r["seen"], int(m.group(2))), max(r["nxt"], int(m.group(4)))
        r["dmg"] += int(m.group(6)); r["kills"] += int(m.group(7)); r["pots"] += int(m.group(8))
        r["hp"] = min(r["hp"], int(m.group(9)))
    out = [f"{'place':34s} {'time':>5s} {'in sight':>12s} {'next to you':>12s} {'damage':>7s} {'kills':>5s} {'potions':>7s} {'lowest hp':>9s}"]
    for sec in order:
        r = by[sec]
        out.append(f"{sec[:34]:34s} {r['t']:4d}s {r['seen']:4d} (avg {r['avg'] / r['t']:.1f}) {r['nxt']:3d} (avg {r['navg'] / r['t']:.1f}) "
                   f"{r['dmg']:7d} {r['kills']:5d} {r['pots']:7d} {r['hp']:8d}%")
    return out


def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def write_dirs():
    base = Path(os.environ.get("APPDATA", "")) / "otcr"
    return [base] if base.exists() else []


def find_log():
    for b in write_dirs():
        for f in b.rglob("autopilot_log.txt"):
            return f
    return None


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    name = args[0]
    route = json.loads((ROUTES / f"{name}.json").read_text(encoding="utf-8"))
    char = route.get("character", "Pilot Vanguard")
    if "--char" in argv:
        char = argv[argv.index("--char") + 1]
    wp = world_points()
    steps = plan_steps(route, wp, Planner(wp))
    print(f"autopilot: route {name}: {len(route['steps'])} steps -> {len(steps)} client steps")
    if "--report" in argv:                              # re-print the report of the last run
        log = find_log()
        for line in report(log.read_text(encoding="utf-8", errors="replace").splitlines(), steps):
            print("  " + line)
        return 0
    if "--plan-only" in argv:
        for i, s in enumerate(steps, 1):
            print(f"  {i:3d} {s}")
        return 0
    if not (port_open(8080) and port_open(7172)):
        sys.exit("autopilot: the server is not running. Start it with windows\\Start-Spirebound.bat first.")
    exe = CLIENT / "otclient.exe"
    if not exe.exists():
        sys.exit("autopilot: the game client is not installed (.local/client).")
    old = find_log()
    if old:
        old.unlink()
    # the test client runs today's Spirebound modules, as an installed client would (windows/Install-Spirebound.ps1
    # copies client/modules/* the same way); before 2026-11-25 only game_autopilot was copied
    shutil.copytree(ROOT / "client" / "modules", CLIENT / "modules", dirs_exist_ok=True)
    run = MODULE_DST / "run.json"
    run.write_text(json.dumps({"name": name, "account": ACCOUNT, "password": PASSWORD, "character": char, "exit": True, "steps": steps,
                                "noPotions": bool(route.get("noPotions", False)), "loginShot": bool(route.get("loginShot", False))}), encoding="utf-8")
    started = time.time()
    proc = subprocess.Popen([str(exe)], cwd=str(CLIENT))
    limit = time.time() + route.get("timeout", 1200)
    log, removed, seen = None, False, 0
    try:
        while time.time() < limit:
            time.sleep(2)
            log = log or find_log()
            if log and not removed:
                run.unlink(missing_ok=True)           # the client has read it: Jay's own client must never autopilot
                removed = True
            if log:
                text = log.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in text[seen:]:
                    if "DONE" in line or "STUCK" in line or "TIMEOUT" in line or "DEATH" in line or "no path" in line:
                        print(line, flush=True)
                seen = len(text)
                if any(" DONE " in ln or ln.strip().endswith("DONE") or "  DONE" in ln for ln in text):
                    break
            if proc.poll() is not None and not log:
                print("autopilot: the client closed before writing a log")
                break
        else:
            print("autopilot: TIMEOUT, stopping the client")
    finally:
        run.unlink(missing_ok=True)
        time.sleep(4)
        if proc.poll() is None:
            proc.terminate()
    if log:
        text = log.read_text(encoding="utf-8", errors="replace").splitlines()
        print("\nREPORT (by place)")
        for line in report(text, steps):
            print("  " + line)
        for line in text:
            if "WHOLE RUN" in line:
                print("  " + line.strip())
        print(f"\nfull log: {log}")
        shots = sorted(p for b in write_dirs() for p in b.rglob("autopilot_*.png") if p.stat().st_mtime >= started)
        for p in shots:
            print(f"screenshot: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
