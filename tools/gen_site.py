#!/usr/bin/env python3
"""Builds the public information website into website/public/ (plain HTML + one CSS file, no tracking,
no outside scripts). Pages are generated from DESIGN.md's rules, maps/floors.py and data/*.csv so the
site cannot drift from the game. Account creation, character pages and the Hall of Fame need a live
database. They are built here from a snapshot of the game's records (roadmap 7.1): the Hall of Fame,
the character pages, the Memorial, the Exile Ledger and who is online. Without a snapshot those pages say they
open with the server. Accounts and first characters are made on the sign-up page of tools/login_server.py;
the Join page explains it and links there.

Usage: python3 tools/gen_site.py            (writes website/public/: no player data, safe to commit)
       python3 tools/gen_site.py --snapshot snap.json [--signup-url URL] [--out DIR]
                                            (the live site with player data; default DIR .local/site, never committed)
       python3 tools/gen_site.py --check    (builds into temp folders, with and without the sample snapshot,
                                             and verifies links; used by tests)

Snapshot (JSON, every part optional):
  {"taken": unix time,
   "online": {"characters": 12, "people": 9},
   "floors": [{"floor": 1, "cleared_at": unix, "credit": ["Name", ...], "last_hit": "Name", "duration": seconds}],
   "characters": [{"name", "level", "vocation", "mode": 1 Normal / 2 Hardcore / 3 Death Game, "retired": bool,
                   "online": bool, "titles": [...], "created": unix}],     (sorted by experience, highest first)
   "memorial": [{"name", "level", "vocation", "cause", "time"}],
   "exiles": [{"name", "reason", "when": unix, "until": unix, or 0 for permanent}]}
The fields match the server's own records (lib/spirebound/boards.lua, floors.lua, deathgame.lua).
"""
from __future__ import annotations

import csv
import datetime
import html
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "maps"))
from floors import FLOORS  # noqa: E402

SITE = "Spirebound"
FLOOR1 = dict(name="Hearthgate Plains", town="Hearthgate")

NAV = [
    ("index.html", "Home"), ("join.html", "Join"), ("how-to-play.html", "How to play"), ("floors.html", "The tower"),
    ("vocations.html", "Vocations"), ("modes.html", "Difficulty"), ("pvp.html", "PvP rules"),
    ("events.html", "Events"), ("hall-of-fame.html", "Hall of Fame"), ("characters.html", "Characters"),
    ("rules.html", "Rules"),
]

SNAP: dict | None = None      # the game's records for the live site (set by main); None = no player data
SIGNUP_URL = ""               # the sign-up page of tools/login_server.py, e.g. https://play.example/signup
MODES = {1: "Normal", 2: "Hardcore", 3: "Death Game"}

CSS = """
:root{--bg:#f6f4ef;--fg:#1d2230;--mute:#5a6275;--card:#ffffff;--line:#d9d5c8;--accent:#1f6f8b;--accent2:#b5502a}
@media (prefers-color-scheme:dark){:root{--bg:#12151d;--fg:#e8e6df;--mute:#9aa3b8;--card:#1a1f2b;--line:#2c3446;--accent:#5fb8d6;--accent2:#e8895f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
header{border-bottom:1px solid var(--line);background:var(--card)}
.wrap{max-width:900px;margin:0 auto;padding:0 16px}
header .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px;padding-top:12px;padding-bottom:12px}
.brand{font-weight:700;font-size:1.25rem;color:var(--accent);text-decoration:none;letter-spacing:.04em}
nav{display:flex;flex-wrap:wrap;gap:4px 14px}
nav a{color:var(--mute);text-decoration:none;font-size:.95rem}
nav a:hover,nav a.here{color:var(--fg)}
nav a.here{border-bottom:2px solid var(--accent2)}
main{padding:24px 0 56px}
h1{font-size:2rem;margin:.2em 0 .4em}h2{font-size:1.35rem;margin:1.6em 0 .4em;color:var(--accent)}h3{margin:1.2em 0 .2em}
p,li{max-width:70ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:12px 0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.95rem}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--card)}
.scroll{overflow-x:auto}
.stat{display:flex;flex-wrap:wrap;gap:12px}.stat .card{flex:1 1 180px;margin:0}.stat b{font-size:1.6rem;display:block}
.pill{display:inline-block;padding:0 8px;border-radius:99px;border:1px solid var(--line);font-size:.8rem;color:var(--mute)}
footer{border-top:1px solid var(--line);color:var(--mute);font-size:.85rem;padding:16px 0}
a{color:var(--accent)}
"""


