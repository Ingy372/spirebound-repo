-- The First Climb: Floor 1's story (roadmap FD1; design docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.1).
-- Eight chapters from Archivist Maren at the Monument follow the first company up Floor 1 and end on the Axe-Lord.
-- Each chapter is a quest in SpireQuests.list (kind = "chapter"), so it gets a quest-log line from the generic
-- catalog; its steps are kept in the quest's killStorage (0 = first step). Loaded from the end of quests.lua so the
-- chapters are in the list before the client's quest catalog is built (lib/core/load.lua).
-- The game side (objects in the world, reading records, the NPC lines): scripts/spirebound/first_climb.lua.
-- Story text never gives away a secret's place (Jay's riddle rule, DESIGN 8.1): only quest places are named.

SpireFirstClimb = SpireFirstClimb or {}

SpireFirstClimb.PREMISE = "The Spire is older than anyone's records, and every tale agrees on one thing: at its summit waits the Summit Wish, one wish, granted to whoever reaches it. Nobody is trapped here. Everyone who walks through the gate came by choice, to win it. Hearthgate is the camp that grew at the foot of the stair."

SpireFirstClimb.GIVER = "Archivist Maren"
SpireFirstClimb.TITLE = "Heir to the First Climb"
SpireFirstClimb.REPORT = "Return to Archivist Maren at the Monument in Hearthgate's plaza and say 'report'."

