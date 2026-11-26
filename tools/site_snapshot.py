#!/usr/bin/env python3
"""Reads the game's records from the database into the snapshot tools/gen_site.py turns into the live website pages
(Hall of Fame, Characters, Memorial, Exile Ledger, Who is online; roadmap 7.1). Read-only: it never writes to the
database.

Where the records live (the server's own code writes them):
  players / players_online / account_bans   ordinary tables
  kv_store "spirebound-floors.floor-N"       first clears (lib/spirebound/floors.lua)
  kv_store "spirebound-memorial.<name>"      fallen Death Game characters (difficulty.lua)
  kv_store "player.<id>.spirebound.*"        difficulty and retired flag per character
  kv_store "account.<id>.spirebound-legacy.titles"   Spirebound titles, account-wide (season.lua, chronicle.lua)
The kv_store values are Canary's ValueWrapper protobuf (decoded below by hand; no library needed).
Canary's own "player.<id>.titles" are Tibia's titles and are never shown.

  python3 tools/site_snapshot.py                 print the snapshot (JSON)
  python3 tools/site_snapshot.py --site [DIR]    build the live site into DIR (default .local/site)
  python3 tools/site_snapshot.py --selftest      decoder and snapshot checks without a database
tools/login_server.py runs this every few minutes and serves the result. Settings: the MYSQL_* variables.
"""
from __future__ import annotations

import json
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

# Accounts kept off the public pages: staff (account type 4 and up: gamemasters, community managers, god) and the test
# accounts Claude's tools make. More with SPIRE_SITE_HIDE="name1,name2".
TEST_ACCOUNTS = ("autopilot", "grokbot", "pilot", "fresh", "claude", "test", "bot")


def hidden_account(acc_name: str, acc_type: int) -> bool:
    import os
    extra = [x.strip().lower() for x in os.environ.get("SPIRE_SITE_HIDE", "").split(",") if x.strip()]
    n = (acc_name or "").lower()
    return acc_type >= 4 or n.startswith(TEST_ACCOUNTS) or n in extra


VOCATIONS = {0: "None", 1: "Arcanist", 2: "Mystic", 3: "Ranger", 4: "Vanguard",
             5: "High Arcanist", 6: "Elder Mystic", 7: "Far Warden", 8: "Blade Warden"}


# ---------------------------------------------------------------- Canary's KV values (protobuf)
def _varint(b: bytes, i: int):
    r = s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        if c < 0x80:
            return r, i
        s += 7


def _fields(b: bytes):
    i = 0
    while i < len(b):
        key, i = _varint(b, i)
        num, wt = key >> 3, key & 7
        if wt == 0:
            v, i = _varint(b, i)
        elif wt == 1:
            v, i = b[i:i + 8], i + 8
        elif wt == 2:
            n, i = _varint(b, i)
            v, i = b[i:i + n], i + n
        elif wt == 5:
            v, i = b[i:i + 4], i + 4
        else:
            raise ValueError(f"wire type {wt}")
        yield num, wt, v


def decode(b: bytes):
    """ValueWrapper: 1 text, 2 whole number, 3 number, 4 list, 5 table (key -> value), 6 true/false."""
    for num, wt, v in _fields(b):
        if num == 1:
            return v.decode("utf-8", "replace")
        if num == 2:
            return v - (1 << 64) if v >= 1 << 63 else v
        if num == 3:
            d = struct.unpack("<d", v)[0]
            return int(d) if d.is_integer() else d
        if num == 4:
            return [decode(x) for n, _w, x in _fields(v) if n == 1]
        if num == 5:
            out = {}
            for n, _w, item in _fields(v):
                if n != 1:
                    continue
                key, val = None, None
                for n2, _w2, x in _fields(item):
                    if n2 == 1:
                        key = x.decode("utf-8", "replace")
                    elif n2 == 2:
                        val = decode(x)
                out[key] = val
            return out
        if num == 6:
            return bool(v)
    return None


def as_list(v):
    """Lua tables come back as {"1": a, "2": b} or as a list, depending on how they were saved."""
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        return [v[k] for k in sorted(v, key=lambda k: int(k) if str(k).isdigit() else 0)]
    return []