def e(s) -> str:
    return html.escape(str(s))


def page(name: str, title: str, body: str) -> str:
    nav = "".join(
        f'<a href="{href}"{" class=here" if href == name else ""}>{e(label)}</a>' for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} - {SITE}</title><link rel="stylesheet" href="style.css"></head>
<body><header><div class="wrap"><a class="brand" href="index.html">{SITE.upper()}</a><nav>{nav}</nav></div></header>
<main><div class="wrap">
<h1>{e(title)}</h1>
{body}
</div></main>
<footer><div class="wrap">{SITE} is a fan-made, non-commercial Open Tibia project. Never pay-to-win.
Building in public; this site is rebuilt from the game's own data files.</div></footer></body></html>
"""


class Raw:
    """A table cell that is already HTML (a link built here), so it is not escaped again."""
    def __init__(self, html_text: str):
        self.html = html_text


def table(head: list[str], rows: list[list]) -> str:
    th = "<tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>" if head else ""
    tr = "".join("<tr>" + "".join(f"<td>{c.html if isinstance(c, Raw) else e(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table>{th}{tr}</table></div>'


def csv_rows(name: str) -> list[dict]:
    with open(ROOT / "data" / name, encoding="utf8", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- pages

def home() -> str:
    return """
<p>An Open Tibia server shaped like a floating tower. Everyone starts on Floor 1. Each floor ends in a labyrinth
and a boss. The first time anyone beats a floor boss, the next floor opens <b>for the whole server</b>.</p>
<div class="card"><b>What makes it different</b><ul>
<li><b>One shared tower.</b> Floors open for everyone, with a server-wide announcement.</li>
<li><b>PvP with teeth, not bullying.</b> Newbie protection, level-range protection, outnumbered shields, bounties and harsh red-skull penalties.</li>
<li><b>Exploration pays.</b> Hidden secrets across every floor, bought by the Info Broker.</li>
<li><b>Houses do things.</b> Portals, Fortune Halls, trophy halls, training rooms, ponds.</li>
<li><b>Never pay-to-win.</b> The best gear and spells come only from playing.</li>
<li><b>Choose your risk.</b> Normal, Hardcore, or Death Game, where dying retires the character.</li></ul></div>
<p>New here? Start with <a href="how-to-play.html">How to play</a>. Pick your vocation on the
<a href="vocations.html">Vocations</a> page and your risk level on <a href="modes.html">Difficulty</a>.</p>
<p>Seasons: each season the tower resets with remixed bosses and secrets. Titles and cosmetics you earn stay on
your account forever.</p>
"""


def how_to_play() -> str:
    return """
<h2>Getting started</h2>
<ol>
<li>Create an account on this site (opens with the server).</li>
<li>Download the Spirebound client. It is the only allowed client; the cavebot and helpers are built in.</li>
<li>Make a character and pick a vocation and difficulty. You can move <i>down</i> a difficulty later, never up.</li>
<li>You start in Hearthgate. Talk to the people there: every quest says what to do next.</li>
</ol>
<h2>Useful commands</h2>
""" + table(["Say", "What it does"], [
        ["J (key)", "Open the Journal: secrets, fishing log, quests, hunting task, top climbers, Memorial"],
        ["!language en / pt / es", "Switch language (English, Portugu&ecirc;s, Espa&ntilde;ol)".replace("&ecirc;", "ê").replace("&ntilde;", "ñ")],
        ["!path", "Your Season Path: daily and weekly goals for cosmetic rewards"],
        ["!top  /  !memorial", "Leaderboards and the Death Game Memorial"],
        ["!arena join  /  !siege join", "Sign up for Arena events and the weekly Spire Siege"],
        ["!lfg", "Looking-for-guild flag and party finder"],
        ["!buyhouse", "Buy a house at its door"],
    ]) + """