-- ---------------------------------------------------------------- records (readable items the player keeps)
-- chain = given by a chapter; loose = lying in the world for explorers (no riddle, no purse: lore and a row)
SpireFirstClimb.RECORDS = {
	{ id = "tally", name = "the Quartermaster's Tally", item = 2818, chain = true,
		text = "THE QUARTERMASTER'S TALLY (copied from three supply stones)\n\nFirst camp: forty-one climbers, forty-one packs. Water good. Rats in the grain already.\n\nSecond camp: rope, two hundred lengths. Lamp oil, eleven casks. Captain Vane says carry less, climb faster.\n\nThird camp: bread to come from the mill at Millcross, every tenth day, paid in advance. The miller's girl keeps the book." },
	{ id = "ledger", name = "the Millcross Bread Ledger", item = 2821, chain = true,
		text = "MILLCROSS BREAD LEDGER, kept by the miller's girl\n\nPaid in advance by Captain Aldric Vane: bread for forty-one, every tenth day, for one season.\n\nFirst delivery: taken. Second: taken. Third: taken.\nFourth delivery: nobody came to collect it.\nFifth delivery: one man came, alone. A healer, Brother Tam. He took one loaf and asked for nothing else. He said the others had gone on without him. He walked south, toward the marsh, and did not come back for the rest." },
	{ id = "prayer", name = "Brother Tam's Prayer", item = 2815, chain = true,
		text = "A scrap of prayer in a shaking hand:\n\n\"Let me not be the one who reached the top. Let me be the one who came back and told them not to go. I told them. They went. Forgive me for turning round, and forgive them for not.\"\n\nSigned: Tam, healer of the First Climb." },
	{ id = "page1", name = "a page of Ione's record (day 40)", item = 2815, chain = true,
		text = "RECORD OF THE FIRST CLIMB, kept by Ione Castellan. Day 40.\n\nCaptain Vane buried the company's pay chest at the last camp so we climb light. \"If we come back, we dig it up. If we don't, nobody needs it.\" Only he knows the place." },
	{ id = "page2", name = "a page of Ione's record (day 52)", item = 2815, chain = true,
		text = "RECORD OF THE FIRST CLIMB. Day 52.\n\nThe road thieves have found our old camp and dig under every tree. Let them dig. The chest was never buried there. The Captain carried it up the stair himself. Where he goes, it goes." },
	{ id = "order", name = "the Garrison's Standing Order", item = 2818, chain = true,
		text = "STANDING ORDER OF THE FIRST CLIMB (copied from the carved stone at the Old Quarry's gate)\n\nHold the quarry. Hold the tower. Let nobody up the stair.\n\nWe four swore it for the forty-one in the oath hall below this quarry. Its way in stands at the quarry's gate, sealed by four oath stones: four must stand on them, and one pull the lever. Keep the oath until we come down.\n\n- A. Vane, captain" },
	{ id = "watchlog", name = "the Old Watchtower's Watch Log", item = 2821, chain = true,
		text = "WATCH LOG, OLD WATCHTOWER\n\nDay 1: Company gone up the stair. All quiet.\nDay 2: All quiet.\nDay 3: All quiet.\n\n(The same two words fill every page after that, in a hand that never changes, to the very end of the book.)\n\nDay 11,904: All quiet. They have not come down." },
	{ id = "letter", name = "Aldric Vane's Unsent Letter", item = 2818, chain = true,
		text = "To whoever reads this at the foot of the stair.\n\nI am Aldric Vane, captain of the First Climb. The others have gone up. I stay behind.\n\nMy order is not to keep the beasts in. It is to let nobody follow. What waits at the summit is real, and we have seen what it costs. Turn back.\n\nIf you will not, then come up and face me. I will be at the top of this stair, and I will not be kind.\n\n- Aldric Vane" },
	{ id = "lastpage", name = "the Last Page", item = 2815, chain = true,
		text = "THE LAST PAGE, in Ione Castellan's hand:\n\n\"The Wish is real. We have seen what it costs. Hold the stair. Let no one climb after us.\"\n\nUnder it, in another hand:\n\n\"They went on anyway. Highlands, by the herd road.\"" },
	-- loose records: lying out for anyone who looks around (not secrets: no riddle, nothing to find with them)
	{ id = "song", name = "the Song of the Forty-One", item = 2815, loose = "carriage_millcross",
		text = "THE SONG OF THE FORTY-ONE (as the Millcross Inn sings it)\n\nForty-one went up the stair,\nwith rope and bread and a captain's prayer.\nThe miller's girl stood at the door,\nand counted them, and counted more.\nOne came down with an empty hand.\nForty stayed in the high land.\n\n(Somebody has written underneath: \"There is no last verse. Stop asking.\")" },
	{ id = "margin", name = "Linnet Marsh's Route Notes", item = 2815, loose = "centre_wolf_copse",
		text = "Scout's notes, Linnet Marsh, First Climb.\n\nWolves den to the west of the river. Keep fires high. The river is the road: follow it and you never lose the stair. Above the Pass the ground climbs to grass country, herd country. Good grazing, bad weather.\n\nTold the Captain the stair is watched from above as well as below. He laughed. I did not." },
	{ id = "rations", name = "a Camp Cook's Scrap", item = 2815, loose = "camp_reed_marsh",
		text = "A cook's scrap, greasy at the corners:\n\nFor the long climb: fish keeps, boar fills, honey cheers. A truffle in the pot and nobody complains about the cold. Turtle eggs from the marsh at low water, if you're quick. Cook it on a camp fire, not in the ashes.\n\nIone's favourite: turtle eggs baked on the fire with a shaved truffle on top. She called it the only good thing about the marsh.\n\nTam says I put too much salt in everything. Tam can cook his own." },
}

function SpireFirstClimb.record(id)
	for _, r in ipairs(SpireFirstClimb.RECORDS) do
		if r.id == id then
			return r
		end
	end
end

