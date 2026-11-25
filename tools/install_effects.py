#!/usr/bin/env python3
"""Put Spirebound's own spell effects (art/effects/game/, made by art/effects/make_fx.py) into the game.

  python tools/install_effects.py client [client_dir]     the game client: new sprite sheets + effect entries
  python tools/install_effects.py server <appearances.dat>  the server's copy: the effect ids, so it agrees to send them
  python tools/install_effects.py check [client_dir]      decode the installed sheets the way the client does

Standard library only (runs on Windows Python or WSL's python3). Safe to run again and again: the client keeps its
original appearances file untouched and gets a patched copy, rebuilt from the original every time.
Effect ids come from SpireFx in server/data-spirebound/lib/spirebound/spells.lua (401 and up).
"""
from __future__ import annotations

import json
import lzma
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "art" / "effects" / "game"
OURS = "appearances-spirebound.dat"
SHEET_PREFIX = "sprites-spirebound-"
STATE = "spirebound_effects.json"


# ---------------------------------------------------------------- protobuf, by hand
def varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def field(num: int, value) -> bytes:
    if isinstance(value, int):
        return varint(num << 3) + varint(value)
    return varint((num << 3) | 2) + varint(len(value)) + value


def read_varint(b: bytes, i: int):
    v = s = 0
    while True:
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if c < 0x80:
            return v, i
        s += 7


def top_fields(b: bytes):
    i = 0
    while i < len(b):
        start = i
        key, i = read_varint(b, i)
        num, wt = key >> 3, key & 7
        if wt == 0:
            v, i = read_varint(b, i)
        elif wt == 2:
            n, i = read_varint(b, i)
            v, i = b[i:i + n], i + n
        elif wt == 5:
            v, i = b[i:i + 4], i + 4
        elif wt == 1:
            v, i = b[i:i + 8], i + 8
        else:
            raise ValueError("bad wire type")
        yield num, wt, v, b[start:i]


def effect_message(e: dict, first_sprite: int | None) -> bytes:
    """One Appearance (an effect). first_sprite None = id only (the server needs nothing else)."""
    level, color = e["light"]
    flags = field(23, field(1, level) + field(2, color)) if level else b""
    if first_sprite is None:
        return field(1, e["id"]) + field(3, flags)
    anim = field(2, 0) + field(4, 1) + field(5, 1)                      # not synchronised, plays once
    for _ in range(e["frames"]):
        anim += field(6, field(1, e["ms"]) + field(2, e["ms"]))
    x, y, w, h = e["box"]
    info = field(1, 1) + field(2, 1) + field(3, 1) + field(4, 1)
    for k in range(e["frames"]):
        info += field(5, first_sprite + e["first"] + k)
    info += field(6, anim) + field(7, max(w, h)) + field(8, 0) + field(9, field(1, x) + field(2, y) + field(3, w) + field(4, h))
    group = field(1, 2) + field(2, 2) + field(3, info)
    return field(1, e["id"]) + field(2, group) + field(3, flags)


CREATURES = ROOT / "art" / "creatures" / "game"


def creature_manifest() -> list:
    f = CREATURES / "creatures.json"
    return json.loads(f.read_text())["creatures"] if f.exists() else []


def rebuild(b: bytes, fn) -> bytes:
    """the message b with each top-level field passed through fn(num, value) -> new value bytes/int, or None to keep"""
    out = bytearray()
    for num, wt, v, raw in top_fields(b):
        nv = fn(num, wt, v)
        out += raw if nv is None else field(num, nv)
    return bytes(out)


def sprite_counts(msg: bytes) -> list:
    """sprites in each frame group of an outfit (standing, walking), with one layer and four directions only"""
    out = []
    for num, wt, v, _ in top_fields(msg):
        if num == 2:
            info = next(x for n, w, x, _ in top_fields(v) if n == 3)
            d = {}
            for n, w, x, _ in top_fields(info):
                d.setdefault(n, []).append(x)
            if d.get(1) != [4] or d.get(4, [1]) != [1] or d.get(2, [1]) != [1] or d.get(3, [1]) != [1]:
                return []
            out.append(len(d.get(5, [])))
    return out