<h2>Sword skills</h2>
<p>Melee and ranged attacks come mostly from <b>sword skills</b> on a hotbar (Ctrl+1 to Ctrl+6, or click). Each weapon family has
its own: Openers, Links and Finishers, chained for combos. Arcanists and Mystics also get big spells that unlock
automatically as you level; no trainer, no gold.</p>
<h2>Fishing, secrets and hunting tasks</h2>
<p>Fish every floor for rare catches and a log to complete. Find hidden secrets and sell what you know to the Info Broker
in Hearthgate. Take daily hunting tasks from Taskmaster Rhen. There is no level cap.</p>
"""


def floors() -> str:
    out = ["<p>Ten floors at launch. Level bands are hunting targets, not doors. Floor 1 is open at the start; every other "
           "floor opens when the server beats the floor boss before it.</p>"]
    sys.path.insert(0, str(ROOT / "maps"))
    from floor1_plan import CAMPS
    f1 = sorted({mon for c in CAMPS for mon, _g, _s in c["mix"]})
    rows = [[1, FLOOR1["name"], FLOOR1["town"], "1-35", ", ".join(f1[:8]), "Axe-Lord of the Stair"]]
    for n, f in sorted(FLOORS.items()):
        hunt = list(f["camp"]) + [f["elite"], f["apex"]]
        rows.append([n, f["name"], f["town"], f"{f['band'][0]}-{f['band'][1]}", ", ".join(hunt), f"{f['floor_boss']} (field boss: {f['field_boss']})"])
    out.append(table(["Floor", "Name", "Town", "Level band", "Hunting grounds", "Bosses"], rows))
    out.append("<h2>Fish by floor</h2>")
    out.append(table(["Floor", "Fish to catch"], [[n, ", ".join(f["fish"])] for n, f in sorted(FLOORS.items())]))
    out.append("<h2>Secrets</h2>")
    with open(ROOT / "tools" / "secrets_src.csv", encoding="utf8", newline="") as fh:
        sec = list(csv.DictReader(fh))
    by_floor: dict[str, int] = {}
    for s in sec:
        by_floor[s["floor"]] = by_floor.get(s["floor"], 0) + 1
    out.append("<p>Secrets are not listed here: finding them is the game. Your in-game Journal shows hints for the ones you have not found.</p>")
    out.append(table(["Floor", "Secrets hidden"], [[k, v] for k, v in sorted(by_floor.items(), key=lambda kv: int(kv[0]))]))
    return "\n".join(out)


def vocations() -> str:
    return "<p>Four familiar vocations. Promotion at level 20 gives the familiar regeneration bump.</p>" + table(
        ["Vocation", "Like Tibia's", "Weapons", "Role"],
        [
            ["Vanguard", "Knight", "Sword, Axe, Club (+ shield)", "Tank, front line"],
            ["Ranger", "Paladin", "Bow, Crossbow, Spear (throwing)", "Ranged damage, some healing"],
            ["Arcanist", "Sorcerer", "Wand", "Area damage, big flashy spells"],
            ["Mystic", "Druid", "Rod", "Healer, support, nature damage"],
        ],
    ) + ("<p>Every vocation unlocks 23 to 25 spells by level, each at its own pace, including utility and support spells. "
         "The rare <b>Twin Fang</b> trial (Vanguards only, three per season) unlocks a second-blade fighting style.</p>")


def modes() -> str:
    return "<p>Chosen at creation. You can move <b>down</b> a difficulty at the Registrar, never up.</p>" + table(
        ["", "Normal", "Hardcore", "Death Game"],
        [
            ["Death", "Standard Tibia penalty", "Heavier penalty (1.5x skill and experience loss, double item drop chance)", "Character is retired to the Memorial"],
            ["Experience bonus", "none", "+25%", "+50%"],
            ["Loot bonus", "none", "+15%", "+30%"],
            ["Exclusive", "-", "Hardcore title", "Deathbound title, exclusive outfit, own leaderboard"],
        ],
    ) + ("<p><b>Player killers can never delete a Death Game character.</b> If another player damaged you in the 60 seconds "
         "before you died and did real damage (at least 15% of your health), or another player dragged the monster "
         "that killed you onto you, it counts as a PvP death: you are not deleted and take the Hardcore penalty instead. "
         "Party members, guildmates and same-IP characters do not count, so nobody can tag themselves immortal.</p>"
         "<p><b>Unfair deaths.</b> A Death Game character killed by a server crash or by lag on the server is restored by "
         "a gamemaster. Your own internet dropping is not unfair: the tower is cruel. Ask a gamemaster within a day.</p>"
         "<p><b>Stepping down</b> to Hardcore or Normal is allowed in town at any time, but it costs the extra experience "
         "the harder path gave you.</p>")


def pvp() -> str:
    return """
