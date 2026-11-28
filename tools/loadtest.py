#!/usr/bin/env python3
"""Load tests with scripted clients (roadmap 9.2) and the Floor 1 capacity measurement (roadmap N2).

Runs on a TEST copy of the server (never the live one): it needs a built .build/server whose config already points at
a test database and spare ports (tools/test_boot.sh on a shifted copy makes one). It makes one test account and
character per bot in that database, starts the server with SPIRE_LOADTEST=1 (switches on the bot brain,
scripts/spirebound/dev_loadbot.lua), logs the bots in with tools/loadbot.py and measures.

    python3 tools/loadtest.py ramp     [--steps 10,25,50,75,100,125] [--minutes 3]
        9.2: bots spread over every Floor 1 hunting ground; per step: the server's tick lag, CPU and memory.
    python3 tools/loadtest.py addon
        6.5c: one character per class walks both of its outfit-addon quests through the real NPC (hi, outfit, yes,
        the kills, report) and the server logs which addons each owns. PASS when every class owns both addons.
    python3 tools/loadtest.py capacity [--steps 1,2,4,6,8,12] [--minutes 10] [--warmup 3]
        N2: that many bots on EVERY ground at once; per step and ground: kills per bot per hour (crowd system on).
    python3 tools/loadtest.py review [--only text]
        The Floor 1 review fixes on real, logged-in characters (scripts/spirebound/dev_review.lua): each case logs a
        character in, does the real thing (dies to a real monster, hits one, loots...) and checks what the server did.

Settings: MYSQL_* from the environment or server/local.env; MYSQL_DATABASE must not be the game's database.
Results: .local/loadtest_<mode>.json and a table on screen.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import loadbot  # noqa: E402

B = ROOT / ".build" / "server"
WILDS = ROOT / "server/data-spirebound/lib/spirebound/wilds_data.lua"
CLASS_SPEED = {4: 1.0, 3: 1.3, 1: 1.2, 2: 1.2}     # tools/gen_economy.py CLASS_SPEED (S1b, measured in the client)
VOCS = [4, 3, 1, 2]                                # vanguard, ranger, arcanist, mystic


def env():
    e = dict(os.environ)
    f = ROOT / "server" / "local.env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                e.setdefault(k.strip(), v.strip().strip('"'))
    e.setdefault("MYSQL_HOST", "127.0.0.1")
    e.setdefault("MYSQL_USER", "spire")
    e.setdefault("MYSQL_PASS", "spiretest")
    return e


def config_value(key):
    m = re.search(r'^%s\s*=\s*"?([^"\n]*)"?' % key, (B / "config.lua").read_text(), re.M)
    return m.group(1).strip() if m else None


def sql(e, db, text):
    r = subprocess.run(["mysql", "-h" + e["MYSQL_HOST"], "-u" + e["MYSQL_USER"], "-p" + e["MYSQL_PASS"], db, "-N"],
                       input=text, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("database error: " + r.stderr[:400])
    return r.stdout


FLOOR1_X = 1800   # Floor 1's map lies west of this (Floors 2-10 start further east: maps/floors.py origin)


def grounds():
    """Floor 1's walled hunting grounds only (Jay, 2026-11-26: Floor 1 first; the bots must never be put on a sealed
    floor, where the floor guard sends them back to town)."""
    out = []
    for m in re.finditer(r'\{ id = "(\w+)", title = "([^"]+)", type = "(\w+)".*?lo = (\d+), hi = (\d+).*?spots = \{\s*'
                         r'\{ n = 1, loop = "\w+", x = (\d+), y = (\d+), z = (\d+)', WILDS.read_text(), re.S):
        if int(m.group(6)) >= FLOOR1_X or re.match(r"f\d+_", m.group(1)):
            continue
        out.append(dict(id=m.group(1), title=m.group(2), type=m.group(3), lo=int(m.group(4)), hi=int(m.group(5)),
                        start=(int(m.group(6)), int(m.group(7)), int(m.group(8)))))
    return out


def exp_for(level):
    return int(50 / 3 * (level ** 3 - 6 * level ** 2 + 17 * level - 12))


def make_bots(e, db, plan, level=None, vocs=None):
    """plan: list of (index, ground). Makes accounts loadbotN, characters 'Loadbot N', fresh session tokens."""
    gs = {g["id"]: g for g in grounds()}
    lines, plan_rows, logins = [], [], []
    now = int(time.time())
    for i, gid in plan:
        g = gs[gid]
        lvl = level or (g["lo"] + g["hi"]) // 2
        voc = (vocs or VOCS)[i % 4]
        dps = (4 + lvl) * CLASS_SPEED[voc]
        name = "Loadbot %03d" % i
        token = hashlib.sha256(os.urandom(16)).hexdigest()
        hexid = "0x" + hashlib.sha256(token.encode()).hexdigest().encode().hex()
        x, y, z = g["start"]
        hp = 150 + 15 * lvl
        lines.append(
            f"INSERT INTO accounts (name, email, password, type, creation) VALUES ('loadbot{i}', 'loadbot{i}@localhost', "
            f"'0000000000000000000000000000000000000000', 1, {now}) ON DUPLICATE KEY UPDATE type = 1;\n"
            f"SET @a = (SELECT id FROM accounts WHERE name = 'loadbot{i}');\n"
            f"INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience, lookbody, "
            f"lookfeet, lookhead, looklegs, looktype, mana, manamax, town_id, conditions, cap, sex, posx, posy, posz) VALUES "
            f"('{name}', 1, @a, {lvl}, {voc}, {hp}, {hp}, {exp_for(lvl)}, 68, 76, 78, 58, 128, 200, 200, 1, '', 800, 1, "
            f"{x}, {y}, {z}) ON DUPLICATE KEY UPDATE account_id = @a, level = {lvl}, vocation = {voc}, health = {hp}, "
            f"healthmax = {hp}, experience = {exp_for(lvl)}, posx = {x}, posy = {y}, posz = {z};\n"
            f"DELETE FROM account_sessions WHERE account_id = @a;\n"
            f"INSERT INTO account_sessions (id, account_id, expires) VALUES ({hexid}, @a, {now + 86400});\n")
        plan_rows.append(f"{name};{gid};{dps:.1f}")
        logins.append((name, token, gid))
    sql(e, db, "".join(lines))
    return plan_rows, logins


class Server:
    def __init__(self, e, plan_file, tee=None):
        self.log = ROOT / ".build" / "loadtest.log"
        envs = dict(e, SPIRE_LOADTEST="1", SPIRE_LOADTEST_PLAN=str(plan_file))
        self.tee = None
        # its own process name: the live server's stop scripts stop every process called "canary" (pkill -x canary),
        # which shut a load test down when the live server was restarted (2026-11-26)
        shutil.copy2(B / "canary", B / "canary-loadtest")
        if tee:   # like the live server: its output also copied into a file on Windows (tools/run_server_wsl.sh)
            self.proc = subprocess.Popen(["./canary-loadtest"], cwd=B, env=envs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.tee = subprocess.Popen(f"tee {tee} > {self.log}", shell=True, stdin=self.proc.stdout)
        else:
            self.proc = subprocess.Popen(["./canary-loadtest"], cwd=B, env=envs, stdout=open(self.log, "w"), stderr=subprocess.STDOUT)
        self.pos = 0
        self.lines = []          # (wall time, line) of every [LOADTEST] line seen
        self.cpu_last = None

    def wait_online(self, seconds=180):
        for _ in range(seconds):
            if "server online!" in self.log.read_text(errors="replace"):
                return True
            if self.proc.poll() is not None:
                return False
            time.sleep(1)
        return False

    def poll_log(self):
        with open(self.log, errors="replace") as f:
            f.seek(self.pos)
            chunk = f.read()
            self.pos = f.tell()
        t = time.time()
        for line in chunk.splitlines():
            if "[LOADTEST]" in line:
                self.lines.append((t, line))

    def sample(self):
        """CPU (% of one core since the last sample) and resident memory (MB) of the server process."""
        try:
            st = Path(f"/proc/{self.proc.pid}/stat").read_text().split()
            ticks = int(st[13]) + int(st[14])
            rss = int(Path(f"/proc/{self.proc.pid}/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 2 ** 20
        except OSError:
            return None
        now = time.time()
        cpu = None
        if self.cpu_last:
            cpu = (ticks - self.cpu_last[1]) / os.sysconf("SC_CLK_TCK") / (now - self.cpu_last[0]) * 100
        self.cpu_last = (now, ticks)
        return cpu, rss

    def stop(self):
        self.proc.send_signal(signal.SIGINT)
        try:
            self.proc.wait(30)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def lag_lines(srv, t0, t1):
    out = []
    for t, line in srv.lines:
        if t0 <= t <= t1 and " lag " in line:
            d = dict(re.findall(r"(\w+)=([\d.]+)", line))
            out.append({k: float(v) for k, v in d.items()})
    return out


def kill_totals(srv, upto):
    """The last cumulative kill count per ground seen up to time `upto`, with the bots and crowd state then."""
    out = {}
    for t, line in srv.lines:
        if t <= upto and " kills " in line:
            m = re.search(r"ground=(\w+) bots=(\d+) kills_total=(\d+) crowd=(\w+)(?: alive=(\d+))?", line)
            if m:
                out[m.group(1)] = (t, int(m.group(2)), int(m.group(3)), m.group(4), int(m.group(5) or -1))
    return out


async def watch(srv, seconds, samples):
    end = time.time() + seconds
    while time.time() < end:
        await asyncio.sleep(5)
        srv.poll_log()
        s = srv.sample()
        if s and s[0] is not None:
            samples.append((time.time(), s[0], s[1]))


async def run(mode, steps, minutes, warmup, tee=None):
    e = env()
    db = config_value("mysqlDatabase")
    if not db or db == "spirebound":
        raise SystemExit("refusing: the built server must use a test database, not the game's")
    port = int(config_value("gameProtocolPort") or 7172)
    gs = grounds()
    # the bot plan for the whole run, in the order bots join
    plan = []
    if mode == "ramp":
        for i in range(max(steps)):
            plan.append((i, gs[i % len(gs)]["id"]))
    else:
        i = 0
        prev = 0
        for n in steps:
            for g in gs:
                for _ in range(n - prev):
                    plan.append((i, g["id"]))
                    i += 1
            prev = n
    plan_rows, logins = make_bots(e, db, plan)
    plan_file = ROOT / ".build" / "loadtest_plan.txt"
    plan_file.write_text("\n".join(plan_rows) + "\n")
    srv = Server(e, plan_file, tee)
    if not srv.wait_online():
        srv.stop()
        raise SystemExit("server did not start (see .build/loadtest.log)")
    print(f"server online (database {db}, game port {port}); {len(logins)} bots planned", flush=True)
    stats = {"online": 0, "failed": 0, "bytes": 0, "errors": []}
    tasks, samples, results = [], [], []
    started = 0
    await watch(srv, 30, samples)                 # idle baseline
    base = lag_lines(srv, 0, time.time())
    results.append(dict(bots=0, **summarise(base, samples, 0, time.time())))
    try:
        for n in steps:
            want = n if mode == "ramp" else n * len(gs)
            new = logins[started:want]
            for name, token, _gid in new:
                tasks.append(asyncio.create_task(loadbot.Bot(name, token, "127.0.0.1", port, stats).run(10 ** 6)))
                await asyncio.sleep(0.6)   # the engine blocks an address that connects more than 5 times 0.5 s apart
            started = want
            t0 = time.time()
            print(time.strftime("%H:%M:%S"), f"{want} bots joined; measuring", flush=True)
            await watch(srv, warmup * 60, samples)
            t1 = time.time()
            k0 = kill_totals(srv, t1)
            await watch(srv, (minutes - warmup) * 60, samples)
            t2 = time.time()
            k1 = kill_totals(srv, t2)
            row = dict(bots=want, online=stats["online"] - stats["failed"], failed=stats["failed"],
                       **summarise(lag_lines(srv, t1, t2), samples, t1, t2))
            if mode == "capacity":
                per = {}
                for g in gs:
                    a, b = k0.get(g["id"]), k1.get(g["id"])
                    if a and b and b[0] > a[0]:
                        hours = (b[0] - a[0]) / 3600
                        per[g["id"]] = dict(bots=b[1], kills=b[2] - a[2], kph_per_bot=round((b[2] - a[2]) / hours / max(1, b[1])),
                                            crowd=b[3], alive=b[4])
                row["grounds"] = per
            results.append(row)
            print(time.strftime("%H:%M:%S"), json.dumps(row), flush=True)
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        srv.stop()
    out = ROOT / ".local" / f"loadtest_{mode}{'_tee' if tee else ''}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(mode=mode, steps=steps, minutes=minutes, when=time.strftime("%Y-%m-%d %H:%M"),
                                   results=results, errors=stats["errors"][:20]), indent=1))
    print("results:", out)
    if stats["errors"]:
        print("client errors (first 5):", *stats["errors"][:5], sep="\n  ")


ADDON_QUESTS = {   # class -> (giver, [(target, count)] for addon 1 and addon 2); must match lib/spirebound/quests.lua
    # AD5 (2026-11-27): addon 2 of Ranger, Arcanist and Mystic is a hunt: (kind, 15, ground) brings the named target out
    4: ("Captain Dorrow", [("Moonhowl", 1), ("Granite Warden", 1)]),
    3: ("Hunter Brannoch", [("Blackthorn", 1), ("Deadeye Sorrel", 1, ("Bandit Crossbowman", 15, "smugglers_ridge"))]),
    1: ("Vesper", [("Prism Shardling", 1), ("The Page-Thief", 1, ("Hedge Hexer", 15, "bandit_road"))]),
    2: ("Fisher Corwin", [("Mossback Snapper", 1), ("Glasswing", 1, ("Field Shardling", 15, "shard_fields"))]),
}


async def addon_test():
    """6.5c end-to-end: each class earns both addons through the real NPC dialogue and kill events."""
    e = env()
    db = config_value("mysqlDatabase")
    if not db or db == "spirebound":
        raise SystemExit("refusing: the built server must use a test database, not the game's")
    port = int(config_value("gameProtocolPort") or 7172)
    vocs = [4, 3, 1, 2]
    plan = [(900 + i, "starter_west") for i in range(4)]
    # a fresh start every time: the test characters are deleted and made again (no quests, no addons)
    sql(e, db, "DELETE FROM players WHERE name IN ('Loadbot 900', 'Loadbot 901', 'Loadbot 902', 'Loadbot 903');")
    _rows, logins = make_bots(e, db, plan, level=26, vocs=vocs)
    plan_file = ROOT / ".build" / "loadtest_plan.txt"
    plan_file.write_text("")                  # no hunting brain for these: they only follow their script
    srv = Server(e, plan_file)
    if not srv.wait_online():
        srv.stop()
        raise SystemExit("server did not start (see .build/loadtest.log)")
    stats = {"online": 0, "failed": 0, "bytes": 0, "errors": []}
    tasks = []
    for (name, token, _g), voc in zip(logins, vocs):
        giver, steps = ADDON_QUESTS[voc]
        script = [(3, "say", "/lt state")]
        for target, count, *hunt in steps:
            script += [(1, "say", "/lt goto " + giver), (2, "say", "hi"), (2, "npc", "outfit"), (2, "npc", "yes"),
                       (1, "say", "/lt state")]
            if hunt:                          # the hunt: 15 of the kind inside the ground first (they call it out)
                kind, n, ground = hunt[0]
                script += [(1, "say", f"/lt goto loop_{ground}_b"), (1, "say", f"/lt kill {kind} {n}"), (n * 0.2 + 2, "say", "/lt state")]
            script += [(1, "say", f"/lt kill {target} {count}"), (count * 0.2 + 1, "say", "/lt state")]
            script += [(1, "say", "/lt goto " + giver), (2, "say", "hi"), (2, "npc", "report"), (2, "npc", "bye"),
                       (1, "say", "/lt state")]
        tasks.append(asyncio.create_task(loadbot.Bot(name, token, "127.0.0.1", port, stats, script).run(5)))
        await asyncio.sleep(0.6)
    try:
        await asyncio.gather(*tasks)
        await asyncio.sleep(3)
    finally:
        srv.stop()
    srv.poll_log()
    final = {}
    for _t, line in srv.lines:
        m = re.search(r"state (Loadbot \d+) voc=(\d) quests=(\S*) addons=(\S*)", line)
        if m:
            final[m.group(1)] = (int(m.group(2)), m.group(3), m.group(4))
    ok = len(final) == 4 and not stats["errors"]
    for name, (voc, quests, addons) in sorted(final.items()):
        own = addons.split(",") if addons else []
        # the engine only reports outfits of the character's own sex as owned, so check the outfit it wears
        looks = {a.split("+")[0] for a in own}
        both = any(f"{lk}+1" in own and f"{lk}+2" in own for lk in looks)
        print(f"{name} (class {voc}): quests {quests or '-'}; addons {addons or 'none'} -> {'PASS' if both else 'FAIL'}")
        ok = ok and both
    if stats["errors"]:
        print("client errors:", *stats["errors"][:5], sep="\n  ")
    print("addon test:", "PASS" if ok else "FAIL")
    return ok


# ---------------------------------------------------------------- review: real characters check the Floor 1 review fixes
# Each case: name, class, level, the scripts of its logins one after another (a death ends a login), and a check over
# the "[LOADTEST] rv <what> <character> key=value ..." lines its character logged (scripts/spirebound/dev_review.lua).
def _rv(lines, what):
    return [kv for w, kv in lines if w == what]


def _check_hardcore(lines):
    before, after = _rv(lines, "before_death")[0], _rv(lines, "state")[-1]
    return after["exp"] < before["exp"], f"blessings {before['bless']}, experience {before['exp']} -> {after['exp']}"


def _check_normal(lines):
    before, after = _rv(lines, "before_death")[0], _rv(lines, "state")[-1]
    return (before["bless"] == 8 and after["exp"] == before["exp"],
            f"blessings {before['bless']}, experience {before['exp']} -> {after['exp']}")


def _check_weapon(lines):
    hits = [h["dealt"] for h in _rv(lines, "hit")]
    power = _rv(lines, "weapon")[0]["power"]
    # the test monster (a Ruin Sentinel) shrugs off 10% of physical damage, and Mastery adds a little on top of the
    # weapon, so: the armed hit must be at least the bare hit times the weapon's power
    return (len(hits) == 2 and hits[0] > 0 and power > 150 and hits[1] >= hits[0] * power / 100 - 2,
            f"a hit of 100 bare-handed deals {hits[0]}; with a maxed Stairlord's Edge (power {power}%) it deals {hits[1]}")


def _xp(lines):
    return _rv(lines, "xp")[0]["gained"]


def _check_xp_plain(lines):
    return _xp(lines) > 0, f"{_xp(lines)} experience for the kill"


def _check_xp_ratio(want, what):
    def check(lines, all_lines=None):
        base = _xp(all_lines["XP plain"])
        got = _xp(lines)
        return abs(got - base * want) <= 2, f"{got} experience against {base} plain ({what})"
    check.needs_all = True
    return check


def _check_loot(lines, all_lines=None):
    off = _rv(all_lines["CB loot, bot off"], "loot")[0]
    on = _rv(lines, "loot")[0]
    a, b = off["coins"], on["coins"]
    return (on["botting"] == 1 and a > 0 and 0.3 * a <= b <= 0.7 * a,
            f"{on['kills']} Road Bandits: {b} coins with the cavebot on against {a} with it off")


_check_loot.needs_all = True

def _check_skill(lines, all_lines=None):
    old = _rv(all_lines["SK old"], "skill")[0]["tries"]
    young = _rv(lines, "skill")[0]["tries"]
    return abs(young - 2 * old) <= 2, f"1000 tries of training count as {young} at level 30 against {old} at level 55"


_check_skill.needs_all = True

XP_MONSTER = "Thornsnap"
def _world_point(name):
    m = re.search(r'\["%s"\] = Position\((\d+), (\d+), (\d+)\)' % name,
                  (ROOT / "server/data-spirebound/lib/spirebound/world_points.lua").read_text())
    return tuple(int(v) for v in m.groups())


UNDERKEEP_BOX = "%d %d %d 3515 2" % _world_point("underkeep_chest")   # the altar the map uses as the strongbox (on a carpet)


ROD_ON_RIVER = "1121 1213 7 3483 1 1125 1213 7"   # the rod lying beside you, on a river tile by the Millcross bridge


def _check_fish(lines):
    t = [r["tries"] for r in _rv(lines, "fishstate")]
    good = len(t) == 4 and t[1] > t[0] and t[2] == t[1] and t[3] > t[2]
    return good, "fishing tries: start %s, cast %s, cast again 0.7 s later %s (refused), 2.7 s later %s" % tuple((t + [None] * 4)[:4])


MEADOW = [(1250, 1052, 7), (1250, 1056, 7), (1250, 1060, 7)]   # open meadow east of the labyrinth corridor
_h = _world_point("boss_private_floor1")
BOSS_HALL = (_h[0] + 2, _h[1] + 4, _h[2])                     # inside the private boss hall


def crystal_steps(mode, at, choice):
    x, y, z = at
    return [[(3, "say", "/rv crystalfloor %s %d %d %d" % (mode, x, y, z)), (1, "use", "%d %d %d 3251 1" % (x - 1, y, z)),
             (1, "modal", "7301 1 %d" % choice), (5, "say", "/rv crystalcount")]]


def _check_crystal(want):
    def check(lines):
        f, c = _rv(lines, "crystalfloor")[0], _rv(lines, "crystalcount")[0]
        here = (c["x"], c["y"], c["z"])
        town = tuple(int(v) for v in f["town"].split(","))
        ground = tuple(int(v) for v in f["ground"].split(","))
        spot = tuple(int(v) for v in f["spot"].split(","))
        if want == "town":
            good = max(abs(here[0] - town[0]), abs(here[1] - town[1])) <= 2 and here[2] == town[2]
        elif want == "ground":
            good = max(abs(here[0] - ground[0]), abs(here[1] - ground[1])) <= 2 and here[2] == ground[2]
        else:                                # refused: still standing beside the crystal's tile
            good = here == (spot[0] + 1, spot[1], spot[2])
        return good, "now at %s (town %s, %s gate %s)" % (here, town, f["gid"], ground)
    return check


CHEST_BANDIT = "%d %d %d 4073 1" % _world_point("chest_bandit_road")


def _check_chest(lines):
    p, s = _rv(lines, "chestprep"), _rv(lines, "state")
    first, second = s[0]["gold"] - p[0]["gold"], s[1]["gold"] - p[1]["gold"]
    return first > 0 and 0 <= second < first, "first character +%d, second character of the account +%d (the daily refill)" % (first, second)


def _check_dg(kind, want):
    def check(lines):
        r = _rv(lines, "dg")[0]
        return r["verdict"] == want, f"{kind}: {r['verdict']} (want {want}; pvp loss {r.get('pvp_loss')}, partner loss {r.get('other_loss')}, zone {r.get('zone')})"
    return check


REVIEW_CASES = [
    dict(name="B4-0 a maxed weapon really adds its damage", voc=4, level=30,
         logins=[[(3, "say", "/rv hit"), (1, "say", "/rv weapon f1_vanguard_sword 5 1"), (1, "say", "/rv hit")]],
         check=_check_weapon),
    dict(name="XP plain", voc=4, level=30, logins=[[(3, "say", "/rv mode normal"), (1, "say", "/rv xp " + XP_MONSTER)]],
         check=_check_xp_plain),
    dict(name="XP Death Game gives +50%", voc=4, level=30,
         logins=[[(3, "say", "/rv mode deathgame"), (1, "say", "/rv xp " + XP_MONSTER)]],
         check=_check_xp_ratio(1.5, "+50%")),
    dict(name="XP Hardcore gives +25%", voc=4, level=30,
         logins=[[(3, "say", "/rv mode hardcore"), (1, "say", "/rv xp " + XP_MONSTER)]],
         check=_check_xp_ratio(1.25, "+25%")),
    dict(name="XP the cavebot gives 45%", voc=4, level=30,
         logins=[[(3, "say", "/rv mode normal"), (1, "say", "/rv bot on"), (1, "say", "/rv xp " + XP_MONSTER)]],
         check=_check_xp_ratio(0.45, "45%")),
    dict(name="SK old", voc=4, level=55, logins=[[(3, "say", "/rv skill")]],
         check=lambda lines: (_rv(lines, "skill")[0]["tries"] > 0, f"{_rv(lines, 'skill')[0]['tries']} tries at level 55")),
    dict(name="SK skills train twice as fast below level 50", voc=4, level=30, logins=[[(3, "say", "/rv skill")]],
         check=_check_skill),
    dict(name="CB loot, bot off", voc=4, level=30, logins=[[(3, "say", "/rv loot Road Bandit 60")]], stay=14,
         check=lambda lines: (_rv(lines, "loot")[0]["coins"] > 0, f"{_rv(lines, 'loot')[0]['coins']} coins from 60 Road Bandits")),
    dict(name="CB loot, bot on: about half the coins", voc=4, level=30,
         logins=[[(3, "say", "/rv bot on"), (1, "say", "/rv loot Road Bandit 60")]], stay=14, check=_check_loot),

    dict(name="A8-1 a level-15 Hardcore death costs experience", voc=4, level=15, ground="starter_east",
         logins=[[(3, "say", "/rv mode hardcore"), (1, "say", "/rv die")], [(3, "say", "/rv state")]], check=_check_hardcore),
    dict(name="A8-1 a level-15 Normal death costs nothing", voc=4, level=15, ground="starter_east",
         logins=[[(3, "say", "/rv mode normal"), (1, "say", "/rv die")], [(3, "say", "/rv state")]], check=_check_normal),
    dict(name="A4-6 every Axe-Lord fighter gets 10 platinum in the bank", voc=4, level=60,
         logins=[[(3, "say", "/rv axelord")]], stay=4,
         check=lambda lines: (_rv(lines, "axelord")[0]["bank_gain"] >= 1000, "bank +%(bank_gain)s" % _rv(lines, "axelord")[0])),
    dict(name="I10 the Sealed Shrine's gold once per account", voc=4, level=60, logins=[[(3, "say", "/rv shrine")]], stay=4,
         check=lambda lines: (_rv(lines, "shrine")[0]["first"] == 1000 and _rv(lines, "shrine")[0]["second"] == 0,
                              "first character %(first)s gold, second %(second)s" % _rv(lines, "shrine")[0])),
    dict(name="I10 the daily reward once per account", voc=4, level=30,
         logins=[[(3, "say", "/rv dailyfresh")], [(6, "say", "/rv state")], [(3, "say", "/rv dailyalt")], [(6, "say", "/rv state")]],
         check=lambda lines: (_rv(lines, "state")[0]["gold"] > _rv(lines, "dailyfresh")[0]["gold"]
                              and _rv(lines, "state")[1]["gold"] == _rv(lines, "state")[0]["gold"],
                              "gold %s -> %s at the first login, %s after an 'other character' login" % (
                                  _rv(lines, "dailyfresh")[0]["gold"], _rv(lines, "state")[0]["gold"], _rv(lines, "state")[1]["gold"]))),
    dict(name="I10 the Underkeep strongbox once per account", voc=4, level=30,
         logins=[[(3, "say", "/rv boxprep fresh"), (1, "use", UNDERKEEP_BOX), (2, "say", "/rv state"),
                  (1, "say", "/rv boxprep"), (1, "use", UNDERKEEP_BOX), (2, "say", "/rv state")]], stay=3,
         check=lambda lines: (_rv(lines, "state")[0]["gold"] - _rv(lines, "boxprep")[0]["gold"] >= 800
                              and _rv(lines, "state")[1]["gold"] == _rv(lines, "boxprep")[1]["gold"],
                              "first open +%d, second (character's own day forgotten) +%d" % (
                                  _rv(lines, "state")[0]["gold"] - _rv(lines, "boxprep")[0]["gold"],
                                  _rv(lines, "state")[1]["gold"] - _rv(lines, "boxprep")[1]["gold"]))),
    dict(name="A7-1 two seconds between fishing casts", voc=4, level=30,
         logins=[[(3, "say", "/rv fishprep"), (1, "usewith", ROD_ON_RIVER), (0.2, "say", "/rv fishstate"),
                  (0.5, "usewith", ROD_ON_RIVER), (0.2, "say", "/rv fishstate"),
                  (2.5, "usewith", ROD_ON_RIVER), (0.2, "say", "/rv fishstate")]], stay=8, check=_check_fish),
    dict(name="A9 the level-9 hint says experience now comes slower", voc=4, level=12, logins=[[(3, "say", "/rv levelnine")]],
         check=lambda lines: (_rv(lines, "level9")[0]["hint"] == 1, "level %(level)s, hint %(hint)s" % _rv(lines, "level9")[0])),
    dict(name="A5-1 the Journal says the Stair Key needs a group", voc=4, level=12, logins=[[(3, "say", "/rv journal")]],
         check=lambda lines: (_rv(lines, "journal")[0]["stairkey_group_line"] == 1, "%(lines)s lines, group line %(stairkey_group_line)s" % _rv(lines, "journal")[0])),
    dict(name="S-1 a shop decoration comes back next season", voc=4, level=30,
         logins=[[(3, "say", "/rv shopon"), (1, "say", "!shop buy candelabrum"), (1, "say", "/rv newseason")],
                 [(6, "say", "/rv shopstate")]],
         check=lambda lines: (_rv(lines, "newseason")[0]["had"] == 1 and _rv(lines, "shopstate")[0]["inbox"] == 1,
                              "bought and carried %s; after the 'new season' login, %s in the Store Inbox" % (
                                  _rv(lines, "newseason")[0]["had"], _rv(lines, "shopstate")[0]["inbox"]))),
    dict(name="T4 a floor perk no longer breaks every hit", voc=4, level=30, logins=[[(3, "say", "/rv perkhit")]],
         check=lambda lines: (_rv(lines, "perkhit")[0]["executioner"] > _rv(lines, "perkhit")[0]["plain"],
                              "100 hit at 20%% health: %(plain)s plain, %(executioner)s with Executioner" % _rv(lines, "perkhit")[0])),
    dict(name="T5 PvP damage is recorded", voc=4, level=60, partner="T5 partner",
         logins=[[(1, "unsecure", ""), (5, "say", "/rv pvpdmg {partner}")]], stay=3,
         check=lambda lines: (_rv(lines, "pvpdmg")[0]["seen"] > 0 and _rv(lines, "pvpdmg")[0]["seen"] == _rv(lines, "pvpdmg")[0]["lost"],
                              "lost %(lost)s, the credit rules saw %(seen)s" % _rv(lines, "pvpdmg")[0])),
    dict(name="T5 partner", voc=4, level=60, logins=[[(1, "unsecure", ""), (1, "say", "/rv state")]], stay=12,
         check=lambda lines: (True, "partner")),
    dict(name="T6 !private refused without the Stair Key", voc=4, level=60,
         logins=[[(3, "say", "/rv privprep"), (1, "say", "!private"), (2, "say", "/rv where")]], stay=3,
         check=lambda lines: (_rv(lines, "privprep")[0]["floor2"] == 1 and _rv(lines, "where")[0]["z"] == 5,
                              "floor 2 open %(floor2)s, key %(key)s" % _rv(lines, "privprep")[0] + ", now on level %(z)s" % _rv(lines, "where")[0])),
    dict(name="T6 !private works with the Stair Key", voc=4, level=60,
         logins=[[(14, "say", "/rv privprep key"), (1, "say", "!private"), (2, "say", "/rv where"), (1, "say", "/rv floorsreset")]], stay=3,
         check=lambda lines: (_rv(lines, "where")[0]["z"] == 4,
                              "key %(key)s" % _rv(lines, "privprep")[0] + ", now on level %(z)s" % _rv(lines, "where")[0])),
    dict(name="TC1 buy an Amber Waycrystal from the Runewright", voc=4, level=30,
         logins=[[(3, "say", "/rv goto Runewright Mael"), (1, "say", "hi"), (1, "npc", "trade"), (1, "buy", "3251 1"),
                  (1, "say", "/rv crystalcount")]], stay=3,
         check=lambda lines: (_rv(lines, "crystalcount")[0]["carried"] == 1 and _rv(lines, "goto")[0]["gold"] - 150 >= 0,
                              "carried %(carried)s after buying" % _rv(lines, "crystalcount")[0])),
    dict(name="TC1 a Waycrystal to Hearthgate", voc=4, level=30, ground="wolf_copse",
         logins=crystal_steps("plain", MEADOW[0], 1), stay=3, check=_check_crystal("town")),
    dict(name="TC1 a Waycrystal to a hunting ground's gate", voc=4, level=30,
         logins=crystal_steps("plain", MEADOW[1], 2), stay=3, check=_check_crystal("ground")),
    dict(name="TC1 a Waycrystal refused in a fight", voc=4, level=30, ground="wolf_copse",
         logins=crystal_steps("fight", MEADOW[2], 1), stay=3, check=_check_crystal("stay")),
    dict(name="TC1 a Waycrystal refused in a boss room", voc=4, level=60,
         logins=crystal_steps("plain", BOSS_HALL, 1), stay=3, check=_check_crystal("stay")),
    dict(name="L1 a ground chest's first reward once per account", voc=4, level=30,
         logins=[[(3, "say", "/rv chestprep bandit_road"), (1, "use", CHEST_BANDIT), (1, "say", "/rv state"),
                  (1, "say", "/rv chestprep bandit_road alt"), (1, "use", CHEST_BANDIT), (1, "say", "/rv state")]], stay=3,
         check=lambda lines: _check_chest(lines)),
    dict(name="L2 the Well Vein's gold once per account", voc=4, level=30, logins=[[(3, "say", "/rv wellvein")]],
         check=lambda lines: (_rv(lines, "wellvein")[0]["first"] == 1000 and _rv(lines, "wellvein")[0]["second"] == 0,
                              "first character %(first)s, second %(second)s" % _rv(lines, "wellvein")[0])),
    dict(name="L3 task gold is never lost to a full backpack", voc=4, level=30, logins=[[(3, "say", "/rv taskdone")]],
         check=lambda lines: (_rv(lines, "taskdone")[0]["ok"] == 1 and _rv(lines, "taskdone")[0]["gained"] == _rv(lines, "taskdone")[0]["reward"],
                              "reward %(reward)s, arrived %(gained)s, backpack slots free %(free_slots)s" % _rv(lines, "taskdone")[0])),
    dict(name="A4-5 a boss kill after a lost fight record still credits", voc=4, level=60,
         logins=[[(3, "say", "/rv bossreload")]], stay=4,
         check=lambda lines: (_rv(lines, "bossreload")[0]["credited"] == 1 and _rv(lines, "bossreload")[0]["had_record"] == 1,
                              "had a record %(had_record)s, credited %(credited)s" % _rv(lines, "bossreload")[0])),
] + [
    # A8-2: each Death Game victim dies beside its own real partner character ("{partner}" is that character's name)
    case for kind, want in (("dragfought", "retire"), ("dragged", "saved"), ("firstvictim", "retire"), ("firstother", "saved"),
                            ("bossother", "retire"))
    for case in (
        dict(name=f"A8-2 DG {kind}: {want}", voc=4, level=60, partner=f"A8-2 partner {kind}",
             logins=[[(1, "unsecure", ""), (5, "say", "/rv dg " + kind + " {partner}")]], stay=4, check=_check_dg(kind, want)),
        dict(name=f"A8-2 partner {kind}", voc=4, level=60, logins=[[(1, "unsecure", ""), (1, "say", "/rv state")]], stay=14,
             check=lambda lines: (True, "partner")))
]


# ---------------------------------------------------------------- roadmap Step 0 (Jay's answers of 2026-11-27)
# Real characters through the game's own packets (trades, moves, attacks, party invites, NPC talk); setup and readings
# through /s0 (scripts/spirebound/dev_step0.lua). "{partner_id}" is the partner character's creature id. Run them a
# group at a time (--only "QA2", --only "QA7"...): some groups change the test world (Floor 2 open, a launch week).
def _s0(lines, what):
    return [kv for w, kv in lines if w == "s0" + what]


def _plan_coins(monster):
    """Coins a kill of this monster gives by the plain drop tables (tools/balance.py, the economy plan)."""
    import balance as b
    monsters, *_ = b.load_game()
    return b.coin_value(monsters[monster]["loot"], 1)


def _check_qa20(lines):
    r = _s0(lines, "loot")[0]
    coins = r["bag"] + r["bank"] + r["left"]
    plan = _plan_coins("Road Bandit") * r["kills"]
    return (0.75 * plan <= coins <= 1.25 * plan and r["bank"] == 0,
            f"{r['kills']} Road Bandits dropped {coins} coins ({r['bag']} into the backpack, {r['bank']} into the bank, "
            f"{r['left']} left in full bodies); the plan says {plan:.0f}")


def _check_followers(lines):
    xp = [x["gained"] for x in _s0(lines, "xp")]
    return len(xp) == 2 and xp[0] > 0 and abs(xp[1] / xp[0] - 0.45) < 0.03, f"alone {xp[0]}, following a botter {xp[1]}"


STEP0_CASES = [
    # QA2 (Q100): each secret piece goes from one character to another through the trade window
    dict(name="QA2 trade: the giver hands over all three secret pieces", voc=4, level=30, partner="QA2 trade: the taker", stay=6,
         logins=[[(3, "say", "/s0 secrets"), (6, "trade", "65535 2 0 3014 0 {partner_id}"), (4, "accept", ""),
                  (4, "trade", "65535 8 0 3552 0 {partner_id}"), (4, "accept", ""),
                  (4, "trade", "65535 9 0 3063 0 {partner_id}"), (4, "accept", ""), (3, "say", "/s0 hold")]],
         check=lambda lines: (_s0(lines, "hold")[0]["held"] == "none", "the giver now holds: %(held)s" % _s0(lines, "hold")[0])),
    dict(name="QA2 trade: the taker", voc=4, level=30, partner="QA2 trade: the giver hands over all three secret pieces", stay=4,
         logins=[[(3, "say", "/s0 offer"), (8, "trade", "65535 1 0 3355 0 {partner_id}"), (3, "accept", ""),
                  (1, "say", "/s0 offer"), (3, "trade", "65535 1 0 3355 0 {partner_id}"), (4, "accept", ""),
                  (1, "say", "/s0 offer"), (3, "trade", "65535 1 0 3355 0 {partner_id}"), (4, "accept", ""),
                  (3, "say", "/s0 hold")]],
         check=lambda lines: (_s0(lines, "hold")[0]["held"] == "millrace_boots,shrinekeepers_pendant,wardens_signet",
                              "the taker now holds: %(held)s" % _s0(lines, "hold")[0])),
    # QA3 (Q77): a Normal death below 30 costs nothing, from 30 the standard loss
    dict(name="QA3 a level-29 Normal death costs nothing", voc=4, level=29, ground="starter_east",
         logins=[[(3, "say", "/rv mode normal"), (1, "say", "/rv die")], [(3, "say", "/rv state")]], check=_check_normal),
    dict(name="QA3 a level-31 Normal death costs the standard loss", voc=4, level=31, ground="starter_east",
         logins=[[(3, "say", "/rv mode normal"), (1, "say", "/rv die")], [(3, "say", "/rv state")]],
         check=lambda lines: (_rv(lines, "before_death")[0]["bless"] == 0 and _check_hardcore(lines)[0],
                              "blessings %s; " % _rv(lines, "before_death")[0]["bless"] + _check_hardcore(lines)[1])),
    # QA11 (Q80): Hardcore keeps the free blessings only below level 8: a level 10 death drops the backpack, a level 5 one doesn't
    dict(name="QA11 a level-10 Hardcore death can lose the backpack", voc=4, level=10, ground="starter_east",
         logins=[[(3, "say", "/rv mode hardcore"), (1, "say", "/s0 offer"), (1, "say", "/s0 bag"), (1, "say", "/rv die")], [(3, "say", "/s0 bag")]],
         check=lambda lines: ((lambda b: (b[0]["bp"] == 1 and b[0]["bless"] == 0 and b[1]["bp"] == 0,
                                          "blessings %s; backpack before %s, after %s" % (b[0]["bless"], b[0]["bp"], b[1]["bp"])))(_s0(lines, "bag")))),
    dict(name="QA11 a level-5 Hardcore death keeps it", voc=4, level=5, ground="starter_east",
         logins=[[(3, "say", "/rv mode hardcore"), (1, "say", "/s0 offer"), (1, "say", "/s0 bag"), (1, "say", "/rv die")], [(3, "say", "/s0 bag")]],
         check=lambda lines: ((lambda b: (b[0]["bp"] == 1 and b[1]["bp"] == 1,
                                          "blessings %s; backpack before %s, after %s" % (b[0]["bless"], b[0]["bp"], b[1]["bp"])))(_s0(lines, "bag")))),
    # QA4 (Q76) and QA20 (Q84): looted coins land in the bag, not the bank, at the planned amount
    dict(name="QA4/QA20 coins from 300 Road Bandits stay in the backpack, at the planned amount", voc=4, level=30, stay=60,
         logins=[[(3, "say", "/s0 offer"), (1, "say", "/s0 loot Road Bandit 300")]],
         check=lambda lines: (_s0(lines, "loot")[0]["bag"] > 0 and _check_qa20(lines)[0], _check_qa20(lines)[1])),
    # QA7 (Q82): no PvP below 50 in boss rooms; two 55s may fight
    dict(name="QA7 a level 60 can't hurt a level 40 in the Axe-Lord's hall", voc=4, level=60, partner="QA7 victim 40 (hall)", stay=3,
         logins=[[(3, "say", "/s0 bossroom axe 1"), (1, "say", "/s0 arm"), (1, "redfist", ""), (1, "attack", "{partner_id}"), (2, "say", "/s0 target"), (1, "say", "/s0 canhit {partner}")]],
         check=lambda lines: (True, "attacker: target %s, rule %s" % ((_s0(lines, "target") or [{"name": "?"}])[0]["name"], (_s0(lines, "canhit") or [{"ok": "?"}])[0]["ok"]))),
    dict(name="QA7 victim 40 (hall)", voc=4, level=40, partner="QA7 a level 60 can't hurt a level 40 in the Axe-Lord's hall", stay=2,
         logins=[[(3, "say", "/s0 bossroom axe"), (16, "say", "/s0 hp")]],
         check=lambda lines: (_s0(lines, "bossroom")[0]["zone"] == "bossroom" and _s0(lines, "hp")[0]["hp"] == _s0(lines, "hp")[0]["max"],
                              "zone %s, health %s of %s" % (_s0(lines, "bossroom")[0]["zone"], _s0(lines, "hp")[0]["hp"], _s0(lines, "hp")[0]["max"]))),
    dict(name="QA7 a level 60 can't hurt a level 40 in the Gate Hound's arena", voc=4, level=60, partner="QA7 victim 40 (arena)", stay=3,
         logins=[[(3, "say", "/s0 bossroom hound 1"), (1, "say", "/s0 arm"), (1, "redfist", ""), (1, "attack", "{partner_id}"), (2, "say", "/s0 target"), (1, "say", "/s0 canhit {partner}")]],
         check=lambda lines: (True, "attacker: target %s, rule %s" % ((_s0(lines, "target") or [{"name": "?"}])[0]["name"], (_s0(lines, "canhit") or [{"ok": "?"}])[0]["ok"]))),
    dict(name="QA7 victim 40 (arena)", voc=4, level=40, partner="QA7 a level 60 can't hurt a level 40 in the Gate Hound's arena", stay=2,
         logins=[[(3, "say", "/s0 bossroom hound"), (16, "say", "/s0 hp")]],
         check=lambda lines: (_s0(lines, "hp")[0]["hp"] == _s0(lines, "hp")[0]["max"],
                              "zone %s, health %s of %s" % (_s0(lines, "bossroom")[0]["zone"], _s0(lines, "hp")[0]["hp"], _s0(lines, "hp")[0]["max"]))),
    dict(name="QA7 two level 55s can fight in the hall", voc=4, level=55, partner="QA7 victim 55 (hall)", stay=3,
         logins=[[(3, "say", "/s0 bossroom axe 1"), (1, "say", "/s0 arm"), (1, "redfist", ""), (1, "attack", "{partner_id}"), (2, "say", "/s0 target"), (1, "say", "/s0 canhit {partner}")]],
         check=lambda lines: (True, "attacker: target %s, rule %s" % ((_s0(lines, "target") or [{"name": "?"}])[0]["name"], (_s0(lines, "canhit") or [{"ok": "?"}])[0]["ok"]))),
    dict(name="QA7 victim 55 (hall)", voc=4, level=55, partner="QA7 two level 55s can fight in the hall", stay=2,
         logins=[[(3, "say", "/s0 bossroom axe"), (16, "say", "/s0 hp")]],
         check=lambda lines: (_s0(lines, "hp")[0]["hp"] < _s0(lines, "hp")[0]["max"],
                              "health %s of %s; tile %s" % (_s0(lines, "hp")[0]["hp"], _s0(lines, "hp")[0]["max"], _s0(lines, "bossroom")[0]))),
    dict(name="QA7 control: two level 55s in the open", voc=4, level=55, partner="QA7 control victim", stay=3,
         logins=[[(3, "say", "/s0 jump 1251 1056 7"), (1, "say", "/s0 arm"), (1, "redfist", ""), (1, "attack", "{partner_id}"), (2, "say", "/s0 target"), (1, "say", "/s0 canhit {partner}")]],
         check=lambda lines: (True, "attacker: target %s, rule %s" % ((_s0(lines, "target") or [{"name": "?"}])[0]["name"], (_s0(lines, "canhit") or [{"ok": "?"}])[0]["ok"]))),
    dict(name="QA7 control victim", voc=4, level=55, partner="QA7 control: two level 55s in the open", stay=2,
         logins=[[(3, "say", "/s0 jump 1250 1056 7"), (16, "say", "/s0 hp")]],
         check=lambda lines: (_s0(lines, "hp")[0]["hp"] < _s0(lines, "hp")[0]["max"], "health %(hp)s of %(max)s" % _s0(lines, "hp")[0])),
    # QA8 (Q92): !private refused while one party member lacks the Stair Key, works once all have it
    dict(name="QA8 the leader's !private: refused, then works", voc=4, level=60, partner="QA8 member", stay=3,
         logins=[[(14, "say", "/rv privprep key"), (2, "invite", "{partner_id}"), (5, "say", "!private"), (2, "say", "/s0 where"),
                  (5, "say", "!private"), (3, "say", "/s0 where"), (1, "say", "/rv floorsreset")]],
         check=lambda lines: (_s0(lines, "where")[0]["z"] == 5 and _s0(lines, "where")[1]["z"] == 4,
                              "after the first !private on level %s, after the second on level %s" % (_s0(lines, "where")[0]["z"], _s0(lines, "where")[1]["z"]))),
    dict(name="QA8 member", voc=4, level=60, partner="QA8 the leader's !private: refused, then works", stay=3,
         logins=[[(15, "say", "/rv privprep"), (3, "join", "{partner_id}"), (6, "say", "/s0 key"), (8, "say", "/s0 where")]],
         check=lambda lines: (_s0(lines, "where")[-1]["z"] == 4, "the member ended on level %s" % _s0(lines, "where")[-1]["z"])),
    # QA9 (Q86): a level 8 can't wield a tier 5 weapon (picked up from the ground into the hand); a level 30 can
    dict(name="QA9 a level 8 can't wield a tier 5 sword", voc=4, level=8, stay=2,
         logins=[[(3, "say", "/s0 jump %d %d %d" % MEADOW[0]), (1, "say", "/s0 ground f1_vanguard_sword 5"),
                  (1, "move", "%d %d %d 3264 1 65535 6 0 1" % (MEADOW[0][0] + 1, MEADOW[0][1], MEADOW[0][2])), (2, "say", "/s0 hand")]],
         check=lambda lines: (_s0(lines, "hand")[0]["gear"] == "none", "in hand: %(gear)s (level %(level)s)" % _s0(lines, "hand")[0])),
    dict(name="QA9 a level 30 can", voc=4, level=30, stay=2,
         logins=[[(3, "say", "/s0 jump %d %d %d" % MEADOW[1]), (1, "say", "/s0 ground f1_vanguard_sword 5"),
                  (1, "move", "%d %d %d 3264 1 65535 6 0 1" % (MEADOW[1][0] + 1, MEADOW[1][1], MEADOW[1][2])), (2, "say", "/s0 hand")]],
         check=lambda lines: (_s0(lines, "hand")[0]["gear"] == "f1_vanguard_sword" and _s0(lines, "hand")[0]["tier"] == 5,
                              "in hand: %(gear)s tier %(tier)s (level %(level)s)" % _s0(lines, "hand")[0])),
    # QA12 (Q14): stepping down from Death Game takes back the bonus experience
    dict(name="QA12 stepping down at the Registrar takes back the bonus", voc=4, level=30, stay=2,
         logins=[[(3, "say", "/rv mode deathgame"), (1, "say", "/s0 bonus 5000"), (1, "say", "/s0 goto Registrar Maelis"),
                  (1, "say", "/s0 state"), (1, "say", "hi"), (2, "npc", "step down"), (2, "npc", "normal"), (2, "npc", "yes"),
                  (2, "say", "/s0 state")]],
         check=lambda lines: ((lambda s: (s[0]["exp"] - s[1]["exp"] == 5000 and s[1]["mode"] == 1,
                                          "experience %d -> %d, mode %d -> %d" % (s[0]["exp"], s[1]["exp"], s[0]["mode"], s[1]["mode"])))(_s0(lines, "state")))),
    # QA15 (Q72): a season started: a full Boar Meadow puts out every crowd group twice
    dict(name="QA15 launch week: a full harder ground puts out twice the crowd", voc=4, level=30, stay=2,
         logins=[[(3, "say", "/s0 launch on"), (1, "say", "/s0 crowd boar_meadow 8"), (1, "say", "/s0 launch off")]],
         check=lambda lines: ((lambda c: (c["week"] == 1 and c["monsters"] == 2 * c["spots"],
                                          "%(state)s, %(spots)s crowd spots, %(monsters)s boars out" % c))(_s0(lines, "crowd")[0]))),
    # QA16 (Q60, Q16, Q53): where the cavebot earns nothing; followers; 3 windows
    dict(name="QA16 the cavebot earns nothing in a starter ground", voc=4, level=8, ground="starter_west", stay=2,
         logins=[[(3, "say", "/s0 bot on"), (1, "say", "/s0 xp Field Rat")]],
         check=lambda lines: (_s0(lines, "xp")[0]["gained"] == 0 and _s0(lines, "xp")[0]["ban"] == "starter",
                              "gained %(gained)s (%(ban)s)" % _s0(lines, "xp")[0])),
    dict(name="QA16 the cavebot earns nothing on Floor 1 in launch week", voc=4, level=12, ground="boar_meadow", stay=2,
         logins=[[(3, "say", "/s0 launch on"), (1, "say", "/s0 bot on"), (1, "say", "/s0 xp Bristle Boar"), (1, "say", "/s0 launch off")]],
         check=lambda lines: (_s0(lines, "xp")[0]["gained"] == 0 and _s0(lines, "xp")[0]["ban"] == "launch",
                              "gained %(gained)s (%(ban)s)" % _s0(lines, "xp")[0])),
    dict(name="QA16 follower: the botting leader", voc=4, level=12, ground="boar_meadow", partner="QA16 follower: same cut as the bot", stay=10,
         logins=[[(3, "say", "/s0 bot on"), (4, "invite", "{partner_id}")]], check=lambda lines: (True, "leader")),
    dict(name="QA16 follower: same cut as the bot", voc=4, level=12, ground="boar_meadow", partner="QA16 follower: the botting leader", stay=2,
         logins=[[(3, "say", "/s0 xp Bristle Boar"), (7, "join", "{partner_id}"), (2, "say", "/s0 xp Bristle Boar")]],
         check=_check_followers),
    dict(name="QA16W windows 1", voc=4, level=8, stay=14, logins=[[(1, "say", "/s0 windows on"), (1, "say", "/s0 where")]],
         check=lambda lines: (len(_s0(lines, "where")) == 1, "in")),
    dict(name="QA16W windows 2", voc=4, level=8, stay=12, delay=3, logins=[[(1, "say", "/s0 where")]],
         check=lambda lines: (len(_s0(lines, "where")) == 1, "in")),
    dict(name="QA16W windows 3", voc=4, level=8, stay=10, delay=4, logins=[[(1, "say", "/s0 where")]],
         check=lambda lines: (len(_s0(lines, "where")) == 1, "in")),
    dict(name="QA16W windows: the 4th is sent away", voc=4, level=8, stay=4, delay=7, logins=[[(3, "say", "/s0 where")]],
         check=lambda lines: (len(_s0(lines, "where")) == 0, "the 4th window was %s" % ("sent away" if not _s0(lines, "where") else "let in"))),
    # QA17 (Q88): a Ranger gets the spear from Dorrow, fights with it and still holds it
    dict(name="QA17 a Ranger's Trailwarden Spear from Dorrow stays in hand after a fight", voc=3, level=12, stay=2,
         logins=[[(3, "say", "/s0 goto Captain Dorrow"), (1, "say", "hi"), (2, "npc", "weapon"), (2, "npc", "spear"),
                  (2, "say", "/s0 hand"), (1, "say", "/s0 spar Field Rat"), (12, "say", "/s0 spar end"), (1, "say", "/s0 hand")]],
         check=lambda lines: ((lambda h, s: (h[0]["gear"] == "f1_ranger_spear" and h[1]["gear"] == "f1_ranger_spear" and s["dealt"] > 0,
                                             "given %s, dealt %s damage, still in hand: %s" % (h[0]["gear"], s["dealt"], h[1]["gear"])))(
             _s0(lines, "hand"), _s0(lines, "sparend")[0]))),
    # QA18 (Q59): with one player online, world events and the weekend rule still run; an arena event waits
    dict(name="QA18 one player online: world events run, the arena waits", voc=4, level=30, stay=2,
         logins=[[(3, "say", "/s0 events")]],
         check=lambda lines: ((lambda e: (e["online"] == 1 and e["event"] != "none" and e["arena"] == 0 and e["weekend"] == 1,
                                          "%(online)s online: world event %(event)s, arena started %(arena)s, weekend bonus %(weekend)s" % e))(_s0(lines, "events")[0]))),
    # WA1: familiarity belongs to its fighter (A levels it, drops it and picks it up, trades it; B carries, then holds it)
    dict(name="WA1 owner: kept through drop and pick-up", voc=4, level=30, partner="WA1 new owner: carried kept, held reset", stay=6,
         logins=[[(3, "say", "/s0 jump 1250 1060 7"), (1, "say", "/s0 offer"), (1, "say", "/rv weapon f1_vanguard_sword 3 0"), (1, "say", "/s0 fam"),
                  (1, "move", "65535 6 0 3264 0 1251 1060 7 1"), (2, "move", "1251 1060 7 3264 1 65535 6 0 1"), (2, "say", "/s0 fam"),
                  (2, "trade", "65535 6 0 3264 0 {partner_id}"), (4, "accept", "")]],
         check=lambda lines: ((lambda f: (f[0]["fam"] == 10 and f[0]["mine"] == 1 and f[1]["fam"] == 10 and f[1]["where"] == "hand",
                                          "levelled: %s; after dropping and picking it up: %s" % (f[0], f[1])))(_s0(lines, "fam")))),
    dict(name="WA1 new owner: carried kept, held reset", voc=4, level=30, partner="WA1 owner: kept through drop and pick-up", stay=3,
         logins=[[(3, "say", "/s0 jump 1250 1061 7"), (1, "say", "/s0 offer"), (10, "trade", "65535 1 0 3355 0 {partner_id}"), (3, "accept", ""),
                  (3, "say", "/s0 fam"), (1, "use", "65535 3 0 2854 0"), (2, "move", "65535 64 0 3264 0 65535 6 0 1"), (2, "say", "/s0 fam"),
                  (1, "say", "/s0 xp Field Rat"), (2, "say", "/s0 fam")]],
         check=lambda lines: ((lambda f: (f[0]["where"] == "carried" and f[0]["fam"] == 10 and f[0]["mine"] == 0
                                          and f[1]["where"] == "hand" and f[1]["fam"] == 0 and f[1]["mine"] == 1 and f[2]["fam"] == 0,
                                          "carried: %s; in hand: %s; after a kill: %s" % (f[0], f[1], f[2])))(_s0(lines, "fam")))),
    # QA19 (Q91): 12 of one guild and 12 others in the Axe-Lord's first kill: 10 of the guild are credited
    dict(name="QA19 the first Axe-Lord kill credits at most 10 of one guild", voc=4, level=60, stay=4,
         logins=[[(3, "say", "/rv floorsreset"), (1, "say", "/s0 guildfight"), (3, "say", "/s0 credit"), (1, "say", "/rv floorsreset")]],
         check=lambda lines: ((lambda c: (c["total"] == 20 and c["guild"] == 10, "%(total)s credited, %(guild)s of them from the guild" % c
                                          + "; fight %s" % _s0(lines, "guildfight")))(_s0(lines, "credit")[0]))),
    # QA21 (Q13): a started season, day 1: the Axe-Lord's hall lets you in
    dict(name="QA21 day 1 of a season: the boss hall is open", voc=4, level=60, stay=2,
         logins=[[(3, "say", "/s0 bosshall"), (6, "say", "/s0 where"), (1, "say", "/s0 launch off")]],
         check=lambda lines: (_s0(lines, "where")[0]["zone"] == "bossroom", "after 6 s still in the hall: %s" % _s0(lines, "where")[0]["zone"])),
]
REVIEW_CASES += STEP0_CASES


async def review_test(only=None):
    e = env()
    db = config_value("mysqlDatabase")
    if not db or db == "spirebound":
        raise SystemExit("refusing: the built server must use a test database, not the game's")
    port = int(config_value("gameProtocolPort") or 7172)
    cases = [c for c in REVIEW_CASES if not only or only.lower() in c["name"].lower()]
    names = []
    for i, c in enumerate(cases):
        c["index"] = 920 + i
        c["char"] = "Loadbot %03d" % c["index"]
        names.append(c["char"])
    sql(e, db, "DELETE FROM players WHERE name IN (%s);" % ", ".join("'%s'" % n for n in names))
    tokens = {}
    for c in cases:   # one at a time: each has its own level and class
        _rows, logins = make_bots(e, db, [(c["index"], c.get("ground", "starter_west"))], level=c["level"], vocs=[c["voc"]] * 4)
        tokens[c["char"]] = logins[0][1]
    plan_file = ROOT / ".build" / "loadtest_plan.txt"
    plan_file.write_text("")
    srv = Server(e, plan_file)
    if not srv.wait_online():
        srv.stop()
        raise SystemExit("server did not start (see .build/loadtest.log)")
    stats = {"online": 0, "failed": 0, "bytes": 0, "errors": []}

    by_name = {x["name"]: x["char"] for x in cases}
    # a character's creature id is 0x10000000 + its database id (Canary's Player::setID): what trades, attacks and party
    # invites address
    ids = {}
    for row in sql(e, db, "SELECT name, id FROM players WHERE name IN (%s);" % ", ".join("'%s'" % n for n in names)).splitlines():
        n, guid = row.rsplit("\t", 1)
        ids[n] = 0x10000000 + int(guid)

    async def play(c):
        await asyncio.sleep(c.get("delay", 0))
        for script in c["logins"]:
            if c.get("partner"):
                partner = by_name.get(c["partner"], "nobody")
                script = [(d, k, t.replace("{partner}", partner).replace("{partner_id}", str(ids.get(partner, 0))))
                          for d, k, t in script]
            await loadbot.Bot(c["char"], tokens[c["char"]], "127.0.0.1", port, stats, script).run(c.get("stay", 3))
            await asyncio.sleep(3)

    try:
        tasks = []
        for c in cases:
            tasks.append(asyncio.create_task(play(c)))
            await asyncio.sleep(0.7)
        await asyncio.gather(*tasks)
        await asyncio.sleep(2)
    finally:
        srv.stop()
    srv.poll_log()
    seen = {}
    for _t, line in srv.lines:
        m = re.search(r"\[LOADTEST\] rv (\w+) (Loadbot \d+)(.*)", line)
        if m:
            kv = {k: (int(v) if re.fullmatch(r"-?\d+", v) else v) for k, v in re.findall(r"(\w+)=(\S+)", m.group(3))}
            seen.setdefault(m.group(2), []).append((m.group(1), kv))
    ok = True
    for c in cases:
        try:
            mine = seen.get(c["char"], [])
            if getattr(c["check"], "needs_all", False):
                good, detail = c["check"](mine, {x["name"]: seen.get(x["char"], []) for x in REVIEW_CASES if "char" in x})
            else:
                good, detail = c["check"](mine)
        except (IndexError, KeyError) as err:
            good, detail = False, "missing log lines (%r): %s" % (err, seen.get(c["char"], []))
        ok = ok and good
        print(f"{'PASS' if good else 'FAIL'}  {c['name']}: {detail}")
    if stats["errors"]:
        print("client notes:", *stats["errors"][:8], sep="\n  ")
    print("review test:", "PASS" if ok else "FAIL")
    return ok


def summarise(lag, samples, t0, t1):
    win = [s for s in samples if t0 <= s[0] <= t1]
    cpu = [s[1] for s in win]
    rss = [s[2] for s in win]
    return dict(lag_avg_ms=round(sum(x.get("lag_avg_ms", 0) for x in lag) / len(lag), 1) if lag else None,
                lag_max_ms=max((x.get("lag_max_ms", 0) for x in lag), default=None),
                late_over_100ms=int(sum(x.get("late_over_100ms", 0) for x in lag)),
                monsters=int(lag[-1]["monsters"]) if lag else None,
                cpu_avg_pct=round(sum(cpu) / len(cpu)) if cpu else None, cpu_max_pct=round(max(cpu)) if cpu else None,
                mem_mb=round(max(rss)) if rss else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["ramp", "capacity", "addon", "review"])
    ap.add_argument("--only", help="review: only the cases whose name contains this")
    ap.add_argument("--steps")
    ap.add_argument("--minutes", type=float)
    ap.add_argument("--warmup", type=float)
    ap.add_argument("--tee", help="also copy the server's output into this file (e.g. on /mnt/c, like the live server)")
    a = ap.parse_args()
    if a.mode == "review":
        sys.exit(0 if asyncio.run(review_test(a.only)) else 1)
    if a.mode == "addon":
        sys.exit(0 if asyncio.run(addon_test()) else 1)
    steps = [int(x) for x in (a.steps or ("10,25,50,75,100,125" if a.mode == "ramp" else "1,2,4,6,8,12")).split(",")]
    minutes = a.minutes or (3 if a.mode == "ramp" else 10)
    warmup = a.warmup if a.warmup is not None else (0.5 if a.mode == "ramp" else 3)
    asyncio.run(run(a.mode, steps, minutes, warmup, a.tee))


if __name__ == "__main__":
    main()
