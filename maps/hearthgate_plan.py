"""Hearthgate v4 (docs/design/hearthgate_v4_plan.md, 2026-11-27): the tile plan, in one place.

Read by the builder (maps/hearthgate.py) and by the checker (tools/hearthgate_plan_check.py), so the two can never
disagree. Coordinates are town-relative: x 0..111 west to east, y 0..95 north to south (the town's top-left corner is
TOWN in maps/floor1_plan.py). Rectangles are (x, y, w, h) and include their walls. Doors are the doorway tile.

Why the shops sit where they do: from the Hearthstone a door must be at most 25 steps away (Jay's goal: short walks).
On a 33-tile plaza that only works where the four avenues leave it, so every shop building stands at an avenue's
mouth with its doors on the plaza side. The Crown Quarter (45 steps) hugs the street along the Hearth's east wall.
"""

W, H = 112, 96
CUT = 12                         # the wall's corners are cut off this far: an eight-sided city
GATES = {"n": [(x, 0) for x in range(55, 59)], "s": [(x, 95) for x in range(55, 59)],
         "w": [(0, y) for y in range(48, 51)], "e": [(111, y) for y in range(48, 51)]}

HEARTHSTONE = (56, 49)           # spawn and respawn point, in the open air at the plaza's centre (temple_hearthgate)
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


# ------------------------------------------------------------------ streets (painted after the cobble fill)
# marble 409 = the avenues and the plaza, flagstone 416 = the high roads, cobble 870 = everything else
STREETS = {
    "North Avenue": ((55, 1, 4, 11), 409),           # north gate to the Hearth's north archway
    "South Avenue": ((55, 65, 4, 30), 409),          # plaza to the south gate
    "West High Road": ((1, 48, 40, 3), 416),
    "East High Road": ((73, 48, 38, 3), 416),
    "North Lane": ((3, 10, 106, 2), 870),            # behind the Hearth: the Northside doors
    "Hearth West Street": ((40, 12, 2, 26), 870),
    "Hearth East Street": ((72, 12, 2, 27), 870),    # the Crown Quarter's doors open onto it
    "Crown Lane": ((86, 20, 23, 3), 870),            # between the two rows of Crown Row
    "Green Lane": ((10, 12, 2, 36), 870),            # Greenside's west houses
    "Lantern Lane": ((2, 59, 26, 2), 870),
    "Lantern Close": ((11, 68, 17, 3), 870),
    "Lantern Cut": ((27, 51, 3, 30), 870),           # north-south through Lantern Row
    "Southgate Lane": ((10, 81, 45, 3), 870),
    "Coach Lane": ((59, 75, 20, 3), 870),
    "Manor Walk": ((93, 51, 3, 12), 409),            # East High Road to the manor gate
}

# ------------------------------------------------------------------ the Hearth: the great hall on the plaza's north side
HEARTH = (42, 12, 30, 23)        # interior x 43..70, y 13..33; three levels
HEARTH_ARCHES = [(56, 12), (57, 12)] + [(x, 34) for x in range(55, 59)] + [(42, y) for y in (22, 23, 24)] + \
                [(71, y) for y in (22, 23, 24)]
HEARTH_TOWER = (49, 18, 16, 11)  # level 3, the Hall of Climbers
# the hall's four rooms: the bank (south-west) and a depot wing (south-east) are nearest the front archway; the second
# depot wing (north-west) and the chapel (north-east) are behind them
DEPOT_BOOTHS = [(61, 25, "s"), (61, 33, "n"), (44, 13, "s"), (44, 21, "n")]    # five booths each: 20 lockers
GALLERY_BOOTHS = [(44, 13, "s"), (61, 13, "s")]
HEARTH_STAIRS = {"hearth_west": (43, 17, 7), "hearth_east": (70, 29, 7), "hearth_hall": (62, 26, 6)}
BANK_COUNTER = (51, 26, 7)       # a vertical counter: the keepers stand west of it, customers east, beside the aisle
BANK_NPCS = {"Broker Nell": (50, 27), "Banker Tolliver": (50, 29), "Trader Osric": (50, 31)}
HEARTH_POINTS = {"depot_hearthgate": (64, 29), "hearth_bank": (52, 29), "hearth_trader": (52, 31), "trade_hall": (52, 30),
                 "shop_bank": (52, 29)}
PRIEST = (61, 19)

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
MANOR_GROUNDS = dict(rect=(80, 63, 28, 22), gate=[(93, 63), (94, 63), (95, 63)])
MANOR_AT = (83, 67)              # maps/manor.py lays the 22 x 16 house here; its door is at (94, 67)
SPIRE_GARDENS = (84, 52, 26, 9)  # a public garden between the East High Road and the manor's grounds

