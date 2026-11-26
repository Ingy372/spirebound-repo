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
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "maps"))
from floors import FLOORS  # noqa: E402

SITE = "Spirebound"
FLOOR1 = dict(name="Hearthgate Plains", town="Hearthgate")

# The side menu: (group, [(page, label), ...]). Pages not built here (sign-up) are added when SIGNUP_URL is set.
MENU = [
    ("Play", [("index.html", "Home"), ("join.html", "Join the tower"), ("how-to-play.html", "How to play")]),
    ("The game", [("floors.html", "The tower"), ("vocations.html", "Vocations"), ("modes.html", "Difficulty"),
                  ("pvp.html", "PvP rules"), ("events.html", "Events")]),
    ("Community", [("hall-of-fame.html", "Hall of Fame"), ("characters.html", "Characters"), ("online.html", "Who is online"),
                   ("memorial.html", "Memorial"), ("exile-ledger.html", "Exile Ledger")]),
    ("Support", [("rules.html", "Rules")]),
]
NAV = [item for _g, items in MENU for item in items]

SNAP: dict | None = None      # the game's records for the live site (set by main); None = no player data
LAST_SNAP: dict | None = None # the latest live snapshot (tools/site_snapshot.py), for pages drawn on request
RENDER_LOCK = threading.RLock()  # the login service draws pages while its website refresh runs: one at a time
SIGNUP_URL = ""               # the sign-up page of tools/login_server.py, e.g. https://play.example/signup
MODES = {1: "Normal", 2: "Hardcore", 3: "Death Game"}
# The banner is reserved for the "money monsters" (Jay, 2026-11-25: "monsters that vets will look forward to running
# into once in the game. Bosses, the fire boar, and a few others that haven't been made yet"). Art names; each one
# walks across the banner as soon as its approved art is in website/public/img (tools/site_art.py). Not made yet:
# the floor bosses, the fire boar (an idea under Later in ROADMAP.md) and the other money monsters in ART_REQUESTS.md.
SHOWCASE = ["azhrakkar", "alpha", "gate_hound", "axe_lord", "underkeeper", "fire_boar", "old_tusk", "moonhowl",
            "hollowfang", "briar_mother", "twin_fang_warden", "vault_wraith"]
IMG = ROOT / "website" / "public" / "img"


def parade() -> list[str]:
    return [n for n in SHOWCASE if (IMG / f"walk_{n}.png").exists()]

