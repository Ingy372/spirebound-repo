"""Real walking directions from the Hearthstone to every Floor 1 hunting ground (roadmap G9, Grok session 3).

The old `!hunt` directions were a straight compass line from the nearest town gate to the middle of the ground's gate
side: "south gate, then about 30 steps west" ended at a river for a Ranger and in forest for a Vanguard, and Toad Pond
wasn't found in 18 minutes. This module finds the path a player really walks (roads preferred, through the town gate,
round water and forest), on the finished map, and turns it into a few legs a person can follow:

    leave Hearthgate by the south gate, follow the road south about 20 steps, then west about 35 steps,
    then south about 10 steps to its north entrance

It also puts a signpost beside every turn ("Toad Pond: north-east"), and writes:
  * maps/hunt_routes.json            (read by tools/gen_bestiary.py for the `!hunt` text and BESTIARY.md)
  * maps/hunt_signposts.json         (where each signpost stands and what it says, for checking)
  * tools/autopilot_routes/g9_hunt_routes.json   (walks every route from the temple through its turns, on foot)

run(m) is called by tools/mapgen.py after the walk test, so edges and whole objects are already in place.
"""
from __future__ import annotations

import heapq
import json
import math
from pathlib import Path

import wilds
from floor1_plan import TOWN, APEX, CAMPS

ROOT = Path(__file__).resolve().parent.parent
X0, Y0, Z = 1000, 1000, 7
DIRS = ["east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"]
D8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
SIDE_NAMES = {"n": "north", "s": "south", "e": "east", "w": "west"}
ROAD_COST, OFF_ROAD_COST, DIAGONAL = 1.0, 2.5, 1.5   # roads are what a new player follows; Tibia's diagonal step is slow
MIN_LEG = 6                                          # shorter wiggles are folded into the next leg
MAX_LEGS = 4