# ---------------------------------------------------------------- the snapshot
def snapshot(sql, now=None) -> dict:
    """sql(query) -> rows of text columns (tools/login_server.py's sql). Returns gen_site's snapshot."""
    kv = {}
    for key, hexval in sql("SELECT key_name, HEX(value) FROM kv_store WHERE key_name LIKE 'spirebound-floors.%' "
                           "OR key_name LIKE 'spirebound-memorial.%' OR key_name LIKE 'player.%.spirebound.difficulty' "
                           "OR key_name LIKE 'player.%.spirebound.retired' OR key_name LIKE 'account.%.spirebound-legacy.titles'"):
        try:
            kv[key] = decode(bytes.fromhex(hexval))
        except (ValueError, IndexError, struct.error):
            pass
    online = {r[0] for r in sql("SELECT player_id FROM players_online")}
    chars, ips, hidden, shown_online = [], set(), set(), 0
    for pid, acc, name, level, voc, deletion, lastip, group, acc_type, acc_name in sql(
            "SELECT p.id, p.account_id, p.name, p.level, p.vocation, p.deletion, p.lastip, p.group_id, a.type, a.name "
            "FROM players p JOIN accounts a ON a.id = p.account_id ORDER BY p.experience DESC, p.level DESC LIMIT 5000"):
        if int(group) >= 4 or hidden_account(acc_name, int(acc_type)):
            hidden.add(name)
            continue
        retired = kv.get(f"player.{pid}.spirebound.retired") is True
        if deletion not in ("0", "") and not retired:
            continue                                    # really deleted, not a fallen Death Game character
        c = {"name": name, "level": int(level), "vocation": VOCATIONS.get(int(voc), "None"),
             "mode": int(kv.get(f"player.{pid}.spirebound.difficulty") or 1), "retired": retired, "online": pid in online}
        titles = kv.get(f"account.{acc}.spirebound-legacy.titles")
        if isinstance(titles, dict) and titles:
            c["titles"] = sorted(titles)
        chars.append(c)
        if pid in online:
            ips.add(lastip)
            shown_online += 1
    floors = []
    for key, rec in kv.items():
        if key.startswith("spirebound-floors.floor-") and isinstance(rec, dict) and rec.get("bossDeadAt"):
            floors.append({"floor": int(key.rsplit("-", 1)[1]), "cleared_at": rec["bossDeadAt"],
                           "credit": as_list(rec.get("credit")), "last_hit": rec.get("lastHit") or "",
                           "duration": rec.get("duration") or 0})
    memorial = [{"name": key.split(".", 1)[1], "level": r.get("level", 0), "vocation": r.get("vocation", "?"),
                 "cause": r.get("cause", "unknown"), "time": r.get("time", 0)}
                for key, r in kv.items() if key.startswith("spirebound-memorial.") and isinstance(r, dict)
                and key.split(".", 1)[1] not in hidden]
    exiles = []
    for acc, reason, banned_at, expires_at, name in sql(
            "SELECT b.account_id, b.reason, b.banned_at, b.expires_at, (SELECT p.name FROM players p WHERE "
            "p.account_id = b.account_id ORDER BY p.level DESC LIMIT 1) FROM account_bans b"):
        if name and name != "NULL" and name not in hidden:
            exiles.append({"name": name, "reason": reason, "when": int(banned_at), "until": max(0, int(expires_at))})
    return {"taken": int(now or time.time()), "online": {"characters": shown_online, "people": len(ips)},
            "floors": sorted(floors, key=lambda f: f["floor"]), "characters": chars, "memorial": memorial, "exiles": exiles}


def build_site(sql, out: Path | None = None, signup_url: str = "/signup") -> Path:
    """Take a snapshot and build the live website from it. Returns the folder."""
    import gen_site
    out = out or ROOT / ".local" / "site"
    snap = snapshot(sql)
    with gen_site.RENDER_LOCK:
        gen_site.SNAP, gen_site.SIGNUP_URL = snap, signup_url
        try:
            gen_site.build(out)
        finally:
            gen_site.SNAP, gen_site.SIGNUP_URL = None, ""
        gen_site.LAST_SNAP = snap
    return out


