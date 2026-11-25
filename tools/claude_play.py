#!/usr/bin/env python3
"""Claude plays the game by hand, one move at a time (the same live client mode as tools/grok_tester.py, but the
"brain" is whoever runs these commands, so Claude can look at each screenshot and decide the next move itself).

    python tools/claude_play.py start --fresh            re-create "Claude Climber" (level 1, Arrival Yard) and log in
    python tools/claude_play.py start                    log in the same character where it left off
    python tools/claude_play.py do '{"type": "fight", "seconds": 20}'   one move (grok_tester's menu), then the state
    python tools/claude_play.py do '[{"do": "walk", "to": [1200, 1300, 7]}]'   or raw autopilot steps
    python tools/claude_play.py look                     the last state again
    python tools/claude_play.py places                   the names walk_to accepts
    python tools/claude_play.py stop                     log out and close the client

Each move prints level, health, what is around, the chat since the last move, and the screenshot's path (copied to
.local/claude_play/<session>/). Needs the server running. Local testing only (the public autopilot account).
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
SESSION = ROOT / ".local" / "claude_play" / "session.json"


def find(name):
    for b in AP.write_dirs():
        for f in b.rglob(name):
            return f
    return None


def load():
    return json.loads(SESSION.read_text(encoding="utf-8")) if SESSION.exists() else {}


def save(s):
    SESSION.parent.mkdir(parents=True, exist_ok=True)
    SESSION.write_text(json.dumps(s), encoding="utf-8")


def log_ended():
    log = find("autopilot_log.txt")
    if not log:
        return None
    for ln in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if ln.rstrip().endswith("DONE") or " DONE " in ln:
            return ln.strip()
    return None


def wait_state(seq, limit=300):
    t = time.time()
    while time.time() - t < limit:
        ended = log_ended()
        if ended:
            sys.exit(f"claude_play: the client stopped: {ended}")
        f = find("autopilot_state.json")
        if f:
            try:
                s = json.loads(f.read_text(encoding="utf-8"))
                if s.get("seq") == seq:
                    time.sleep(1.5)                 # the screenshot is written just after the state
                    return s
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(1)
    sys.exit("claude_play: no answer from the client")


def show(state, sess):
    names = sorted(GT.places(AP.world_points()))
    text = GT.describe(state, names)
    text = text[:text.index("Places you can walk_to")].rstrip()     # the long list: see `places`
    shot = find(state.get("screenshot", "")) if state.get("screenshot") else None
    run = Path(sess["run"])
    if shot:
        dst = run / f"move_{state['seq']:03d}.png"
        from PIL import Image                       # half size: enough to read the screen, a quarter of the cost to look at
        img = Image.open(shot)
        img.resize((img.width // 2, img.height // 2)).save(dst)
        text += f"\nScreenshot: {dst}"
    with open(run / "transcript.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== state {state['seq']} ===\n{text}\n")
    (run / "last_state.txt").write_text(text, encoding="utf-8")
    print(text)


def start(argv):
    if not (AP.port_open(8080) and AP.port_open(7172)):
        sys.exit("claude_play: the server is not running.")
    if "--fresh" in argv:
        GT.CHARACTER = CHARACTER
        GT.fresh_character()
    for b in AP.write_dirs():
        for pat in ("autopilot_state.json", "autopilot_cmd.json", "autopilot_log.txt"):
            for f in b.rglob(pat):
                f.unlink()
    shutil.copytree(ROOT / "client" / "modules", AP.CLIENT / "modules", dirs_exist_ok=True)   # all our modules, as autopilot does
    run_file = AP.MODULE_DST / "run.json"
    run_file.write_text(json.dumps({"name": "claude_play", "account": AP.ACCOUNT, "password": AP.PASSWORD,
                                    "character": CHARACTER, "exit": True, "live": True, "steps": []}), encoding="utf-8")
    subprocess.Popen([str(AP.CLIENT / "otclient.exe")], cwd=str(AP.CLIENT))
    run = ROOT / ".local" / "claude_play" / time.strftime("%Y-%m-%d_%H%M")
    run.mkdir(parents=True, exist_ok=True)
    sess = {"seq": 0, "run": str(run)}
    save(sess)
    state = wait_state(0, 180)
    run_file.unlink(missing_ok=True)                 # read: Jay's own client must never start the autopilot
    show(state, sess)


def do(argv):
    sess = load()
    state = json.loads((Path(sess["run"]) / "last_state.json").read_text(encoding="utf-8")) \
        if (Path(sess["run"]) / "last_state.json").exists() else wait_state(sess["seq"], 10)
    move = json.loads(argv[0])
    if isinstance(move, list):
        steps = move
    else:
        wp = AP.world_points()
        planner = AP.Planner(wp) if move.get("type") == "walk_to" else None
        steps, err = GT.to_steps(move, state, GT.places(wp), planner, wp)
        if err:
            sys.exit(f"claude_play: that move does not work: {err}")
    sess["seq"] += 1
    find("autopilot_state.json").parent.joinpath("autopilot_cmd.json").write_text(
        json.dumps({"seq": sess["seq"], "steps": steps}), encoding="utf-8")
    save(sess)
    with open(Path(sess["run"]) / "transcript.txt", "a", encoding="utf-8") as f:
        f.write(f"\n>>> move {sess['seq']}: {argv[0]}\n")
    state = wait_state(sess["seq"])
    (Path(sess["run"]) / "last_state.json").write_text(json.dumps(state), encoding="utf-8")
    show(state, sess)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, rest = argv[0], argv[1:]
    if cmd == "start":
        start(rest)
    elif cmd == "do":
        do(rest)
    elif cmd == "look":
        print((Path(load()["run"]) / "last_state.txt").read_text(encoding="utf-8"))
    elif cmd == "places":
        print("\n".join(sorted(GT.places(AP.world_points()))))
    elif cmd == "stop":
        sess = load()
        f = find("autopilot_state.json")
        if f:
            f.parent.joinpath("autopilot_cmd.json").write_text(json.dumps({"seq": sess.get("seq", 0) + 1, "stop": True}))
        print("claude_play: asked the client to stop")
    else:
        sys.exit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
