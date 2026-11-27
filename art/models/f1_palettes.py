#!/usr/bin/env python3
"""Palettes for the Floor 1 creatures that wore borrowed Tibia looks until 2026-11-27 (small game, ground-feature
monsters, the Underkeep's Wing 1, the Oathkeeper...). Normal Python:

  python art/models/f1_palettes.py

Like art/pipeline/boss_palettes.py: the anchors live here, so palette.json can always be rebuilt (after a merge
conflict in palette.json: take main's copy, rerun the four pipeline palette scripts, then this one). It only ADDS its
own ramp sets; it never changes another creature's. Each colour is (dark, light, mid) turned into an 8-tone ramp.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent / "pipeline"
sys.path.insert(0, str(PIPE))
from outfit_palette import base, ramp  # noqa: E402

PAL = {}
flat = lambda c: [list(c)] * 8   # noqa: E731

# ---------------------------------------------------------------- small game on the lawns (Q94)
# Meadow Hare: silver-grey with a warm buff wash (Tibia's rabbit is brown), cream belly, black-tipped long ears,
# a white scut, amber eyes.
SILVER = ((34, 34, 42), (222, 216, 202), (128, 122, 116))
PAL["meadow_hare"] = {
    "body": ramp(*SILVER), "head": ramp(*SILVER), "belly": ramp((120, 112, 100), (255, 250, 238), (222, 214, 196)),
    "snout": ramp((110, 102, 92), (250, 244, 230), (206, 196, 180)), "nose": ramp((90, 40, 46), (240, 160, 160)),
    "ear": ramp(*SILVER), "eye": ramp((40, 22, 12), (210, 150, 70), (110, 64, 26)),
    "leg_near": ramp((40, 38, 44), (210, 204, 190), (124, 118, 110)), "leg_far": ramp((30, 28, 34), (160, 154, 144), (92, 88, 82)),
    "paw_near": ramp((110, 104, 96), (250, 246, 236)), "paw_far": ramp((84, 80, 74), (200, 196, 186)),
    "tail_base": ramp((150, 146, 140), (255, 255, 255)), "tail_tip": ramp((170, 166, 160), (255, 255, 255)),
    "eartip": ramp((6, 6, 8), (64, 60, 62), (24, 22, 24)), "inner": ramp((120, 70, 70), (250, 196, 190), (210, 140, 136)),
    "buff": ramp((54, 46, 38), (232, 212, 180), (150, 134, 110)), "line": flat((20, 18, 20)),
    "hindfoot": ramp((60, 56, 54), (236, 230, 216), (150, 144, 134)),
}

# Dapple Fawn: cool dun-taupe (Tibia's deer is red-brown), a dark stripe down the spine with rows of bright cream
# dapples either side, cream belly and throat, dark-rimmed big ears, a black nose, dark brown eyes.
DUN = ((36, 28, 28), (190, 160, 128), (112, 88, 72))
PAL["dapple_fawn"] = {
    "body": ramp(*DUN), "head": ramp(*DUN), "belly": ramp((120, 110, 96), (255, 248, 230), (222, 210, 186)),
    "snout": ramp((60, 50, 44), (220, 204, 176), (140, 122, 104)), "nose": flat((16, 14, 16)),
    "ear": ramp(*DUN), "eye": ramp((10, 8, 8), (120, 80, 50), (40, 26, 20)),
    "leg_near": ramp((36, 30, 30), (196, 174, 146), (110, 92, 78)), "leg_far": ramp((26, 22, 22), (150, 132, 110), (80, 66, 56)),
    "paw_near": flat((22, 18, 18)), "paw_far": flat((16, 14, 14)),
    "tail_base": ramp(*DUN), "tail_tip": ramp((170, 160, 146), (255, 252, 244)),
    "spot": ramp((170, 156, 130), (255, 252, 236), (240, 230, 206)), "stripe": ramp((20, 16, 18), (110, 88, 74), (56, 44, 40)),
    "rim": ramp((14, 12, 12), (80, 66, 60), (36, 30, 28)), "inner": ramp((120, 96, 90), (246, 222, 210), (200, 170, 160)),
    "line": flat((24, 18, 18)),
}

# Thistle Hen: slate-blue plumage freckled with white (Tibia's chicken is white with a red comb), a rust breast, a
# spiky thistle-purple crest with lilac tips, a bronze-black tail, horn beak, orange legs.
SLATE_HEN = ((22, 26, 38), (164, 176, 196), (70, 80, 102))
PAL["thistle_hen"] = {
    "body": ramp(*SLATE_HEN), "head": ramp((20, 22, 32), (140, 150, 170), (60, 66, 86)),
    "breast": ramp((60, 20, 12), (236, 150, 96), (164, 74, 40)), "wing": ramp((18, 22, 32), (140, 150, 170), (56, 64, 84)),
    "tail": ramp((10, 10, 12), (150, 120, 70), (40, 34, 28)), "crest": ramp((40, 10, 50), (230, 150, 240), (130, 50, 150)),
    "crestip": ramp((150, 100, 170), (255, 230, 255), (220, 180, 240)), "beak": ramp((110, 90, 50), (255, 240, 190), (220, 190, 120)),
    "wattle": ramp((90, 20, 50), (240, 110, 150), (180, 50, 90)), "eye": flat((250, 190, 60)),
    "leg": ramp((110, 50, 10), (255, 190, 90), (220, 120, 40)), "foot": ramp((110, 50, 10), (255, 190, 90), (220, 120, 40)),
    "speck": ramp((180, 186, 196), (255, 255, 255)), "line": flat((14, 14, 22)),
}

# Acorn Squirrel: dusky ash-grey (Tibia's squirrel is red-brown with a pale tail), a cream belly, a huge charcoal brush
# of a tail frosted russet at the end, russet ear tufts, a golden acorn with a dark cap in its mouth.
ASH_SQ = ((30, 30, 40), (200, 196, 196), (96, 96, 108))
PAL["acorn_squirrel"] = {
    "body": ramp(*ASH_SQ), "head": ramp(*ASH_SQ), "belly": ramp((120, 110, 96), (255, 248, 230), (220, 206, 180)),
    "snout": ramp((80, 74, 70), (236, 228, 214), (160, 150, 140)), "nose": flat((30, 20, 22)),
    "ear": ramp(*ASH_SQ), "eye": ramp((6, 6, 8), (90, 80, 80), (24, 22, 24)),
    "leg_near": ramp((30, 28, 30), (170, 162, 154), (90, 86, 84)), "leg_far": ramp((22, 20, 22), (130, 124, 118), (66, 62, 62)),
    "paw_near": ramp((60, 56, 52), (210, 200, 186)), "paw_far": ramp((44, 40, 38), (160, 152, 140)),
    "tail_base": ramp((10, 10, 16), (130, 124, 136), (44, 42, 52)), "tail_tip": ramp((60, 26, 14), (236, 176, 120), (150, 76, 40)),
    "tuft": ramp((60, 20, 8), (240, 150, 90), (170, 70, 30)), "acorn": ramp((90, 50, 10), (255, 214, 120), (200, 140, 50)),
    "cap": ramp((24, 16, 10), (130, 96, 60), (66, 46, 28)), "stripe": ramp((70, 30, 14), (230, 160, 100), (150, 80, 40)),
    "line": flat((20, 16, 18)),
}

# ---------------------------------------------------------------- ground-feature monsters (FD2)
# Nest Queen: the meadow wasps' mother: a long honey-gold abdomen with burgundy-black bands (her wasps are amber and
# blue-black; Tibia's are lemon and brown), a russet fuzzy thorax, an ivory crown of horn spikes, ember eyes, smoky
# amber wings torn ragged, a glowing amber venom drop.
PAL["nest_queen"] = {
    "thorax": ramp((40, 14, 8), (230, 150, 80), (140, 64, 30)), "abdomen": ramp((90, 46, 6), (255, 226, 120), (214, 150, 30)),
    "stripe": ramp((16, 4, 10), (120, 50, 70), (52, 14, 30)), "head": ramp((16, 4, 10), (120, 50, 70), (52, 14, 30)),
    "face": ramp((90, 60, 20), (255, 230, 150), (200, 160, 80)), "eye": ramp((120, 10, 6), (255, 160, 90), (230, 60, 30)),
    "stinger": ramp((10, 4, 8), (90, 50, 60), (36, 16, 24)), "wing": ramp((90, 70, 50), (226, 206, 170), (170, 146, 110)),
    "leg": ramp((14, 6, 10), (100, 60, 64), (40, 20, 28)), "antenna": flat((26, 10, 18)), "vein": flat((50, 30, 26)),
    "waist": ramp((16, 4, 10), (120, 50, 70), (52, 14, 30)), "crown": ramp((120, 100, 60), (255, 250, 220), (230, 214, 160)),
    "venom": ramp((180, 100, 10), (255, 250, 170), (255, 200, 60)),
}

# Elder Sproutling: a sproutling grown old: a sage-olive bulb face on a grey-brown bark trunk, a crown of deep emerald
# leaves (bluer and darker than the meadow grass) with pale-pink blossoms, mossy patches, amber eyes under bark brows.
PAL["elder_sproutling"] = {
    "bulb": ramp((22, 34, 20), (186, 200, 132), (92, 114, 62)), "bark": ramp((24, 18, 14), (176, 150, 120), (92, 74, 56)),
    "ridge": flat((20, 14, 10)), "eye": ramp((140, 70, 0), (255, 230, 120), (250, 170, 30)), "brow": ramp((20, 14, 10), (120, 96, 70), (60, 46, 32)),
    "mouth": flat((16, 10, 8)), "leaf": ramp((4, 24, 20), (96, 170, 112), (24, 92, 62)), "vein": flat((150, 214, 150)),
    "twig": ramp((24, 18, 14), (160, 132, 100), (84, 64, 46)), "root": ramp((22, 16, 12), (150, 120, 90), (76, 58, 40)),
    "moss": ramp((20, 44, 18), (130, 176, 80), (60, 104, 40)), "blossom": ramp((170, 100, 120), (255, 236, 240), (240, 180, 196)),
}

# Bandit Lieutenant: the approved road bandit's palette with a wine-black hood and cape (the bandits wear mud-brown, the
# captain a red coat), a mustard officer's scarf, a dark leather-green jerkin, tan crossed knife belts, a bright tin
# badge, steel knives.
_BANDIT = json.loads((PIPE / "palette.json").read_text(encoding="utf-8"))["ramps"]["bandit"]
WINE = ((16, 8, 12), (140, 74, 80), (62, 26, 34))
PAL["bandit_lieutenant"] = {**_BANDIT,
    "hood": ramp(*WINE), "cape": ramp(*WINE), "rim": ramp((8, 4, 6), (90, 44, 50), (36, 14, 20)),
    "scarf": ramp((80, 54, 8), (246, 206, 100), (190, 140, 36)), "torso": ramp((14, 20, 16), (110, 130, 100), (46, 60, 44)),
    "arm_a": ramp((14, 20, 16), (110, 130, 100), (46, 60, 44)), "arm_b": ramp((14, 20, 16), (110, 130, 100), (46, 60, 44)),
    "strap": ramp((44, 26, 12), (220, 170, 110), (140, 96, 54)), "badge": ramp((90, 96, 106), (255, 255, 255), (200, 206, 214)),
    "knife": ramp((60, 64, 76), (250, 252, 255), (170, 178, 192)),
}

# ---------------------------------------------------------------- the Underkeep, Wing 1
# Mire Toad: a cave-mud toad, slate-violet skin (Tibia's toad is orange-gold, the pond's emerald, the Goldback bottle-green),
# a dirty lichen-ochre belly, near-black blotches, and glowing poison-green glands: two big ones behind the eyes, a row
# down each flank and a toxic seam down the spine; sickly yellow-green eyes, glistening slime drips.
MIRE = ((16, 14, 24), (150, 136, 160), (66, 58, 82))
PAL["mire_toad"] = {
    "body": ramp(*MIRE), "head": ramp(*MIRE), "leg": ramp((14, 12, 20), (140, 128, 150), (60, 54, 72)),
    "belly": ramp((70, 60, 30), (220, 206, 140), (150, 134, 80)), "blotch": ramp((6, 4, 10), (40, 30, 50), (18, 14, 24)),
    "wart": ramp((50, 44, 60), (200, 190, 206), (120, 110, 130)), "stripe": ramp((20, 50, 14), (150, 210, 90), (60, 130, 34)),
    "eye": ramp((90, 100, 10), (250, 255, 150), (200, 220, 50)), "pupil": flat((6, 5, 8)),
    "foot": ramp((60, 54, 50), (200, 190, 170), (130, 120, 108)), "line": flat((6, 4, 10)),
    "gland": ramp((30, 70, 14), (210, 250, 130), (100, 180, 40)), "slime": ramp((60, 90, 70), (220, 250, 220), (140, 190, 150)),
}

# Sluice Warden: a giant drowned toad, cold slate-teal skin (no Tibia toad is blue), a pale bone-grey belly, a rusted
# iron sluice grate grown into its back (rust-orange plate, darker bars, pale rivets), a hanging chain, river moss,
# pale aqua eyes.
DROWN = ((10, 22, 28), (150, 186, 190), (52, 84, 94))
PAL["sluice_warden"] = {**PAL["mire_toad"],
    "body": ramp(*DROWN), "head": ramp(*DROWN), "leg": ramp((8, 18, 22), (120, 150, 156), (42, 66, 74)),
    "belly": ramp((80, 84, 80), (236, 232, 214), (170, 170, 156)), "blotch": ramp((4, 10, 14), (34, 56, 64), (16, 30, 36)),
    "wart": ramp((40, 60, 66), (190, 210, 210), (110, 136, 140)), "stripe": ramp((4, 10, 14), (34, 56, 64), (16, 30, 36)),
    "eye": ramp((20, 110, 120), (230, 255, 250), (120, 230, 230)), "foot": ramp((50, 60, 60), (200, 204, 196), (120, 130, 126)),
    "grate": ramp((50, 18, 6), (240, 150, 80), (150, 64, 24)), "bar": ramp((22, 10, 6), (150, 90, 56), (70, 34, 16)),
    "rivet": ramp((110, 100, 90), (255, 240, 210), (200, 180, 150)), "chain": ramp((30, 24, 22), (190, 170, 150), (96, 80, 70)),
    "moss": ramp((10, 36, 20), (110, 180, 110), (40, 100, 56)),
}

# ---------------------------------------------------------------- the Oathroom (FD3)
# The Oathkeeper: pale tarnished silver plate (the Stairwardens are blackened iron, the Axe-Lord rusted bronze), a faded
# cornflower-blue tabard and cape (lighter than the Stairwardens' slate), bronze trim, a pale oath-stone on the chest
# whose crack glows warm gold like the visor (the Stairwardens' light is cold blue), a tall shield with an ivory raised
# hand, a flanged steel mace, an unlit bronze lantern.
SILVERPLATE = ((40, 42, 52), (236, 234, 226), (130, 132, 140))
PAL["oathkeeper"] = {**base(hair=((40, 42, 52), (180, 176, 168)), arms=SILVERPLATE, legs=SILVERPLATE,
                           boots=((30, 26, 24), (150, 130, 110), (76, 64, 54)), torso=SILVERPLATE,
                           cuff=((60, 34, 12), (250, 210, 130), (170, 112, 44)),
                           belt=((26, 18, 14), (140, 100, 66), (70, 48, 30)), buckle=((90, 54, 14), (255, 230, 150))),
    "skin": ramp((40, 42, 52), (236, 234, 226), (130, 132, 140)), "nose": ramp((40, 42, 52), (236, 234, 226), (130, 132, 140)),
    "hand": ramp((40, 42, 52), (236, 234, 226), (130, 132, 140)),
    "eye": flat((255, 214, 110)), "brow": flat((10, 10, 14)),
    "helm": ramp((36, 38, 48), (240, 238, 230), (126, 128, 138)), "visor": flat((8, 8, 12)),
    "trim": ramp((60, 34, 12), (250, 210, 130), (170, 112, 44)), "cloth": ramp((26, 34, 64), (176, 196, 236), (84, 104, 160)),
    "stone": ramp((70, 70, 76), (240, 238, 232), (160, 158, 156)), "crack": ramp((200, 120, 20), (255, 250, 200), (255, 200, 80)),
    "glow": ramp((190, 110, 20), (255, 246, 190), (255, 196, 80)), "shield": ramp((24, 32, 60), (160, 182, 226), (76, 96, 150)),
    "sign": ramp((150, 140, 116), (255, 252, 240), (230, 222, 200)), "haft": ramp((24, 16, 12), (150, 110, 74), (76, 52, 32)),
    "steel": ramp((50, 54, 64), (250, 250, 248), (160, 164, 174)), "lantern": ramp((30, 18, 8), (190, 140, 70), (100, 66, 30)),
    "rivet": ramp((90, 54, 14), (255, 236, 170), (200, 150, 60)),
}

# ---------------------------------------------------------------- the Proving and companions
# Bramblejaw: an old yard boar, a deep oxblood-rust coat (Tibia's boar is orange-brown; our herd is charcoal or quilled),
# a shaggy darker mane, bramble-green thorny vines tangled round it with pale thorns and a few leaves, a pale scar across
# the snout, a torn ear, short yellowed tusks, small amber eyes.
OXRUST = ((22, 8, 10), (176, 112, 104), (80, 32, 30))
PAL["bramblejaw"] = {
    "body": ramp(*OXRUST), "head": ramp(*OXRUST), "belly": ramp((30, 16, 12), (170, 126, 100), (90, 56, 40)),
    "snout": ramp((50, 30, 26), (220, 170, 146), (130, 86, 70)), "nose": ramp((30, 16, 16), (180, 120, 110), (90, 50, 46)),
    "ear": ramp(*OXRUST), "eye": flat((250, 180, 50)),
    "leg_near": ramp((18, 8, 6), (130, 80, 62), (60, 28, 20)), "leg_far": ramp((14, 6, 4), (100, 60, 46), (46, 22, 16)),
    "paw_near": flat((24, 18, 16)), "paw_far": flat((18, 14, 12)),
    "tail_base": ramp(*OXRUST), "tail_tip": ramp((14, 8, 6), (90, 60, 40), (40, 24, 16)),
    "mane": ramp((10, 6, 8), (200, 150, 120), (60, 30, 26)), "vine": ramp((10, 28, 10), (130, 190, 80), (44, 100, 34)),
    "thorn": ramp((120, 110, 80), (255, 250, 220), (220, 210, 170)), "leaf": ramp((10, 40, 16), (120, 200, 100), (40, 120, 50)),
    "tusk": ramp((110, 96, 60), (250, 236, 190), (210, 190, 130)), "scar": ramp((150, 110, 100), (250, 220, 210), (220, 180, 170)),
    "brow": flat((14, 8, 6)),
}

# Wolf Companion (the Mystic's summon): pale silver-sage flanks (Tibia's wolf is plain grey, the meadow wolf ochre, the
# alpha teal-silver with a black mane), a dark slate-teal saddle, cream belly and cheeks, a garland of green leaves
# round the neck, jade spirit runes on the shoulders, glowing jade eyes.
SAGE = ((30, 38, 40), (214, 222, 206), (112, 124, 118))
PAL["wolf_companion"] = {
    "body": ramp(*SAGE), "head": ramp(*SAGE), "belly": ramp((110, 110, 96), (255, 252, 236), (220, 216, 196)),
    "snout": ramp((80, 84, 78), (240, 240, 226), (170, 172, 160)), "nose": flat((18, 18, 20)),
    "ear": ramp(*SAGE), "eye": flat((120, 255, 190)),
    "leg_near": ramp((26, 32, 34), (190, 198, 186), (96, 106, 102)), "leg_far": ramp((20, 26, 28), (150, 158, 148), (74, 82, 80)),
    "paw_near": ramp((40, 40, 38), (200, 200, 190)), "paw_far": ramp((30, 30, 28), (150, 150, 142)),
    "tail_base": ramp(*SAGE), "tail_tip": ramp((150, 156, 146), (255, 255, 250)),
    "saddle": ramp((8, 20, 24), (90, 130, 130), (30, 60, 64)), "bib": ramp((120, 120, 106), (255, 252, 236), (224, 220, 200)),
    "brow": flat((40, 56, 58)), "line": flat((16, 22, 24)),
    "leaf": ramp((8, 40, 18), (140, 220, 120), (40, 130, 56)), "rune": ramp((40, 160, 110), (220, 255, 230), (110, 240, 180)),
}

# Drain Matron (the Underkeep's Wing 2 boss): the Mire Toads' monstrous mother: deep plum-bruise skin with ochre mottling
# (Tibia's toad is orange-gold), a sallow belly and a swollen yellow throat sac, a back pitted with a honeycomb of pale
# luminous-green egg pockets, drooping jowls, poison-green eyes.
PLUM = ((18, 8, 20), (170, 120, 160), (76, 40, 74))
PAL["drain_matron"] = {**PAL["mire_toad"],
    "body": ramp(*PLUM), "head": ramp(*PLUM), "leg": ramp((14, 6, 16), (130, 90, 124), (58, 30, 56)),
    "belly": ramp((80, 66, 30), (236, 220, 150), (170, 150, 80)), "blotch": ramp((60, 40, 10), (200, 160, 70), (130, 96, 34)),
    "wart": ramp((50, 30, 50), (210, 180, 200), (130, 96, 124)), "stripe": ramp((14, 6, 16), (100, 60, 96), (44, 20, 44)),
    "eye": ramp((40, 120, 20), (220, 255, 140), (130, 230, 60)),
    "egg": ramp((60, 120, 50), (240, 255, 210), (160, 230, 130)), "pocket": ramp((8, 4, 10), (70, 40, 66), (30, 14, 30)),
    "sac": ramp((110, 80, 20), (255, 236, 150), (220, 180, 70)),
}


def main():
    path = PIPE / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(PAL)
    path.write_bytes((json.dumps(data, indent=1) + "\n").encode("utf-8"))
    print("wrote", ", ".join(PAL), "into", path.name)


if __name__ == "__main__":
    main()
