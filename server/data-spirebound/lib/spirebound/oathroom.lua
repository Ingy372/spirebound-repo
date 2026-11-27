-- The Oathroom: Floor 1's one hand-made group quest (roadmap FD3; design docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.3).
-- Four climbers of level 30 stand on the four oath stones in the Old Quarry and one pulls the lever. Inside (25 minutes,
-- one team at a time): the Captain's hall (hold the line), the Scout's hall (two pairs, four levers), the Keeper's hall
-- (a floor of rune tiles), the Healer's hall (the Oathkeeper and his four braziers), then four chests: each character
-- takes one, once a season. Rules and numbers here; the game side is scripts/spirebound/oathroom.lua; the map is
-- maps/floor1_story.py. Loaded from the end of quests.lua so its quest-log entry is in the catalog.

SpireOathroom = SpireOathroom or {}
local O = SpireOathroom

O.LEVEL = 30
O.TEAM = 4
O.TIME_LIMIT = 25 * 60          -- seconds inside, then everyone is put out
O.HOLD = 180                    -- the Captain's hall: three minutes of waves
O.WAVE_EVERY = 20
O.WAVES = {                      -- the garrison comes down the corridor (existing Floor 1 monsters)
	{ "Ruin Sentinel", "Ruin Archer" },
	{ "Ruin Sentinel", "Ruin Sentinel" },
	{ "Ruin Archer", "Ruin Archer", "Ruin Sentinel" },
}
O.SCOUT_GUARDS = { north_a = "Ruin Sentinel", south_a = "Ruin Sentinel", north_b = "Ruin Archer", south_b = "Ruin Archer" }
O.LEVERS = {                     -- lever -> its carved mark and the gate it opens (each pair opens the other pair's way)
	{ id = "l1", mark = "SUN", opens = "sg1" },
	{ id = "l2", mark = "MOON", opens = "ng1" },
	{ id = "l3", mark = "STAR", opens = "sg2" },
	{ id = "l4", mark = "FLAME", opens = "ng2" },
}
O.CLOSED_AT_START = { "g1", "ng1", "sg1", "ng2", "sg2", "g4" }
O.RUNE_ROWS, O.RUNE_LANES = 9, 5
O.RUNE_HURT = 0.25               -- a wrong rune takes a quarter of your health, never the last point
O.BOSS = "The Oathkeeper"        -- made by tools/gen_monsters.py (Session D); a stand-in is used until it exists
O.BOSS_STANDIN = "The Unfinished"
O.BRAZIER_HEAL = 0.01            -- of his health, per lit brazier, every 2 seconds
O.DOUSE_SECONDS = 3              -- standing beside a brazier this long puts it out...
O.DOUSE_STUN = 4000              -- ...and leaves you out of the fight this long (ms)
O.RELIGHT_EVERY = 40             -- one cold brazier lights again this often
O.KEEPER_GOLD = 10000

O.CHESTS = {
	{ id = "captain", name = "the Captain's chest", text = "one free tier step on a Floor 1 weapon you own" },
	{ id = "scout", name = "the Scout's chest", text = "the Oathbound Pack, a backpack with its own look" },
	{ id = "keeper", name = "the Keeper's chest", text = "10,000 gold" },
	{ id = "healer", name = "the Healer's chest", text = "the Oathkeeper's Mantle, an aura" },
}

-- the quest-log entry: no giver; it starts when you go in and ends when you take a chest
O.QUEST = {
	id = "fd3_oath", floor = 1, side = true, auto = true, kind = "oath", name = "The Oathroom", giver = "the Oathroom",
	storage = 51321, killStorage = 51322, count = 5, minLevel = O.LEVEL, reward = { exp = 0 },
	offer = "",
	step = "A group quest for four climbers of level 30. The way in: the four oath stones just outside the Old Quarry's gate (the First Climb's standing order, chapter 6, tells of it). Four stand on the stones, one pulls the lever.",
	steps = {
		{ text = "The Captain's hall: hold the line for three minutes. Not one of the garrison may get past the marked line behind you." },
		{ text = "The Scout's hall: split into two pairs, north and south. Pull the four levers in the order carved at the entrance (SUN, MOON, STAR, FLAME); each lever opens the other pair's next door." },
		{ text = "The Keeper's hall: read the safe path in the book on the lectern, then walk the rune tiles row by row. Wrong tiles hurt." },
		{ text = "The Healer's hall: defeat the Oathkeeper. He heals from four braziers: stand beside one for a few seconds to put it out." },
		{ text = "The reward room: take one of the four chests (one per character each season). Everyone will see which you chose." },
	},
	report = "Take one of the four chests in the reward room.", thanks = "",
}
O.QUEST.reward.exp = 25000
table.insert(SpireQuests.list, O.QUEST)

-- ---------------------------------------------------------------- pure
-- Pure: may this team go in? tiles = list of 4 entries { level = n } or false (nobody on that stone)
function O.entryCheck(tiles, busy)
	if busy then
		return false, "Another team is inside the oath hall. Wait until they come out (25 minutes at most)."
	end
	local n = 0
	for i = 1, O.TEAM do
		local t = tiles[i]
		if t then
			n = n + 1
			if t.level < O.LEVEL then
				return false, string.format("%s is below level %d. The oath hall opens only for climbers of level %d.", t.name or "Someone", O.LEVEL, O.LEVEL)
			end
		end
	end
	if n < O.TEAM then
		return false, string.format("Four climbers must stand on the four oath stones (%d of 4 are standing).", n)
	end
	return true
end

-- Pure: a random safe path, one lane (1..5) per row, each row at most one lane from the last
function O.makePath(rand)
	local path, lane = {}, rand(1, O.RUNE_LANES)
	for row = 1, O.RUNE_ROWS do
		if row > 1 then
			lane = math.max(1, math.min(O.RUNE_LANES, lane + rand(-1, 1)))
		end
		path[row] = lane
	end
	return path
end

local ORD = { "first", "second", "third", "fourth", "fifth" }
-- Pure: the book on the lectern, in Ione's words
function O.pathText(path)
	local lines = { "From Ione Castellan's record, the Keeper's floor:", "", "Count the stones of each row from the north wall. Step only on these:", "" }
	for row, lane in ipairs(path) do
		table.insert(lines, string.format("Row %d%s: the %s stone.", row, row == 1 and " (by the door)" or "", ORD[lane]))
	end
	table.insert(lines, "")
	table.insert(lines, "Anywhere else, the floor remembers you.")
	return table.concat(lines, "\n")
end

-- Pure: is this step safe? row/lane counted from 1
function O.safe(path, row, lane)
	return path[row] == lane
end

-- Pure: the next lever in the order, given how many are pulled
function O.leverResult(pulled, leverIndex)
	if leverIndex ~= pulled + 1 then
		return "wrong"
	end
	return pulled + 1 == #O.LEVERS and "last" or "next"
end

-- Pure: damage of a wrong rune: a quarter of max health, never the last point
function O.runeDamage(health, maxHealth)
	return math.max(0, math.min(health - 1, math.floor(maxHealth * O.RUNE_HURT)))
end

-- Pure: which chest may this character open? taken = the season of the last chest taken (or nil)
function O.mayTake(clearedThisRun, takenSeason, season)
	if not clearedThisRun then
		return false, "The chests open only for the team that broke the Oathkeeper."
	end
	if takenSeason == season then
		return false, "You have already taken a chest from the oath hall this season."
	end
	return true
end