<p>PvP is real, but the game protects newer and weaker players. Toxicity is the thing we are built against.</p>
<h2>Where you can fight</h2>
""" + table(["Zone", "Rule"], [
        ["Safe (towns)", "No attacks of any kind: streets, temple, depot, bank, shops, houses."],
        ["Guarded", "Roads and starter fields. An unjust kill counts as three, and town guards hunt the killer for 30 minutes."],
        ["Open", "Most hunting grounds. Normal skull rules."],
        ["Contested", "Each floor's apex spawn. Kills give no skull; killers earn Blood Marks. Victims drop more."],
        ["Deadzone", "The deepest areas. Contested rules, bigger losses, the best experience and loot."],
    ]) + "<h2>Protections</h2><ol>" + "".join(f"<li>{e(x)}</li>" for x in [
        "Newbie protection: below level 50 you cannot attack players and they cannot attack you (except in boss rooms), even on Contested and Deadzone ground, where only players of 50 and above fight. New characters also get 2 hours of play-time protection.",
        "Level-range protection: you cannot start a fight with a player below 70% of your level, outside Contested, Deadzone and boss rooms. They can still defend themselves.",
        "Outnumbered shield: if 3 or more different players hit you within 10 seconds, you take 10% less player damage per attacker beyond 2 (up to 40% less).",
        "Guild-farming shield: if the same guild kills you twice within 6 hours outside a war, you get a 30-minute Sanctuary against that guild.",
        "Bounties on red players, paid only to killers who are not in the same guild, party or network as the target.",
        "Wars are by consent: both guild leaders must sign, and war kills never cause skulls.",
        "A kill on a player 30+ levels below you counts double toward skulls.",
    ]) + "</ol><h2>Skulls</h2>" + table(["Skull", "You get it for", "Lasts", "Penalty"], [
        ["Orange", "1-2 unjust kills in 24 hours", "30 minutes per kill, max 2 hours", "Killing you is justified"],
        ["Red", "3 unjust kills in 24 h, 5 in 7 days, or 10 in 30 days", "7 days after the last unjust kill", "Lose your whole backpack and equipment on death; double death penalty; towns closed to you; no boss rooms; automatic bounty"],
        ["Black", "6 unjust kills in 24 h, or 10 in 7 days", "14 days after the last unjust kill", "Red penalties, plus no teleport gates or party-share experience"],
    ])


def events() -> str:
    return """
<p>Times are server time.</p>""" + table(["Event", "When", "What"], [
        ["Arena", "Daily, sign-ups at 19:00 and 22:00", "Last Man Standing, Team Rush and Capture the Banner on a walled arena. Same health and fixed hits for everyone, so level and gear do not matter. Nobody dies or loses anything. Level 20+, 4-20 fighters. Say <b>!arena join</b>.".replace("<b>", "").replace("</b>", "")],
        ["Spire Siege", "Every Sunday, sign-ups 19:45, starts 20:00", "Guilds fight over a throne room for 30 minutes. The winner holds the keep for a week: +5% experience and loot and a leader title. Level-scaled like the Arena. Say !siege join."],
        ["Weekend bonuses", "Fridays to Sundays", "Rotating bonuses for fishing, secrets and experience."],
        ["New floor", "When a floor boss falls", "The whole server is told and the next floor opens for everyone."],
        ["Seasons", "Every few months", "The tower resets and bosses and secrets are remixed. Titles and cosmetics are kept."],
    ])


# ---------------------------------------------------------------- accounts and the game's records (roadmap 7.1)

def slug(name: str) -> str:
    return "char-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + ".html"


def when(ts) -> str:
    if not ts:
        return "-"
    return datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).strftime("%Y-%m-%d")


def span(seconds) -> str:
    s = int(seconds or 0)
    return f"{s // 60} min {s % 60:02d} s" if s else "-"


def char_link(name: str) -> Raw:
    known = {c["name"] for c in (SNAP or {}).get("characters", [])}
    return Raw(f'<a href="{slug(name)}">{e(name)}</a>' if name in known else e(name))


def not_yet(what: str, records: bool = True) -> str:
    tail = " This page is rebuilt from the game's own records while the server runs." if records else ""
    return f'<div class="card"><b>Opens with the server.</b> {e(what)}{e(tail)}</div>'


def taken() -> str:
    ts = (SNAP or {}).get("taken")
    return f'<p class="pill">Updated {e(when(ts))}</p>' if ts else ""


def join() -> str:
    if SIGNUP_URL:
        go = (f'<p><a class="pill" href="{e(SIGNUP_URL)}">Create your account</a></p>'
              "<p>The sign-up page asks for an e-mail address, a password (8 characters or more) and your first "
              "character's name.</p>")
    else:
        go = not_yet("Account sign-up opens here when the server opens. During the friends test, Jay sends you the address.", records=False)
    return go + """
