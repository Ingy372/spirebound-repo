#!/usr/bin/env python3
"""Count every look a player can see on Floors 1-3 and how much of it is still borrowed (roadmap N4, ART_COUNT.md).

  python tools/art_count.py            prints the counts as JSON, writes .local/scratch/art_count_ids.json

Read-only: reads the generated map, monster and NPC files, item tables and the local client files
(.local/client, CipSoft art, Jay's PC only; set ART_COUNT_LOCAL to another .local folder to use that one).
Changes nothing. Rerun it when art lands to refresh ART_COUNT.md."""
import collections, json, re, struct, sys
from pathlib import Path

import os
WT = MAIN = Path(__file__).resolve().parent.parent
LOCAL = Path(os.environ.get("ART_COUNT_LOCAL", MAIN / ".local"))
THINGS = LOCAL / "client/data/things/1511"
sys.path.insert(0, str(WT / "tools")); sys.path.insert(0, str(WT / "maps"))
import spriteview as sv
sv.THINGS = THINGS
from spriteview import fields, packed
import mapgen


def _out():
    p = MAIN / ".local" / "scratch"
    p.mkdir(parents=True, exist_ok=True)
    return p / "art_count_ids.json"


# ---- appearances: sprite ids per thing, all frame groups
def load_app(path):
    out = {1: {}, 2: {}, 3: {}, 4: {}}
    flags = {}
    for num, wt, v in fields(path.read_bytes()):
        if num not in out:
            continue
        iid, spr, fl, name = None, [], set(), ""
        for n2, w2, v2 in fields(v):
            if n2 == 1: iid = v2
            elif n2 == 2 and w2 == 2:
                for n3, w3, v3 in fields(v2):
                    if n3 == 3 and w3 == 2:
                        for n4, w4, v4 in fields(v3):
                            if n4 == 5: spr += packed(v4) if w4 == 2 else [v4]
            elif n2 == 3 and w2 == 2:
                for n3, w3, v3 in fields(v2):
                    fl.add(n3)
            elif n2 == 4 and w2 == 2: name = v2.decode("utf-8", "ignore")
        if iid is not None:
            out[num][iid] = sorted(set(spr)); flags[(num, iid)] = (fl, name)
    return out, flags
orig = next(p for p in THINGS.glob("appearances-*.dat") if "spirebound" not in p.name)
APP, FLAGS = load_app(orig)
APP_SB, _ = load_app(THINGS / "appearances-spirebound.dat")

# ---- map: every item id on each tile, floors 1-3 by x
data = (WT / "server/data-spirebound/world/spirebound.otbm").read_bytes()
sys.setrecursionlimit(100000)
def parse(i):
    i += 1; typ = data[i]; i += 1; props, ch = bytearray(), []
    while True:
        b = data[i]
        if b == 0xFD: props.append(data[i + 1]); i += 2
        elif b == 0xFE: c, i = parse(i); ch.append(c)
        elif b == 0xFF: return (typ, bytes(props), ch), i + 1
        else: props.append(b); i += 1
root, _ = parse(4)
def floor_of(x):
    if x < 2000: return 1
    n = 2 + (x - 2000) // 400
    return n
mapids = {1: collections.Counter(), 2: collections.Counter(), 3: collections.Counter()}
def items_in(node, f):
    typ, p, ch = node
    if typ == 6:
        mapids[f][struct.unpack("<H", p[:2])[0]] += 1
    for c in ch: items_in(c, f)
def walk(node):
    typ, p, ch = node
    if typ == 4:
        bx, by, bz = struct.unpack("<HHB", p[:5])
        for t in ch:
            if t[0] in (5, 14):
                f = floor_of(bx + t[1][0])
                if f > 3: continue
                tp = t[1][2:] if t[0] == 5 else t[1][6:]
                k = 0
                while k < len(tp):
                    a = tp[k]
                    if a == 3: k += 5
                    elif a == 9: mapids[f][struct.unpack("<H", tp[k+1:k+3])[0]] += 1; k += 3
                    else: break
                for it in t[2]: items_in(it, f)
    else:
        for c in ch: walk(c)
walk(root)
allmap = collections.Counter()
for f in mapids: allmap.update(mapids[f])

BANK, TAKE = 1, 18
walls = mapgen.WALL_IDS | mapgen.ROOF_IDS | set(mapgen.PLATEAU_EDGE.values())
for fam in mapgen.FAMILIES.values():
    walls |= {v for v in fam.values() if v}
def is_door(i):
    return "door" in FLAGS.get((1, i), (set(), ""))[1].lower()

# ---- carried items from tables
lua = WT / "server/data-spirebound"
mon_files = sorted((lua / "monster/floor1").glob("*.lua")) + sorted(lua.glob("monster/floors/f[23]_*.lua"))
carry = set()
for f in mon_files:
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"monster\.loot\s*=\s*\{(.*?)\n\}", t, re.S)
    if m: carry |= {int(x) for x in re.findall(r"\bid\s*=\s*(\d+)", m.group(1))}