def compass(dx: float, dy: float) -> str:
    ang = math.degrees(math.atan2(dy, dx)) % 360
    return DIRS[int(((ang + 22.5) % 360) // 45)]


def town_rect():
    return (X0 + TOWN["x"], Y0 + TOWN["y"], X0 + TOWN["x"] + TOWN["w"] - 1, Y0 + TOWN["y"] + TOWN["h"] - 1)


def in_town(p) -> bool:
    x0, y0, x1, y1 = town_rect()
    return x0 <= p[0] <= x1 and y0 <= p[1] <= y1


def exit_side(p) -> str:
    """Which side of Hearthgate's wall a path leaving town at p goes through."""
    x0, y0, x1, y1 = town_rect()
    d = {"west": abs(p[0] - x0), "east": abs(p[0] - x1), "north": abs(p[1] - y0), "south": abs(p[1] - y1)}
    return min(d, key=d.get)


def dijkstra(m, start, block):
    """Cheapest walk from start to every reachable Floor 1 surface tile. Returns the previous-tile map."""
    roads = getattr(m, "road_tiles", set())
    lim = (X0, Y0, X0 + 400, Y0 + 400)
    dist, prev = {start: 0.0}, {start: None}
    todo = [(0.0, start)]
    while todo:
        d, p = heapq.heappop(todo)
        if d > dist.get(p, 1e18):
            continue
        for a, b in D8:
            q = (p[0] + a, p[1] + b, Z)
            if not (lim[0] <= q[0] < lim[2] and lim[1] <= q[1] < lim[3]):
                continue
            if not wilds.walkable(m, q, block):
                continue
            if a and b and not (wilds.walkable(m, (p[0] + a, p[1], Z), block) and wilds.walkable(m, (p[0], p[1] + b, Z), block)):
                continue                                   # no squeezing between two blocked corners
            step = ROAD_COST if q in roads else OFF_ROAD_COST
            nd = d + step * (DIAGONAL if a and b else 1.0)
            if nd < dist.get(q, 1e18):
                dist[q], prev[q] = nd, p
                heapq.heappush(todo, (nd, q))
    return prev


def backtrack(prev, goal):
    if goal not in prev:
        return None
    out, p = [], goal
    while p is not None:
        out.append(p)
        p = prev[p]
    return out[::-1]


def rdp(points, eps):
    """Ramer-Douglas-Peucker: the few corners that matter on a long wiggly path."""
    if len(points) < 3:
        return list(points)
    (x1, y1), (x2, y2) = points[0][:2], points[-1][:2]
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    best, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        x, y = points[i][:2]
        d = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / L
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [points[0], points[-1]]
    return rdp(points[:idx + 1], eps)[:-1] + rdp(points[idx:], eps)


def steps_between(path, i, j):
    return j - i


def legs_for(path, roads):
    """Split the part of the path outside town into at most MAX_LEGS legs: (compass, steps, on_road, turn_tile)."""
    k = next((i for i, p in enumerate(path) if not in_town(p)), None)
    if k is None:
        return None, []
    side = exit_side(path[k])
    rest = path[k:]
    idx = {p: i for i, p in enumerate(rest)}
    for eps in (3, 5, 8, 12, 20, 40):
        corners = rdp(rest, eps)
        legs = []
        for a, b in zip(corners, corners[1:]):
            ia, ib = idx[a], idx[b]
            seg = rest[ia:ib + 1]
            road = sum(1 for p in seg if p in roads) >= 0.6 * len(seg)
            legs.append([compass(b[0] - a[0], b[1] - a[1]), ib - ia, road, b])
        merged = []
        for leg in legs:                               # same heading twice in a row: one leg
            if merged and merged[-1][0] == leg[0]:
                merged[-1][1] += leg[1]
                merged[-1][2] = merged[-1][2] or leg[2]
                merged[-1][3] = leg[3]
            else:
                merged.append(leg)
        while len(merged) > 1 and min(l[1] for l in merged) < MIN_LEG:
            i = min(range(len(merged)), key=lambda n: merged[n][1])
            j = i + 1 if i + 1 < len(merged) else i - 1  # fold a tiny leg into its neighbour
            merged[j][1] += merged[i][1]
            if j > i:
                pass
            else:
                merged[j][3] = merged[i][3]
            del merged[i]
        if len(merged) <= MAX_LEGS:
            return side, merged
    return side, merged


def fine_turns(path, roads):
    """The places outside town where a player could take the wrong way: where the route turns while the road carries on
    straight ahead (a fork), or where it steps off the road. Returns [tile, compass of the next stretch] for each.
    A road that simply bends needs no sign: you follow it."""
    k = next((i for i, p in enumerate(path) if not in_town(p)), None)
    if k is None:
        return []
    rest = path[k:]
    on_path = set(rest)
    idx = {p: i for i, p in enumerate(rest)}
    corners = rdp(rest, 1.5)
    out = []

    def unit(v):
        return (v > 0) - (v < 0)

    def next_heading(i):
        j = min(i + 8, len(rest) - 1)
        return compass(rest[j][0] - rest[i][0], rest[j][1] - rest[i][1])

    near_path = {(p[0] + a, p[1] + b, Z) for p in rest for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2)}

    def other_road(c):
        """Road tiles 3-6 steps from c that the route does not use: another branch leaves here."""
        n = 0
        for a in range(-6, 7):
            for b in range(-6, 7):
                if max(abs(a), abs(b)) < 3:
                    continue
                t = (c[0] + a, c[1] + b, Z)
                if t in roads and t not in near_path:
                    n += 1
        return n >= 4

    for c in corners[:-1]:                             # the gate exit and every bend
        i = idx[c]
        leaves = c in roads and all(q not in roads for q in rest[i + 1:i + 4])
        if other_road(c) or leaves:
            out.append([list(c), next_heading(i)])
    # the last stretch from the road to the ground's gate: a sign where the route leaves the road for good
    last_road = max((i for i, p in enumerate(rest) if p in roads), default=None)
    if last_road is not None and len(rest) - 1 - last_road >= 4:
        out.append([list(rest[last_road]), next_heading(last_road)])
    merged = []
    for t, h in out:                                   # one sign per place
        if merged and max(abs(merged[-1][0][0] - t[0]), abs(merged[-1][0][1] - t[1])) <= 5:
            merged[-1][1] = h
        else:
            merged.append([t, h])
    return merged


def round_steps(n: int) -> int:
    return max(5, int(round(n / 5.0)) * 5)


def describe(side, legs, door):
    parts = [f"leave Hearthgate by the {side} gate"]
    for i, (heading, n, road, _t) in enumerate(legs):
        what = f"follow the road {heading}" if road else f"walk {heading}"
        parts.append(("then " if i else "") + f"{what} about {round_steps(n)} steps")
    text = ", ".join(parts)
    return f"{text} to {door}"


def grounds(m):
    """(id, title, entrance tiles, side word) for every ground and the apex."""
    by_id = {c["id"]: c for c in CAMPS}
    out = []
    for L in getattr(m, "wilds", []):
        c = by_id.get(L["id"], {})
        side = SIDE_NAMES.get(c.get("gate"))
        out.append((L["id"], c.get("title", L["id"]), [(x, y, Z) for x, y in L["gate"]], side))
    ax, ay = m.points["apex_watchtower"][0] - 22, m.points["apex_watchtower"][1] - 40
    out.append((APEX["id"], APEX["title"], [(ax + 22, ay + 43, Z), (ax + 23, ay + 43, Z)], "south"))
    return out


def sign_spot(m, block, turn, avoid, roads):
    """A free open tile next to a turn: walkable, not a road, not on any route, nothing on it."""
    tx, ty = turn[0], turn[1]
    for r in (1, 2, 3):
        for a in range(-r, r + 1):
            for b in range(-r, r + 1):
                if max(abs(a), abs(b)) != r:
                    continue
                q = (tx + a, ty + b, Z)
                if q in avoid or q in roads or in_town(q) or m.items.get(q):
                    continue
                if not wilds.walkable(m, q, block):
                    continue
                # keep it out of narrow places: every neighbour walkable, so a sign never closes a gap
                if all(wilds.walkable(m, (q[0] + c, q[1] + d, Z), block) for c, d in D8):
                    return q
    return None


def run(m, write=True):
    """write=False: place the signposts only (tools/maprender.py, so renders show what the game has)."""
    block = wilds.blockers()
    roads = getattr(m, "road_tiles", set())
    start = tuple(m.points["temple_hearthgate"])
    prev = dijkstra(m, start, block)
    routes, problems, all_paths, paths_by = {}, [], set(), {}
    for gid, title, gate, side_word in grounds(m):
        ends = [g for g in gate if g in prev]
        if not ends:
            problems.append(f"{gid}: no walking path from the Hearthstone to its gate")
            continue
        paths = [backtrack(prev, g) for g in ends]
        path = min(paths, key=len)
        exit_gate, legs = legs_for(path, roads)
        door = f"its {side_word} entrance" if side_word else "it"
        text = describe(exit_gate, legs, door)
        turns = [list(l[3]) for l in legs[:-1]]       # where a new leg starts (the autopilot walks through these)
        forks = fine_turns(path, roads)               # every bend the path takes outside town: the signposts go here
        routes[gid] = dict(title=title, text=text, exit=exit_gate, legs=[[l[0], round_steps(l[1]), l[2]] for l in legs],
                           turns=turns, forks=forks, gate=list(path[-1]), steps=len(path) - 1,
                           via=[list(p) for p in path[30:-5:30]])         # stops every 30 steps along the same path

        all_paths.update(path)
        paths_by[gid] = path
    # signposts at the forks, one per place (forks within 3 tiles share a sign); each names every ground whose route
    # passes within 2 tiles of it, with the way that route goes on from there
    posts = []
    for gid, r in routes.items():
        for t, _heading in r["forks"]:
            if not any(max(abs(p["at"][0] - t[0]), abs(p["at"][1] - t[1])) <= 3 for p in posts):
                posts.append(dict(at=t, lines=[]))
    for p in posts:
        for gid, path in paths_by.items():
            hits = [i for i, q in enumerate(path) if max(abs(q[0] - p["at"][0]), abs(q[1] - p["at"][1])) <= 2]
            if not hits:
                continue
            i = hits[-1]
            j = min(i + 8, len(path) - 1)
            if j == i:
                continue
            p["lines"].append(f"{routes[gid]['title']}: {compass(path[j][0] - path[i][0], path[j][1] - path[i][1])}")
    placed, signs = 0, []
    for p in posts:
        q = sign_spot(m, block, p["at"], all_paths, roads)
        if q is None:
            problems.append(f"no room for a signpost near {tuple(p['at'])}")
            continue
        text = "Hunting grounds. " + ". ".join(sorted(p["lines"])) + "."
        m.sign(q[0], q[1], Z, text)
        signs.append(dict(at=list(q), text=text))
        placed += 1
    if not write:
        return routes, placed, problems
    (ROOT / "maps" / "hunt_routes.json").write_text(json.dumps(routes, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                                                     newline="\n")
    (ROOT / "maps" / "hunt_signposts.json").write_text(json.dumps(signs, indent=1) + "\n", encoding="utf-8", newline="\n")
    write_autopilot(routes, start)
    write_autopilot(routes, start, only=["apex_watchtower"])   # the longest route on its own, for a quick rerun
    return routes, placed, problems


def write_autopilot(routes, start, only=None):
    """One autopilot route that walks each `!hunt` direction from the temple: through every turn to the ground's gate,
    on foot. Between grounds it jumps back to the temple (getting back is not part of a direction)."""
    steps = [{"do": "say", "text": "/pilot level 40", "note": "strong enough not to stop and fight on the way"},
             {"do": "wait", "seconds": 1}]
    for gid in sorted(routes, key=lambda g: routes[g]["steps"]):
        if only and gid not in only:
            continue
        r = routes[gid]
        steps.append({"do": "jump", "to": list(start), "note": f"back to the temple: start of the {r['title']} route"})
        steps.append({"do": "wait", "seconds": 2})
        for t in r["via"]:                           # the client walks only so far in one go: every 30 steps of the path
            steps.append({"do": "walk", "to": t, "fight": False, "timeout": 120, "note": f"{r['title']}: on the way"})
        steps.append({"do": "walk", "to": r["gate"], "fight": False, "timeout": 120, "note": f"{r['title']}: arrived at the gate"})
        steps.append({"do": "shot", "name": f"g9_{gid}"})
    steps.append({"do": "jump", "to": list(start)})
    steps.append({"do": "say", "text": "/pilot level 12"})
    steps.append({"do": "say", "text": "/pilot logout"})
    name = "g9_hunt_routes" if not only else "g9_" + "_".join(only)
    route = {"name": name, "character": "Pilot Ranger", "timeout": 2400,
             "about": "G9: walks every !hunt direction from the temple, through each turn, to the ground's gate, on foot. "
                      "Generated by maps/hunt_routes.py; do not edit by hand.",
             "steps": steps}
    (ROOT / "tools" / "autopilot_routes" / f"{name}.json").write_text(json.dumps(route, indent=1) + "\n",
                                                                             encoding="utf-8", newline="\n")