<h2>How joining works</h2>
<ol>
<li><b>Read the <a href="rules.html">rules</a>.</b> The sign-up page asks you to agree to them.</li>
<li><b>Make an account.</b> Your password is never stored as plain text. Extra accounts are fine (up to 3 game clients on one computer at once).</li>
<li><b>Name your first character</b> on the same page: 3 to 20 letters, each word starting with a capital
(for example Mira or Tom Reed). Pick a name of your own: names from other games, real people's names and rude
names break the <a href="rules.html">rules</a>, and a gamemaster will ask you to change them.</li>
<li><b>Download the Spirebound client</b> and log in with your e-mail and password.</li>
<li><b>Pick your vocation in the game, not here.</b> Every character wakes in the Arrival Yard with no vocation.
A short guided path (under ten minutes) ends at the Registrar in Hearthgate, where you choose your vocation and
your difficulty. You will know how fighting feels before you choose.</li>
</ol>
<h2>More characters</h2>
<p>Each account can hold several characters. Making another one from this site comes with the full account pages;
until then, ask a gamemaster in game.</p>
<h2>Keeping your account safe</h2>
<ul><li>Use a password you use nowhere else.</li>
<li>Staff will never ask for your password, in game or anywhere else.</li>
<li>Too many wrong passwords from one address make that address wait a few minutes.</li></ul>
"""


def hall_of_fame() -> str:
    more = ('<p>See also the <a href="memorial.html">Memorial</a>, the <a href="exile-ledger.html">Exile Ledger</a> and '
            '<a href="online.html">who is online</a>.</p>')
    if SNAP is None:
        return not_yet("The first clear of every floor, the top climbers and the Death Game leaderboard will be listed here.") + more
    out = [taken(), "<h2>First clears</h2>",
           "<p>The first group to beat each floor boss opened the next floor for the whole server.</p>"]
    fl = [f for f in sorted(SNAP.get("floors", []), key=lambda f: f.get("floor", 0)) if f.get("cleared_at")]
    if fl:
        out.append(table(["Floor", "Cleared", "By", "Final blow", "Fight time"], [
            [f["floor"], when(f.get("cleared_at")),
             Raw(", ".join(char_link(n).html for n in f.get("credit", [])) or "-"),
             char_link(f["last_hit"]) if f.get("last_hit") else "-", span(f.get("duration"))] for f in fl]))
    else:
        out.append("<p>No floor has been cleared yet. Floor 1's boss is waiting.</p>")
    chars = SNAP.get("characters", [])
    for title, mode in (("Top climbers", None), ("Hardcore", 2), ("Death Game", 3)):
        rows = [c for c in chars if mode is None or c.get("mode") == mode][:20]
        out.append(f"<h2>{e(title)}</h2>")
        if not rows:
            out.append("<p>Nobody yet.</p>")
            continue
        out.append(table(["#", "Character", "Level", "Vocation", "Difficulty", ""], [
            [i + 1, char_link(c["name"]), c.get("level", 0), c.get("vocation", "None"), MODES.get(c.get("mode", 1), "Normal"),
             "fallen" if c.get("retired") else ""] for i, c in enumerate(rows)]))
    return "\n".join(out) + more


def characters() -> str:
    if SNAP is None:
        return not_yet("Every character gets a page: level, vocation, difficulty and titles.")
    chars = sorted(SNAP.get("characters", []), key=lambda c: c["name"].lower())
    if not chars:
        return taken() + "<p>No characters yet.</p>"
    return taken() + f'<p>{len(chars)} characters, A to Z. Ranked lists are in the <a href="hall-of-fame.html">Hall of Fame</a>.</p>' + \
        table(["Character", "Level", "Vocation", "Difficulty", ""], [
            [char_link(c["name"]), c.get("level", 0), c.get("vocation", "None"), MODES.get(c.get("mode", 1), "Normal"),
             "online" if c.get("online") else ("fallen" if c.get("retired") else "")] for c in chars])


def character(c: dict) -> str:
    rank = next((i + 1 for i, x in enumerate(SNAP.get("characters", [])) if x["name"] == c["name"]), None)
    rows = [["Level", c.get("level", 0)], ["Vocation", c.get("vocation", "None")],
            ["Difficulty", MODES.get(c.get("mode", 1), "Normal")], ["Rank", f"#{rank} in the tower" if rank else "-"],
            ["Status", "Online now" if c.get("online") else ("Fallen (Death Game)" if c.get("retired") else "Offline")]]
    if c.get("created"):
        rows.append(["Climbing since", when(c["created"])])
    clears = sorted(f["floor"] for f in SNAP.get("floors", []) if c["name"] in f.get("credit", []))
    if clears:
        rows.append(["First clears", ", ".join(f"Floor {n}" for n in clears)])
    out = [taken(), table([], rows)]
    if c.get("titles"):
        out.append("<h2>Titles</h2><p>" + " ".join(f'<span class="pill">{e(x)}</span>' for x in c["titles"]) + "</p>")
    fell = next((m for m in SNAP.get("memorial", []) if m["name"] == c["name"]), None)
    if fell:
        out.append(f"<h2>On the Memorial</h2><p>Fell at level {e(fell.get('level', 0))} to {e(fell.get('cause', 'unknown'))} "
                   f"on {e(when(fell.get('time')))}.</p>")
    out.append('<p><a href="characters.html">All characters</a></p>')
    return "\n".join(out)


def memorial() -> str:
    intro = ("<p>Every Death Game climber who fell this season. Only monsters, bosses, traps and the tower itself can "
             "put a name here.</p>")
    if SNAP is None:
        return intro + not_yet("Fallen Death Game characters will be listed here.")
    m = sorted(SNAP.get("memorial", []), key=lambda r: (-int(r.get("level", 0)), r.get("time", 0)))
    if not m:
        return intro + taken() + "<p>Nobody has fallen yet.</p>"
    return intro + taken() + table(["#", "Character", "Level", "Vocation", "Fell to", "Date"], [
        [i + 1, char_link(r["name"]), r.get("level", 0), r.get("vocation", "?"), r.get("cause", "unknown"), when(r.get("time"))]
        for i, r in enumerate(m)])


def exile_ledger() -> str:
    intro = ("<p>Every ban for cheating (third-party bots, modified clients, selling gold or accounts for money) is "
             "public, with its reason. A ban covers the person's other accounts too. Mutes and short chat bans are not "
             'listed. The <a href="rules.html">Rules</a> say what leads where.</p>')
    if SNAP is None:
        return intro + not_yet("Bans will be listed here.")
    x = sorted(SNAP.get("exiles", []), key=lambda r: -int(r.get("when", 0)))
    if not x:
        return intro + taken() + "<p>Nobody has been banned. Long may it last.</p>"
    return intro + taken() + table(["Character", "Reason", "Since", "Until"], [
        [r["name"], r.get("reason", ""), when(r.get("when")), when(r["until"]) if r.get("until") else "permanent"] for r in x])


def online() -> str:
    intro = ("<p>Characters online and real people online, side by side, so nobody wonders whether the count is padded. "
             "One person may run up to two clients.</p>")
    if SNAP is None:
        return intro + not_yet("The live count will be shown here.")
    o = SNAP.get("online", {})
    names = sorted((c for c in SNAP.get("characters", []) if c.get("online")), key=lambda c: -int(c.get("level", 0)))
    out = [intro, taken(), f'<div class="stat"><div class="card"><b>{e(o.get("characters", len(names)))}</b>characters online</div>'
           f'<div class="card"><b>{e(o.get("people", "-"))}</b>real people online</div></div>']
    if names:
        out.append(table(["Character", "Level", "Vocation"], [[char_link(c["name"]), c.get("level", 0), c.get("vocation", "None")] for c in names]))
    return "\n".join(out)


# A made-up snapshot so --check exercises every data page (no real players in it).
SAMPLE = {
    "taken": 1795000000, "online": {"characters": 3, "people": 2},
    "floors": [{"floor": 1, "cleared_at": 1794900000, "credit": ["Mira Vale", "Tom Reed", "Odessa Thorne"], "last_hit": "Tom Reed", "duration": 1260}],
    "characters": [
        {"name": "Tom Reed", "level": 61, "vocation": "Blade Warden", "mode": 1, "online": True, "titles": ["Floor 1 First Clear"], "created": 1794000000},
        {"name": "Mira Vale", "level": 58, "vocation": "Elder Mystic", "mode": 2, "online": True},
        {"name": "Odessa Thorne", "level": 55, "vocation": "Far Warden", "mode": 3},
        {"name": "Pip Hollow", "level": 22, "vocation": "Arcanist", "mode": 3, "retired": True},
        {"name": "Wren", "level": 3, "vocation": "None", "mode": 1, "online": True},
    ],
    "memorial": [{"name": "Pip Hollow", "level": 22, "vocation": "Arcanist", "cause": "a Grey Alpha", "time": 1794950000}],
    "exiles": [{"name": "Quick Coin", "reason": "Selling gold for real money", "when": 1794960000, "until": 0}],
}


def rules() -> str:
    """The full rulebook, from tools/player_rules.py (the same text the sign-up page shows)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import player_rules
    return player_rules.to_html({"pvp": "pvp.html", "modes": "modes.html", "ledger": "exile-ledger.html"})