def standard_outfit(msg: bytes, first: int) -> bytes:
    """the outfit with its frame groups replaced by ours: standing (N E S W) and walking (8 steps x N E S W, 300 ms a
    step, like the rat), one layer; everything else (flags, name) kept"""
    def info(start, phases):
        b = field(1, 4) + field(2, 1) + field(3, 1) + field(4, 1)
        for k in range(4 * phases):
            b += field(5, start + k)
        if phases > 1:
            anim = field(2, 0) + field(4, 0)
            for _ in range(phases):
                anim += field(6, field(1, 300) + field(2, 300))
            b += field(6, anim)
        return b + field(7, 32)
    out = bytearray()
    for num, wt, v, raw in top_fields(msg):
        if num != 2:
            out += raw
        if num == 1:
            out += field(2, field(1, 0) + field(2, 0) + field(3, info(first, 1)))
            out += field(2, field(1, 1) + field(2, 1) + field(3, info(first + 4, 8)))
    return bytes(out)


def reskin_outfit(msg: bytes, first: int) -> bytes:
    """an outfit Appearance with its sprites replaced, in order, by first, first+1, ... (R22: our creature art)"""
    counter = [first]

    def info_fn(num, wt, v):
        if num == 5 and wt == 0:
            counter[0] += 1
            return counter[0] - 1
        return None

    def group_fn(num, wt, v):
        return rebuild(v, info_fn) if num == 3 else None

    def outfit_fn(num, wt, v):
        return rebuild(v, group_fn) if num == 2 else None

    return rebuild(msg, outfit_fn)


def manifest() -> dict:
    return json.loads((GAME / "effects.json").read_text())


def strip_effects(data: bytes, ids: set[int]) -> bytes:
    """the appearances file without any effect entry (field 3) whose id is one of ours"""
    out = bytearray()
    for num, wt, v, raw in top_fields(data):
        if num == 3:
            eid = next((x for n, w, x, _ in top_fields(v) if n == 1), None)
            if eid in ids:
                continue
        out += raw
    return bytes(out)


# ---------------------------------------------------------------- client
def things_dir(client: Path) -> Path:
    d = client / "data" / "things" / "1511"
    if not (d / "catalog-content.json").exists():
        sys.exit(f"install_effects: no client files in {d} (run windows\\Install-Client.bat first)")
    return d


def install_client(client: Path) -> None:
    things = things_dir(client)
    m = manifest()
    cat_path = things / "catalog-content.json"
    catalog = json.loads(cat_path.read_text())
    state_path = things / STATE
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    app = next(c for c in catalog if c.get("type") == "appearances")
    if app["file"] != OURS:                       # a fresh client download: this is the original
        state["original"] = app["file"]
    original = state.get("original")
    if not original or not (things / original).exists():
        sys.exit("install_effects: cannot find the client's original appearances file; run windows\\Install-Client.bat")
    # sprite sheets: drop ours, put them back after the client's own last sprite
    catalog = [c for c in catalog if not str(c.get("file", "")).startswith(SHEET_PREFIX)]
    first = max(c["lastspriteid"] for c in catalog if c.get("type") == "sprite") + 1
    sid = first
    for i, sh in enumerate(m["sheets"]):
        name = f"{SHEET_PREFIX}{i}.bmp.lzma"
        (things / name).write_bytes((GAME / sh["file"]).read_bytes())
        catalog.append({"type": "sprite", "file": name, "spritetype": 3, "firstspriteid": sid,
                        "lastspriteid": sid + sh["count"] - 1, "area": 0})
        sid += sh["count"]
    creature_first = {}
    for c in creature_manifest():
        name = f"{SHEET_PREFIX}creature-{c['name']}.bmp.lzma"
        (things / name).write_bytes((CREATURES / c["file"]).read_bytes())
        catalog.append({"type": "sprite", "file": name, "spritetype": 3, "firstspriteid": sid,
                        "lastspriteid": sid + c["count"] - 1, "area": 0})
        for look in c["looks"]:
            creature_first[look] = sid
        sid += c["count"]
    for old in things.glob(SHEET_PREFIX + "*"):
        if not any(c.get("file") == old.name for c in catalog):
            old.unlink()
    ids = {e["id"] for e in m["effects"]}
    data = strip_effects((things / original).read_bytes(), ids)
    if creature_first:                            # our approved creatures in place of the placeholder looks
        out = bytearray()
        for num, wt, v, raw in top_fields(data):
            look = next((x for n, w, x, _ in top_fields(v) if n == 1), None) if num == 2 else None
            if look in creature_first and sprite_counts(v) == [4, 32]:
                out += field(2, reskin_outfit(v, creature_first[look]))
            elif look in creature_first:                       # another layout: our standard one instead
                out += field(2, standard_outfit(v, creature_first[look]))
            else:
                out += raw
        data = bytes(out)
    for e in m["effects"]:
        data += field(3, effect_message(e, first))
    (things / OURS).write_bytes(data)
    app = next(c for c in catalog if c.get("type") == "appearances")
    app["file"] = OURS
    cat_path.write_text(json.dumps(catalog, indent=1))
    state.update({"first_sprite": first, "effects": sorted(ids)})
    state_path.write_text(json.dumps(state, indent=1))
    print(f"install_effects: {len(ids)} spell effects and {len(m['sheets'])} sprite sheets installed in the client "
          f"(sprites {first}-{sid - 1}); creatures: {', '.join(c['name'] for c in creature_manifest()) or 'none'}")


