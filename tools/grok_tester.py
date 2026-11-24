#!/usr/bin/env python3
"""A Grok play tester: Grok plays a fresh character on Jay's local server and writes a playtest report.

How it works: the game client's test module (client/modules/game_autopilot, "live" mode) logs in the character and,
after every move, writes what the character sees (a screenshot, health, nearby monsters and NPCs, recent chat) to
autopilot_state.json. This script sends that to Grok, Grok picks the next move from a fixed menu (walk somewhere,
fight, talk to an NPC, say something, use an item...), and the script turns the move into client steps. At the end
Grok writes a report as a first-time player: what was fun, confusing, boring or broken.

Needs: the server running (windows\\Start-Spirebound.bat) and an xAI API key in server/local.env (never in git):
    XAI_API_KEY=xai-...
    XAI_MODEL=grok-4          (optional: any xAI model that accepts images)
Run:
    python tools/grok_tester.py --fresh              a brand-new character, up to 60 moves / 40 minutes
    python tools/grok_tester.py --turns 30           continue the same character for 30 moves
    python tools/grok_tester.py --dry --fresh        a stand-in brain (no Grok, no cost) to test the plumbing
Reports go to docs/playtests/grok_<time>.md; screenshots and the full transcript to .local/grok_runs/<time>/.
"""
from __future__ import annotations

import base64
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))
import autopilot as AP  # noqa: E402

CHARACTER = "Grok Climber"
API = "https://api.x.ai/v1"
MODEL_PREFERENCE = ["grok-4", "grok-4-latest", "grok-4-fast", "grok-2-vision-1212", "grok-2-vision"]
MAX_SAY = 80


# ---------------------------------------------------------------- settings and the xAI API
def settings():
    out = {}
    env = ROOT / "server" / "local.env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"')
    for k in ("XAI_API_KEY", "XAI_MODEL"):
        if os.environ.get(k):
            out[k] = os.environ[k]
    return out


def api(path, key, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                 method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"grok_tester: the xAI API said {e.code}: {e.read().decode()[:300]}")


def pick_model(key, wanted):
    if wanted:
        return wanted
    have = [m["id"] for m in api("/models", key).get("data", [])]
    for m in MODEL_PREFERENCE:
        if m in have:
            return m
    return have[0] if have else "grok-4"