for name in ["gear_data.lua", "shop.lua", "wilds_data.lua", "tasks.lua", "tasks_floors.lua", "economy.lua", "crafting.lua", "quests.lua"]:
    p = lua / "lib/spirebound" / name
    if p.exists():
        t = p.read_text(encoding="utf-8", errors="ignore")
        carry |= {int(x) for x in re.findall(r"\b(?:base|itemId|item|clientId|reward|id)\s*=\s*(\d{3,5})\b", t)}
# NPC shops on floors 1-3
npcxml = (lua / "world/spirebound-npc.xml").read_text()
npc_names = set()
for cx, block in re.findall(r'centerx="(\d+)".*?\n(.*?)</npc>', npcxml, re.S):
    if floor_of(int(cx)) <= 3:
        npc_names |= set(re.findall(r'name="([^"]+)"', block))
npc_looks, npc_found = {}, set()
for f in sorted((lua / "npc").glob("*.lua")):
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'internalNpcName\s*=\s*"([^"]+)"', t) or re.search(r'local\s+\w+\s*=\s*"([^"]+)"', t)
    nm = m.group(1) if m else f.stem
    if nm not in npc_names: continue
    npc_found.add(nm)
    lt = re.search(r"lookType\s*=\s*(\d+)", t)
    if lt: npc_looks[nm] = int(lt.group(1))
    carry |= {int(x) for x in re.findall(r"(?:clientId|itemId|itemid)\s*=\s*(\d+)", t)}
carry = {i for i in carry if i in APP[1]}
# takeable map items also count as items
for i in allmap:
    if TAKE in FLAGS.get((1, i), (set(),))[0]: carry.add(i)

ground = {i for i in allmap if BANK in FLAGS.get((1, i), (set(),))[0]}
wallset = {i for i in allmap if i in walls or is_door(i)} - ground
objects = set(allmap) - ground - wallset - carry

def spr(kind, ids):
    return sum(len(APP[kind].get(i, [])) for i in ids)

# ---- creatures
def looks(files):
    out = {}
    for f in files:
        t = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"lookType\s*=\s*(\d+)", t); n = re.search(r'name\s*=\s*"([^"]+)"', t) or re.search(r'createMonsterType\("([^"]+)"', t)
        if m: out[f.stem] = int(m.group(1))
    return out
mons = looks(mon_files)
sys.path.insert(0, str(WT / "tools"))
src = (WT / "tools/make_creature_sheets.py").read_text()
CRE = eval(re.search(r"CREATURES = (\{.*?\})\n", src, re.S).group(1))
ours_looks = {l for v in CRE.values() for l in v}

# ---- effects
eff_names = set()
for f in mon_files + list((lua / "scripts").rglob("*.lua")) + list((lua / "lib").rglob("*.lua")):
    eff_names |= set(re.findall(r"CONST_(?:ME|ANI)_[A-Z_]+", f.read_text(encoding="utf-8", errors="ignore")))
fx_ours = len(list((WT / "art/effects/game").glob("*"))) if (WT / "art/effects/game").exists() else 0
avg_me = sum(len(v) for v in APP[3].values()) / max(1, len(APP[3]))
avg_ani = sum(len(v) for v in APP[4].values()) / max(1, len(APP[4]))

# ---- interface images
ui = [p for p in (LOCAL / "client").rglob("*") if p.suffix.lower() in (".png", ".apng") and "screenshots" not in str(p).lower()]
ui_ours = [p for p in (WT / "client").rglob("*.png")]

res = dict(
  floors={f: len(c) for f, c in mapids.items()},
  ground=(len(ground), spr(1, ground)), walls=(len(wallset), spr(1, wallset)),
  objects=(len(objects), spr(1, objects)), items=(len(carry), spr(1, carry)),
  items_on_map=len([i for i in carry if i in allmap]),
  monsters=dict(files=len(mon_files), looks=sorted(set(mons.values())), ours=sorted(set(mons.values()) & ours_looks),
                sprites_borrowed=spr(2, set(mons.values()) - ours_looks)),
  mon_by_look={l: sorted(k for k, v in mons.items() if v == l) for l in set(mons.values())},
  npcs=dict(names=len(npc_names), found=len(npc_found), looks=sorted(set(npc_looks.values())), missing=sorted(npc_names - npc_found),
            sprites=spr(2, set(npc_looks.values()))),
  effects=dict(names=sorted(eff_names), n_me=len([e for e in eff_names if "_ME_" in e]), n_ani=len([e for e in eff_names if "_ANI_" in e]),
               avg_me=avg_me, avg_ani=avg_ani, ours_files=fx_ours),
  ui=dict(total=len(ui), ours=len(ui_ours)),
  outfit_sprites={l: len(APP[2].get(l, [])) for l in [128,129,130,131,132,133,134,143,144,145,146,136,137,138,139,140,141,142,147,148,149,150]},
)
print(json.dumps(res, indent=1, default=list))
json.dump(dict(ground=sorted(ground), walls=sorted(wallset), objects=sorted(objects), items=sorted(carry),
               names={i: FLAGS.get((1, i), (0, ""))[1] for i in set(allmap) | carry}),
          open(_out(), "w"), indent=0)
