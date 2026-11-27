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
    4: ("Captain Dorrow", [("Moonhowl", 1), ("Granite Warden", 1)]),
    3: ("Hunter Brannoch", [("Blackthorn", 1), ("Bandit Crossbowman", 40)]),
    1: ("Vesper", [("Prism Shardling", 1), ("Hedge Hexer", 30)]),
    2: ("Fisher Corwin", [("Mossback Snapper", 1), ("Field Shardling", 40)]),
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
        for target, count in steps:
            script += [(1, "say", "/lt goto " + giver), (2, "say", "hi"), (2, "npc", "outfit"), (2, "npc", "yes"),
                       (1, "say", "/lt state")]
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
    dict(name="A4-5 a boss kill after a lost fight record still credits", voc=4, level=60,
         logins=[[(3, "say", "/rv bossreload")]], stay=4,
         check=lambda lines: (_rv(lines, "bossreload")[0]["credited"] == 1 and _rv(lines, "bossreload")[0]["had_record"] == 1,
                              "had a record %(had_record)s, credited %(credited)s" % _rv(lines, "bossreload")[0])),
] + [
    # A8-2: each Death Game victim dies beside its own real partner character ("{partner}" is that character's name)
    case for kind, want in (("dragfought", "retire"), ("dragged", "saved"), ("firstvictim", "retire"), ("firstother", "saved"))
    for case in (
        dict(name=f"A8-2 DG {kind}: {want}", voc=4, level=60, partner=f"A8-2 partner {kind}",
             logins=[[(1, "unsecure", ""), (5, "say", "/rv dg " + kind + " {partner}")]], stay=4, check=_check_dg(kind, want)),
        dict(name=f"A8-2 partner {kind}", voc=4, level=60, logins=[[(1, "unsecure", ""), (1, "say", "/rv state")]], stay=14,
             check=lambda lines: (True, "partner")))
]


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

    async def play(c):
        for script in c["logins"]:
            if c.get("partner"):
                script = [(d, k, t.replace("{partner}", by_name.get(c["partner"], "nobody"))) for d, k, t in script]
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
