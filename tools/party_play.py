#!/usr/bin/env python3
"""A party of test characters plays Floor 1 on its own, ground after ground (the Floor 1 party playtest, 2026-11-26).

    python tools/party_play.py run [--minutes 120] [--ground <id>]    hunt, resupply in town, move up as levels rise
    python tools/party_play.py town                                   one resupply trip now
    python tools/party_play.py report                                 the numbers so far, one line per ground

Uses the clients that `tools/claude_play.py start --as <tag>` opened (tags tank, heal, dps; tank leads). All three
walk the same planned path as a pack (followers can't follow a leader down a hole), fight what comes close, hunt at
each of the ground's loop points (surface and cave), and heal each other (the client's party heals). Between laps it
checks supplies: low on potions or a heavy bag sends the party to town to sell loot (Trader Osric) and buy potions
(Alchemist Ivo) and food (Innkeeper Roan). Every lap is written to .local/claude_play/party_laps.jsonl: time, ground,
experience, gold, potions and food used, deaths, lowest health, per character. No /pilot shortcuts: real levels, real
walking, real shops (the client only asks "/pilot fightkit" to know which spells it has learned).
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))
import autopilot as AP  # noqa: E402
import claude_play as CP  # noqa: E402
import grok_tester as GT  # noqa: E402

TAGS = ["tank", "heal", "dps"]
LAPS = ROOT / ".local" / "claude_play" / "party_laps.jsonl"
# (ground id, title, levels) easiest first: the party hunts the hardest ground its lowest member is ready for
GROUNDS = [
    ("starter_east", "Toad Pond", 3, 7),
    ("starter_south", "Sproutling Glade", 5, 10),
    ("wasp_fields", "Waspgrass Fields", 7, 12),
    ("boar_meadow", "Boar Meadow", 9, 15),
    ("burrow_hills", "Burrow Hills", 11, 16),
    ("wolf_copse", "Wolf Copse", 12, 18),
    ("reed_marsh", "Reedmarsh", 14, 19),
    ("thornsnap_hollow", "Thornsnap Hollow", 14, 20),
    ("shard_fields", "Shard Fields", 17, 24),
    ("bandit_road", "The Bandit Road", 19, 27),
    ("old_quarry", "The Old Quarry", 23, 30),
]
HUNT = 75                    # seconds at each loop point
COINS = {"item 3031": 1, "gold coin": 1, "item 3035": 100, "platinum coin": 100, "item 3043": 10000, "crystal coin": 10000}
POTIONS = {"heal": ("health potion", "strong health potion"), "mana": ("mana potion", "strong mana potion")}
WANT = {"tank": {"health potion": 30, "mana potion": 10}, "heal": {"mana potion": 40, "health potion": 15},
        "dps": {"mana potion": 40, "health potion": 15}}   # bought in this order while the gold lasts


def wp():
    return AP.world_points()


_PLANNER = None


def planner():
    global _PLANNER
    if _PLANNER is None:
        _PLANNER = AP.Planner(wp())
    return _PLANNER


def state(tag):
    sess = CP.load(tag)
    f = Path(sess["run"]) / "last_state.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def bag_count(st, name):
    n = 0
    for e in st.get("backpack", []):
        m = re.match(r"(.+?)(?: x(\d+))?$", e)
        if m and m.group(1) == name:
            n += int(m.group(2) or 1)
    return n


def gold(st):
    return sum(bag_count(st, k) * v for k, v in COINS.items())


def everyone(steps_for, label, limit=1800):
    """Send each tag its steps (a function of its state), wait for all, return the new states."""
    sent = {}
    for t in TAGS:
        st = state(t)
        steps = steps_for(t, st)
        if not steps:
            continue
        err = CP.send(t, steps)
        if err:
            print(f"  [{t}] {err}")
            continue
        sent[t] = CP.load(t)["seq"]
    out, end = {}, time.time() + limit
    while sent and time.time() < end:
        for t, seq in list(sent.items()):
            s = CP.read_state(t, seq)
            if s:
                del sent[t]
                if "ended" in s:
                    sys.exit(f"party_play: client {t} stopped: {s['ended']}")
                time.sleep(1)
                sess = CP.load(t)
                (Path(sess["run"]) / "last_state.json").write_text(json.dumps(s), encoding="utf-8")
                out[t] = s
        time.sleep(1)
    for t in sent:
        print(f"  [{t}] no answer after {label}")
    return out


def walk_steps(here, goal, fight=True):
    """A planned walk on one floor, as short hops."""
    if here[2] != goal[2]:
        return [{"do": "walk", "to": list(goal), "fight": fight, "timeout": 60}]
    path = planner().path(tuple(here), tuple(goal), lim=400)
    if path is None:
        return [{"do": "walk", "to": list(goal), "fight": fight, "timeout": 90}]
    return [{"do": "walk", "to": list(p), "fight": fight, "timeout": 60} for p in AP.hops(path)]


_BESIDE = {}


def beside(npc):
    """A tile next to an NPC that can be walked to from the temple (not behind its counter)."""
    if npc in _BESIDE:
        return _BESIDE[npc]
    temple = tuple(wp()["temple_hearthgate"])
    for r in (1, 2, 3):
        ring = [(npc[0] + dx, npc[1] + dy, npc[2]) for dy in range(r, -r - 1, -1) for dx in range(-r, r + 1)
                if max(abs(dx), abs(dy)) == r]
        for p in ring:
            if planner().ok(p) and planner().path(temple, p, lim=400) is not None:
                _BESIDE[npc] = p
                return p
    return (npc[0], npc[1] + 1, npc[2])


def stairs_for(gid, near):
    """The ground's cave stairs (the stairs-up tile on z 8) closest to a cave point."""
    pts = [v for k, v in wp().items() if k.startswith(f"stairs_{gid}_") or k == f"stairs_den_{gid}"]
    pts = [p for p in pts if p[2] == near[2]]
    return min(pts, key=lambda p: abs(p[0] - near[0]) + abs(p[1] - near[1])) if pts else None