PAGES = {
    "index.html": ("Welcome to the tower", home),
    "how-to-play.html": ("How to play", how_to_play),
    "floors.html": ("The tower", floors),
    "vocations.html": ("Vocations", vocations),
    "modes.html": ("Difficulty", modes),
    "pvp.html": ("PvP rules", pvp),
    "events.html": ("Events", events),
    "rules.html": ("Rules", rules),
    "join.html": ("Join the tower", join),
    "hall-of-fame.html": ("Hall of Fame", hall_of_fame),
    "characters.html": ("Characters", characters),
    "memorial.html": ("Memorial", memorial),
    "exile-ledger.html": ("Exile Ledger", exile_ledger),
    "online.html": ("Who is online", online),
}


def build(out: Path) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    (out / "style.css").write_text(CSS.strip() + "\n", encoding="utf8")
    for old in out.glob("char-*.html"):          # characters can be renamed or deleted between snapshots
        old.unlink()
    names = []
    for name, (title, fn) in PAGES.items():
        (out / name).write_text(page(name, title, fn()), encoding="utf8")
        names.append(name)
    for c in (SNAP or {}).get("characters", []):
        name = slug(c["name"])
        (out / name).write_text(page(name, c["name"], character(c)), encoding="utf8")
        names.append(name)
    return names


