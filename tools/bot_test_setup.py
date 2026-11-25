#!/usr/bin/env python3
"""Test settings for the built-in bot on Jay's PC (roadmap M5): a HealBot rule (dewfall below 70% health) and a
two-point cavebot route across the Hearth Square, for tools/autopilot.py m5_heal_only_live.

    python tools/bot_test_setup.py on     write the settings (keeps a copy of the bot's saved state)
    python tools/bot_test_setup.py off    remove them and put the saved state back

Files are written with plain line endings: vBot reads a route with Windows line endings as empty (found 2026-11-25).
Run "off" after the test: the settings live in the player's own bot folder."""
import json, os, shutil, sys
from pathlib import Path

BOT = Path(os.environ["APPDATA"]) / "otcr" / "otclient" / "otclient" / "bot" / "vBot_4.8"
ROUTE = BOT / "cavebot_configs" / "m5test.cfg"
HEAL = BOT / "vBot_configs" / "profile_1" / "HealBot.json"
STORE = BOT / "storage" / "profile_1.json"
BACKUP = Path(__file__).resolve().parent.parent / ".local" / "bot_storage_backup.json"


def profile(n, on, spells):
    return {"enabled": on, "spellTable": spells, "itemTable": [], "name": "Profile #%d" % n, "Visible": True,
            "Cooldown": True, "Interval": True, "Conditions": True, "Delay": True, "MessageDelay": False}


def on():
    BACKUP.parent.mkdir(exist_ok=True)
    if STORE.exists():
        shutil.copy(STORE, BACKUP)
    ROUTE.parent.mkdir(parents=True, exist_ok=True)
    ROUTE.write_bytes(b"goto:1229,1303,7\ngoto:1239,1303,7\n")
    HEAL.parent.mkdir(parents=True, exist_ok=True)
    spell = {"index": 1, "spell": "dewfall", "sign": "<", "origin": "HP%", "cost": 5, "value": 70, "enabled": True}
    hb = {"currentHealBotProfile": 1, "healbot": [profile(1, True, [spell])] + [profile(i, False, []) for i in range(2, 6)]}
    HEAL.write_text(json.dumps(hb, indent=2), encoding="utf-8", newline="\n")
    d = json.loads(STORE.read_text(encoding="utf-8")) if STORE.exists() else {}
    d.setdefault("_configs", {})["cavebot_configs"] = {"enabled": True, "selected": "m5test"}
    STORE.write_text(json.dumps(d, indent=2), encoding="utf-8", newline="\n")
    print("bot test settings on")


def off():
    ROUTE.unlink(missing_ok=True)
    HEAL.unlink(missing_ok=True)
    if BACKUP.exists():
        shutil.copy(BACKUP, STORE)
        BACKUP.unlink()
    print("bot test settings off")


{"on": on, "off": off}[sys.argv[1] if len(sys.argv) > 1 else "off"]()
