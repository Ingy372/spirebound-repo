#!/usr/bin/env python3
"""Claude plays the game by hand, one move at a time (the same live client mode as tools/grok_tester.py, but the
"brain" is whoever runs these commands, so Claude can look at each screenshot and decide the next move itself).

One character:
    python tools/claude_play.py start --fresh            re-create "Claude Climber" (level 1, Arrival Yard) and log in
    python tools/claude_play.py start                    log in the same character where it left off
    python tools/claude_play.py do '{"type": "fight", "seconds": 20}'   one move (grok_tester's menu), then the state
    python tools/claude_play.py do '[{"do": "walk", "to": [1232, 1280, 7]}]'   or raw autopilot steps
    python tools/claude_play.py look                     the last state again
    python tools/claude_play.py places                   the names walk_to accepts
    python tools/claude_play.py stop                     log out and close the client

A party (2026-11-26, the Floor 1 party playtest): several clients at once, each with a short tag.
    python tools/claude_play.py start --as tank --char "Pilot Bram" --account autopilot2 --fresh
    python tools/claude_play.py do --as tank '{"type": "walk_to", "place": "hearth"}'
    python tools/claude_play.py party '{"tank": {...move...}, "heal": [...raw steps...]}'   all at once, waits for all
    python tools/claude_play.py look --as tank | stop --as tank
Characters must be named "Pilot ..." (a test character can never open a floor or claim a first clear).

Extra moves on top of grok_tester's menu: {"type": "walk_to", "to": [x, y, z]} (a planned walk to a tile),
{"type": "hunt", "seconds": 300, "radius": 7}, {"type": "assist", "leader": "Pilot Bram", "seconds": 300, "ranged": true},
{"type": "trade", "buy": [["health potion", 50]], "sell": ["*"]}, {"type": "say"/"npc", "text": ...} (no length cap).
Each move prints level, health, what is around, the chat since the last move, and the screenshot's path (copied to
.local/claude_play/<session>/). Needs the server running. Local testing only (the public autopilot accounts).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))
import autopilot as AP  # noqa: E402
import grok_tester as GT  # noqa: E402

CHARACTER = "Claude Climber"
BRIEF = "--full" not in sys.argv and any(a == "party" for a in sys.argv[1:2])
BASE = ROOT / ".local" / "claude_play"


def opt(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        val = argv[i + 1]
        del argv[i:i + 2]
        return val
    return default


def files(tag):
    sfx = f"_{tag}" if tag else ""
    return f"autopilot_state{sfx}.json", f"autopilot_cmd{sfx}.json", f"autopilot_log{sfx}.txt"


def session_file(tag):
    return BASE / (f"session_{tag}.json" if tag else "session.json")


def find(name):
    for b in AP.write_dirs():
        for f in b.rglob(name):
            return f
    return None


def load(tag):
    f = session_file(tag)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def save(tag, s):
    BASE.mkdir(parents=True, exist_ok=True)
    session_file(tag).write_text(json.dumps(s), encoding="utf-8")


def log_ended(tag):
    log = find(files(tag)[2])
    if not log:
        return None
    for ln in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if ln.rstrip().endswith("DONE") or " DONE " in ln:
            return ln.strip()
    return None


def read_state(tag, seq):
    ended = log_ended(tag)
    if ended:
        return {"ended": ended}
    f = find(files(tag)[0])
    if f:
        try:
            s = json.loads(f.read_text(encoding="utf-8"))
            if s.get("seq") == seq:
                return s
        except (json.JSONDecodeError, OSError):
            pass
    return None


def wait_state(tag, seq, limit=900):
    t = time.time()
    while time.time() - t < limit:
        s = read_state(tag, seq)
        if s:
            if "ended" in s:
                sys.exit(f"claude_play: the client{' ' + tag if tag else ''} stopped: {s['ended']}")
            time.sleep(1.5)                         # the screenshot is written just after the state
            return s
        time.sleep(1)
    sys.exit(f"claude_play: no answer from the client {tag or ''}")


def show(state, sess, tag, shot=True):
    names = sorted(GT.places(AP.world_points()))
    text = GT.describe(state, names)
    text = text[:text.index("Places you can walk_to")].rstrip()     # the long list: see `places`
    head = f"[{tag}] {sess.get('char', '')}  " if tag else ""
    extra = f"   (deaths so far {state.get('died', 0)}, food eaten {state.get('food', 0)})"
    text = head + text.replace("\n", "\n", 1) + extra
    src = find(state.get("screenshot", "")) if state.get("screenshot") else None
    run = Path(sess["run"])
    if src and shot:
        dst = run / f"move_{state['seq']:03d}.png"
        from PIL import Image                       # half size: enough to read the screen, a quarter of the cost to look at
        img = Image.open(src)
        img.resize((img.width // 2, img.height // 2)).save(dst)
        text += f"\nScreenshot: {dst}"
    with open(run / "transcript.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== state {state['seq']} ===\n{text}\n")
    (run / "last_state.txt").write_text(text, encoding="utf-8")
    (run / "last_state.json").write_text(json.dumps(state), encoding="utf-8")
    if BRIEF:                                        # (party) one line plus the game's own messages, not the chatter
        mons = [c for c in state.get("around", []) if c["kind"] == "monster" and c["dz"] == 0]
        noise = ("pilot fightkit", "Pilot ", "You see ", "Using one of")
        msgs = [m for m in state.get("messages", []) if not m.startswith(noise)]
        text = (f"[{tag}] L{state['level']} xp {state['experience']}  hp {state['health']}/{state['maxHealth']}  "
                f"mana {state['mana']}/{state['maxMana']}  at ({state['x']}, {state['y']}, {state['z']})  monsters {len(mons)}"
                f"  deaths {state.get('died', 0)} food {state.get('food', 0)}\n   bag: {', '.join(state.get('backpack', []))[:300]}"
                + "".join(f"\n   | {m[:400]}" for m in msgs[-12:]) + (f"\n   shot: {dst}" if src and shot else ""))
    print(text)


def start(argv):
    tag = opt(argv, "--as")
    char = opt(argv, "--char", CHARACTER)
    account = opt(argv, "--account", "autopilot")
    if not (AP.port_open(8080) and AP.port_open(7172)):
        sys.exit("claude_play: the server is not running.")
    if tag and not char.startswith("Pilot "):
        sys.exit('claude_play: party characters must be named "Pilot ..." (test characters never open a floor)')
    if "--fresh" in argv:
        GT.CHARACTER = char
        fresh(char, account)
    for b in AP.write_dirs():
        for pat in files(tag):
            for f in b.rglob(pat):
                f.unlink()
    shutil.copytree(ROOT / "client" / "modules", AP.CLIENT / "modules", dirs_exist_ok=True)   # all our modules, as autopilot does
    run_file = AP.MODULE_DST / "run.json"
    plan = {"name": "claude_play" + (f"_{tag}" if tag else ""), "account": f"{account}@localhost", "password": AP.PASSWORD,
            "character": char, "exit": True, "live": True, "steps": []}
    if tag:
        plan.update(tag=tag, log=files(tag)[2], home=False)   # never the test jump home when it stops
    run_file.write_text(json.dumps(plan), encoding="utf-8")
    subprocess.Popen([str(AP.CLIENT / "otclient.exe")], cwd=str(AP.CLIENT), stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)   # (a pipe left open would hang the caller)
    run = BASE / (time.strftime("%Y-%m-%d_%H%M") + (f"_{tag}" if tag else ""))
    run.mkdir(parents=True, exist_ok=True)
    sess = {"seq": 0, "run": str(run), "char": char, "account": account}
    save(tag, sess)
    state = wait_state(tag, 0, 180)
    run_file.unlink(missing_ok=True)                 # read: Jay's own client must never start the autopilot
    show(state, sess, tag)


def fresh(char, account):
    """Delete and re-create a test character: level 1, no vocation, so it starts in the Arrival Yard like a new player."""
    sql = (f"SET @acc=(SELECT id FROM accounts WHERE name='{account}'); "
           f"SET @old=(SELECT id FROM players WHERE name='{char}'); "
           f"DELETE FROM kv_store WHERE @old IS NOT NULL AND key_name LIKE CONCAT('player.', @old, '.%'); "
           f"DELETE FROM players WHERE name='{char}'; "
           f"INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience, lookbody, lookfeet, "
           f"lookhead, looklegs, looktype, mana, manamax, town_id, conditions, cap, sex) VALUES ('{char}', 1, @acc, 1, 0, "
           f"150, 150, 0, 68, 76, 78, 58, 128, 55, 55, 1, '', 400, 1);")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "--", "mysql", "-h127.0.0.1", "-uspire", "-pspiretest",
                        "spirebound", "-e", sql], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"claude_play: could not re-create {char}: {r.stderr.strip()}")
    print(f"claude_play: {char} re-created on {account} (level 1, starts in the Arrival Yard)")


def to_steps(move, state):
    """A move (dict) or raw steps (list) into client steps."""
    if isinstance(move, list):
        return move, None
    t = move.get("type")
    here = (state["x"], state["y"], state["z"])
    if t == "walk_to" and "to" in move:
        goal = tuple(move["to"])
        if goal[2] != here[2]:
            return None, "that tile is on another floor"
        path = AP.Planner(AP.world_points()).path(here, goal, lim=400)
        if path is None:
            return None, "no walkable path from here"
        return [{"do": "walk", "to": list(p), "fight": move.get("fight", True), "timeout": 60} for p in AP.hops(path)], None
    if t == "hunt":
        return [{"do": "hunt", "seconds": int(move.get("seconds", 60)), "radius": int(move.get("radius", 7))}], None
    if t == "assist":
        s = {"do": "assist", "leader": move["leader"], "seconds": int(move.get("seconds", 60))}
        for k in ("radius", "leash", "ranged"):
            if k in move:
                s[k] = move[k]
        return [s], None
    if t == "trade":
        return [{"do": "trade", "buy": move.get("buy", []), "sell": move.get("sell", [])}], None
    if t in ("say", "npc"):
        return [{"do": t, "text": str(move.get("text", ""))}, {"do": "wait", "seconds": 2}], None
    wp = AP.world_points()
    planner = AP.Planner(wp) if t == "walk_to" else None
    return GT.to_steps(move, state, GT.places(wp), planner, wp)


def send(tag, move):
    sess = load(tag)
    lj = Path(sess["run"]) / "last_state.json"
    state = json.loads(lj.read_text(encoding="utf-8")) if lj.exists() else wait_state(tag, sess["seq"], 10)
    steps, err = to_steps(move, state)
    if err:
        return f"that move does not work: {err}"
    sess["seq"] += 1
    f = find(files(tag)[0])
    f.parent.joinpath(files(tag)[1]).write_text(json.dumps({"seq": sess["seq"], "steps": steps}), encoding="utf-8")
    save(tag, sess)
    with open(Path(sess["run"]) / "transcript.txt", "a", encoding="utf-8") as fh:
        fh.write(f"\n>>> move {sess['seq']}: {json.dumps(move)}\n")
    return None


def do(argv):
    tag = opt(argv, "--as")
    shot = "--noshot" not in argv
    argv = [a for a in argv if a != "--noshot"]
    err = send(tag, json.loads(argv[0]))
    if err:
        sys.exit("claude_play: " + err)
    sess = load(tag)
    show(wait_state(tag, sess["seq"]), sess, tag, shot)


def party(argv):
    """Several moves at once: {"tag": move, ...}; waits until every client has finished its move."""
    shot = "--noshot" not in argv
    shots = opt(argv, "--shot")                      # only this tag's screenshot (saves looking at three)
    argv = [a for a in argv if a != "--noshot"]
    moves = json.loads(argv[0])
    for tag, move in moves.items():
        err = send(tag, move)
        if err:
            print(f"[{tag}] {err}")
    pending = {t: load(t)["seq"] for t in moves}
    end = time.time() + 1800
    while pending and time.time() < end:
        for tag, seq in list(pending.items()):
            s = read_state(tag, seq)
            if s:
                del pending[tag]
                if "ended" in s:
                    print(f"[{tag}] the client stopped: {s['ended']}")
                    continue
                time.sleep(1.5)
                show(s, load(tag), tag, shot and (shots is None or shots == tag))
                print()
        time.sleep(1)
    for tag in pending:
        print(f"[{tag}] no answer yet")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, rest = argv[0], list(argv[1:])
    if cmd == "start":
        start(rest)
    elif cmd == "do":
        do(rest)
    elif cmd == "party":
        party(rest)
    elif cmd == "look":
        tag = opt(rest, "--as")
        print((Path(load(tag)["run"]) / "last_state.txt").read_text(encoding="utf-8"))
    elif cmd == "places":
        print("\n".join(sorted(GT.places(AP.world_points()))))
    elif cmd == "stop":
        tag = opt(rest, "--as")
        sess = load(tag)
        f = find(files(tag)[0])
        if f:
            f.parent.joinpath(files(tag)[1]).write_text(json.dumps({"seq": sess.get("seq", 0) + 1, "stop": True}))
        print("claude_play: asked the client to stop")
    else:
        sys.exit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