def lap_plan(gid):
    """The ground's loop: [(kind, point)], kind = walk (surface hunt spot), down/up (cave stairs), cave (cave spot)."""
    w = wp()
    loops = sorted((k, v) for k, v in w.items() if k.startswith(f"loop_{gid}_"))
    surface = [v for k, v in loops if v[2] == 7]
    cave = [v for k, v in loops if v[2] == 8]
    plan = [("walk", w[f"gate_{gid}"])] + [("hunt", p) for p in surface]
    for c in cave:
        st = stairs_for(gid, c)
        if st:
            plan += [("down", st), ("hunt", c), ("up", st)]
    plan.append(("walk", w[f"gate_{gid}"]))
    return plan


def segment_steps(kind, p, here):
    if kind == "walk":
        return walk_steps(here, p)
    if kind == "hunt":
        return walk_steps(here, p) + [{"do": "hunt", "seconds": HUNT, "radius": 7}]
    if kind == "down":                         # walk onto the hole/stairs above the cave's stairs-up tile
        above = (p[0], p[1], p[2] - 1)
        steps = walk_steps(here, above)
        steps[-1]["arrive_z"] = p[2]
        return steps
    if kind == "up":
        steps = walk_steps(here, p)
        steps[-1]["arrive_z"] = p[2] - 1
        return steps
    return []


def snapshot():
    out = {}
    for t in TAGS:
        st = state(t) or {}
        out[t] = dict(level=st.get("level"), xp=st.get("experience", 0), gold=gold(st), died=st.get("died", 0),
                      food=st.get("food", 0), hp_pots=sum(bag_count(st, n) for n in POTIONS["heal"]),
                      mana_pots=sum(bag_count(st, n) for n in POTIONS["mana"]))
    return out


def lowest_hp_since(tag, since):
    """The lowest health % in this client's log since `since` (seconds into the run), from the sample lines."""
    f = CP.find(CP.files(tag)[2])
    low = 100
    if f:
        for ln in f.read_text(encoding="utf-8", errors="replace").splitlines()[-4000:]:
            m = re.match(r"\s*([\d.]+)\s+at .* health (\d+)%", ln)
            if m and float(m.group(1)) >= since:
                low = min(low, int(m.group(2)))
    return low