def jpeg_b64(png_path, width=1024):
    from PIL import Image
    img = Image.open(png_path).convert("RGB")
    if img.width > width:
        img = img.resize((width, int(img.height * width / img.width)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=70)
    return base64.b64encode(buf.getvalue()).decode()


def first_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- what Grok knows about the world
def places(wp):
    """Named places Grok may walk to: town buildings, NPCs, hunting-ground gates (with levels)."""
    out = {}
    for k, v in wp.items():
        if k.startswith("shop_") or k in ("temple_hearthgate", "depot_hearthgate", "monument", "training_yard",
                                          "tutorial_registrar", "tutorial_pen", "trade_hall"):
            out[k.replace("shop_", "").replace("_", " ")] = tuple(v)
    from floor1_plan import CAMPS
    for c in CAMPS:
        if f"gate_{c['id']}" in wp:
            out[f"{c['title']} (levels {c['levels'][0]}-{c['levels'][1]})"] = tuple(wp[f"gate_{c['id']}"])
    npc = (ROOT / "server/data-spirebound/world/spirebound-npc.xml").read_text(encoding="utf-8")
    for cx, cy, cz, body in re.findall(r'<npc centerx="(\d+)" centery="(\d+)" centerz="(\d+)"[^>]*>(.*?)</npc>', npc, re.S):
        for name, x, y in re.findall(r'name="([^"]+)" x="(-?\d+)" y="(-?\d+)"', body):
            px, py = int(cx) + int(x), int(cy) + int(y)
            if cz == "7" and 1000 <= px <= 1500 and 1000 <= py <= 1500:
                out[f"NPC {name}"] = (px, py + 1, 7)      # stand in front of them
    return out


SYSTEM = """You are a play tester for Spirebound, a new Open Tibia server (a Tibia-like online RPG). You are playing a
brand-new character for the first time, like a real new player who has never seen this server. Play naturally: read
signs and NPC lines, follow the hints the game gives you, explore, fight monsters your level, try the quests. The owner
wants honest feedback on whether the game is fun, clear and worth playing, compared with other Open Tibia servers.

Each turn you get a screenshot and the character's state. Reply with ONE JSON object and nothing else:
{"thought": "what you notice and why you choose this", "note": "optional: one piece of feedback for the report
(something fun, confusing, boring, ugly or broken), or empty", "action": {...}}

Actions (pick exactly one):
- {"type": "walk_to", "place": "<a name from the places list>"}  walk there (you fight monsters that block you)
- {"type": "step", "dx": <-8..8>, "dy": <-8..8>}   walk a short way (x grows east, y grows south); stairs and holes
  take you up or down when you step on them
- {"type": "fight", "seconds": <10..60>}   attack the nearest monsters for that long
- {"type": "say", "text": "..."}   say something in public chat: "hi" to start talking to an NPC, a spell's words to
  cast it, or a command like "!spells", "!upgrade", "!guide"
- {"type": "npc", "text": "..."}   after "hi", talk to the NPC (the words in {braces} in their lines are keywords)
- {"type": "use", "dx": <-1..1>, "dy": <-1..1>}   use/open what is on a tile next to you (a chest, a lever, a door)
- {"type": "wait", "seconds": <2..20>}   wait (regain health and mana)
- {"type": "finish"}   stop playing (when you are done or stuck)

Tips: in Tibia you heal by waiting or with potions and healing spells; dying costs experience. Keep moves small when
monsters are near. If an action fails twice, try something else. Never type commands that start with "/"."""


def describe(state, place_names):
    around = sorted(state.get("around", []), key=lambda c: max(abs(c["dx"]), abs(c["dy"])))[:12]
    lines = [
        f"Level {state['level']} (experience {state['experience']}), health {state['health']}/{state['maxHealth']}, "
        f"mana {state['mana']}/{state['maxMana']}, position ({state['x']}, {state['y']}, floor z={state['z']}).",
        "Nearby: " + ("; ".join(f"{c['kind']} {c['name']} at dx={c['dx']}, dy={c['dy']}{'' if c['dz'] == 0 else ', dz=' + str(c['dz'])}"
                                 f" ({c['health']}% health)" for c in around) or "nobody."),
        "Wearing: " + (", ".join(state.get("worn", [])) or "nothing."),
        "Backpack: " + (", ".join(state.get("backpack", [])) or "nothing open."),
        "Recent messages (oldest first):\n" + ("\n".join("  " + m for m in state.get("messages", [])[-15:]) or "  none"),
        "Places you can walk_to: " + "; ".join(place_names),
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- turning a move into client steps
def to_steps(action, state, plan, planner, wp):
    here = (state["x"], state["y"], state["z"])
    t = action.get("type")
    clamp = lambda v, lo, hi: max(lo, min(hi, int(v)))
    if t == "walk_to":
        goal = plan.get(action.get("place", ""))
        if not goal:
            return None, f"unknown place {action.get('place')!r}"
        if goal[2] != here[2]:
            return None, "that place is on another floor: find the stairs first"
        path = planner.path(here, goal, lim=260)
        if path is None:
            return None, "no walkable path from here"
        return [{"do": "walk", "to": list(p), "fight": True, "timeout": 60} for p in AP.hops(path)], None
    if t == "step":
        dx, dy = clamp(action.get("dx", 0), -8, 8), clamp(action.get("dy", 0), -8, 8)
        return [{"do": "walk", "to": [here[0] + dx, here[1] + dy, here[2]], "fight": False, "timeout": 20}], None
    if t == "fight":
        return [{"do": "hunt", "seconds": clamp(action.get("seconds", 20), 10, 60), "radius": 7}], None
    if t in ("say", "npc"):
        text = str(action.get("text", ""))[:MAX_SAY]
        if not text or text.startswith("/"):
            return None, "nothing to say (and commands starting with / are not allowed)"
        return [{"do": t, "text": text}, {"do": "wait", "seconds": 2}], None
    if t == "use":
        dx, dy = clamp(action.get("dx", 0), -1, 1), clamp(action.get("dy", 0), -1, 1)
        return [{"do": "use", "at": [here[0] + dx, here[1] + dy, here[2]]}], None
    if t == "wait":
        return [{"do": "wait", "seconds": clamp(action.get("seconds", 5), 2, 20)}], None
    return None, f"unknown action {t!r}"


# ---------------------------------------------------------------- a stand-in brain (--dry): no Grok, no cost
def dry_brain(state, turn, plan):
    near = sorted(state.get("around", []), key=lambda c: max(abs(c["dx"]), abs(c["dy"])))
    mons = [c for c in near if c["kind"] == "monster" and c["dz"] == 0 and max(abs(c["dx"]), abs(c["dy"])) <= 6]
    npcs = [c for c in near if c["kind"] == "npc" and max(abs(c["dx"]), abs(c["dy"])) <= 3]
    if turn == 4:                                 # exercise the path planner once
        return {"thought": "plumbing test: a long walk", "note": "", "action": {"type": "walk_to", "place": "tutorial registrar"}}
    if state["health"] < state["maxHealth"] * 0.4:
        return {"thought": "low health", "note": "", "action": {"type": "wait", "seconds": 10}}
    if mons:
        return {"thought": "monster near", "note": "", "action": {"type": "fight", "seconds": 20}}
    if npcs and turn % 3 == 0:
        return {"thought": "talk", "note": "", "action": {"type": "say", "text": "hi"}}
    if npcs and turn % 3 == 1:
        return {"thought": "ask", "note": "", "action": {"type": "npc", "text": random.choice(["quest", "yes", "hunt"])}}
    return {"thought": "explore", "note": "dry run", "action": {"type": "step", "dx": random.randint(-6, 6), "dy": random.randint(-6, 6)}}


# ---------------------------------------------------------------- the character
def fresh_character():
    """Delete and re-create the Grok tester: level 1, no vocation, so it starts in the Arrival Yard like a new player."""
    sql = (f"SET @acc=(SELECT id FROM accounts WHERE name='autopilot'); "
           f"SET @old=(SELECT id FROM players WHERE name='{CHARACTER}'); "
           f"DELETE FROM kv_store WHERE @old IS NOT NULL AND key_name LIKE CONCAT('player.', @old, '.%'); "
           f"DELETE FROM players WHERE name='{CHARACTER}'; "
           f"INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience, lookbody, lookfeet, "
           f"lookhead, looklegs, looktype, mana, manamax, town_id, conditions, cap, sex) VALUES ('{CHARACTER}', 1, @acc, 1, 0, "
           f"150, 150, 0, 68, 76, 78, 58, 128, 55, 55, 1, '', 400, 1);")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "--", "mysql", "-h127.0.0.1", "-uspire", "-pspiretest",
                        "spirebound", "-e", sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"grok_tester: could not re-create {CHARACTER}: {r.stderr.strip()}")
    print(f"grok_tester: {CHARACTER} re-created (level 1, starts in the Arrival Yard)")


# ---------------------------------------------------------------- the run
def main(argv):
    opt = lambda name, default: argv[argv.index(name) + 1] if name in argv else default
    dry = "--dry" in argv
    turns, minutes = int(opt("--turns", 60)), float(opt("--minutes", 40))
    cfg = settings()
    key = cfg.get("XAI_API_KEY")
    if key and not key.startswith("xai-"):         # the placeholder windows\Grok-Playtest.bat leaves for Jay
        key = None
    if not dry and not key:
        sys.exit("grok_tester: no XAI_API_KEY. Put XAI_API_KEY=... in server/local.env (see the top of this file), "
                 "or run with --dry to test without Grok.")
    model = "dry" if dry else pick_model(key, cfg.get("XAI_MODEL") or opt("--model", None))
    if not (AP.port_open(8080) and AP.port_open(7172)):
        sys.exit("grok_tester: the server is not running. Start it with windows\\Start-Spirebound.bat first.")
    if "--fresh" in argv:
        fresh_character()
    stamp = time.strftime("%Y-%m-%d_%H%M")
    run_dir = ROOT / ".local" / "grok_runs" / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    wp = AP.world_points()
    planner = AP.Planner(wp)
    plan = places(wp)
    place_names = sorted(plan)
    print(f"grok_tester: model {model}, up to {turns} moves / {minutes:.0f} minutes; files in {run_dir}")

    # start the client in live mode
    wdirs = AP.write_dirs()
    for b in wdirs:
        for f in list(b.rglob("autopilot_state.json")) + list(b.rglob("autopilot_cmd.json")) + list(b.rglob("autopilot_log.txt")):
            f.unlink()
    shutil.copytree(AP.MODULE_SRC, AP.MODULE_DST, dirs_exist_ok=True)
    run = AP.MODULE_DST / "run.json"
    run.write_text(json.dumps({"name": "grok_tester", "account": AP.ACCOUNT, "password": AP.PASSWORD, "character": CHARACTER,
                               "exit": True, "live": True, "steps": []}), encoding="utf-8")
    proc = subprocess.Popen([str(AP.CLIENT / "otclient.exe")], cwd=str(AP.CLIENT))

    def find(name):
        for b in AP.write_dirs():
            for f in b.rglob(name):
                return f
        return None

    def done_in_log():
        log = find("autopilot_log.txt")
        if not log:
            return None
        for ln in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if " DONE " in ln or ln.rstrip().endswith("DONE") or "  DONE" in ln:
                return ln.strip()
        return None

    history, notes, transcript = [], [], []
    seq, deadline, ended = 0, time.time() + minutes * 60, None
    try:
        for turn in range(1, turns + 1):
            # wait for the client to report the result of the last move
            state, t_wait = None, time.time()
            while time.time() - t_wait < 240:
                ended = done_in_log()
                if ended:
                    break
                f = find("autopilot_state.json")
                if f:
                    try:
                        s = json.loads(f.read_text(encoding="utf-8"))
                        if s.get("seq") == seq:
                            state = s
                            break
                    except (json.JSONDecodeError, OSError):
                        pass
                time.sleep(1)
                if turn == 1:
                    run.unlink(missing_ok=True) if find("autopilot_log.txt") else None
            if ended or not state:
                ended = ended or "no answer from the client"
                break
            run.unlink(missing_ok=True)                # the client has read it: Jay's own client must never autopilot
            time.sleep(1.5)                           # the screenshot is written just after the state
            shot = find(state.get("screenshot", "")) if state.get("screenshot") else None
            if shot:
                shutil.copy(shot, run_dir / f"turn_{turn:03d}.png")
            text = describe(state, place_names)
            if dry:
                reply = dry_brain(state, turn, plan)
            else:
                content = [{"type": "text", "text": f"Move {turn}.\n" + text}]
                if shot:
                    content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + jpeg_b64(shot)}})
                msgs = [{"role": "system", "content": SYSTEM}]
                if notes:
                    msgs.append({"role": "user", "content": "Your feedback notes so far:\n" + "\n".join("- " + n for n in notes[-20:])})
                for h in history[-6:]:
                    msgs += [{"role": "user", "content": h["state"]}, {"role": "assistant", "content": json.dumps(h["reply"])}]
                msgs.append({"role": "user", "content": content})
                out = api("/chat/completions", key, {"model": model, "messages": msgs, "temperature": 0.7})
                reply = first_json(out["choices"][0]["message"]["content"]) or {"thought": "unreadable reply", "action": {"type": "wait", "seconds": 3}}
            action = reply.get("action") or {"type": "wait", "seconds": 3}
            if reply.get("note"):
                notes.append(str(reply["note"]))
            print(f"  move {turn:3d}: {json.dumps(action)}  | {str(reply.get('thought', ''))[:110]}", flush=True)
            transcript.append({"turn": turn, "state": text, "reply": reply})
            history.append({"state": f"Move {turn}.\n" + text, "reply": reply})
            if action.get("type") == "finish" or time.time() > deadline:
                ended = "the tester finished" if action.get("type") == "finish" else "time is up"
                break
            steps, err = to_steps(action, state, plan, planner, wp)
            if err:
                history[-1]["reply"] = dict(reply, result=f"that move did not work: {err}")
                steps = [{"do": "wait", "seconds": 1}]
            seq += 1
            cmd = find("autopilot_state.json").parent / "autopilot_cmd.json"
            cmd.write_text(json.dumps({"seq": seq, "steps": steps}), encoding="utf-8")
        else:
            ended = ended or "all moves used"
    finally:
        f = find("autopilot_state.json")
        if f:
            (f.parent / "autopilot_cmd.json").write_text(json.dumps({"seq": seq + 1, "stop": True}), encoding="utf-8")
        run.unlink(missing_ok=True)
        time.sleep(6)
        if proc.poll() is None:
            proc.terminate()
    print(f"grok_tester: ended ({ended}) after {len(transcript)} moves")
    (run_dir / "transcript.json").write_text(json.dumps(transcript, indent=1), encoding="utf-8")
    log = find("autopilot_log.txt")
    if log:
        shutil.copy(log, run_dir / "client_log.txt")

    # the report
    if dry:
        report = "# Dry run (no Grok)\n\n" + "\n".join(f"- move {t['turn']}: {json.dumps(t['reply']['action'])}" for t in transcript)
    else:
        moves = "\n".join(f"{t['turn']}. {t['reply'].get('thought', '')} -> {json.dumps(t['reply'].get('action'))}" for t in transcript)
        ask = ("You just finished a playtest session of Spirebound. Write the playtest report in Markdown for the owner, "
               "who is not a programmer. Sections: 1) What I did (short). 2) What was fun. 3) What was confusing or unclear. "
               "4) What was boring or slow. 5) Bugs or things that looked broken. 6) How it compares with other Open Tibia "
               "servers you know. 7) The five changes that would most make you keep playing. Be specific and honest.\n\n"
               f"How it ended: {ended}.\nYour notes during play:\n" + "\n".join("- " + n for n in notes) + "\n\nYour moves:\n" + moves)
        out = api("/chat/completions", key, {"model": model, "messages": [{"role": "system", "content": SYSTEM},
                                                                       {"role": "user", "content": ask}]})
        report = out["choices"][0]["message"]["content"]
    out_dir = ROOT / "docs" / "playtests"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"grok_{stamp}.md"
    path.write_text(f"*Grok play tester ({model}), {stamp}, {len(transcript)} moves, ended: {ended}. Screenshots and "
                    f"transcript: .local/grok_runs/{stamp}/*\n\n" + report + "\n", encoding="utf-8")
    print(f"grok_tester: report written to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