def selftest():
    def wrap(num, payload: bytes) -> bytes:
        return bytes([(num << 3) | 2, len(payload)]) + payload

    def text(s):
        return wrap(1, s.encode())

    def double(d):
        return bytes([(3 << 3) | 1]) + struct.pack("<d", d)

    def entry(k, v):
        return wrap(1, wrap(1, k.encode()) + wrap(2, v))

    assert decode(bytes.fromhex("19000000000000F03F")) == 1, "a real difficulty value from the database"
    assert decode(bytes.fromhex("2A00")) == {}, "an empty floor record"
    assert decode(bytes([0x30, 1])) is True and decode(text("Tom")) == "Tom"
    floor = wrap(5, entry("bossDeadAt", double(1794900000)) + entry("lastHit", text("Tom Reed")) +
                 entry("credit", wrap(5, entry("1", text("Mira Vale")) + entry("2", text("Tom Reed")))) +
                 entry("duration", double(1260)))
    rec = decode(floor)
    assert rec["bossDeadAt"] == 1794900000 and as_list(rec["credit"]) == ["Mira Vale", "Tom Reed"], rec
    real = bytes.fromhex("2AB3010A9A010A06636F756E7473128F012A8C010A120A05666C6F6F72120919000000000000F03F0A130A06626561636F6E12"
                         "091900000000000010400A130A06736563726574120919000000000000F03F0A110A046B696C6C1209190000000000805640"
                         "0A120A05717565737412091900000000000008400A110A0470617468120919000000000000F03F0A120A056C6576656C1209"
                         "1900000000000044400A140A0763686170746572120919000000000000F03F")
    assert decode(real)["counts"]["kill"] == 90, "a real Chronicle record from the database"

    def fake(q):
        if q.startswith("SELECT key_name"):
            return [["spirebound-floors.floor-1", floor.hex()], ["spirebound-floors.floor-2", "2A00"],
                    ["player.7.spirebound.difficulty", "19" + struct.pack("<d", 3).hex()],
                    ["player.7.spirebound.retired", "3001"],
                    ["spirebound-memorial.Pip Hollow", wrap(5, entry("level", double(22)) + entry("cause", text("a Grey Alpha"))).hex()],
                    ["account.2.spirebound-legacy.titles", wrap(5, entry("Floor 1 First Clear", double(1))).hex()]]
        if q.startswith("SELECT player_id"):
            return [["5"], ["6"], ["2"]]
        if q.startswith("SELECT p.id"):
            return [["1", "1", "Gm Owner", "500", "0", "0", "100", "6", "6", "jay"],
                    ["2", "9", "Spell Ranger", "300", "3", "0", "100", "1", "1", "autopilot"],
                    ["5", "2", "Tom Reed", "61", "8", "0", "100", "1", "1", "tomr"], ["6", "3", "Mira Vale", "58", "6", "0", "100", "1", "1", "mira"],
                    ["7", "4", "Pip Hollow", "22", "1", "1794950000", "200", "1", "1", "pip"],
                    ["8", "4", "Gone Away", "9", "0", "1794950000", "200", "1", "1", "pip"]]
        if q.startswith("SELECT b.account_id"):
            return [["9", "Selling gold for real money", "1794960000", "0", "Quick Coin"]]
        return []
    s = snapshot(fake, now=1795000000)
    names = [c["name"] for c in s["characters"]]
    assert names == ["Tom Reed", "Mira Vale", "Pip Hollow"], f"deleted characters are left out, fallen ones kept: {names}"
    pip = s["characters"][2]
    assert pip["retired"] and pip["mode"] == 3 and s["characters"][0]["titles"] == ["Floor 1 First Clear"]
    assert s["online"] == {"characters": 2, "people": 1}, "two characters from one address are one person; test characters not counted"
    assert "Gm Owner" not in names and "Spell Ranger" not in names, "staff and test accounts stay off the public pages"
    assert [f["floor"] for f in s["floors"]] == [1], "only cleared floors"
    assert s["memorial"][0]["name"] == "Pip Hollow" and s["exiles"][0]["until"] == 0
    import gen_site
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        build_site(fake, Path(d))
        assert (Path(d) / "char-tom-reed.html").exists() and "Quick Coin" in (Path(d) / "exile-ledger.html").read_text(encoding="utf8")
        assert gen_site.SNAP is None, "the plain site is left as it was"
    print("site_snapshot selftest: OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    from login_server import sql
    if "--site" in sys.argv:
        i = sys.argv.index("--site")
        out = Path(sys.argv[i + 1]) if i + 1 < len(sys.argv) else None
        print("site:", build_site(sql, out))
    else:
        print(json.dumps(snapshot(sql), indent=1))