CSS = """
:root{--night:#07060a;--stone:#15120f;--panel:#1d1813;--panel2:#241e17;--edge:#5c4625;--gold:#e9c36a;--gold2:#ffdf8f;
--ember:#ff8a3d;--spire:#63d8ef;--fg:#e9e2d0;--mute:#a99f88;--row:#201a14;--row2:#2a2219;--danger:#e0533d}
*{box-sizing:border-box}
html{background:var(--night)}
body{margin:0;color:var(--fg);font:15px/1.6 "Segoe UI",Tahoma,Verdana,sans-serif;
background:radial-gradient(ellipse at 50% -10%,#2a2140 0,#120e1b 45%,var(--night) 75%) fixed,var(--night)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.5;
background-image:radial-gradient(1px 1px at 12% 18%,#fff8 50%,#0000 51%),radial-gradient(1px 1px at 72% 9%,#fff7 50%,#0000 51%),
radial-gradient(1.5px 1.5px at 38% 30%,#fffa 50%,#0000 51%),radial-gradient(1px 1px at 88% 34%,#fff6 50%,#0000 51%),
radial-gradient(1px 1px at 55% 14%,#fff6 50%,#0000 51%),radial-gradient(1.5px 1.5px at 22% 40%,#fff5 50%,#0000 51%)}
a{color:var(--gold);text-decoration:none}a:hover{color:var(--gold2);text-decoration:underline}
h1,h2,h3,.logo,.box-title,.btn,.menu-group{font-family:"Trajan Pro","Cinzel","Palatino Linotype","Book Antiqua",Palatino,Georgia,serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
/* banner */
.banner{position:relative;height:290px;overflow:hidden;border-bottom:3px solid var(--edge);
background:linear-gradient(180deg,#0000 55%,#0b0907 100%),radial-gradient(ellipse at 50% 120%,#3a2a12 0,#0000 60%)}
.banner .tower{position:absolute;right:9%;bottom:10px;height:270px;opacity:.95;filter:drop-shadow(0 0 18px #63d8ef55)}
.banner .tower.far{right:auto;left:7%;height:170px;opacity:.45;filter:drop-shadow(0 0 10px #63d8ef33) blur(.5px)}
.banner .inner{position:relative;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding-bottom:90px}
.logo{display:inline-block;font-size:clamp(2.2rem,7vw,4.4rem);font-weight:700;letter-spacing:.12em;line-height:1;color:var(--gold2);
background:linear-gradient(180deg,#fff3c4 0,#f2c75e 45%,#b9822a 55%,#f7d77f 100%);-webkit-background-clip:text;background-clip:text;
-webkit-text-fill-color:transparent;filter:drop-shadow(0 3px 0 #3b2709) drop-shadow(0 0 14px #ffb54a66)}
.logo:hover{text-decoration:none}
.tagline{margin-top:10px;color:#f4e6c2;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 2px 4px #000}
.parade{position:absolute;left:0;right:0;bottom:10px;height:64px;pointer-events:none;overflow:hidden}
.parade img{position:absolute;bottom:0;left:-70px;width:64px;height:64px;animation:walk linear infinite;filter:drop-shadow(0 3px 2px #000c)}
@keyframes walk{from{left:-70px}to{left:100%}}
.ground{position:absolute;left:0;right:0;bottom:0;height:12px;background:linear-gradient(180deg,#3d2e18,#1a130b)}
/* top bar */
.topbar{background:linear-gradient(180deg,#2b2117,#1a140e);border-bottom:1px solid #000;box-shadow:0 2px 0 #3d2f1a inset}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:8px;padding-bottom:8px;flex-wrap:wrap}
.topbar .links{display:flex;flex-wrap:wrap;gap:4px 18px;font-size:.92rem}
.topbar .links a{color:var(--fg)}.topbar .links a:hover,.topbar .links a.here{color:var(--gold2)}
/* buttons */
.btn{display:inline-block;padding:10px 26px;border-radius:6px;font-weight:700;letter-spacing:.08em;color:#2a1604!important;
background:linear-gradient(180deg,#ffe29a,#f0ad3c 50%,#c9741d);border:1px solid #6b3a0a;box-shadow:0 0 0 2px #00000080,0 0 18px #ff9a3c55,inset 0 1px 0 #fff6;
text-shadow:0 1px 0 #ffe9b0;text-decoration:none!important}
.btn:hover{filter:brightness(1.1)}
.btn.small{padding:6px 16px;font-size:.85rem}
/* three columns */
.layout{display:grid;grid-template-columns:210px minmax(0,1fr) 240px;gap:18px;padding-top:20px;padding-bottom:40px}
.box{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--edge);border-radius:6px;
box-shadow:0 0 0 1px #000,0 8px 24px #0009,inset 0 1px 0 #ffffff10;margin-bottom:18px;overflow:hidden}
.box-title{position:relative;padding:9px 14px;font-size:1.02rem;font-weight:700;letter-spacing:.08em;color:var(--gold2);
background:linear-gradient(180deg,#4a3519,#2b1f10);border-bottom:1px solid #000;text-shadow:0 2px 2px #000}
.box-title:after{content:"";position:absolute;left:10px;right:10px;bottom:-1px;height:1px;background:linear-gradient(90deg,#0000,var(--gold),#0000)}
.box-body{padding:14px 18px}
.box-body>:first-child{margin-top:0}
main .box-title{font-size:1.25rem;padding:12px 18px}
.menu-group{color:var(--gold);font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;padding:10px 14px 4px;border-top:1px solid #0006}
.menu-group:first-child{border-top:0}
.menu a{display:block;padding:5px 14px 5px 26px;color:var(--fg);position:relative;font-size:.95rem}
.menu a:before{content:"";position:absolute;left:12px;top:50%;width:6px;height:6px;margin-top:-3px;transform:rotate(45deg);background:#6d5530}
.menu a:hover,.menu a.here{background:#ffffff0d;color:var(--gold2);text-decoration:none}
.menu a.here:before,.menu a:hover:before{background:var(--ember);box-shadow:0 0 6px var(--ember)}
.status-line{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #ffffff14}
.status-line b{color:var(--gold2)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;background:#777}
.dot.on{background:#53e07a;box-shadow:0 0 8px #53e07a}.dot.soon{background:var(--ember);box-shadow:0 0 8px var(--ember)}
.mini{list-style:none;margin:0;padding:0;counter-reset:n}
.mini li{counter-increment:n;display:flex;gap:8px;padding:3px 0;border-bottom:1px dashed #ffffff12}
.mini li:before{content:counter(n);color:var(--ember);font-weight:700;min-width:1.2em}
.mini span{margin-left:auto;color:var(--mute)}
.floorbar{height:12px;border-radius:6px;background:#0008;border:1px solid #000;overflow:hidden;margin:6px 0}
.floorbar i{display:block;height:100%;background:linear-gradient(90deg,var(--spire),#b18cff);box-shadow:0 0 10px var(--spire)}
/* content */
h2{color:var(--gold2);font-size:1.3rem;margin:1.5em 0 .5em;padding-bottom:4px;border-bottom:1px solid #5c462566}
h3{color:var(--gold);margin:1.2em 0 .3em}
p,li{max-width:75ch}
ul li::marker{color:var(--ember)}
b{color:#fff4d6}
.card{background:#0000004d;border:1px solid #5c462588;border-left:3px solid var(--ember);border-radius:4px;padding:10px 14px;margin:12px 0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.93rem;border:1px solid #000}
th,td{padding:6px 10px;text-align:left;vertical-align:top;border-bottom:1px solid #0007}
th{background:linear-gradient(180deg,#4a3519,#30230f);color:var(--gold2);font-family:Georgia,serif;letter-spacing:.03em}
tr:nth-child(odd) td{background:var(--row)}tr:nth-child(even) td{background:var(--row2)}
tr:hover td{background:#3a2e1d}
.scroll{overflow-x:auto}
.stat{display:flex;flex-wrap:wrap;gap:12px}.stat .card{flex:1 1 180px;margin:0;text-align:center}
.stat b{font-size:2rem;display:block;color:var(--gold2);font-family:Georgia,serif}
.pill{display:inline-block;padding:1px 10px;border-radius:99px;border:1px solid var(--edge);background:#0006;font-size:.8rem;color:var(--gold)}
.hero .lead{font-size:1.12rem;margin-top:0}
.stage{display:flex;justify-content:center;flex-wrap:wrap;gap:0 10px;margin:4px 0 0;padding:0 0 6px;
background:radial-gradient(ellipse at 50% 92%,#ff8a3d33 0,#0000 60%);border-bottom:1px solid #5c462566}
.stage figure{margin:0 10px;text-align:center}.stage img{width:64px;height:64px;display:block;margin:6px auto 0}
.stage figcaption{font-family:Georgia,serif;color:var(--gold2);font-size:.95rem}
.features{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:14px 0}
.feature{display:flex;gap:10px;align-items:flex-start;background:#0000004d;border:1px solid #5c462566;border-radius:6px;padding:10px}
.feature img{width:64px;height:64px;flex:none;margin:-6px 0 -6px -6px}
.feature b{display:block;color:var(--gold2);font-family:Georgia,serif;font-size:1.02rem}
.voc{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:14px 0}
.voc div{text-align:center;background:#0000004d;border:1px solid #5c462566;border-radius:6px;padding:8px 10px 12px}
.voc img{width:64px;height:64px;margin:4px 0 0}
.voc b{display:block;color:var(--gold2);font-family:Georgia,serif;font-size:1.15rem}
/* forms (sign-up pages) */
.form label{display:block;margin:0 0 12px;color:var(--mute);font-size:.92rem}
.form input[type=text],.form input[type=email],.form input[type=password],.form input:not([type]){display:block;width:100%;margin-top:4px;padding:9px 10px;
border-radius:4px;border:1px solid var(--edge);background:#0c0a08;color:var(--fg);font-size:1rem}
.form input:focus{outline:2px solid var(--ember);outline-offset:0}
.form .choice{display:inline-flex;align-items:center;gap:6px;margin-right:16px;color:var(--fg)}
.msg{padding:10px 14px;background:#00000066;border:1px solid var(--edge);border-left:4px solid var(--ember);border-radius:4px}
footer{border-top:3px solid var(--edge);background:#0b0907;color:var(--mute);font-size:.85rem;padding:18px 0;text-align:center}
@media (max-width:980px){.layout{grid-template-columns:1fr}.layout main{order:1}.layout .side{order:2;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0 18px}
.layout .side-left{order:3}.banner{height:240px}.banner .tower{right:50%;transform:translateX(50%);height:220px;opacity:.35}.banner .tower.far{display:none}
.banner .inner{padding-bottom:70px}}
@media (max-width:560px){.topbar .btn{display:none}}
"""

