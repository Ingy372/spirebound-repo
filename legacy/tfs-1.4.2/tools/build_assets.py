#!/usr/bin/env python3
"""assets.csv + PNGs -> Spirebound.dat, Spirebound.spr, items.otb, items.xml (03_TECH_STACK, 18_ART).

Art resolution order for every sprite (first hit wins):
  1. assets/png/<path>          hand-made, Grok, or commissioned art (committed)
  2. assets/generated/<path>    procedural art from tools/procedural_tiles.py (rebuilt on demand)
  3. a labeled placeholder      tools/placeholder_art.py

Item rows come from assets/assets.csv plus, automatically, every item in data/weapons.csv,
data/armor.csv, data/materials.csv and data/consumables.csv (names and stats from the design tables).

Outputs (git-ignored): assets/build/{Spirebound.dat, Spirebound.spr, items.otb, items.xml, manifest.json}
--install copies items.otb/items.xml into server/data/items/ and dat/spr into client/data/things/1098/.

Every run ends with a round-trip test: the written files are read back and compared with what was
meant to be written (thing flags, sizes, sprite ids, decoded pixels, otb items). Any mismatch exits 1.

Usage: python3 tools/build_assets.py [--install]
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path
from xml.sax.saxutils import quoteattr

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import otformats as otf  # noqa: E402
import placeholder_art as ph  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
BUILD = ASSETS / "build"
S = 32

DIRS = ["n", "e", "s", "w"]


# ------------------------------------------------------------------ rows

def load_rows():
    rows = []
    with open(ASSETS / "assets.csv", newline="") as f:
        for r in csv.DictReader(f):
            r["id"] = int(r["id"])
            r["frames"] = int(r["frames"] or 1)
            rows.append(r)
    have = {(r["category"], r["id"]) for r in rows}

    def add(tid, name, flags, xml, note):
        if ("item", tid) in have:
            return
        rows.append({"id": tid, "category": "item", "name": name, "flags": flags, "size": "1x1",
                     "frames": 1, "png": "", "xml": xml, "notes": note})

    slot_of = {"helm": "head", "body": "body", "legs": "legs", "boots": "feet"}
    with open(ROOT / "data" / "weapons.csv", newline="") as f:
        for r in csv.DictReader(f):
            atk = str(r["attack"])
            if atk.startswith("def"):
                xml = f"weight=600;slotType=two-handed;weaponType=shield;defense={atk.split()[1]}"
            else:
                wtype = {"slinger": "distance", "arcanist": "wand"}.get(r["path"], "sword")
                hands = "two-handed" if r["path"] in ("cleaver", "slinger") else "hand"
                xml = f"weight={800 if hands == 'two-handed' else 500};slotType={hands};weaponType={wtype};attack={atk}"
            add(int(r["item_id"]), r["name"].lower(), "pickup", xml, "data/weapons.csv")
    with open(ROOT / "data" / "armor.csv", newline="") as f:
        for r in csv.DictReader(f):
            xml = f"weight=400;slotType={slot_of.get(r['slot'], r['slot'])};armor={r['armor']}"
            add(int(r["item_id"]), r["name"].lower(), "pickup", xml, "data/armor.csv")
    with open(ROOT / "data" / "materials.csv", newline="") as f:
        for r in csv.DictReader(f):
            add(int(r["item_id"]), r["name"].lower(), "stackable;pickup", "weight=100", "data/materials.csv")
    with open(ROOT / "data" / "consumables.csv", newline="") as f:
        for r in csv.DictReader(f):
            add(int(r["item_id"]), r["name"].lower(), "stackable;pickup", "weight=100", "data/consumables.csv")
    return rows


def parse_flags(s):
    out = []
    for tok in filter(None, (t.strip() for t in s.split(";"))):
        name, *args = tok.split(":")
        out.append((name, otf.normalize_attr(name, tuple(int(a) for a in args))))
    return out


# ------------------------------------------------------------------ art

def ensure_generated():
    marker = ASSETS / "generated" / "ground" / "grass_0.png"
    if not marker.exists():
        subprocess.run([sys.executable, str(ROOT / "tools" / "procedural_tiles.py")], check=True)


def resolve(rel: str):
    for base in (ASSETS / "png", ASSETS / "generated"):
        p = base / rel
        if p.exists():
            return Image.open(p).convert("RGBA"), str(p.relative_to(ROOT))
    return None, None


def item_images(row):
    """Returns (list of phase images WxH tiles each, source label)."""
    w, h = (int(x) for x in row["size"].split("x"))
    rel = row["png"].split(":", 1)[1] if row["png"].startswith("generated:") else (row["png"] or f"items/{row['id']}.png")
    im, src = resolve(rel)
    if im is None:
        im, src = ph.item_icon(row["id"], row["name"], w, h), "placeholder"
    frames = row["frames"]
    fw = S * w
    if im.size != (fw * frames, S * h):
        im = im.resize((fw * frames, S * h), Image.NEAREST)
    return [im.crop((i * fw, 0, (i + 1) * fw, S * h)) for i in range(frames)], src


def outfit_images(row):
    """dict[(dir, frame)] -> image. frame 0 is idle; frames 1..n are walk frames."""
    lt, n = row["id"], row["frames"]
    out, srcs = {}, set()
    for d, dn in enumerate(DIRS):
        for fr in range(n + 1):
            im, src = resolve(f"outfits/{lt}/{dn}_{fr}.png")
            if im is None:
                im, src = ph.outfit_frame(lt, row["name"], d, fr), "placeholder"
            out[(d, fr)] = im.resize((S, S), Image.NEAREST) if im.size != (S, S) else im
            srcs.add("art" if src != "placeholder" else "placeholder")
    return out, "placeholder" if srcs == {"placeholder"} else ("art" if srcs == {"art"} else "mixed")


def effect_images(row):
    n = row["frames"]
    im, src = resolve(f"effects/{row['id']}.png")
    if im is None:
        return [ph.effect_frame(row["id"], i, n) for i in range(n)], "placeholder"
    if im.size != (S * n, S):
        im = im.resize((S * n, S), Image.NEAREST)
    return [im.crop((i * S, 0, (i + 1) * S, S)) for i in range(n)], src


def missile_image(row):
    im, src = resolve(f"missiles/{row['id']}.png")
    if im is None:
        return ph.missile_icon(row["id"]), "placeholder"
    return (im.resize((S, S), Image.NEAREST) if im.size != (S, S) else im), src


# ------------------------------------------------------------------ sprite sheet

class SpriteSheet:
    def __init__(self):
        self.blocks = []        # pixel blocks, index 0 = sprite id 1
        self.pixels = []        # canonical RGBA (alpha thresholded) for round-trip
        self.index = {}

    def add_tile(self, tile: Image.Image) -> int:
        raw = bytearray(tile.tobytes())
        for i in range(3, len(raw), 4):  # binary alpha, as the 10.98 sprite format stores it
            if raw[i] >= 128:
                raw[i] = 255
            else:
                raw[i - 3:i + 1] = b"\0\0\0\0"
        raw = bytes(raw)
        if not any(raw[3::4]):
            return 0  # fully transparent -> sprite 0
        key = hashlib.sha1(raw).digest()
        if key not in self.index:
            self.blocks.append(otf.encode_sprite(raw))
            self.pixels.append(raw)
            self.index[key] = len(self.blocks)
        return self.index[key]

    def add_image(self, im: Image.Image, w: int, h: int):
        """Tibia order: index 0 is the bottom-right 32x32 cell; x then y, growing up-left."""
        ids = []
        for hy in range(h):
            for wx in range(w):
                x0 = (w - wx - 1) * S
                y0 = (h - hy - 1) * S
                ids.append(self.add_tile(im.crop((x0, y0, x0 + S, y0 + S))))
        return ids


# ------------------------------------------------------------------ otb / xml mapping

def otb_item(row, flags):
    names = {n for n, _ in flags}
    args = dict(flags)
    it = otf.OtbItem(row["id"], row["id"])
    if "ground" in names:
        it.group = otf.OTB_GROUP["ground"]; it.speed = args["ground"][0] if args["ground"] else 0
    elif "container" in names:
        it.group = otf.OTB_GROUP["container"]
    elif "splash" in names:
        it.group = otf.OTB_GROUP["splash"]
    elif "fluid" in names:
        it.group = otf.OTB_GROUP["fluid"]
    F = otf.OTB_FLAG
    fl = 0
    if "block" in names: fl |= F["block_solid"]
    if "blockmissile" in names: fl |= F["block_projectile"]
    if "blockpath" in names: fl |= F["block_pathfind"]
    if "height" in names: fl |= F["has_height"]
    if "multiuse" in names or "usable" in names: fl |= F["useable"]
    if "pickup" in names: fl |= F["pickupable"]
    if "immovable" not in names and "ground" not in names: fl |= F["moveable"]
    if "stackable" in names: fl |= F["stackable"]
    if "hangable" in names: fl |= F["hangable"]
    if "hooksouth" in names: fl |= F["vertical"]
    if "hookeast" in names: fl |= F["horizontal"]
    if "rotate" in names: fl |= F["rotatable"]
    if "animate" in names or row["frames"] > 1: fl |= F["animation"]
    if "forceuse" in names: fl |= F["force_use"]
    if "writable" in names or "writableonce" in names: fl |= F["readable"]
    for n, order in (("border", 1), ("bottom", 2), ("top", 3)):
        if n in names:
            fl |= F["always_on_top"]; it.top_order = order
    if "light" in names:
        it.light = args["light"]
    it.flags = fl
    it.name = row["name"]
    return it


XML_KEYS = {"containersize": "containerSize", "slottype": "slotType", "weapontype": "weaponType",
            "corpsetype": "corpseType", "decayto": "decayTo", "maxtextlen": "maxTextLen"}


def xml_item(row):
    attrs = [kv.split("=", 1) for kv in filter(None, row["xml"].split(";"))]
    lines = [f'\t<item id="{row["id"]}" name={quoteattr(row["name"])}>']
    field = None
    for k, v in attrs:
        k = XML_KEYS.get(k.lower(), k)
        if k == "field":
            field = v; continue
        lines.append(f'\t\t<attribute key="{k}" value={quoteattr(v)} />')
    if field:
        lines.append(f'\t\t<attribute key="field" value="{field}" />')
    lines.append("\t</item>")
    return "\n".join(lines)


def check_engine_ids(rows):
    ids = {r["id"] for r in rows if r["category"] == "item"}
    src = (ROOT / "server" / "src" / "spire_ids.h").read_text()
    missing = []
    for name, val in re.findall(r"constexpr uint16_t (SPIRE_ID_\w+) = (\d+);", src):
        v = int(val)
        if v == 0:
            continue
        span = 17 if name == "SPIRE_ID_DEPOT_BOX_FIRST" else 1
        for k in range(span):
            if v + k not in ids:
                missing.append(f"{name}+{k}={v + k}" if span > 1 else f"{name}={v}")
    return missing


# ------------------------------------------------------------------ main

def main(install=False):
    ensure_generated()
    rows = load_rows()
    missing = check_engine_ids(rows)
    if missing:
        print("FAIL: engine item ids missing from assets.csv:", ", ".join(missing)); return 1

    sheet = SpriteSheet()
    dat = {"item": {}, "outfit": {}, "effect": {}, "missile": {}}
    otb_items, xml_rows, report = [], [], {"placeholder": 0, "art": 0}

    for row in sorted(rows, key=lambda r: (r["category"], r["id"])):
        cat = row["category"]
        if cat == "item":
            if row["id"] < 100:
                raise SystemExit(f"item id {row['id']} < 100")
            flags = parse_flags(row["flags"])
            w, h = (int(x) for x in row["size"].split("x"))
            frames, src = item_images(row)
            sprites = []
            for fr in frames:
                sprites += sheet.add_image(fr, w, h)
            g = otf.FrameGroup(width=w, height=h, exact=max(w, h) * S, phases=len(frames), sprites=sprites)
            if len(frames) > 1:
                g.anim = (True, 0, 0, [(300, 300)] * len(frames))
            dat["item"][row["id"]] = otf.Thing(attrs=list(flags), groups=[g])
            otb_items.append(otb_item(row, flags))
            xml_rows.append(xml_item(row))
        elif cat == "outfit":
            imgs, src = outfit_images(row)
            n = row["frames"]
            idle = otf.FrameGroup(gtype=0, px=4, phases=1, sprites=[sheet.add_image(imgs[(d, 0)], 1, 1)[0] for d in range(4)])
            mov_sprites = []
            for fr in range(1, n + 1):
                for d in range(4):
                    mov_sprites.append(sheet.add_image(imgs[(d, fr)], 1, 1)[0])
            moving = otf.FrameGroup(gtype=1, px=4, phases=n, sprites=mov_sprites,
                                    anim=(True, 0, 0, [(120, 120)] * n) if n > 1 else None)
            dat["outfit"][row["id"]] = otf.Thing(attrs=[], groups=[idle, moving])
        elif cat == "effect":
            frames, src = effect_images(row)
            g = otf.FrameGroup(phases=len(frames), sprites=[sheet.add_image(f, 1, 1)[0] for f in frames])
            if len(frames) > 1:
                g.anim = (True, 1, 0, [(100, 100)] * len(frames))
            dat["effect"][row["id"]] = otf.Thing(attrs=[], groups=[g])
        elif cat == "missile":
            im, src = missile_image(row)
            sid = sheet.add_image(im, 1, 1)[0]
            dat["missile"][row["id"]] = otf.Thing(attrs=[], groups=[otf.FrameGroup(px=3, py=3, sprites=[sid] * 9)])
        else:
            raise SystemExit(f"unknown category {cat}")
        report["placeholder" if src == "placeholder" else "art"] += 1

    spr_body = b"".join(sheet.blocks)
    spr_sig = zlib.crc32(spr_body) & 0xFFFFFFFF
    spr = otf.write_spr(spr_sig, sheet.blocks)
    dat_tmp = otf.write_dat(0, dat["item"], dat["outfit"], dat["effect"], dat["missile"])
    dat_sig = zlib.crc32(dat_tmp[4:]) & 0xFFFFFFFF
    datb = otf.write_dat(dat_sig, dat["item"], dat["outfit"], dat["effect"], dat["missile"])
    otb = otf.write_otb(otb_items, build=dat_sig & 0xFFFF)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- generated by tools/build_assets.py; do not edit -->\n<items>\n' + \
        "\n".join(xml_rows) + "\n</items>\n"

    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "Spirebound.spr").write_bytes(spr)
    (BUILD / "Spirebound.dat").write_bytes(datb)
    (BUILD / "items.otb").write_bytes(otb)
    (BUILD / "items.xml").write_text(xml)

    # ---------------- round trip
    errors = []
    sig2, things = otf.read_dat((BUILD / "Spirebound.dat").read_bytes())
    if sig2 != dat_sig:
        errors.append("dat signature")
    for ci, key in enumerate(("item", "outfit", "effect", "missile")):
        for tid, t in dat[key].items():
            r = things[ci].get(tid)
            if r is None:
                errors.append(f"{key} {tid} missing"); continue
            if [(n, tuple(a)) for n, a in r.attrs] != [(n, tuple(a)) for n, a in t.attrs]:
                errors.append(f"{key} {tid} attrs {r.attrs} != {t.attrs}")
            for g1, g2 in zip(t.groups, r.groups):
                if (g1.width, g1.height, g1.layers, g1.px, g1.py, g1.pz, g1.phases, g1.sprites) != \
                   (g2.width, g2.height, g2.layers, g2.px, g2.py, g2.pz, g2.phases, g2.sprites):
                    errors.append(f"{key} {tid} frame group differs")
            if len(t.groups) != len(r.groups):
                errors.append(f"{key} {tid} group count")
    ssig, blocks = otf.read_spr((BUILD / "Spirebound.spr").read_bytes())
    if ssig != spr_sig or len(blocks) != len(sheet.pixels):
        errors.append("spr header")
    for i, (blk, want) in enumerate(zip(blocks, sheet.pixels)):
        if otf.decode_sprite(blk) != want:
            errors.append(f"sprite {i + 1} pixels differ")
            if len(errors) > 20:
                break
    (major, minor, _), items = otf.read_otb((BUILD / "items.otb").read_bytes())
    if (major, minor) != (otf.OTB_MAJOR, otf.OTB_MINOR_1098):
        errors.append("otb version")
    want = {i.server_id: i for i in otb_items}
    got = {i.server_id: i for i in items}
    if set(want) != set(got):
        errors.append("otb item set differs")
    for sid, i in want.items():
        g = got.get(sid)
        if g and (g.client_id, g.group, g.flags, g.speed, g.light, g.top_order, g.name) != \
           (i.client_id, i.group, i.flags, i.speed, i.light, i.top_order, i.name):
            errors.append(f"otb item {sid} differs")
    for sid in want:
        if sid not in dat["item"]:
            errors.append(f"otb item {sid} has no client thing")

    manifest = {
        "dat_signature": f"{dat_sig:08x}", "spr_signature": f"{spr_sig:08x}",
        "dat_sha256": hashlib.sha256(datb).hexdigest(), "spr_sha256": hashlib.sha256(spr).hexdigest(),
        "items": len(dat["item"]), "max_item_id": max(dat["item"]), "outfits": len(dat["outfit"]),
        "effects": len(dat["effect"]), "missiles": len(dat["missile"]), "sprites": len(sheet.blocks),
        "things_with_placeholder_art": report["placeholder"], "things_with_art": report["art"],
        "round_trip": "pass" if not errors else "FAIL",
    }
    (BUILD / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    if install:
        items_dir = ROOT / "server" / "data" / "items"
        items_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(BUILD / "items.otb", items_dir / "items.otb")
        shutil.copy(BUILD / "items.xml", items_dir / "items.xml")
        things_dir = ROOT / "client" / "data" / "things" / "1098"
        things_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(BUILD / "Spirebound.dat", things_dir / "Spirebound.dat")
        shutil.copy(BUILD / "Spirebound.spr", things_dir / "Spirebound.spr")

    print(f"build_assets: {manifest['items']} items (max id {manifest['max_item_id']}), {manifest['outfits']} outfits, "
          f"{manifest['effects']} effects, {manifest['missiles']} missiles, {manifest['sprites']} unique sprites; "
          f"art {report['art']}, placeholder {report['placeholder']}")
    if errors:
        print("ROUND-TRIP FAIL:\n  " + "\n  ".join(errors[:30]))
        return 1
    print("round-trip: pass (dat, spr pixels, otb re-read and match)")
    return 0


if __name__ == "__main__":
    sys.exit(main(install="--install" in sys.argv))