def check(out: Path, names: list[str]) -> list[str]:
    problems = []
    for name in names:
        text = (out / name).read_text(encoding="utf8")
        for href in re.findall(r'href="([^"#]+)"', text):
            if SIGNUP_URL and html.unescape(href) == SIGNUP_URL:
                continue
            if href.startswith("http"):
                problems.append(f"{name}: external link {href}")
            elif not (out / href).exists():
                problems.append(f"{name}: broken link {href}")
        if "<script" in text.lower():
            problems.append(f"{name}: has a script")
    return problems


def arg(flag: str) -> str | None:
    i = sys.argv.index(flag) if flag in sys.argv else -1
    return sys.argv[i + 1] if 0 <= i < len(sys.argv) - 1 else None


def main() -> int:
    global SNAP, SIGNUP_URL
    if "--check" in sys.argv:
        problems, count = [], 0
        for snap, url in ((None, ""), (SAMPLE, "https://play.example/signup")):
            SNAP, SIGNUP_URL = snap, url
            with tempfile.TemporaryDirectory() as d:
                names = build(Path(d))
                problems += [f"{'sample' if snap else 'plain'}: {p}" for p in check(Path(d), names)]
                count += len(names)
        SNAP, SIGNUP_URL = None, ""
        print(f"site: {count} pages (plain + sample snapshot), {len(problems)} problems")
        for p in problems:
            print("  " + p)
        return 1 if problems else 0
    SIGNUP_URL = arg("--signup-url") or ""
    snap = arg("--snapshot")
    public = ROOT / "website" / "public"
    if snap:
        SNAP = json.loads(Path(snap).read_text(encoding="utf8"))
        out = Path(arg("--out") or ROOT / ".local" / "site")
        if out.resolve() == public.resolve():
            sys.exit("A site with player data must not go into website/public (that folder is committed). Use --out.")
    else:
        out = public
    names = build(out)
    print(f"site: wrote {len(names)} pages to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