-- ---------------------------------------------------------------- the eight chapters
-- step texts: one per step; a step with `count` has "%d of N" filled from the step's own counter
local CH = {
	{ id = "fc1", level = 4, title = "The Missing Names", exp = 800, gold = 150,
		offer = "Everyone in Hearthgate came here to win the Summit Wish. But we were not the first. A company called the First Climb built this town's oldest walls, went up the stair, and never came down. Their names were on the Monument once; someone chiselled the top rows off, and nobody will say who. Help me prove they were real? Start by reading those scraped rows, right here on the Monument.",
		steps = {
			{ text = "Read the scraped top rows of the Monument in Hearthgate's plaza (use the Monument, beside Archivist Maren)." },
			{ text = "Find the First Climb's supply mark on Hearthgate's oldest wall, beside the north gate where Captain Dorrow stands (use the marked stone)." },
		},
		thanks = "An arrow over a tally of three: the First Climb's supply mark, on our oldest wall. They were real. Their quartermaster marked every camp like that. Come back when you reach level 8 and we'll follow the trail." },
	{ id = "fc2", level = 8, title = "The Quartermaster's Trail", exp = 2400, gold = 400,
		offer = "The First Climb's quartermaster left a supply stone at every camp they used. Three should still stand in the training grounds: the Ratwarren (west gate), Toad Pond (east gate) and the Sproutling Glade (south gate). Read all three for me?",
		steps = {
			{ text = "Read the First Climb's supply stones in the Ratwarren (west of town), Toad Pond (east) and the Sproutling Glade (south): %d of 3.", count = 3 },
		},
		thanks = "\"The miller's girl keeps the book.\" The mill at Millcross baked for them! Miller Agna's family has run it for generations. Come back at level 12 and we'll ask her about it." },
	{ id = "fc3", level = 12, title = "Bread for the Climb", exp = 5000, gold = 600,
		offer = "The tally says the Millcross mill baked for the First Climb, and \"the miller's girl keeps the book\". That girl was Miller Agna's grandmother. Go and ask Agna about the first climb?",
		steps = {
			{ text = "Ask Miller Agna at the mill in Millcross, far to the west, about the first climb (say 'climb')." },
			{ text = "Find the old flour store on the mill road in Thornsnap Hollow (north-west of Hearthgate) and open the flour bin where the ledger was kept." },
			{ text = "Thornsnaps burst out of the flour bin. Defeat them: %d of 3.", count = 3 },
			{ text = "Open the flour bin in Thornsnap Hollow again and take the ledger." },
		},
		thanks = "\"One man came, alone. A healer, Brother Tam.\" One of them came back! And he walked south, into the marsh. Come back at level 15." },
	{ id = "fc4", level = 15, title = "The One Who Turned Back", exp = 6000, gold = 800,
		offer = "Brother Tam, the First Climb's healer, came down alone, and the marsh folk buried him in Reedmarsh, across the river south-west of town. Find his grave. Miller Agna sent this wreath of wheat for him, if you want to lay it there. Will you go?",
		steps = {
			{ text = "Find Brother Tam's grave in Reedmarsh (south-west of Hearthgate, across the river) and use it." },
			{ text = "Choose: take Tam's pendant to Archivist Maren for the archive (use the grave again), or leave it with him and lay Agna's wheat wreath (use the wreath on the grave)." },
		},
		thanks = "" }, -- the thanks depends on the choice (SpireFirstClimb.CHOICES)
	{ id = "fc5", level = 19, title = "The Pay Chest", exp = 9000, gold = 1500,
		offer = "Ione Castellan kept the First Climb's record, and the bandits on the Bandit Road (east, then north of town) pass her pages around: their captains carry them. Captain Dorrow's lost patrol was following the same trail. The captains never ride alone, so take friends. Bring me two pages?",
		steps = {
			{ text = "Defeat Bandit Captains on the Bandit Road (north-east of Hearthgate, a group ground) and take the pages of Ione's record they carry: %d of 2.", count = 2 },
		},
		thanks = "So the bandits dig for a chest that went up the stair years ago. The pages speak of a garrison, too: the First Climb kept watch from the Old Quarry and the Old Watchtower. Come back at level 24." },
	{ id = "fc6", level = 24, title = "The Watch That Never Ended", exp = 12000, gold = 2000,
		offer = "The First Climb quarried the stair's stone in the Old Quarry and kept watch from the Old Watchtower, and the Ruin Guards there still stand at their posts. Read their standing order, carved in the Old Quarry, then their watch log in the Old Watchtower's keep?",
		steps = {
			{ text = "In the Old Quarry (north of Hearthgate, off the Pass Road), read the garrison's standing order, carved on a stone beside the four oath stones just outside the quarry's gate (use it)." },
			{ text = "In the Old Watchtower (far north-west, up the Watch Road from Millcross), reach the keep at its heart and read the watch log on the captain's table." },
		},
		thanks = "Thousands of days of \"all quiet\". They are still keeping the watch. And the order is signed A. Vane: Captain Aldric Vane. His field desk stood at the foot of the stair. Come back at level 28, with the Stair Key." },
	{ id = "fc7", level = 28, title = "The Rearguard", exp = 15000, gold = 2500,
		offer = "Captain Aldric Vane's field desk stands at the foot of the labyrinth, past the Gate Hound's Pass. Its drawer is locked, and the lock was made for the same key that opens the Axe-Lord's hall. Make the Stair Key and read what's in the drawer?",
		steps = {
			{ text = "Find Aldric Vane's field desk at the foot of the labyrinth, past the Gate Hound's Pass, and open it with the Stair Key (the Stair Key quest in your log says how to make it)." },
		},
		thanks = "\"I will be at the top of this stair.\" The Axe-Lord of the Stair... was Captain Vane all along, still following his last order: let nobody follow. Come back at level 30, and bring friends." },
	{ id = "fc8", level = 30, title = "The Last Page", exp = 20000, gold = 3000, rewardTitle = "Heir to the First Climb",
		offer = "The Axe-Lord of the Stair is Aldric Vane, the First Climb's rearguard. Defeat him at the top of the labyrinth, with a party, and bring me whatever he carries. This is the end of their trail on our floor. Will you?",
		steps = {
			{ text = "Defeat the Axe-Lord of the Stair at the top of the labyrinth (a party fight). The last page of Ione's record is on him." },
		},
		thanks = "\"They went on anyway.\" So the First Climb is still up there, somewhere above us. I've put their names back on the Monument, and yours under them: Heir to the First Climb. And the archive owes you a Floor 1 perk: say {perk} to choose it." },
}