# Our own tower, drawn here (no borrowed art): stacked tiers narrowing upwards, glowing windows, a crystal at the top.
TOWER_SVG = """<svg class="tower" viewBox="0 0 220 260" aria-hidden="true"><defs>
<linearGradient id="st" x1="0" x2="1"><stop offset="0" stop-color="#2b2433"/><stop offset=".5" stop-color="#4a3f57"/><stop offset="1" stop-color="#1c1724"/></linearGradient>
<radialGradient id="gl"><stop offset="0" stop-color="#bff6ff"/><stop offset=".4" stop-color="#63d8ef"/><stop offset="1" stop-color="#63d8ef" stop-opacity="0"/></radialGradient></defs>
<circle cx="110" cy="26" r="34" fill="url(#gl)" opacity=".8"/>
<path d="M104 8 L110 0 L116 8 L113 30 L107 30 Z" fill="#9ff0ff"/>
<path d="M60 260 L66 200 L154 200 L160 260 Z M70 200 L76 150 L144 150 L150 200 Z M80 150 L85 105 L135 105 L140 150 Z M89 105 L93 66 L127 66 L131 105 Z M96 66 L99 34 L121 34 L124 66 Z" fill="url(#st)" stroke="#0a0810" stroke-width="2"/>
<path d="M62 200 H158 M72 150 H148 M82 105 H138 M91 66 H129" stroke="#8a7650" stroke-width="3"/>
<g fill="#ffb54a"><rect x="86" y="220" width="8" height="14" rx="4"/><rect x="126" y="220" width="8" height="14" rx="4"/><rect x="106" y="230" width="8" height="30" rx="4" fill="#2a1b08" stroke="#ffb54a"/>
<rect x="92" y="170" width="7" height="12" rx="3.5"/><rect x="121" y="170" width="7" height="12" rx="3.5"/><rect x="106" y="120" width="8" height="13" rx="4"/>
<rect x="107" y="80" width="6" height="10" rx="3" fill="#9ff0ff"/><rect x="107" y="42" width="6" height="10" rx="3" fill="#9ff0ff"/></g></svg>"""


