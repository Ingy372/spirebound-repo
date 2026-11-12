#!/usr/bin/env python3
"""Writes BESTIARY.md and the in-game hunting guide from the Floor 1 plan and the monster table.

  * maps/floor1_plan.py   where each hunting ground is and what lives there
  * tools/gen_monsters.py what each monster is (health, experience, loot)
  -> BESTIARY.md                                              for Jay (plain English)
  -> server/data-spirebound/lib/spirebound/hunting_guide.lua  the data and rules behind `!hunt` and the NPC hunting advice

Run after changing either source:  python3 tools/gen_bestiary.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))

from floor1_plan import APEX, CAMPS, ROLE_TEXT, TOWN  # noqa: E402
from gen_monsters import MONSTERS  # noqa: E402

XP_RATE = 25  # stage multiplier below level 51 (server/core-overrides/stages.lua, DESIGN.md 5.5)
TOWN_CENTER = (TOWN["x"] + TOWN["w"] // 2, TOWN["y"] + TOWN["h"] // 2)

ITEM_NAMES = {3031: "gold coins", 3035: "platinum coins", 3577: "meat", 3582: "ham", 266: "health potions", 268: "mana potions",
              236: "strong health potions", 3607: "cheese", 5897: "wolf paws", 3294: "short swords", 3286: "maces",
              3361: "leather armor", 3359: "brass armor", 3352: "chain helmets", 3274: "axes", 3447: "arrows", 3350: "bows",
              3355: "leather helmets", 3577 + 0: "meat"}

TIPS = {
    "Field Rat": "Weakest thing in the tower. Perfect for your first three levels.",
    "Hopper Toad": "Hits a little harder than a rat. Still safe for a fresh climber.",
    "Sproutling": "Spits an earth blast from a few tiles away; step up to it and it stops spitting.",
    "Meadow Wasp": "Fast, low health, poisons. Kill it quickly and let the poison wear off.",
    "Bristle Boar": "Straight melee, no tricks. The classic early experience stop. Drops ham: free healing food.",
    "Burrow Mole": "Slow with lots of health. Safe, steady experience if you have patience.",
    "Meadow Wolf": "Comes in packs and fights in a crowd. Fight with your back to a wall.",
    "Grey Alpha": "Leads a wolf pack and calls two wolves when hurt. Worth killing first: the drops are better.",
    "Thornsnap": "Poisons you. Carry a health potion or two, or the Cleanse spell.",
    "Reed Snapper": "Tough shell, slow. It carries more coins than anything else at this level.",
    "Field Shardling": "Hits with energy and shrugs off energy: Arcanist wands do little here. Use fire or melee.",
    "Road Bandit": "Carries coins and gear you can sell. Often in groups of three or four.",
    "Bandit Captain": "A tough leader who calls two bandits. Drops platinum coins. Take friends the first time.",
    "Ruin Sentinel": "Slow, hits hard, takes little damage from plain weapons. Holy damage works best.",
    "Ruin Archer": "Keeps its distance and shoots. Close the gap or fight around corners.",
    "Stonehorn Ram": "Charges in a straight line: watch for the warning on the ground and step aside.",
}

DIRS = ["east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"]


def need(level: int) -> int:
    """Experience needed to reach `level` (the standard formula)."""
    return round(50 * (level ** 3 - 6 * level ** 2 + 17 * level - 12) / 3)


def direction(x: int, y: int) -> str:
    """Compass direction and walking distance from the middle of Hearthgate to a spot (map y grows downward)."""
    import math
    dx, dy = x - TOWN_CENTER[0], y - TOWN_CENTER[1]
    ang = math.degrees(math.atan2(dy, dx)) % 360
    name = DIRS[int(((ang + 22.5) % 360) // 45)]
    steps = int(round(max(abs(dx), abs(dy)) / 10.0)) * 10
    return f"{name}, about {steps} steps from the city centre"


def kills_per_level(level: int, xp: int) -> float:
    return (need(level + 1) - need(level)) / (xp * XP_RATE)


def loot_line(mon: dict) -> str:
    out = []
    for iid, chance, maxc in mon.get("loot", []):
        name = ITEM_NAMES.get(iid, f"item {iid}")
        if iid == 3031:
            out.append(f"gold (up to {maxc})")
        elif chance >= 20000:
            out.append(f"{name} ({chance // 1000}%)")
        elif chance >= 3000:
            out.append(f"{name} (rare, {chance / 1000:.0f}%)")
    return ", ".join(out) or "nothing of note"


def build_ladder() -> list[dict]:
    rows = []
    for c in CAMPS:
        monsters = [m for m, _, _ in c["mix"]]
        cx, cy = c["x"] + c["w"] // 2, c["y"] + c["h"] // 2
        rows.append(dict(id=c["id"], title=c["title"], lo=c["levels"][0], hi=c["levels"][1], role=c["role"], monsters=monsters,
                         where=direction(cx, cy), note=c["note"], zone=c["zone"], area=c["w"] * c["h"]))
    ax, ay = 30 + 22, 30 + 22
    rows.append(dict(id=APEX["id"], title=APEX["title"], lo=APEX["levels"][0], hi=APEX["levels"][1], role="xp+money",
                     monsters=["Stonehorn Ram"], where=direction(ax, ay), note=APEX["note"], zone="contested", area=44 * 44))
    return sorted(rows, key=lambda r: (r["lo"], r["hi"]))


def lua_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_lua(ladder: list[dict]) -> None:
    out = ["-- GENERATED by tools/gen_bestiary.py from maps/floor1_plan.py. Do not edit by hand.",
           "-- The hunting ladder for Floor 1: which ground suits which level, and the advice players are given.",
           "SpireHunt = { floor = 1, camps = {"]
    for r in ladder:
        mons = ", ".join(lua_string(m) for m in r["monsters"])
        out.append(f"\t{{ id = {lua_string(r['id'])}, title = {lua_string(r['title'])}, lo = {r['lo']}, hi = {r['hi']}, role = {lua_string(r['role'])}, "
                   f"zone = {lua_string(r['zone'])}, monsters = {{ {mons} }}, where = {lua_string(r['where'])}, note = {lua_string(r['note'])} }},")
    out.append("} }")
    out.append(LUA_RULES)
    (ROOT / "server" / "data-spirebound" / "lib" / "spirebound" / "hunting_guide.lua").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


LUA_RULES = '''
-- Pure: what to hunt at `level`. Returns { xp = camp or nil, money = camp or nil, next = camp or nil, beyond = bool }.
-- xp: the best experience ground you are ready for (the hardest camp whose range includes your level).
-- money: the best coin ground for your level. next: the first ground you have not reached yet.
function SpireHunt.recommend(level)
	local best = { xp = nil, money = nil, next = nil, beyond = false }
	local top = 0
	for _, c in ipairs(SpireHunt.camps) do
		top = math.max(top, c.hi)
		if level >= c.lo and level <= c.hi then
			local slot = (c.role == "money") and "money" or "xp"
			if not best[slot] or c.lo > best[slot].lo then
				best[slot] = c
			end
			if c.role == "xp+money" then
				if not best.money or c.lo > best.money.lo then
					best.money = c
				end
			end
		elseif c.lo > level and (not best.next or c.lo < best.next.lo) then
			best.next = c
		end
	end
	best.beyond = level > top
	return best
end

local function describe(c)
	return string.format("%s (%s, levels %d-%d): %s", table.concat(c.monsters, " and "), c.title, c.lo, c.hi, c.where)
end

-- Pure: the advice text for a level
function SpireHunt.advice(level)
	local r = SpireHunt.recommend(level)
	local parts = {}
	if r.beyond then
		return "You have outgrown Floor 1's hunting grounds. The Old Watchtower is still rewarding, the Underkeep hides stronger prey, and the Gate Hound and the Axe-Lord stand between you and Floor 2."
	end
	if level < 5 then
		table.insert(parts, "Start with " .. describe(r.xp or SpireHunt.camps[1]) .. ".")
	elseif r.xp then
		table.insert(parts, "For experience: " .. describe(r.xp) .. ".")
	end
	if r.money then
		table.insert(parts, "For money: " .. describe(r.money) .. ".")
	end
	if r.next then
		table.insert(parts, string.format("Next step at level %d: %s.", r.next.lo, describe(r.next)))
	end
	if #parts == 0 then
		table.insert(parts, "Try the grounds around Hearthgate.")
	end
	return table.concat(parts, " ")
end
'''


def write_md(ladder: list[dict]) -> None:
    L = []
    L.append("# Spirebound Bestiary: Floor 1, Hearthgate Plains\n")
    L.append("*Generated by `python3 tools/gen_bestiary.py` from `maps/floor1_plan.py` and `tools/gen_monsters.py`. Do not edit by hand: change the plan or the monster table and rerun.*\n")
    L.append("## How a climber moves through Floor 1\n")
    L.append("Floor 1 is a ladder. Each hunting ground is one step. You stay until levelling slows down, then walk to the next step. "
             "Two kinds of ground exist side by side:\n")
    L.append("- **Experience grounds** give the fastest levels for their range.\n"
             "- **Money grounds** give less experience but drop more coins and gear you can sell.\n")
    L.append("Level ranges overlap on purpose, so there is always a choice. Type `!hunt` in game (or ask Innkeeper Bess, Hunter Brannoch, "
             "Merchant Wenna or Guide Pell about hunting) and you are told where to go for your level.\n")
    L.append("**Safety rings.** The four starter grounds and the roads around the city are *Guarded*: players cannot attack each other there. "
             "Everything beyond is *Open*. The Old Watchtower is *Contested*, with fights between players allowed.\n")
    L.append(f"**Numbers.** Experience below level 51 is multiplied by {XP_RATE} (DESIGN.md 5.5), so a monster listed with 40 experience gives {40 * XP_RATE}. "
             "\"Kills per level\" below says how many kills one level costs at the start and at the end of the range.\n")

    L.append("## The ladder, step by step\n")
    L.append("| # | Level | Ground | Role | Monsters | Where |")
    L.append("|---|---|---|---|---|---|")
    for i, r in enumerate(ladder, 1):
        L.append(f"| {i} | {r['lo']}-{r['hi']} | **{r['title']}** | {ROLE_TEXT[r['role']]} | {', '.join(r['monsters'])} | {r['where']} |")
    L.append("")
    L.append("### The suggested route\n")
    L.append("1. **Level 1 to 4, the Ratwarren.** Fight rats just outside the west gate. A few kills and you are level 4.")
    L.append("2. **Level 3 to 10, Toad Pond and Sproutling Glade.** Toads east of the city, sproutlings south. Still inside the safe ring.")
    L.append("3. **Level 7 to 12, Waspgrass Fields.** The first ground north of the gate. Captain Dorrow has a quest for it.")
    L.append("4. **Level 9 to 16, Boar Meadow and Burrow Hills.** Boars are the classic experience stop; moles are slower but sturdier. "
             "From here on, other players can attack you. Walk with friends.")
    L.append("5. **Level 12 to 20, Wolf Copse, Thornsnap Hollow, Reedmarsh.** Wolves and thornsnaps for experience, snappers for your first real coins. "
             "Hunter Brannoch's quests start here.")
    L.append("6. **Level 17 to 27, Shard Fields and the Bandit Road.** Shardlings are the experience step. Bandits are the money step: coins, gear and platinum from the captains.")
    L.append("7. **Level 23 to 30, the Old Quarry.** The toughest ordinary ground on the floor. Sentinels and archers guard it.")
    L.append("8. **Level 28 to 40, the Old Watchtower.** The apex spawn: good experience and money long after you could leave Floor 1, with other players fighting for it.")
    L.append("9. **Around level 20 to 30, the Gate Hound at the Pass.** Its fall opens the labyrinth. Then the labyrinth, then the Axe-Lord of the Stair, whose first defeat opens Floor 2 for everyone.\n")

    L.append("## Hunting grounds in detail\n")
    for r in ladder:
        L.append(f"### {r['title']}  (levels {r['lo']}-{r['hi']}, {ROLE_TEXT[r['role']]})")
        L.append(f"*{r['where']}. Safety: {r['zone']}.*\n")
        L.append(r["note"] + "\n")
        L.append("| Monster | Health | Experience | Kills per level (start / end) | Drops |")
        L.append("|---|---|---|---|---|")
        for name in r["monsters"]:
            mon = MONSTERS[name]
            k1 = kills_per_level(r["lo"], mon["xp"])
            k2 = kills_per_level(r["hi"], mon["xp"])
            L.append(f"| {name} | {mon['hp']} | {mon['xp']} | {k1:.0f} / {k2:.0f} | {loot_line(mon)} |")
        L.append("")
        for name in r["monsters"]:
            if name in TIPS:
                L.append(f"- **{name}:** {TIPS[name]}")
        L.append("")

    L.append("## Bosses and secrets on Floor 1\n")
    L.append("- **Gate Hound** (field boss, the Pass, north): three heads, howls that scare you every 20 seconds, calls wolves at half health. Its first defeat opens the labyrinth for everyone.")
    L.append("- **Axe-Lord of the Stair** (floor boss, top of the labyrinth): marked-tile cleaves; at 60% he calls captains; below 25% he draws a long curved blade with a three-tile line attack. His first defeat opens Floor 2.")
    L.append("- **Old Tusk** (secret boss, hidden in the Boar Meadow): a huge boar that charges. Found through a secret.")
    L.append("- **The Underkeep** (hidden under Hearthgate, behind the drain grate in the south-west corner of the city): tuned for Floor 2 levels; do not enter early.\n")

    L.append("## Every monster at a glance\n")
    L.append("| Monster | Health | Experience | Found at |")
    L.append("|---|---|---|---|")
    seen = []
    for r in ladder:
        for name in r["monsters"]:
            if name not in seen:
                seen.append(name)
                mon = MONSTERS[name]
                where = ", ".join(x["title"] for x in ladder if name in x["monsters"])
                L.append(f"| {name} | {mon['hp']} | {mon['xp']} | {where} |")
    L.append("")
    L.append("## How the progression rules work (for the developers)\n")
    L.append("- The ladder lives in `maps/floor1_plan.py`. The map builder draws each ground at its position and places its monsters "
             "(about one monster per 30 tiles, in groups of at most nine, never closer than eight tiles apart).")
    L.append("- `tools/gen_bestiary.py` turns the same data into this file and into `lib/spirebound/hunting_guide.lua`.")
    L.append("- In game, `SpireHunt.recommend(level)` picks the hardest experience ground and the hardest money ground whose level range includes the player, "
             "plus the next ground to aim for. `!hunt` and several NPCs use it.")
    L.append("- Later floors follow the same recipe: one plan file per floor, camps in level order, an apex spawn, a field boss and a floor boss.")
    (ROOT / "BESTIARY.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    ladder = build_ladder()
    write_lua(ladder)
    write_md(ladder)
    print(f"wrote BESTIARY.md and hunting_guide.lua ({len(ladder)} hunting grounds)")


if __name__ == "__main__":
    main()
