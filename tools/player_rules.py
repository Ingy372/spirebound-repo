#!/usr/bin/env python3
"""Spirebound's rulebook for players: the one place the full rules are written (Jay, 2026-11-25: the website "needs
to have a copy of the server rules and what they aren't allowed to do").

Shown on the website (tools/gen_site.py, rules.html), on the sign-up page (tools/login_server.py, /rules, which new
players must tick before making an account) and written to docs/RULES.md. The short version players see in game
with !rules and the punishment ladder live in server/data-spirebound/lib/spirebound/moderation.lua; this file reads
them from there (never edits them) so the website shows exactly what the game shows, and the self-test fails if the
two ever disagree.

  python tools/player_rules.py --write-md     rewrite docs/RULES.md from this file
  python tools/player_rules.py --selftest     checks used by tools/test_boot.sh
Standard library only.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODERATION = ROOT / "server" / "data-spirebound" / "lib" / "spirebound" / "moderation.lua"

NOT_ALLOWED = [
    ("In chat and towards other players", [
        "Slurs, hate speech, threats, or picking on someone for who they are (where they come from, their religion, "
        "gender, sexuality, a disability).",
        "Sexual messages or harassment of any kind.",
        "Following or harassing someone outside the game, or sharing anyone's personal details (real name, address, "
        "photos, accounts elsewhere).",
        "Spam: flooding a channel, the same message over and over, or advertising other servers, websites or anything for sale.",
        "Pretending to be a gamemaster, a member of staff or one of the tower's NPCs.",
    ]),
    ("Names", [
        "Rude names, names from other games or books, names of real, well-known people, and names that look like a "
        "staff title (GM, Admin, Tutor...). The sign-up page refuses most of them; a gamemaster renames the rest.",
    ]),
    ("Cheating", [
        "Any bot, macro, auto-clicker or program other than the Spirebound client, or a changed copy of our client.",
        "Hiding the built-in cavebot, or getting around its cost or its limits in fights with players.",
        "Auto-fishing.",
        "Using a bug, a hole in the map or a broken quest for gain. Found one? Say !report and tell us; we thank people "
        "who do.",
        "Trying to get into someone else's account, or attacking or overloading the server.",
        "Running more than 3 game clients on one computer at the same time.",
    ]),
    ("Money and trades", [
        "Selling or buying characters, accounts, items or gold for real money, or offering to.",
        "Scams: lying about what a trade is, swapping items at the last second, fake promises of payment. Trades are "
        "at your own risk, but a deliberate scam is punished. Staff can see the market and trade logs.",
    ]),
    ("Fights", [
        "Hunting the same newer player again and again. Player killing is part of the game where the zones allow it; "
        "bullying is not, and the skull and bounty rules punish it.",
        "Asking a friend to get killed, or killing your own characters, to farm bounties, rewards or leaderboard places.",
    ]),
]

ALLOWED = [
    "The cavebot and helpers built into the Spirebound client. While the cavebot runs you earn 45% of the experience "
    "and half the loot, and the cut lasts 10 minutes after you switch it off. Auto-targeting on its own costs nothing.",
    "Extra characters, and playing several accounts at once (up to 3 clients on one computer). Extra characters may "
    "hunt anywhere, not only in town.",
    "Training while online.",
    "Player killing where the zone allows it, inside the skull, bounty and protection rules (see PvP rules).",
]

DETAILS = [
    ("Bots and helpers", [
        "Our own client is the only allowed client; its helpers are built in so nobody needs anything else.",
        "Secrets, rare chests and the Twin Fang trial never trigger while the cavebot is on. Boss rooms do not let a "
        "cavebot character in.",
        "In fights with players the helpers only heal: no automatic haste, attacks or counters, and the cavebot stops walking.",
        "Suspicious patterns are logged for staff to look at. Nobody is banned automatically.",
        "Third-party bots or a hidden cavebot: first time, a 7-day ban and the gains removed; second time, a permanent ban.",
    ]),
    ("Never pay-to-win", [
        "The donation shop sells looks, house decorations and conveniences only. Nothing in it gives damage, defence, "
        "healing, experience, skill speed, loot or gear stats. No experience boosts, no loot boxes, and shop items can "
        "never be gambled.",
        "Shop items can be traded on the market for gold, so players can earn them by playing.",
    ]),
    ("Fair play for the Death Game", [
        "Only monsters, bosses, traps and the tower itself can retire a Death Game character. A death where another "
        "player did real damage in the last 60 seconds counts as a player death instead (see Difficulty).",
        "A server crash or server lag that kills a Death Game character is undone by a gamemaster. Ask within a day.",
    ]),
    ("Bans are public", [
        "Every ban for cheating or real-money trading is listed with its reason in the Exile Ledger on this site.",
        "A ban covers the person's other accounts too.",
    ]),
]

GM_NOTES = [
    "`/reports` lists open reports (`/reports clear` when done). `/mute <name>, <minutes>` and `/unmute <name>`.",
    "`/gmlog` shows the last GM actions. Every mute, restore, calendar and scope change is written there and in the server log.",
    "Unfair Death Game deaths (a server crash or server lag): `/restore <name>`.",
]


def _lua_list(name: str) -> list[str]:
    """A list of strings from moderation.lua (SpireMod.RULES or SpireMod.LADDER), read only."""
    if not MODERATION.exists():
        return []
    m = re.search(r"SpireMod\." + name + r"\s*=\s*\{(.*?)\n\}", MODERATION.read_text(encoding="utf-8"), re.S)
    return [s.replace('\\"', '"') for s in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))] if m else []


def in_game_rules() -> list[str]:
    """The short rules exactly as !rules shows them in game (without the heading and blank lines)."""
    return [l.lstrip("- ").strip() for l in _lua_list("RULES") if l.startswith("-")]


def ladder() -> list[str]:
    """The punishment ladder exactly as the game shows it, without the "1." numbers."""
    return [re.sub(r"^\d+\.\s*", "", l) for l in _lua_list("LADDER")]


def to_html(links: dict | None = None) -> str:
    """The rulebook as HTML. links: optional {"pvp": url, "modes": url, "ledger": url} for the cross-references."""
    links = links or {}
    e = html.escape

    def lst(items, tag="ul"):
        return f"<{tag}>" + "".join(f"<li>{e(x)}</li>" for x in items) + f"</{tag}>"

    out = ["<p>Spirebound is built against toxicity: fight hard where the game allows it, and be decent everywhere. "
           "These are the rules. Breaking them leads to the steps at the bottom of this page.</p>",
           "<h2>In short</h2><p>What you see in game when you say <b>!rules</b>:</p>", lst(in_game_rules())]
    out.append("<h2>What is not allowed</h2>")
    for title, items in NOT_ALLOWED:
        out.append(f"<h3>{e(title)}</h3>" + lst(items))
    out.append("<h2>What is allowed (so nobody has to ask)</h2>" + lst(ALLOWED))
    for title, items in DETAILS:
        out.append(f"<h2>{e(title)}</h2>" + lst(items))
    out.append("<h2>Reports and what happens to rule breakers</h2>"
               "<p>In game, say <b>!report &lt;name&gt;, &lt;what happened&gt;</b>. A gamemaster reads every report. "
               "Public chat blocks the worst words in English, Portuguese and Spanish.</p>" + lst(ladder(), "ol"))
    page = "\n".join(out)
    for word, key in (("PvP rules", "pvp"), ("Difficulty", "modes"), ("Exile Ledger", "ledger")):
        if links.get(key):
            page = page.replace(f"(see {word})", f'(see <a href="{e(links[key])}">{word}</a>)', 1)
            page = page.replace(f"the {word} on this site", f'the <a href="{e(links[key])}">{word}</a> on this site', 1)
    return page


def to_markdown() -> str:
    md = ["# Spirebound rules and the punishment ladder", "",
          "Written from `tools/player_rules.py` (`python tools/player_rules.py --write-md`); edit that file, not this one. "
          "The same rules are on the website and the sign-up page. Claude's draft, Jay can change any of it.", "",
          "## In short (what `!rules` shows in game)"] + [f"- {l}" for l in in_game_rules()] + ["", "## What is not allowed"]
    for title, items in NOT_ALLOWED:
        md += ["", f"### {title}"] + [f"- {x}" for x in items]
    md += ["", "## What is allowed"] + [f"- {x}" for x in ALLOWED]
    for title, items in DETAILS:
        md += ["", f"## {title}"] + [f"- {x}" for x in items]
    md += ["", "## What happens to rule breakers"] + [f"{i}. {l}" for i, l in enumerate(ladder(), 1)]
    md += ["", "## For gamemasters"] + [f"- {x}" for x in GM_NOTES]
    return "\n".join(md) + "\n"


def selftest():
    rules, steps = in_game_rules(), ladder()
    assert len(rules) >= 5, "the in-game short rules were read from moderation.lua"
    assert len(steps) == 5 and steps[0].startswith("A warning"), "the in-game ladder was read from moderation.lua"
    page = to_html({"pvp": "pvp.html"})
    for r in rules + steps:
        assert html.escape(r) in page, f"the website is missing an in-game line: {r}"
    assert 'href="pvp.html"' in page and "<script" not in page.lower()
    assert "3 clients" in page and "Training while online" in page, "Jay's 2026-11-25 answer: extra accounts and trainers are fine"
    md = (ROOT / "docs" / "RULES.md")
    assert md.exists() and md.read_text(encoding="utf-8") == to_markdown(), \
        "docs/RULES.md is out of date: run python tools/player_rules.py --write-md"
    print(f"player_rules selftest: OK ({sum(len(i) for _, i in NOT_ALLOWED)} not-allowed rules, in-game lines match)")


if __name__ == "__main__":
    if "--write-md" in sys.argv:
        (ROOT / "docs" / "RULES.md").write_text(to_markdown(), encoding="utf-8")
        print("wrote docs/RULES.md")
    elif "--selftest" in sys.argv:
        selftest()
    else:
        print(to_markdown())
