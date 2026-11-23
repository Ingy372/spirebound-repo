#!/usr/bin/env python3
"""The client's spellbook, cooldown bar and action bar list Spirebound's spells (not Tibia's).

  python tools/gen_spellbook.py           write client/modules/gamelib/spells.lua and game_spelllist/spelllist.otui
  python tools/gen_spellbook.py --check   fail if they are out of date with the server's spell tables

Reads the server's tables (server/data-spirebound/lib/spirebound/spells.lua and sword_skills.lua) and the stock
client files in .local/client (OTClient Redemption, MIT); swaps in our spells, vocation names and filter labels.
Spell ids match the server's (301+ spells, 241+ sword skills), so cooldown icons light up.
Icons borrow the stock spell icon sheet until our own icons exist (ART_REQUESTS.md, spell icons).
Run it after any change to the spell tables (the in-game test checks the counts match).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "server" / "data-spirebound" / "lib" / "spirebound"
STOCK = ROOT / ".local" / "client" / "modules"
OUT = ROOT / "client" / "modules"

VOC = {"A": 1, "M": 2, "R": 3, "V": 4}
VOC_NAME = {1: "Arcanist", 2: "Mystic", 3: "Ranger", 4: "Vanguard"}
NAMES = {0: "None", 1: "Arcanist", 2: "Mystic", 3: "Ranger", 4: "Vanguard",
         5: "High Arcanist", 6: "Elder Mystic", 7: "Far Warden", 8: "Blade Warden"}
GROUP_MS = {"attack": 2000, "healing": 1000, "support": 2000}
GROUP_ID = {"attack": 1, "healing": 2, "support": 3}
ELEMENT = {"FIRE": "fire", "ENERGY": "energy", "ICE": "ice", "EARTH": "earth", "HOLY": "holy", "PHYSICAL": "physical", "DEATH": "death"}

# stock icon numbers (index into the client's spell icon sheet)
ICON_TARGET = {"fire": 25, "energy": 28, "ice": 31, "earth": 34, "holy": 38, "death": 37, "physical": 17}
ICON_AREA = {"fire": 43, "energy": 40, "ice": 45, "earth": 46, "holy": 39, "death": 53, "physical": 24}
ICON_BIG = {"fire": 48, "energy": 51, "ice": 49, "earth": 47, "holy": 39, "death": 53, "physical": 23}
ICON_KIND = {
    "heal_self": 5, "heal": 6, "heal_target": 7, "heal_party": 8, "heal_zone": 8, "heal_burst": 8, "heal_chain": 8,
    "hot_target": 14, "heal_last_stand": 59, "mana_party": 14, "haste": 100, "party_haste": 101, "dash": 97,
    "blink": 97, "leap_away": 97, "trail_dash": 97, "manashield": 123, "dr_self": 121, "dr_target": 121,
    "dr_party": 121, "dr_adjacent": 121, "reflect": 121, "party_buff": 95, "form": 150, "taunt": 96, "light": 116,
    "find_person": 113, "reveal": 113, "levitate": 124, "purify": 9, "cleanse": 9, "summon": 117, "decoy": 117,
    "invisible": 138, "food": 106, "seed": 106, "undying": 59, "mark": 109, "slow_area": 110, "gravity": 136,
    "vine_wall": 47, "breach": 17, "banner": 111, "break_free": 118, "strike": 22,
}
ICON_FAMILY = {"sword": 22, "axe": 21, "club": 24, "bow": 17, "crossbow": 58, "spear": 18, "wand": 126, "fist": 16}

WHAT = {
    "attack_target": "Strikes your target", "attack_area": "Hits every monster in an area",
    "zone": "Leaves burning ground that hurts whatever stands in it", "conjure": "Makes items from a blank rune or from nothing",
    "party_buff": "Strengthens you and your party for a while", "heal_self": "Heals you",
    "form": "Takes on a battle form for a while", "heal_party": "Heals you and your party nearby",
    "haste": "Makes you faster for a while, and frees you from slows and roots", "dr_party": "Your party takes less damage for a while",
    "taunt": "Makes nearby monsters attack you", "summon": "Calls a creature to fight beside you",
    "strike": "A heavy melee blow", "heal_zone": "Heals everyone of your party standing in the area for a while",
    "heal_target": "Heals a friend (say the name; no name heals you)", "blink": "Jumps you a few tiles forward",
    "vine_wall": "Grows a wall of vines across the way ahead (fire burns it)", "undying": "The next killing blow leaves you at 1 health",
    "trail_dash": "Dashes forward leaving a trail of fire", "slow_area": "Slows every monster around you",
    "seed": "Plants a seed that saves you from a monster's killing blow", "reveal": "Shows hidden creatures nearby",
    "reflect": "Throws part of the damage you take back at the attacker", "purify": "Removes poison, burns and other bad effects",
    "party_haste": "Makes your whole party faster and frees them from slows", "mark": "Marks your target: everyone hits it harder",
    "manashield": "Damage takes your mana before your health", "mana_party": "Restores mana to your party",
    "light": "Makes light around you", "levitate": "Floats you up or down a level (say up or down)",
    "leap_away": "Leaps you back away from danger", "invisible": "Makes you invisible to most monsters",
    "hot_target": "Heals a friend a little at a time", "heal_last_stand": "A big heal that works best when you are nearly dead",
    "heal_chain": "A heal that jumps between party members", "heal_burst": "A burst of healing around you", "heal": "Heals you",
    "gravity": "Pulls monsters in toward one spot", "food": "Makes food", "find_person": "Tells you where a player is (say the name)",
    "dr_target": "A friend takes less damage for a while", "dr_self": "You take less damage for a while",
    "dr_adjacent": "Shields the friends standing next to you", "decoy": "Leaves a decoy that monsters attack",
    "dash": "Dashes you forward", "cleanse": "Removes poison, burns and other bad effects", "break_free": "Breaks you free of slows and roots",
    "breach": "An arrow that breaks the first vine wall or barrier ahead", "banner": "Plants a banner that strengthens your party around it",
}
RIDERS = [("push", "knocks it back"), ("root", "pins it in place"), ("chain", "jumps to nearby monsters"),
          ("leech", "heals you for part of the damage"), ("dashTo", "leaps you next to it first"),
          ("vuln", "breaks its armour"), ("execute", "hits harder on wounded targets"),
          ("opener", "hits harder on untouched targets"), ("delay", "lands a moment after the cast"),
          ("hits", "fires several shots")]


def field(line, name, pat=r'"([^"]*)"'):
    m = re.search(r"\b" + name + r" = " + pat, line)
    return m.group(1) if m else None


def spell_rows():
    rows = []
    for line in (LIB / "spells.lua").read_text(encoding="utf-8").splitlines():
        if not line.startswith("\t{ name = "):
            continue
        r = {"name": field(line, "name"), "words": field(line, "words"), "kind": field(line, "kind"),
             "mana": int(field(line, "mana", r"(\d+)") or 0), "cd": float(field(line, "cd", r"([\d.]+)") or 0),
             "element": ELEMENT.get(field(line, "element", r"COMBAT_([A-Z]+)DAMAGE") or "", None),
             "lostArt": field(line, "lostArt", r"(\d+)"), "style": field(line, "style", r"(\d+)"), "riders": [t for k, t in RIDERS if re.search(r"\b" + k + r" = ", line)]}
        voc = re.search(r'\bvoc = ("all"|\{[^}]*\})', line).group(1)
        r["voc"] = [1, 2, 3, 4] if voc == '"all"' else [VOC[v] for v in re.findall(r"[AMRV]", voc)]
        lv = re.search(r"\blevel = (\d+|\{[^}]*\})", line).group(1)
        r["levels"] = {VOC[k]: int(n) for k, n in re.findall(r"\[([AMRV])\] = (\d+)", lv)} if lv.startswith("{") else {v: int(lv) for v in r["voc"]}
        rows.append(r)
    return rows


def skill_rows():
    rows = []
    for line in (LIB / "sword_skills.lua").read_text(encoding="utf-8").splitlines():
        if line.startswith("\t{ key = "):
            rows.append({"name": field(line, "name"), "words": field(line, "words"), "family": field(line, "family"),
                         "tag": field(line, "tag"), "area": field(line, "area"), "cd": int(field(line, "cd", r"(\d+)")),
                         "level": int(field(line, "level", r"(\d+)") or 1)})
    return rows


def group_of(r):
    k = r["kind"]
    if k in ("attack_target", "attack_area", "trail_dash") or (k == "zone" and r["element"]):
        return "attack"
    return "healing" if "heal" in k else "support"


def icon_of(r):
    k, e = r["kind"], r["element"] or "physical"
    if k == "attack_target":
        return 22 if (e == "physical" and 4 in r["voc"]) else ICON_TARGET[e]
    if k in ("attack_area", "zone"):
        if e == "physical" and 4 in r["voc"]:
            return 21 if min(r["levels"].values()) >= 60 else 24
        return (ICON_BIG if min(r["levels"].values()) >= 100 else ICON_AREA)[e]
    if k == "conjure":
        return 71 if "barrier" in r["words"] else 70 if "rune" in r["words"] else 105
    return ICON_KIND.get(k, 116)


def lua(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def entry(key, **f):
    parts = []
    for k, v in f.items():
        if isinstance(v, bool):
            v = "true" if v else "false"
        elif isinstance(v, str):
            v = lua(v)
        elif isinstance(v, dict):
            v = "{" + ", ".join(f"[{a}] = {b}" for a, b in v.items()) + "}"
        elif isinstance(v, list):
            v = "{" + ", ".join(str(x) for x in v) + "}"
        parts.append(f"{k} = {v}")
    return f"        [{lua(key)}] = {{{', '.join(parts)}}},"


def spellinfo():
    out = []
    for i, r in enumerate(spell_rows(), 1):
        g = group_of(r)
        vocs = sorted(r["voc"]) + [v + 4 for v in sorted(r["voc"])]
        desc = WHAT.get(r["kind"], "A spell")
        if r["element"] and r["kind"] in ("attack_target", "attack_area", "zone"):
            desc += f" with {r['element']}"
        if r["riders"]:
            desc += "; " + ", ".join(r["riders"])
        desc += "."
        lv = r["levels"]
        if len(set(lv.values())) > 1:
            desc += " Learned at level " + ", ".join(f"{lv[v]} ({VOC_NAME[v]})" for v in sorted(lv)) + "."
        if r["lostArt"]:
            desc += f" Lost Art: learned by finishing the Floor {r['lostArt']} story quests."
        if r["style"]:
            desc += " Style ability: learned when your class's Mastery reaches 10 (say !style)."
        out.append(entry(r["name"], id=300 + i, name=r["name"], words=r["words"],
                         type="Conjure" if r["kind"] == "conjure" else "Instant", level=min(lv.values()), mana=r["mana"],
                         soul=0, maglevel=0, icon="", clientId=icon_of(r), group={GROUP_ID[g]: GROUP_MS[g]},
                         needTarget=r["kind"] == "attack_target", parameter=r["kind"] in ("find_person", "levitate", "heal_target", "hot_target", "dr_target"),
                         range=-1, exhaustion=int(r["cd"] * 1000), premium=False, vocations=vocs, special=bool(r["lostArt"] or r["style"]),
                         source=0, description=desc))
    for i, s in enumerate(skill_rows(), 1):
        out.append(entry(s["name"], id=240 + i, name=s["name"], words=s["words"], type="Sword skill", level=s["level"],
                         mana=0, soul=0, maglevel=0, icon="", clientId=ICON_FAMILY.get(s["family"], 22), group={1: 1000},
                         needTarget=s["area"] in ("target", "targetaround1"), parameter=False, range=-1, exhaustion=s["cd"],
                         premium=False, vocations=list(range(1, 9)), special=False, source=0,
                         description=f"Sword skill for a {s['family']} ({s['tag']}). Opener, then link, then finisher within 4 s: +30% damage."))
    return out


def block(s, start, end_marker):
    a = s.index(start)
    b = s.index(end_marker, a)
    return a, b


def build():
    s = (STOCK / "gamelib" / "spells.lua").read_text(encoding="utf-8")
    # once installed, the "stock" file is our own output: start the swap at our marker so the result is the same
    mark = "-- Spirebound: generated by tools/gen_spellbook.py"
    a, b = block(s, mark if mark in s else "SpellInfo = {", "\nVocationNames = {")
    s = s[:a] + "-- Spirebound: generated by tools/gen_spellbook.py from the server's spell tables (do not edit by hand)\nSpellInfo = {\n    Default = {\n" + \
        "\n".join(spellinfo()) + "\n    }\n}\n" + s[b:]
    a, b = block(s, "VocationNames = {", "}\n")
    s = s[:a] + "VocationNames = {\n" + "\n".join(f"    [{k}] = {lua(v)}," for k, v in NAMES.items()) + "\n" + s[b:]
    o = (STOCK / "game_spelllist" / "spelllist.otui").read_text(encoding="utf-8")
    for old, new in (("Sorcerer", "Arcanist"), ("Druid", "Mystic"), ("Paladin", "Ranger"), ("Knight", "Vanguard")):
        o = o.replace(f"!text: tr('{old}')", f"!text: tr('{new}')")
    if "    !text: tr('Monk')\n    visible: false\n" not in o:
        o = o.replace("    !text: tr('Monk')\n", "    !text: tr('Monk')\n    visible: false\n")
    return {OUT / "gamelib" / "spells.lua": s, OUT / "game_spelllist" / "spelllist.otui": o}


def main():
    files = build()
    if "--check" in sys.argv:
        stale = [p for p, t in files.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            sys.exit("spellbook out of date, run python tools/gen_spellbook.py: " + ", ".join(str(p.relative_to(ROOT)) for p in stale))
        print("spellbook up to date")
        return
    for p, t in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8", newline="\n")
    print(f"wrote {len(spell_rows())} spells and {len(skill_rows())} sword skills into the client spellbook")


if __name__ == "__main__":
    main()
