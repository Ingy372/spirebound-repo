"""Hearthgate v4.1 (docs/design/hearthgate_v4_plan.md, 2026-11-27): the tile plan, in one place.

Read by the builder (maps/hearthgate.py) and by the checker (tools/hearthgate_plan_check.py), so the two can never
disagree. Coordinates are town-relative: x 0..111 west to east, y 0..95 north to south (the town's top-left corner is
TOWN in maps/floor1_plan.py). Rectangles are (x, y, w, h) and include their walls. Doors are the doorway tile.

v4.1 (Jay, 2026-11-27): "make it more of an 8 sided wall instead of slightly cut corners", "the town is grey, brighten it
up some", "build the depot in the center of town in the same circular layout ... combine the depot and the spawn in
area. the home or depot of floor 1 should feel busy and alive", and the Green's pond "needs some detail work. it can also
be just a few tiles bigger". So: the corners are cut twice as deep, the ground between buildings is grass with paved
streets, and the Hearth is now the round court at the plaza's centre: the Hearthstone in the middle, twenty depot
lockers facing it, the bank and Vesper at counters on its sides. The big hall north of the plaza is the Climbers'
Temple (chapel, trading gallery, Hall of Climbers).

Why the shops sit where they do: from the Hearthstone a door must be at most 25 steps away (Jay's goal: short walks).
On a 33-tile plaza that only works where the four avenues leave it, so every shop building stands at an avenue's
mouth with its doors on the plaza side. The Crown Quarter (45 steps) hugs the street along the temple's east side.
"""

W, H = 112, 96
CUT = 24                         # the wall's corners are cut off this far: a real eight-sided city (was 12)
GATES = {"n": [(x, 0) for x in range(55, 59)], "s": [(x, 95) for x in range(55, 59)],
         "w": [(0, y) for y in range(48, 51)], "e": [(111, y) for y in range(48, 51)]}

HEARTHSTONE = (56, 49)           # spawn and respawn point, at the centre of the Hearth (temple_hearthgate)
PLAZA_C, PLAZA_R = (56.5, 49.0), 16.0


def inside_wall(x, y):
    """On or inside the city wall (the octagon)."""
    return (0 <= x < W and 0 <= y < H and x + y >= CUT and (W - 1 - x) + y >= CUT
            and x + (H - 1 - y) >= CUT and (W - 1 - x) + (H - 1 - y) >= CUT)


