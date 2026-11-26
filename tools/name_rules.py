#!/usr/bin/env python3
"""The name checker for new accounts and characters (Jay, 2026-11-25: "add a name checker when players are creating
new accounts and characters"). Used by the sign-up page in tools/login_server.py; any later page that makes
characters must call it too.

A character name is refused when it:
  - breaks the shape: 3-20 letters in 1-3 words, each word starting with a capital, no letter 3 times in a row;
  - is or contains a name from another game (tools/banned_names.txt, the same list tools/check_names.py uses),
    including one letter off for longer names (Kiritto, Ferumbraz);
  - contains a rude word (the in-game chat filter's list in lib/spirebound/moderation.lua, plus the name-only list
    tools/name_blocklist.txt), also hidden inside a longer word or written with digits (Fuk3r, xXwhoreXx);
  - pretends to be staff (GM, Gamemaster, Admin, God, Tutor, Support...);
  - is the name of one of our NPCs or monsters (Vesper, Banker Tolliver, Field Rat).
An account name is never shown to other players, but it gets the rude-word and staff checks too.

  python tools/name_rules.py "Some Name" ...      check names by hand
  python tools/name_rules.py --selftest           the checks used by tools/test_boot.sh
Standard library only (runs on Windows Python and WSL's python3). Reads its lists once, at first use.
"""
from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "server" / "data-spirebound"

SHAPE = re.compile(r"^[A-Z][a-z]+( [A-Z][a-z]+){0,2}\Z")
# Look-alike digits and symbols players use to slip a word past a filter
LEET = str.maketrans({"0": "o", "1": "i", "!": "i", "|": "i", "3": "e", "4": "a", "@": "a", "5": "s", "$": "s",
                      "7": "t", "8": "b", "9": "g", "+": "t"})
# Ordinary words that may end an NPC's name ("the Hearthgate Baker") but stay free for players
JOBS = {"baker", "hunter", "fisher", "miller", "guard", "captain", "trader", "banker", "priest", "merchant", "scout",
        "elder", "outfitter", "quartermaster", "crier", "tailor", "smith", "weaponsmith", "armorer", "alchemist",
        "fletcher", "guide", "warden", "keeper", "broker", "registrar", "postmaster", "coachman", "coachwoman",
        "lamplighter", "housewright", "runewright", "innkeeper", "promoter", "ascendant", "little", "old", "young", "market"}
# Short words caught even inside a longer word
STRONG = {"fuck", "cunt", "shit", "nazi", "rape", "porn", "puta", "fdp"}
# Staff titles nobody may wear (whole words, any case)
STAFF = {"gm", "cm", "god", "admin", "administrator", "gamemaster", "tutor", "senior", "staff", "support", "moderator",
         "mod", "owner", "official", "server", "system", "spirebound", "community", "manager", "helper", "dev",
         "developer", "hoster"}


def _lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [l.strip().lower() for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]


@lru_cache(maxsize=1)
def lists():
    """(banned names, rude words, our own NPC and monster names, NPC personal names) read from the repo."""
    banned = _lines(ROOT / "tools" / "banned_names.txt")
    rude = set(_lines(ROOT / "tools" / "name_blocklist.txt"))
    mod = DATA / "lib" / "spirebound" / "moderation.lua"
    if mod.exists():                                           # the chat filter's words, read (never edited) here
        m = re.search(r"SpireMod\.BLOCKED\s*=\s*\{(.*?)\n\}", mod.read_text(encoding="utf-8"), re.S)
        if m:
            rude |= {w.lower() for w in re.findall(r'"([^"]+)"', m.group(1))}
    ours, npc_words = set(), []
    for f in (DATA / "npc").glob("*.lua"):
        m = re.search(r'local npcName = "([^"]+)"', f.read_text(encoding="utf-8", errors="ignore"))
        if m:
            ours.add(m.group(1).lower())
            npc_words.append(m.group(1).lower().split())
    for f in (DATA / "monster").rglob("*.lua"):
        m = re.search(r'createMonsterType\("([^"]+)"', f.read_text(encoding="utf-8", errors="ignore"))
        if m:
            ours.add(m.group(1).lower())
    # An NPC's own name is protected: the last word of "Banker Tolliver" or "Guide Pell", or a one-word name (Vesper).
    # Job words (Banker, Hunter, Miller...) are left free for players: any word used as a job somewhere is skipped.
    jobs = {ws[0] for ws in npc_words if len(ws) > 1} | JOBS
    personal = {ws[-1] for ws in npc_words if ws[-1] not in jobs and len(ws[-1]) >= 3}
    return banned, rude, ours, personal


def _one_edit(a: str, b: str) -> bool:
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = j = diff = 0
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            diff += 1
            j += 1
            if diff > 1:
                return False
        else:
            i += 1
            j += 1
    return True