def e(s) -> str:
    return html.escape(str(s))


def side_status() -> str:
    """The right-hand boxes: server status, how far the tower is open, the top climbers, a join button."""
    snap = SNAP
    if snap is None:
        status = ('<div class="status-line"><span><i class="dot soon"></i>Server</span><b>Opening soon</b></div>'
                  '<div class="status-line"><span>Floors</span><b>10</b></div>'
                  '<div class="status-line"><span>Start</span><b>Floor 1</b></div>')
        opened = 1
        top = '<p style="margin:0;color:var(--mute)">The race to the top starts on opening day.</p>'
    else:
        o = snap.get("online", {})
        status = (f'<div class="status-line"><span><i class="dot on"></i>Online</span><b>{e(o.get("characters", 0))}</b></div>'
                  f'<div class="status-line"><span>Real people</span><b>{e(o.get("people", 0))}</b></div>'
                  f'<div class="status-line"><span>Climbers</span><b>{len(snap.get("characters", []))}</b></div>')
        opened = 1 + len([f for f in snap.get("floors", []) if f.get("cleared_at")])
        chars = snap.get("characters", [])[:5]
        top = ('<ol class="mini">' + "".join(f'<li>{char_link(c["name"]).html}<span>{e(c.get("level", 0))}</span></li>' for c in chars)
               + "</ol>" + '<p style="margin:8px 0 0"><a href="hall-of-fame.html">Hall of Fame &raquo;</a></p>') if chars else \
            '<p style="margin:0;color:var(--mute)">Nobody yet. Be the first.</p>'
    opened = min(opened, 10)
    return (f'<div class="box"><div class="box-title">Server</div><div class="box-body">{status}</div></div>'
            f'<div class="box"><div class="box-title">The tower</div><div class="box-body"><div class="status-line"><span>Floors open</span>'
            f'<b>{opened} / 10</b></div><div class="floorbar"><i style="width:{opened * 10}%"></i></div>'
            '<p style="margin:6px 0 0;font-size:.88rem;color:var(--mute)">Beat a floor boss first and the next floor opens for everyone.</p></div></div>'
            f'<div class="box"><div class="box-title">Top climbers</div><div class="box-body">{top}</div></div>'
            '<div class="box"><div class="box-title">Join the climb</div><div class="box-body" style="text-align:center">'
            '<img src="img/walk_vesper.png" alt="" width="64" height="64" style="margin:2px 0 -4px">'
            '<p style="margin:8px 0 12px">Free to play. Never pay-to-win.</p><a class="btn" href="join.html">Play now</a></div></div>')