def wall_tiles():
    """The octagon's outline: every inside tile with an outside neighbour (2 tiles thick on the diagonals, which is
    how a diagonal wall is drawn: a staircase of pieces)."""
    out = set()
    for y in range(H):
        for x in range(W):
            if inside_wall(x, y) and any(not inside_wall(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                out.add((x, y))
    return out


def in_plaza(x, y):
    return (x - PLAZA_C[0]) ** 2 + (y - PLAZA_C[1]) ** 2 <= PLAZA_R ** 2


# ------------------------------------------------------------------ streets (painted on the grass)
# marble 409 = the avenues and the plaza, flagstone 416 = the high roads, cobble 870 = the lanes
STREETS = {
    "North Avenue": ((55, 1, 4, 11), 409),           # north gate to the temple's north archway
    "South Avenue": ((55, 65, 4, 30), 409),          # plaza to the south gate
    "West High Road": ((1, 48, 40, 3), 416),
    "East High Road": ((73, 48, 38, 3), 416),
    "North Lane": ((16, 10, 80, 2), 870),            # the Northside doors
    "Temple West Street": ((42, 12, 2, 26), 870),
    "Temple East Street": ((70, 12, 2, 27), 870),    # the Crown Quarter's doors open onto it
    "Crown Lane": ((72, 20, 33, 2), 870),            # between the two rows of Crown Row
    "Green Lane": ((10, 16, 2, 32), 870),            # Greenside's west houses
    "Lantern Lane": ((2, 59, 26, 2), 870),
    "Lantern Close": ((11, 68, 17, 3), 870),
    "Lantern Cut": ((27, 51, 3, 30), 870),           # north-south through Lantern Row
    "Southgate Lane": ((14, 81, 41, 3), 870),
    "Coach Lane": ((59, 75, 12, 3), 870),
    "Coach Cut": ((70, 78, 2, 5), 870),
    "Manor Lane": ((70, 83, 20, 2), 870),            # the houses south of the manor's grounds
    "Garden Row": ((99, 61, 2, 10), 870),            # the house east of the manor's grounds
    "Manor Walk": ((84, 51, 3, 11), 409),            # East High Road to the manor gate
}

# ------------------------------------------------------------------ the Hearth: the round hall at the plaza's centre
# Jay, 2026-11-27: "make the depot (middle of town) a building. make it circular as you can ... this will be the main hub
# of the city. i will set the top floor as the waypoint for teleport crystals and it will also have the monument".
# Then (same day): "flip the floor plan. i think the actual bank booths in the setup you have should be on the second
# floor". Ground floor: the Hearthstone (where you appear, and where Waycrystals bring you: point hearth_waypoint),
# the Monument, the Floor Beacon, the Arena Champion and the free stalls; the four avenues enter by archways and
# stairs go up on both sides. Second floor: sixteen lockers facing the middle from the north and south, the bank's
# counter on the west side, Broker Nell and Vesper on the east. A round red roof over it all.
HEARTH_R = 14.5                  # the wall stands on the rim of this circle round PLAZA_C


def hearth_tiles():
    """(inside, wall): every tile of the round hall, and the ring of wall round it (an inside tile with an outside
    neighbour: a staircase of pieces, like the city wall)."""
    cx, cy = PLAZA_C
    inside = {(x, y) for x in range(int(cx - HEARTH_R) - 1, int(cx + HEARTH_R) + 2)
              for y in range(int(cy - HEARTH_R) - 1, int(cy + HEARTH_R) + 2)
              if (x - cx) ** 2 + (y - cy) ** 2 <= HEARTH_R ** 2}
    wall = {(x, y) for (x, y) in inside if any((x + a, y + b) not in inside for a in (-1, 0, 1) for b in (-1, 0, 1))}
    return inside, wall


def hearth_arch(x, y):
    """The four archways where the avenues come in (ground floor only)."""
    return (55 <= x <= 58) or (48 <= y <= 50)


HEARTH_COURT = (42, 35, 30, 29)  # the hall's bounding box
DEPOT_ROWS = [(47, 42, "s"), (60, 42, "s"), (47, 56, "n"), (60, 56, "n")]    # first locker; four booths each
DEPOT_SWITCH = (53, 43)          # the locker nearest the Hearthstone: its switch tile (point depot_hearthgate)
HEARTH_COUNTERS = [(45, 44, 4), (68, 44, 4)]                                 # vertical, (x, top y, length)
BANK_NPCS = {"Banker Tolliver": (44, 45), "Trader Osric": (44, 47), "Broker Nell": (69, 45)}
VESPER = (69, 47)
HEARTH_POINTS = {"depot_hearthgate": DEPOT_SWITCH, "hearth_bank": (46, 45), "hearth_trader": (46, 47),
                 "trade_hall": (46, 46), "shop_bank": (46, 45)}
HEARTH_BRAZIERS = [(54, 47), (59, 47), (54, 51), (59, 51)]   # on the corners of the Hearthstone's frame (x 54..59)
HEARTH_STAIRS = {"hearth_up_west": (45, 52, 7), "hearth_up_east": (68, 52, 7)}
# the ground floor round the Hearthstone (the lockers and bank above use the same x, y on level 6)
WAYPOINT = HEARTHSTONE          # where a Floor 1 Waycrystal brings you (tools/crystals.py TOWN_POINT)
MONUMENT = (51, 39)              # hero statue; its sign beside it; point "monument" one tile south
BEACON_BOWLS = [(62, 41), (64, 42), (66, 44), (67, 46)]
NOTICE_BOARD = (48, 42)
ARENA_STATUE = (52, 59)
STALLS = [(47, 44), (64, 54), (47, 54), (62, 59)]     # free trading stalls, 3 counters each
FOUNTAIN = (49, 32)              # in the temple garden, just north of the Hearth

# ------------------------------------------------------------------ the Climbers' Temple, north of the plaza
TEMPLE = (44, 12, 26, 19)        # interior x 45..68, y 13..29; three levels
TEMPLE_ARCHES = [(56, 12), (57, 12)] + [(x, 30) for x in range(55, 59)] + [(44, y) for y in (21, 22, 23)] + \
                [(69, y) for y in (21, 22, 23)]
TEMPLE_TOWER = (49, 18, 16, 11)  # level 3, the Hall of Climbers
TEMPLE_STAIRS = {"hearth_west": (45, 17, 7), "hearth_east": (68, 28, 7), "hearth_hall": (62, 24, 6)}
PRIEST = (61, 18)
TEMPLE_GARDEN = (44, 31, 26, 2)  # flower beds between the temple and the plaza

# ------------------------------------------------------------------ shops: six buildings at the avenue mouths
# rooms: (shop name, keeper, kind, room interior (x, y, w, h), door, side). A room's counter stands 3 tiles in from its
# door, the keeper behind it. "split" is the inner wall between the two rooms.
SHOP_BLOCKS = [
    dict(rect=(31, 38, 10, 10), style="brick", split=("y", 42), tall=True, rooms=[
        ("Weaponsmith", "Weaponsmith Garrick", "weapons", (32, 39, 8, 3), (40, 40), "e"),
        ("Armorer", "Armorer Hesta", "armor", (32, 43, 8, 4), (40, 45), "e")]),
    dict(rect=(31, 51, 10, 10), style="sand", split=("y", 56), tall=False, rooms=[
        ("General Store", "Merchant Wenna", "general", (32, 52, 8, 4), (40, 53), "e"),
        ("Quartermaster's Stores", "Quartermaster Bryn", "general", (32, 57, 8, 3), (40, 58), "e")]),
    dict(rect=(73, 39, 10, 9), style="stone", split=("y", 43), tall=True, rooms=[
        ("Runewright", "Runewright Mael", "runes", (74, 40, 8, 3), (73, 41), "w"),
        ("Fletcher", "Fletcher Tamsin", "fletcher", (74, 44, 8, 3), (73, 45), "w")]),
    dict(rect=(73, 51, 10, 10), style="timber", split=("y", 56), tall=False, rooms=[
        ("Alchemist", "Alchemist Ivo", "alchemist", (74, 52, 8, 4), (73, 53), "w"),
        ("Tailor", "Tailor Quill", "tailor", (74, 57, 8, 3), (73, 58), "w")]),
    dict(rect=(60, 65, 11, 10), style="brick", split=("y", 69), tall=True, rooms=[
        ("Housewright's Workshop", "Housewright Orla", "plain", (61, 66, 9, 3), (60, 67), "w"),
        ("Post Office", "Postmaster Hobb", "post", (61, 70, 9, 4), (60, 71), "w")]),
]
INN = dict(rect=(43, 65, 11, 13), door=(53, 67), side="e", style="timber")    # The Lantern & Lark, rooms upstairs
GUARDHOUSE = dict(rect=(60, 2, 9, 8), door=(60, 6), side="w", captain=(59, 8))

# ------------------------------------------------------------------ the Crown Quarter (north-east)
ASCENDANCY = dict(rect=(74, 22, 12, 9), door=(74, 26), side="w", npc=(78, 26))
HUNTERS_HALL = dict(rect=(74, 31, 14, 8), door=(74, 35), side="w", ladder=(86, 32))
GUILD_HALL = dict(rect=(84, 39, 13, 9), door=(90, 47), side="s", stairs=(95, 41))
TRAINING_YARD = dict(rect=(98, 37, 11, 11), gaps=[(99, 47), (100, 47)], point=(103, 42))

# ------------------------------------------------------------------ Spire Manor in its own walled grounds (south-east)
MANOR_GROUNDS = dict(rect=(72, 62, 26, 21), gate=[(84, 62), (85, 62), (86, 62)])
MANOR_AT = (74, 65)              # maps/manor.py lays the 22 x 16 house here; its door is at (85, 65)
SPIRE_GARDENS = (87, 52, 23, 9)  # a public garden beside Manor Walk, between the East High Road and the grounds

# ------------------------------------------------------------------ yards and green places
COACH_YARD = dict(rect=(60, 82, 10, 11), gap=(60, 87), ferro=(64, 87), carriage=(64, 86))
OLD_WELL = (2, 62, 9, 9)         # the Underkeep grate stays at (5, 66): the Underkeep's exit lands at (5, 68)
GRATE = (5, 66)
GREEN = (13, 15, 17, 20)         # Hearthgate Green, with its pond
GREEN_PATHS = [(13, 21, 17, 1), (17, 15, 1, 20)]
POND = dict(c=(24, 28), rx=4, ry=3, pier=(24, 24, 1, 3))    # the pond, and a little wooden pier from its north shore
POCKET_GARDEN = (49, 84, 5, 9)

# ------------------------------------------------------------------ 29 houses in seven streets (maps/house_plans.py
# gives every lot its own plan). (lot x, y, w, h, door side, storeys, wall style)
HOUSES = [
    ("Northside", 1600, [(25, 2, 8, 8, "s", 1, "timber"), (34, 2, 8, 8, "s", 2, "brick"), (43, 2, 8, 8, "s", 1, "sand"),
                         (70, 2, 8, 8, "s", 1, "timber"), (79, 2, 8, 8, "s", 2, "brick")]),
    ("Crown Row", 3200, [(74, 12, 8, 8, "s", 2, "white"), (83, 12, 8, 8, "s", 2, "sand"), (92, 13, 7, 7, "s", 2, "white"),
                         (89, 23, 8, 8, "n", 2, "sand"), (98, 23, 8, 8, "n", 2, "white")]),
    ("Greenside", 1800, [(2, 27, 8, 8, "e", 1, "timber"), (2, 36, 8, 8, "e", 1, "sand"), (32, 13, 8, 8, "w", 1, "brick"),
                         (32, 22, 8, 8, "w", 1, "timber"), (13, 37, 8, 8, "n", 1, "sand"), (22, 37, 8, 8, "n", 1, "brick")]),
    ("Lantern Row", 1200, [(3, 52, 7, 7, "n", 1, "brick"), (11, 52, 7, 7, "n", 1, "timber"), (19, 52, 7, 7, "n", 1, "sand"),
                           (12, 61, 7, 7, "n", 1, "timber"), (20, 61, 7, 7, "n", 1, "brick"),
                           (12, 71, 7, 7, "n", 1, "sand"), (20, 71, 7, 7, "n", 1, "timber")]),
    ("Southgate Row", 1600, [(22, 84, 8, 8, "n", 2, "sand"), (31, 84, 8, 8, "n", 1, "timber"),
                             (40, 84, 8, 8, "n", 2, "brick")]),
    ("Manor Lane", 1800, [(71, 85, 8, 8, "n", 1, "timber"), (80, 85, 8, 8, "n", 2, "white")]),
    ("Garden Row", 1800, [(101, 62, 8, 8, "w", 1, "sand")]),
]

# what a player should reach quickly; the checker measures each one (the tile in front of the door)
SERVICES = {
    "Stairs to depot + bank (W)": (46, 52), "Stairs to depot + bank (E)": (67, 52), "Priest Odran": (61, 19),
    "Weaponsmith": (41, 40), "Armorer": (41, 45), "General Store": (41, 53), "Quartermaster": (41, 58),
    "Runewright": (72, 41), "Fletcher": (72, 45), "Alchemist": (72, 53), "Tailor": (72, 58),
    "Housewright": (59, 67), "Post Office": (59, 71), "Inn": (54, 67),
    "Ascendancy": (73, 26), "Hunters' Hall": (73, 35), "Guild Hall": (90, 48), "Training Yard": (99, 48),
    "Spire Manor": (85, 64), "Coach Yard": (59, 87), "Underkeep grate": (5, 67),
}
SHOP_GOAL, CROWN_GOAL = 25, 45
CROWN = ("Ascendancy", "Hunters' Hall", "Guild Hall", "Training Yard")
SHOPS = ("Weaponsmith", "Armorer", "General Store", "Quartermaster", "Runewright", "Fletcher", "Alchemist", "Tailor",
         "Housewright", "Post Office", "Inn")
