#!/usr/bin/env python3
"""Builds the public information website into website/public/ (plain HTML + one CSS file, no tracking,
no outside scripts). Pages are generated from DESIGN.md's rules, maps/floors.py and data/*.csv so the
site cannot drift from the game. Account creation, character pages and the Hall of Fame need a live
database and come from MyAAC (roadmap 7.1); this is the static wiki and rules part.

Usage: python3 tools/gen_site.py            (writes website/public/)
       python3 tools/gen_site.py --check    (builds into a temp folder and verifies links; used by tests)
"""
from __future__ import annotations

import csv
import html
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
    ("index.html", "Home"), ("how-to-play.html", "How to play"), ("floors.html", "The tower"),
    ("vocations.html", "Vocations"), ("modes.html", "Difficulty"), ("pvp.html", "PvP rules"),
    ("events.html", "Events"), ("rules.html", "Rules"),
]

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


def table(head: list[str], rows: list[list]) -> str:
    th = "".join(f"<th>{e(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><tr>{th}</tr>{tr}</table></div>'


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
<p>Melee and ranged attacks come mostly from <b>sword skills</b> on a hotbar (Shift+1 to Shift+9). Each weapon family has
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
    ) + ("<p>Every vocation unlocks about 20 spells by level, including utility and support spells. "
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
        "Newbie protection: below level 50 you cannot attack players and they cannot attack you (except in boss rooms), and the border blocks you from Contested and Deadzone zones. New characters also get 2 hours of play-time protection.",
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


def rules() -> str:
    return """
<h2>Be decent</h2>
<ul><li>No harassment, hate speech or targeted abuse. PvP is fine; stalking someone out of the game is not.</li>
<li>No scams. Trades are your own risk; staff can see market and trade logs.</li>
<li>One person, up to two clients at once.</li></ul>
<h2>Bots and helpers</h2>
<ul><li>Our own client is the only allowed client. Its built-in <b>cavebot</b> is allowed: while it runs you earn 45% experience and half the loot, and the cut lasts 10 minutes after you switch it off. Manual play is more than twice as good.</li>
<li>Secrets, rare chests and the Twin Fang trial never trigger while the cavebot is on. Boss rooms do not let a cavebot character in.</li>
<li>Auto-targeting on its own costs nothing.</li>
<li>Third-party bots, modified clients, auto-fishing and hiding the cavebot are not allowed. First offense: 7-day ban and gains removed. Second: permanent.</li>
<li>Suspicious patterns are logged for staff review; no automatic bans.</li></ul>
<h2>Never pay-to-win</h2>
<p>The donation shop sells cosmetics, housing decorations and conveniences only. Nothing in it gives damage, defense,
healing, experience, skill speed, loot or gear stats. No experience boosts, no loot boxes, and shop items can never be gambled.
Shop items can be traded on the market for gold, so players can earn cosmetics by playing.</p>
<h2>Fair play for the Death Game</h2>
<p>Only monsters, bosses, traps and the environment can retire a Death Game character. See <a href="modes.html">Difficulty</a>.</p>
<h2>Reports and what happens to rule breakers</h2>
<p>In game, say <b>!report &lt;name&gt;, &lt;what happened&gt;</b>. A gamemaster reads every report. Say <b>!rules</b> to read these rules in game.
Public chat blocks the worst words in English, Portuguese and Spanish.</p>
<ol><li>A warning from a gamemaster.</li><li>A mute: 1 hour, then 24 hours, then 7 days.</li>
<li>A ban of the character: 1 day, then 7 days.</li><li>A ban of the account: 30 days.</li>
<li>A permanent ban. Cheating with third-party bots, selling accounts or gold for money, or abusing a bug for gain skips straight to step 3 or 5.</li></ol>
"""


PAGES = {
    "index.html": ("Welcome to the tower", home),
    "how-to-play.html": ("How to play", how_to_play),
    "floors.html": ("The tower", floors),
    "vocations.html": ("Vocations", vocations),
    "modes.html": ("Difficulty", modes),
    "pvp.html": ("PvP rules", pvp),
    "events.html": ("Events", events),
    "rules.html": ("Rules", rules),
}


def build(out: Path) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    (out / "style.css").write_text(CSS.strip() + "\n", encoding="utf8")
    for name, (title, fn) in PAGES.items():
        (out / name).write_text(page(name, title, fn()), encoding="utf8")
    return list(PAGES)


def check(out: Path) -> list[str]:
    problems = []
    for name in PAGES:
        text = (out / name).read_text(encoding="utf8")
        for href in re.findall(r'href="([^"#]+)"', text):
            if href.startswith("http"):
                problems.append(f"{name}: external link {href}")
            elif not (out / href).exists():
                problems.append(f"{name}: broken link {href}")
        if "<script" in text.lower():
            problems.append(f"{name}: has a script")
    return problems


def main() -> int:
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as d:
            names = build(Path(d))
            problems = check(Path(d))
        print(f"site: {len(names)} pages, {len(problems)} problems")
        for p in problems:
            print("  " + p)
        return 1 if problems else 0
    out = ROOT / "website" / "public"
    names = build(out)
    print(f"site: wrote {len(names)} pages to {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