def check_client(client: Path) -> None:
    """Decode every installed sheet with the same steps as the client (raw LZMA1 that must reach its end marker,
    BMP offset at byte 10), and confirm each effect id and its sprites are in the patched file."""
    things = things_dir(client)
    catalog = json.loads((things / "catalog-content.json").read_text())
    ours = [c for c in catalog if str(c.get("file", "")).startswith(SHEET_PREFIX)]
    assert ours, "no Spirebound sheets in the catalog"
    for c in ours:
        data = (things / c["file"]).read_bytes()
        i = 0
        while data[i] == 0:
            i += 1
        assert data[i:i + 5] == bytes([0x70, 0x0A, 0xFA, 0x80, 0x24]), c["file"]
        i += 5
        while data[i] & 0x80:
            i += 1
        i += 1
        assert i == 32, f"{c['file']}: header is {i} bytes, the client expects 32"
        lclppb = data[i]
        dict_size = int.from_bytes(data[i + 1:i + 5], "little")
        filt = {"id": lzma.FILTER_LZMA1, "dict_size": dict_size, "lc": lclppb % 9, "lp": (lclppb // 9) % 5, "pb": lclppb // 45}
        dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[filt])
        raw = dec.decompress(data[i + 13:])
        assert dec.eof, f"{c['file']}: the LZMA stream has no end marker (the client would refuse it)"
        off = int.from_bytes(raw[10:14], "little")
        assert off + 384 * 384 * 4 <= len(raw) <= 589946, f"{c['file']}: wrong picture size {len(raw)}"
    app = next(c for c in catalog if c.get("type") == "appearances")
    data = (things / app["file"]).read_bytes()
    found = {}
    for num, wt, v, raw in top_fields(data):
        if num == 3:
            d = {n: x for n, w, x, _ in top_fields(v)}
            found[d.get(1)] = d
    m = manifest()
    lo = min(c["firstspriteid"] for c in ours)
    hi = max(c["lastspriteid"] for c in ours)
    for e in m["effects"]:
        assert e["id"] in found, f"effect {e['id']} ({e['name']}) missing"
        group = next(x for n, w, x, _ in top_fields(found[e["id"]][2]) if n == 3)
        sprites = [x for n, w, x, _ in top_fields(group) if n == 5]
        assert len(sprites) == e["frames"] and all(lo <= s <= hi for s in sprites), e["name"]
    print(f"install_effects check: {len(ours)} sheets decode like the client does; {len(m['effects'])} effects present")


# ---------------------------------------------------------------- server
def patch_server(path: Path) -> int:
    """append our effect ids to the server's appearances file (Canary only allows effects listed there)"""
    m = manifest()
    ids = {e["id"] for e in m["effects"]}
    data = strip_effects(path.read_bytes(), ids)
    for e in m["effects"]:
        data += field(3, effect_message(e, None))
    path.write_bytes(data)
    return len(ids)


def main(argv):
    cmd = argv[0] if argv else "client"
    if cmd == "client":
        install_client(Path(argv[1]) if len(argv) > 1 else ROOT / ".local" / "client")
    elif cmd == "check":
        check_client(Path(argv[1]) if len(argv) > 1 else ROOT / ".local" / "client")
    elif cmd == "server":
        print(f"install_effects: {patch_server(Path(argv[1]))} spell effects registered with the server")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