def _rude(text: str) -> str | None:
    """The rude word hidden in text, if any. Words of 5+ letters, and the few strong 4-letter ones in STRONG, are caught
    inside longer words too; other short ones only as whole words, so names like Dicken or Assunta still pass.
    In name_blocklist.txt a line starting with = is always whole-word only."""
    _, rude, _, _ = lists()
    t = text.lower().translate(LEET)
    words = re.findall(r"[a-zà-ÿ]+", t)
    joined = "".join(words)
    squeezed = re.sub(r"(.)\1+", r"\1", joined)                # fuuuck -> fuck
    for w in rude:
        whole = w.startswith("=")
        w = w.lstrip("=")
        if w in words or w in (re.sub(r"(.)+", r"", x) for x in words):
            return w
        if not whole and (len(w) >= 5 or w in STRONG) and (w in joined or w in squeezed):
            return w
    return None


def check_character(name: str) -> tuple[bool, str]:
    """(ok, message for the player). The name should already have its spaces tidied (" ".join(name.split()))."""
    if not (3 <= len(name) <= 20 and SHAPE.match(name)):
        return False, "The character name must be 3 to 20 letters, each word starting with a capital (e.g. Mira or Tom Reed)."
    words = name.lower().split()
    if any(len(w) < 2 for w in words):
        return False, "Each word of the name needs at least two letters."
    if re.search(r"(.)\1\1", name.lower()):
        return False, "The same letter three times in a row is not allowed in a name."
    if any(w in STAFF for w in words):
        return False, "That name is not allowed: it looks like a staff title (GM, Admin, Tutor...)."
    if not all(re.search(r"[aeiouy]", w) for w in words):
        return False, "That does not look like a name. Each word needs a vowel."
    if _rude(name):
        return False, "That name is not allowed: it contains a rude word. Please pick another."
    banned, _, ours, personal = lists()
    low, joined = name.lower(), "".join(words)
    for b in banned:
        if re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", low) or (len(b) >= 6 and b.replace(" ", "") in joined):
            return False, "That name belongs to another game or its world. Please pick a name of your own."
        if " " not in b and len(b) >= 6 and any(_one_edit(w, b) for w in words):
            return False, "That name is too close to a name from another game. Please pick a name of your own."
    if low in ours:
        return False, "That is the name of someone (or something) in the tower. Please pick a name of your own."
    if any(w in personal for w in words):
        return False, "That name belongs to one of the tower's people. Please pick a name of your own."
    return True, ""


def check_account(name: str) -> tuple[bool, str]:
    """Account names are private, but no rude words or staff titles in them either."""
    if _rude(name):
        return False, "That account name is not allowed: it contains a rude word."
    low = name.lower().translate(LEET)
    if any(re.fullmatch(s + r"\d*", low) or low.startswith(s + "_") for s in STAFF) or re.match(r"^(gm|cm|god|admin)", low):
        return False, "That account name is not allowed: it looks like a staff account."
    return True, ""


def selftest():
    good = ["Mira", "Tom Reed", "Odessa Thorne", "Wren", "Ash Varrow", "Cassia Moor", "Hugo", "Clara Bell", "Assunta",
            "Dicken", "Petra", "Analise", "Cassandra", "Richard Turner", "Hancock"]
    bad = ["Kirito", "Kiritto", "Asuna Blade", "The Ferumbras", "Ferumbraz", "Fuck", "Fuuuck Off", "Xwhorex",
           "Gm Mira", "Admin", "God Of War", "Vesper", "Banker Tolliver", "Tolliver", "Field Rat", "Aaaron",
           "Brr", "tom reed", "A", "Mira Vale The Great Fourth", "Puta", "Caralho Doido", "Retardo"]
    for n in good:
        ok, why = check_character(n)
        assert ok, f"{n!r} should pass: {why}"
    for n in bad:
        assert not check_character(n)[0], f"{n!r} should be refused"
    for n in ("friend1", "miravale", "tomreed77"):
        assert check_account(n)[0], n
    for n in ("admin", "gm1", "godking", "fuckyou", "sh1tfuck"):
        assert not check_account(n)[0], n
    banned, rude, ours, personal = lists()
    assert banned and rude and len(ours) > 50 and "tolliver" in personal, "the lists were read"
    assert "banker" not in personal and "priest" not in personal, "job words are not personal names"
    print(f"name_rules selftest: OK ({len(banned)} names from other games, {len(rude)} rude words, "
          f"{len(ours)} names of our own, {len(personal)} NPC personal names)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    for arg in sys.argv[1:]:
        n = " ".join(arg.split())
        ok, why = check_character(n)
        print(f"{n}: {'OK' if ok else 'refused - ' + why}")