SpireFirstClimb.CHAPTERS = {}
for i, c in ipairs(CH) do
	local q = {
		id = c.id, floor = 1, kind = "chapter", chapter = i, giver = SpireFirstClimb.GIVER,
		name = string.format("The First Climb (%d of 8): %s", i, c.title),
		storage = 51300 + i, killStorage = 51310 + i, minLevel = c.level,
		requires = i > 1 and CH[i - 1].id or nil, count = #c.steps,
		reward = { exp = c.exp, gold = c.gold, title = c.rewardTitle },
		offer = c.offer, steps = c.steps, report = SpireFirstClimb.REPORT, thanks = c.thanks,
		step = c.steps[1].text, -- (kept for code that reads q.step)
	}
	table.insert(SpireFirstClimb.CHAPTERS, q)
	table.insert(SpireQuests.list, q)
end

-- Chapter 4's choice: both pay the same; a different keepsake and title, and the look line says which
SpireFirstClimb.CHOICES = {
	pendant = { title = "Keeper of the Archive", keepsake = "fc_archive_seal", look = "took Brother Tam's pendant to the archive",
		thanks = "His pendant. It goes into the archive, under glass, where nobody can forget him again. Take this seal of the archive with my thanks. Come back at level 19." },
	wreath = { title = "Tam's Mourner", keepsake = "fc_reed_flower", look = "left Brother Tam his pendant and laid a wreath",
		thanks = "You left it with him, and laid Agna's wreath. She'll be glad. Some things belong where they are. Keep that flower from his grave. Come back at level 19." },
}

SpireFirstClimb.ITEMS = {
	wreath = 3605,  -- Agna's wheat wreath: a bunch of wheat, an item you use ON something (the flowers first used could not be aimed at the grave; FD1b)
	pendant = 3039, -- Brother Tam's pendant (placeholder: a red stone, so nobody can wear it for its stats)
}

-- ---------------------------------------------------------------- pure
-- progress value = step * 100 + the step's own counter (kills, stones, pages)
function SpireFirstClimb.encode(step, sub)
	return step * 100 + (sub or 0)
end

function SpireFirstClimb.decode(v)
	v = math.max(0, v or 0)
	return math.floor(v / 100), v % 100
end