def page(name: str, title: str, body: str) -> str:
    groups = []
    for group, items in MENU:
        links = "".join(f'<a href="{href}"{" class=here" if href == name else ""}>{e(label)}</a>' for href, label in items)
        if group == "Play" and SIGNUP_URL:
            links += (f'<a href="{e(SIGNUP_URL)}">Create account</a><a href="{e(newchar_url())}">New character</a>'
                      f'<a href="{e(security_url())}">Account security</a>')
        groups.append(f'<div class="menu-group">{e(group)}</div>{links}')
    top = "".join(f'<a href="{h}"{" class=here" if h == name else ""}>{e(l)}</a>' for h, l in
                  [("index.html", "Home"), ("floors.html", "The tower"), ("hall-of-fame.html", "Hall of Fame"),
                   ("online.html", "Who is online"), ("rules.html", "Rules")])
    # the money monsters, evenly spaced along the road, each at a slightly different pace
    walkers = "".join(f'<img src="img/walk_{n}.png" alt="" style="animation-duration:{d}s;animation-delay:-{d * i / len(shown):.1f}s">'
                      for shown in [parade()] for i, n in enumerate(shown) for d in [52 + (i % 3) * 4])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} - {SITE}</title><link rel="stylesheet" href="style.css"></head>
<body>
<header class="banner">{TOWER_SVG.replace('class="tower"', 'class="tower far"')}{TOWER_SVG}<div class="inner"><a class="logo" href="index.html">SPIREBOUND</a>
<div class="tagline">Climb the tower. Open each floor for everyone.</div></div>
<div class="parade">{walkers}</div><div class="ground"></div></header>
<div class="topbar"><div class="wrap"><nav class="links">{top}</nav><a class="btn small" href="join.html">Play now</a></div></div>
<div class="wrap layout">
<aside class="side-left"><div class="box menu"><div class="box-title">Menu</div>{"".join(groups)}<div style="height:8px"></div></div></aside>
<main><section class="box"><div class="box-title">{e(title)}</div><div class="box-body">
{body}
</div></section></main>
<aside class="side">{side_status()}</aside>
</div>
<footer><div class="wrap">{SITE} is a fan-made, non-commercial Open Tibia project. Never pay-to-win.
The creatures on this site are our own art. This site is rebuilt from the game's own data.</div></footer></body></html>
"""


def shell(title: str, body: str, here: str = "", signup_url: str = "/signup") -> str:
    """A page in the website's frame for the login service's own pages (sign-up, another character), drawn on request
    with the latest live snapshot in the side boxes."""
    global SNAP, SIGNUP_URL
    with RENDER_LOCK:
        old = SNAP, SIGNUP_URL
        SNAP, SIGNUP_URL = LAST_SNAP, signup_url
        try:
            return page(here, title, body)
        finally:
            SNAP, SIGNUP_URL = old


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
    feats = [
        ("ram", "One shared tower", "Floors open for everyone, with a server-wide announcement when a boss falls."),
        ("alpha", "PvP with teeth, not bullying", "Newbie and level-range protection, outnumbered shields, bounties and harsh red skulls."),
        ("shardling", "Exploration pays", "Secrets hidden on every floor, bought by the Info Broker."),
        ("mole", "Houses do things", "Portals, trophy halls, training rooms and ponds."),
        ("sproutling", "Never pay-to-win", "The best gear and spells come only from playing."),
        ("thornsnap", "Choose your risk", "Normal, Hardcore, or Death Game, where dying retires the character."),
    ]
    tiles = "".join(f'<div class="feature"><img src="img/stand_{s}.png" alt=""><div><b>{e(t)}</b>{e(d)}</div></div>' for s, t, d in feats)
    return f"""