# ------------------------------------------------------------------ yards and green places
COACH_YARD = dict(rect=(60, 82, 10, 11), gap=(60, 87), ferro=(64, 87), carriage=(64, 86))
OLD_WELL = (2, 62, 9, 9)         # the Underkeep grate stays at (5, 66): the Underkeep's exit lands at (5, 68)
GRATE = (5, 66)
GREEN = (12, 13, 18, 21)         # Hearthgate Green, with its pond
POCKET_GARDEN = (49, 84, 5, 9)

# ------------------------------------------------------------------ 30 houses in six streets (maps/house_plans.py
# gives every lot its own plan). (lot x, y, w, h, door side, storeys, wall style)
HOUSES = [
    ("Northside", 1600, [(14, 2, 8, 8, "s", 1, "timber"), (23, 2, 8, 8, "s", 2, "brick"), (32, 2, 8, 8, "s", 1, "sand"),
                         (41, 2, 8, 8, "s", 1, "timber"), (70, 2, 8, 8, "s", 1, "sand"), (79, 2, 8, 8, "s", 2, "timber"),
                         (88, 2, 8, 8, "s", 1, "brick")]),
    ("Crown Row", 3200, [(74, 12, 8, 8, "s", 2, "white"), (83, 12, 8, 8, "s", 2, "sand"), (92, 12, 8, 8, "s", 2, "white"),
                         (101, 12, 8, 8, "s", 2, "timber"), (89, 23, 8, 8, "n", 2, "sand"), (98, 23, 8, 8, "n", 2, "white")]),
    ("Greenside", 1800, [(2, 13, 8, 8, "e", 1, "timber"), (2, 22, 8, 8, "e", 1, "sand"), (2, 31, 8, 8, "e", 1, "timber"),
                         (32, 13, 8, 8, "w", 1, "brick"), (32, 22, 8, 8, "w", 1, "timber"), (13, 37, 8, 8, "n", 1, "sand")]),
    ("Lantern Row", 1200, [(3, 52, 7, 7, "n", 1, "brick"), (11, 52, 7, 7, "n", 1, "timber"), (19, 52, 7, 7, "n", 1, "sand"),
                           (12, 61, 7, 7, "n", 1, "timber"), (20, 61, 7, 7, "n", 1, "brick"),
                           (12, 71, 7, 7, "n", 1, "sand"), (20, 71, 7, 7, "n", 1, "timber")]),
    ("Southgate Row", 1600, [(13, 84, 8, 8, "n", 1, "brick"), (22, 84, 8, 8, "n", 2, "sand"), (31, 84, 8, 8, "n", 1, "timber"),
                             (40, 84, 8, 8, "n", 2, "brick")]),
]

# ------------------------------------------------------------------ the plaza
MONUMENT = (49, 42)              # hero statue; its sign below it; point "monument" one tile south
BEACON_BOWLS = [(62, 42), (64, 42), (66, 42), (68, 42)]
ARENA_STATUE = (49, 56)
FOUNTAIN = (64, 56)
VESPER = (59, 53)
NOTICE_BOARD = (53, 45)
STALLS = [(43, 44), (43, 54), (67, 46), (67, 53), (47, 61), (63, 61)]     # free trading stalls, 3 counters each

# what a player should reach quickly; the checker measures each one (the tile in front of the door)
SERVICES = {
    "Depot (nearest locker)": None, "Bank counter": (52, 29), "Trader Osric": (52, 31), "Priest Odran": (61, 20),
    "Weaponsmith": (41, 40), "Armorer": (41, 45), "General Store": (41, 53), "Quartermaster": (41, 58),
    "Runewright": (72, 41), "Fletcher": (72, 45), "Alchemist": (72, 53), "Tailor": (72, 58),
    "Housewright": (59, 67), "Post Office": (59, 71), "Inn": (54, 67),
    "Ascendancy": (73, 26), "Hunters' Hall": (73, 35), "Guild Hall": (90, 48), "Training Yard": (99, 48),
    "Spire Manor": (94, 66), "Coach Yard": (59, 87), "Underkeep grate": (5, 67),
}
SHOP_GOAL, CROWN_GOAL = 25, 45
CROWN = ("Ascendancy", "Hunters' Hall", "Guild Hall", "Training Yard")
SHOPS = ("Weaponsmith", "Armorer", "General Store", "Quartermaster", "Runewright", "Fletcher", "Alchemist", "Tailor",
         "Housewright", "Post Office", "Inn")