-- Pure: the quest-log line of a chapter at a progress value (state 1)
function SpireFirstClimb.stepLine(q, value)
	local step, sub = SpireFirstClimb.decode(value)
	local s = q.steps[math.min(step + 1, #q.steps)]
	if s.count then
		return string.format(s.text, math.min(sub, s.count), s.count)
	end
	return s.text
end

-- Pure: which chapter a character is on, from a state reader st(q) -> storage value. Returns the first chapter not
-- yet done (and its state), or nil when all eight are done.
function SpireFirstClimb.current(st)
	for _, q in ipairs(SpireFirstClimb.CHAPTERS) do
		local s = st(q)
		if s ~= 3 then
			return q, s
		end
	end
end

function SpireFirstClimb.get(id)
	for _, q in ipairs(SpireFirstClimb.CHAPTERS) do
		if q.id == id then
			return q
		end
	end
end

-- Townsfolk on the First Climb: one line each, and they disagree (design 4.1)
SpireFirstClimb.LORE = {
	["Guide Pell"] = "The First Climb? Before my time. Archivist Maren at the Monument knows their story. Some call them heroes. I call them the first ones to climb in a hurry.",
	["Captain Dorrow"] = "The First Climb were soldiers, like my watch. Soldiers follow orders, even bad ones. Remember that, if you ever meet one.",
	["Hunter Brannoch"] = "Fools, the lot of them. Forty-one went up with one season's bread. You don't climb a tower like that. You hunt it, step by step.",
	["Vesper"] = "My grandfather swore they were paid to go. Somebody wanted that Wish badly enough to hire a whole company. Who? Now that's a story I'd buy.",
	["Fisher Corwin"] = "The marsh folk still leave reeds on a grave out there, and they never say whose. Folk round here don't like to talk about the First Climb.",
	["Miller Agna"] = "Grandmother baked for them. She always said their captain paid in advance, and it was the last honest coin she ever saw.",
	["Crier Halsey"] = "Hear ye! The First Climb! Heroes of Hearthgate, every one! ...Well, that's how the old song goes.",
	["Lamplighter Odo"] = "Their lamps were the first ones lit on these streets. Mine are the newest. Funny, that.",
	["Baker Wenna"] = "They took a whole season's bread and never came back for the last loaves. My mother still says it like it happened to her.",
	["Old Teodric"] = "I saw their names on the Monument when I was a boy. One morning they were gone, chiselled clean off, and the council never said a word.",
	["Little Bix"] = "Mum says the First Climb are still up there, and if I'm bad they'll come down the stair and get me!",
	["Guard Ressa"] = "The Ruin Guards at the quarry still salute an old banner nobody flies any more. Loyal. Creepy, but loyal.",
	["Porter Gimble"] = "Forty-one packs up the stair, they say. I carried three today and my back is done. Heroes, every one of them.",
	["Lysa the Florist"] = "Somebody leaves flowers at the Monument every spring, right where the names were. Not me. Well. Not only me.",
	["Corwin the Minstrel"] = "I know the song! \"Forty-one went up the stair...\" Nobody ever taught me the last verse. Maybe there isn't one.",
}

-- the names restored on the Monument (chapter 8 restores them for that player)
SpireFirstClimb.NAMES = {
	"Captain Aldric Vane, rearguard (Vanguard)",
	"Linnet Marsh, scout (Ranger)",
	"Ione Castellan, record keeper (Arcanist)",
	"Brother Tam, healer (Mystic), who came back",
	"and thirty-seven more, who went on.",
}

-- Pure: the Monument's top section for a player who is (or is not) an Heir
function SpireFirstClimb.monumentHeader(isHeir, heirName)
	if not isHeir then
		return "THE TOP ROWS: the oldest names on the Monument have been chiselled off. Only scratches remain.\n"
	end
	local lines = { "THE FIRST CLIMB (restored by Archivist Maren):" }
	for _, n in ipairs(SpireFirstClimb.NAMES) do
		table.insert(lines, "  " .. n)
	end
	table.insert(lines, "Found again by " .. heirName .. ", Heir to the First Climb.")
	return table.concat(lines, "\n") .. "\n"
end