<div class="hero"><div>
<p class="lead">An Open Tibia server shaped like a floating tower. Everyone starts on <b>Floor 1</b>.
Each floor ends in a labyrinth and a boss. The first time anyone beats a floor boss, the next floor opens
<b>for the whole server</b>.</p>
<p><a class="btn" href="join.html">Start climbing</a> &nbsp; <a href="how-to-play.html">How to play &raquo;</a></p></div></div>
<h2>Four vocations</h2>
<div class="stage">{"".join(f'<figure><img src="img/walk_{v}.png" alt=""><figcaption>{v.title()}</figcaption></figure>' for v in ("vanguard", "ranger", "arcanist", "mystic"))}</div>
<h2>What makes it different</h2>
<div class="features">{tiles}</div>
<h2>Seasons</h2>
<p>Each season the tower resets with remixed bosses and secrets. Titles and cosmetics you earn stay on your account forever.</p>
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
    cards = "".join(f'<div><img src="img/walk_{n}.png" alt=""><b>{n.title()}</b>{e(r)}</div>' for n, r in
                    [("vanguard", "Front line, sword and shield"), ("ranger", "Bows, crossbows and spears"),
                     ("arcanist", "Big, flashy area spells"), ("mystic", "Healing and nature magic")])
    return f'<div class="voc">{cards}</div>' + "<p>Four familiar vocations. Promotion at level 20 gives the familiar regeneration bump.</p>" + table(
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


def security_url() -> str:
    """The account security page (two-step login, new password) of tools/login_server.py."""
    return SIGNUP_URL.rsplit("signup", 1)[0] + "security" if "signup" in SIGNUP_URL else ""


def newchar_url() -> str:
    """The make-another-character page sits next to the sign-up page (tools/login_server.py /newchar)."""
    return SIGNUP_URL.rsplit("signup", 1)[0] + "newchar" if "signup" in SIGNUP_URL else ""


def join() -> str:
    if SIGNUP_URL:
        go = (f'<p><a class="pill" href="{e(SIGNUP_URL)}">Create your account</a></p>'
              "<p>The sign-up page asks for an e-mail address, a password (8 characters or more) and your first "
              "character's name.</p>")
    else:
        go = not_yet("Account sign-up opens here when the server opens. During the friends test, Jay sends you the address.", records=False)
    more = ("<p>Extra characters are welcome: up to 10 on one account, and they can hunt anywhere. "
            + (f'<a href="{e(newchar_url())}">Make another character</a> with your account name and password.</p>'
               if SIGNUP_URL else "The page to make them opens with the server.</p>"))
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
""" + more + """
<h2>Keeping your account safe</h2>
<ul><li>Use a password you use nowhere else.</li>
<li>Staff will never ask for your password, in game or anywhere else.</li>
<li>Too many wrong passwords from one address make that address wait a few minutes.</li>
<li>Switch on <b>two-step login</b> on the Account security page: logging in then also needs a code from an
authenticator app on your phone.</li></ul>
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
    img, src = out / "img", ROOT / "website" / "public" / "img"
    if src.is_dir() and img.resolve() != src.resolve():
        img.mkdir(exist_ok=True)
        for f in src.iterdir():
            (img / f.name).write_bytes(f.read_bytes())
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
            if SIGNUP_URL and html.unescape(href) in (SIGNUP_URL, newchar_url(), security_url()):
                continue
            if href.startswith("http"):
                problems.append(f"{name}: external link {href}")
            elif not (out / href).exists():
                problems.append(f"{name}: broken link {href}")
        for src in re.findall(r'src="([^"]+)"', text):
            if not (out / src).exists():
                problems.append(f"{name}: missing picture {src}")
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