def run_lap(gid, title):
    before, t0 = snapshot(), time.time()
    for kind, p in lap_plan(gid):
        everyone(lambda t, st: segment_steps(kind, p, (st["x"], st["y"], st["z"])), f"{kind} {p}")
    after = snapshot()
    secs = time.time() - t0
    rec = {"t": time.strftime("%H:%M"), "ground": title, "secs": int(secs), "chars": {}}
    for t in TAGS:
        a, b = before[t], after[t]
        rec["chars"][t] = dict(level=b["level"], xp=b["xp"] - a["xp"], gold=b["gold"] - a["gold"], deaths=b["died"] - a["died"],
                               food=b["food"] - a["food"], hp_pots=a["hp_pots"] - b["hp_pots"],
                               mana_pots=a["mana_pots"] - b["mana_pots"])
    LAPS.parent.mkdir(parents=True, exist_ok=True)
    with open(LAPS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    xph = {t: int(rec["chars"][t]["xp"] * 3600 / max(1, secs)) for t in TAGS}
    print(f"{rec['t']} {title}: lap {int(secs)}s; " + "; ".join(
        f"{t} L{rec['chars'][t]['level']} xp/h {xph[t]} gold {rec['chars'][t]['gold']:+d} hp-pots {rec['chars'][t]['hp_pots']} "
        f"mana-pots {rec['chars'][t]['mana_pots']} deaths {rec['chars'][t]['deaths']}" for t in TAGS), flush=True)
    return rec


def needs_town():
    """A town trip when someone is nearly out of potions, a bag is full, or someone can afford a real restock."""
    for t in TAGS:
        st = state(t) or {}
        hp = sum(bag_count(st, n) for n in POTIONS["heal"])
        mp = sum(bag_count(st, n) for n in POTIONS["mana"])
        if len(st.get("backpack", [])) >= 18:
            return f"{t}'s backpack is nearly full"
        if hp < 2 or (t != "tank" and mp < 2):
            return f"{t} is nearly out of potions"
        if gold(st) >= 400 and (hp < 8 or (t != "tank" and mp < 10)):
            return f"{t} can afford a restock"
    return None


def town():
    """Sell loot, buy potions and food, the way a player does."""
    pl = GT.places(wp())
    funds = {}
    def bank(t, st):
        here = (st["x"], st["y"], st["z"])
        talk = [{"do": "say", "text": "hi"}, {"do": "wait", "seconds": 2}]
        for w in ("deposit all", "yes", "balance", "bye"):
            talk += [{"do": "npc", "text": w}, {"do": "wait", "seconds": 2}]
        return walk_steps(here, beside(pl["NPC Banker Tolliver"])) + talk
    for npc, trade in (("NPC Trader Osric", lambda t, st: {"sell": ["*"]}),
                       ("NPC Alchemist Ivo", lambda t, st: {"sell": ["empty potion flask"],
                                                             "buy": [[k, max(0, n - bag_count(st, k))] for k, n in WANT[t].items()
                                                                     if n - bag_count(st, k) > 0]}),
                       ("NPC Innkeeper Roan", lambda t, st: {"buy": [["ham", max(0, 10 - bag_count(st, "ham"))]]})):
        goal = pl.get(npc)
        if not goal:
            print(f"  town: no {npc}")
            continue
        if npc == "NPC Alchemist Ivo":           # after selling: bank the coins (stacks of 100 fill a 20-slot bag); shops
            for t in TAGS:                       # take the price from the bank (checked 2026-11-26)
                funds[t] = gold(state(t) or {})
            out = everyone(bank, "bank")
            for t, st in out.items():
                bal = [m for m in st.get("messages", []) if "balance" in m.lower()]
                if bal:
                    m = re.search(r"([\d,]+) gold", bal[-1])
                    if m:
                        funds[t] = max(funds[t], int(m.group(1).replace(",", "")))
            print("  bank: " + ", ".join(f"{t} {funds[t]} gold" for t in TAGS), flush=True)
            # a party shares: whoever got the loot (the kill credit) tops up the others through the bank
            rich = max(TAGS, key=lambda t: funds[t])
            need = {t: 600 - funds[t] for t in TAGS if t != rich and funds[t] < 600}
            give = {t: min(n, max(0, (funds[rich] - 600) // max(1, len(need)))) for t, n in need.items()}
            give = {t: g for t, g in give.items() if g >= 50}
            if give:
                names = {t: CP.load(t)["char"] for t in TAGS}
                def share(t, st):
                    if t != rich:
                        return []
                    talk = [{"do": "say", "text": "hi"}, {"do": "wait", "seconds": 2}]
                    for o, g in give.items():
                        talk += [{"do": "npc", "text": f"transfer {g} to {names[o]}"}, {"do": "wait", "seconds": 2},
                                 {"do": "npc", "text": "yes"}, {"do": "wait", "seconds": 2}]
                    return talk + [{"do": "npc", "text": "bye"}]
                everyone(share, "share")
                for o, g in give.items():
                    funds[o] += g
                    funds[rich] -= g
                print(f"  shared: {rich} sent " + ", ".join(f"{g} to {o}" for o, g in give.items()), flush=True)
        def steps(t, st, goal=goal, trade=trade):
            here = (st["x"], st["y"], st["z"])
            tr = trade(t, st)
            tr["buy"] = [b for b in tr.get("buy", []) if b[1] > 0]
            # can't afford it all: buy what the gold allows (potions about 50 each, food 8)
            g = funds.get(t, gold(st))
            for b in tr["buy"]:
                each = 8 if b[0] == "ham" else 50
                b[1] = min(b[1], max(0, g // each))
                g -= b[1] * each
            funds[t] = g
            tr["buy"] = [b for b in tr["buy"] if b[1] > 0]
            near = beside(goal)
            return walk_steps(here, near, fight=True) + [{"do": "trade", **tr}, {"do": "wait", "seconds": 2}]
        everyone(steps, f"town {npc}")
    print("town: " + "; ".join(f"{t} gold {gold(state(t))} hp-pots {bag_count(state(t), 'health potion')} "
                               f"mana-pots {bag_count(state(t), 'mana potion')} ham {bag_count(state(t), 'ham')}" for t in TAGS), flush=True)


def pick_ground(force=None):
    if force:
        return next(g for g in GROUNDS if g[0] == force)
    low = min((state(t) or {}).get("level", 1) for t in TAGS)
    ok = [g for g in GROUNDS if g[2] <= low]
    return ok[-1] if ok else GROUNDS[0]


def run(argv):
    minutes = float(CP.opt(argv, "--minutes", 120))
    force = CP.opt(argv, "--ground")
    plan = [g for g in (CP.opt(argv, "--plan", "") or "").split(",") if g]   # e.g. boar_meadow,wasp_fields: these laps first
    end = time.time() + minutes * 60
    while time.time() < end:
        why = needs_town()
        if why:
            print(f"town trip: {why}", flush=True)
            town()
        gid, title, lo, hi = pick_ground(plan.pop(0) if plan else force)
        run_lap(gid, title)


def report():
    if not LAPS.exists():
        print("no laps yet")
        return
    by = {}
    for ln in LAPS.read_text(encoding="utf-8").splitlines():
        r = json.loads(ln)
        g = by.setdefault(r["ground"], {"secs": 0, "laps": 0, **{t: dict(xp=0, gold=0, hp=0, mp=0, deaths=0, food=0, lv=0) for t in TAGS}})
        g["secs"] += r["secs"]
        g["laps"] += 1
        for t, c in r["chars"].items():
            g[t]["xp"] += c["xp"]; g[t]["gold"] += c["gold"]; g[t]["hp"] += c["hp_pots"]; g[t]["mp"] += c["mana_pots"]
            g[t]["deaths"] += c["deaths"]; g[t]["food"] += c["food"]; g[t]["lv"] = c["level"]
    for name, g in by.items():
        h = max(1, g["secs"]) / 3600
        print(f"{name}: {g['laps']} laps, {g['secs'] // 60} min")
        for t in TAGS:
            c = g[t]
            print(f"   {t:4s} to L{c['lv']}: {int(c['xp'] / h)} xp/h, {int(c['gold'] / h):+d} gold/h (after shopping not counted), "
                  f"{c['hp'] / h:.0f} health and {c['mp'] / h:.0f} mana potions/h, {c['food']} food, {c['deaths']} deaths")


QUEST_GIVERS = ["NPC Captain Dorrow", "NPC Hunter Brannoch", "NPC Fisher Corwin", "NPC Miller Agna"]


def quests(givers=None):
    """Visit the quest givers: hand in what is finished, take what is offered (each says hi, report, quest, yes)."""
    pl = GT.places(wp())
    for npc in givers or QUEST_GIVERS:
        goal = pl[npc]
        def steps(t, st, goal=goal):
            here = (st["x"], st["y"], st["z"])
            talk = [{"do": "say", "text": "hi"}, {"do": "wait", "seconds": 2}]
            for w in ("report", "quest", "yes", "quest", "yes", "bye"):
                talk += [{"do": "npc", "text": w}, {"do": "wait", "seconds": 2}]
            return walk_steps(here, beside(goal)) + talk
        out = everyone(steps, f"quests {npc}")
        for t, st in out.items():
            said = [m for m in st.get("messages", []) if m.startswith(npc[4:] + ":") or "quest" in m.lower() or "experience" in m]
            print(f"  [{t}] {npc[4:]}: " + " / ".join(m[:160] for m in said[-6:]), flush=True)


def form():
    """The tank invites, the others accept, shared experience on: the way players do it."""
    names = {t: CP.load(t)["char"] for t in TAGS}
    lead = names["tank"]
    everyone(lambda t, st: [{"do": "party", "invite": [names["heal"], names["dps"]], "share": True, "seconds": 60}] if t == "tank"
             else [{"do": "wait", "seconds": 4}, {"do": "party", "join": lead, "seconds": 60}], "party")
    print("party: " + ", ".join(f"{t} shield {state(t).get('shield')}" for t in TAGS))


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, rest = argv[0], list(argv[1:])
    if cmd == "run":
        run(rest)
    elif cmd == "quests":
        quests(rest or None)
    elif cmd == "form":
        form()
    elif cmd == "town":
        town()
    elif cmd == "report":
        report()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
