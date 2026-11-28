-- Story quests and floor perks (DESIGN.md 8.3). Roadmap 2.11.
-- Every quest shows its next step in the client's quest log (lib/core/quests/catalog/q*.lua read from here).
-- Storage values: -1 not started, 1 hunting, 2 ready to report, 3 done.

SpireQuests = {
	list = {
		{ id = "q1_1", floor = 1, name = "Bread for the Road", giver = "Miller Agna", storage = 50101, killStorage = 50111,
			target = "Bristle Boar", count = 15, reward = { exp = 4950, gold = 600 },
			offer = "The inn is out of meat and the climbers are hungry. Hunt 15 bristle boars in the meadow south-west of Hearthgate. Will you?",
			step = "Hunt Bristle Boars in the boar meadow (south-west of Hearthgate): %d of %d.",
			report = "Return to Miller Agna in Millcross and say 'report'.",
			thanks = "Wonderful! The stew pot will be full for a week. Here's 600 gold." },
		-- Gear progression (spec 4.5): the barracks' weapon is tempered once you prove yourself in Wolf Copse
		{ id = "q1_temper", floor = 1, name = "Tempered in the Field", giver = "Captain Dorrow", storage = 50135, killStorage = 50136,
			target = "Meadow Wolf", count = 15, reward = { exp = 7400, temper = true, gold = 300 }, minLevel = 12, requiresWeapon = true,
			offer = "That weapon of yours is still raw steel. Blood it on 15 meadow wolves in Wolf Copse, west of town across the river, and my smith will temper it (raw steel only: a weapon below tier 2). Will you?",
			step = "Hunt Meadow Wolves in Wolf Copse (west of Hearthgate, across the river): %d of %d.",
			report = "Return to Captain Dorrow at Hearthgate's north gate and say 'report'.",
			thanks = "Good. My smith tempered it while you talked: one tier stronger. And 300 gold for the trouble." },
		{ id = "q1_2", floor = 1, name = "The Lost Patrol", giver = "Captain Dorrow", storage = 50102, killStorage = 50112,
			-- party playtest 2026-11-26: the Captain and his escort wiped a level 23-25 party of three twice; the Bandit
			-- Road is a group ground, so the offer says so and waits until level 23
			target = "Bandit Captain", count = 2, reward = { exp = 7250, gold = 1200 }, minLevel = 23,
			offer = "My patrol never came back from the bandit road in the east. Two bandit captains run that road, and they never ride alone: take a party of four. Bring them down?",
			step = "Defeat Bandit Captains on the bandit road (east of Hearthgate): %d of %d.",
			report = "Return to Captain Dorrow at Hearthgate's north gate and say 'report'.",
			thanks = "Then my men are avenged. Take this, 1,200 gold, and my thanks." },
		-- P9b (FLOOR1_REVIEW.md: "find the patrol's survivor and walk him home"): an escort. Patrolman Teodric waits in the
		-- Smugglers' Cellar under the Bandit Road; say "follow" to him and he walks with you (scripts/spirebound/escort.lua).
		{ id = "q1_2b", floor = 1, name = "The Last of the Patrol", giver = "Captain Dorrow", storage = 50235, killStorage = 50236,
			kind = "escort", side = true, requires = "q1_2", minLevel = 23, count = 1, reward = { exp = 9000, gold = 1500 },
			offer = "One of my patrol is alive: Patrolman Teodric. The bandits keep him in their cellar under the bandit road. Cut him loose and walk him home to me, alive?",
			step = "Free Patrolman Teodric in the Smugglers' Cellar under the bandit road, say 'follow' to him, and walk him back to Captain Dorrow alive (%d of %d).",
			report = "Bring Patrolman Teodric to Captain Dorrow at Hearthgate's north gate and say 'report'.",
			thanks = "Teodric! You brought him home. The watch owes you, climber: 1,500 gold, and a place at our fire." },
		{ id = "q1_3", floor = 1, name = "Millstone", giver = "Miller Agna", storage = 50103, killStorage = 50113,
			target = "Thornsnap", count = 20, reward = { exp = 8650, gold = 900, title = "Millhand" }, requires = "q1_1",
			offer = "Thornsnaps have overgrown the old mill road in the hollow north of town. Clear 20 of them so the millstones can come through?",
			step = "Clear Thornsnaps in the thornsnap hollow (north-west of Hearthgate): %d of %d.",
			report = "Return to Miller Agna in Millcross and say 'report'.",
			thanks = "The road's clear! You've earned the name Millhand, and 900 gold." },
		-- R12: a hand-written quest line whose reward is gear for your path, not gold
		{ id = "q1_iron1", floor = 1, minLevel = 11, name = "Iron for the Stair (1 of 2)", giver = "Hunter Brannoch", storage = 50131, killStorage = 50132,
			target = "Burrow Mole", count = 25, reward = { exp = 5950, gold = 200 },
			offer = "The Hall's armourer wants mole claws for rivets: they never rust. Twenty-five moles from Burrow Hills, north-east of town. Will you?",
			step = "Hunt Burrow Moles in Burrow Hills (north-east of Hearthgate): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "Good claws. Here's a little for the walk. Ask me for a quest again: the armourer has one more request." },
		{ id = "q1_iron2", floor = 1, name = "Iron for the Stair (2 of 2)", giver = "Hunter Brannoch", storage = 50133, killStorage = 50134,
			target = "Road Bandit", count = 30, reward = { exp = 7250, gear = true }, requires = "q1_iron1",
			offer = "The rivets need iron, and the bandits east of town stole a cartload of it. Take back thirty bandits' worth of it. The armourer will make you something for your path.",
			step = "Defeat Road Bandits on the Bandit Road (north-east of Hearthgate): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "The iron's back! The armourer made this for you. Wear it well, climber." },
		{ id = "q2_horn1", floor = 2, side = true, name = "The Hornbreaker's Due (1 of 2)", giver = "Scout of Highrest", storage = 50231, killStorage = 50232,
			target = "Ridge Cat", count = 40, reward = { gold = 1000 },
			offer = "Ridge cats stalk our herders. Forty of them, and the herders will trust you. Will you?",
			step = "Hunt Ridge Cats on Floor 2: %d of %d.",
			report = "Return to Scout of Highrest and say 'report'.",
			thanks = "The herders are talking about you. Ask me again: there is one more thing." },
		{ id = "q2_horn2", floor = 2, side = true, name = "The Hornbreaker's Due (2 of 2)", giver = "Scout of Highrest", storage = 50233, killStorage = 50234,
			target = "Stonehide Bull", count = 5, reward = { gear = true }, requires = "q2_horn1",
			offer = "The stonehide bulls in the labyrinth wear horns tougher than steel. Five of them, and our smith will forge you gear from what they leave.",
			step = "Defeat Stonehide Bulls on Floor 2: %d of %d.",
			report = "Return to Scout of Highrest and say 'report'.",
			thanks = "The smith outdid herself. This is yours." },
		{ id = "t1_1", floor = 1, side = true, name = "First Blood", giver = "Guide Pell", storage = 50121, killStorage = 50122,
			target = "Pen Rat", count = 3, reward = { exp = 100, gold = 100 }, -- G7: was 300 (level 4 before leaving the yard)
			offer = "Let's find out what you can do. Rats have taken the cellar of the Old Granary, the house just along the path: go in and take the stairs down. Defeat three of them, and open a body to take the cheese it carries: the gate after the granary won't open without one. Ready?",
			step = "Defeat the rats in the Old Granary's cellar (the house along the stone path, stairs down): %d of %d.",
			report = "Return to Guide Pell at the start of the path and say 'report'.",
			thanks = "Well fought! Here are 100 gold. Now follow the path to the Registrar. Say 'hunt' to me any time you wonder where to fight next." },
		-- more of the Hearthgate ladder (each one sends you to the next step: see BESTIARY.md)
		{ id = "q1_4", floor = 1, name = "Wasp Nest", giver = "Captain Dorrow", storage = 50104, killStorage = 50114,
			target = "Meadow Wasp", count = 12, reward = { exp = 3400, gold = 500 },
			offer = "Wasps have nested in the fields just north of the gate, and they sting my guards. Clear out 12 of them?",
			step = "Kill Meadow Wasps in the Waspgrass Fields (just north of Hearthgate): %d of %d.",
			report = "Return to Captain Dorrow at Hearthgate's north gate and say 'report'.",
			thanks = "Quiet at last. Here is 500 gold for your trouble." },
		{ id = "q1_5", floor = 1, name = "Pelts for the Hall", giver = "Hunter Brannoch", storage = 50105, killStorage = 50115,
			target = "Meadow Wolf", count = 20, reward = { exp = 7400, gold = 1200 },
			offer = "The Hunters' Hall needs wolf pelts. The wolves of the Copse, across the river beside Millcross, will do. Twenty of them. Will you hunt them?",
			step = "Kill Meadow Wolves in Wolf Copse (west of Hearthgate, across the river): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall (north of the plaza) and say 'report'.",
			thanks = "Fine pelts. The Hall pays 1,200 gold, and I have more work if you want it." },
		{ id = "q1_6", floor = 1, name = "Quarry Watch", giver = "Hunter Brannoch", storage = 50106, killStorage = 50116,
			target = "Ruin Archer", count = 10, reward = { exp = 9500, gold = 2500, title = "Quarrywatch" }, requires = "q1_5",
			offer = "Archers have taken the Old Quarry, north of town, and our scouts cannot pass. Bring down ten of them. A long walk, and a real fight. Ready?",
			step = "Kill Ruin Archers in the Old Quarry (north of Hearthgate, off the Pass Road): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "The scouts can pass again. You have earned the title Quarrywatch and 2,500 gold." },
		-- side quests: they pay well but do not block the Floor 1 perk
		{ id = "s1_1", floor = 1, side = true, name = "Snapper Season", giver = "Fisher Corwin", storage = 50107, killStorage = 50117,
			target = "Reed Snapper", count = 15, reward = { exp = 6050, gold = 1500 },
			offer = "Snappers are tearing my nets in the marsh across the river. Thin them out: fifteen. I'll pay what I can.",
			step = "Kill Reed Snappers in Reedmarsh (south-west, across the river): %d of %d.",
			report = "Return to Fisher Corwin at the Fisher's Huts and say 'report'.",
			thanks = "My nets will last the season. Take 1,500 gold." },
		{ id = "s1_2", floor = 1, side = true, name = "Mole Hills", giver = "Miller Agna", storage = 50108, killStorage = 50118,
			target = "Burrow Mole", count = 15, reward = { exp = 5950, gold = 1000 }, requires = "q1_1",
			offer = "Moles from the Burrow Hills are digging up the grain road. Fifteen of them should discourage the rest. Will you?",
			step = "Kill Burrow Moles in the Burrow Hills (north-east of Hearthgate): %d of %d.",
			report = "Return to Miller Agna in Millcross and say 'report'.",
			thanks = "The road is whole again. Here's 1,000 gold." },
		{ id = "s1_3", floor = 1, side = true, name = "The Alpha", giver = "Hunter Brannoch", storage = 50109, killStorage = 50119,
			target = "Grey Alpha", count = 1, reward = { exp = 7400, gold = 1800 }, requires = "q1_5",
			offer = "One Grey Alpha leads every wolf pack, and it calls its wolves when hurt. Kill one and I will pay you well. Interested?",
			step = "Kill a Grey Alpha in Wolf Copse (west of Hearthgate, across the river): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "An Alpha! That is a hunter's work. 1,800 gold." },
		{ id = "s1_4", floor = 1, side = true, name = "Shard Hunt", giver = "Hunter Brannoch", storage = 50110, killStorage = 50120,
			target = "Field Shardling", count = 20, reward = { exp = 10700, gold = 2200 }, requires = "s1_3",
			offer = "The Shard Fields, south-east of the city, are filling with shardlings. Twenty of them, if you can stand their sting. Are you in?",
			step = "Kill Field Shardlings in the Shard Fields (south-east of Hearthgate): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "Twenty shardlings. You are becoming a real climber. 2,200 gold." },
		-- P9 (FLOOR1_REVIEW.md F1-20): quests that aren't "kill N of X"
		-- a lore set: six carved stones in the wilds (placed at start-up by scripts/spirebound/quest_objects.lua)
		{ id = "l1_stones", floor = 1, side = true, kind = "collect", collect = "builders", name = "The Builders' Stones", giver = "Vesper",
			storage = 50139, killStorage = 50140, count = 6, reward = { exp = 6000, gold = 800, title = "Stonereader" },
			offer = "Six carved stones stand in the wilds around Hearthgate, older than the town: one each in Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow, the Shard Fields and the Burrow Hills. Read all six and you'll know who raised the Spire. I pay well for a story like that. Ready?",
			step = "Read the builders' stones in the wilds (Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow, Shard Fields, Burrow Hills): %d of %d.",
			report = "Return to Vesper in Hearthgate and say 'report'.",
			thanks = "Wardwrights. A tower built to hold something down, not to reach the sky. That will sell. 800 gold, and the name Stonereader is yours." },
		-- a lever puzzle; the answer is carved on a stone in the same marsh
		{ id = "p1_sluice", floor = 1, side = true, kind = "collect", collect = "sluice", name = "The Old Sluice", giver = "Fisher Corwin",
			storage = 50141, killStorage = 50142, count = 1, reward = { exp = 3000, gold = 400 },
			offer = "Out in Reedmarsh there's an old sluice with three levers that nobody can work. The builders carved the order on a stone somewhere in the marsh, never far from the levers. Open it and tell me what was behind it?",
			step = "Open the old sluice in Reedmarsh: find the carved stone that gives the lever order, then pull the three levers in that order (%d of %d).",
			report = "Return to Fisher Corwin by the river and say 'report'.",
			thanks = "A strongbox under the sluice! Keep what was in it. Here's my 400 on top." },
		-- the boss-access chain: three pieces open the Axe-Lord's hall (scripts/spirebound/stair_key.lua). Starts by itself
		-- with the first piece; there is nobody to report to.
		{ id = "k1_stairkey", floor = 1, side = true, kind = "key", auto = true, name = "The Stair Key", giver = "the Stair Key",
			storage = 50143, killStorage = 50144, count = 3, reward = { exp = 4000 },
			offer = "", step = "Make the Stair Key that opens the Axe-Lord's hall: help defeat the Gate Hound in the Pass, help defeat the Stonehorn Ram at the Old Watchtower, and finish Hunter Brannoch's Iron for the Stair. %d of %d pieces.",
			report = "The Stair Key is whole.", thanks = "" },
		-- a delivery with a choice: the guards or the bandits
		{ id = "d1_flour", floor = 1, side = true, minLevel = 12, kind = "deliver", item = 3603, name = "Flour for the Gate", giver = "Miller Agna",
			storage = 50137, killStorage = 50138, count = 1, reward = { exp = 2500, gold = 300, title = "Honest Carter" },
			offer = "The guards at Hearthgate's north gate have had no bread in a week. Carry this sack of flour to Captain Dorrow? Mind the Bandit Road: there's a fence there who would pay far more for it, and I would never know. Ready?",
			step = "Carry Agna's flour to Captain Dorrow at Hearthgate's north gate (or sell it to Fence Marrow, on the road just south of the Bandit Road).",
			report = "Give the flour to Captain Dorrow or to Fence Marrow: say 'report' to either.",
			choices = {
				["Captain Dorrow"] = { reward = { exp = 2500, gold = 300, title = "Honest Carter" },
					thanks = "Flour! The lads will eat tonight. Here's 300 gold, and the gate knows your name now." },
				["Fence Marrow"] = { reward = { exp = 2500, gold = 900, title = "Friend of the Road" },
					thanks = "Heh. Nobody misses one sack. 900 gold, and the road remembers its friends." },
			} },
	},
	PERKS = {
		[1] = {
			{ key = "thick_skin", name = "Thick Skin", text = "+5% maximum health" },
			{ key = "light_step", name = "Light Step", text = "+10 movement speed" },
		},
	},
}

-- FD1 (Floor 1 depth design 4.1): the old kill-count story quests stay as jobs (same pay), so no work is lost; the
-- Floor 1 story is now The First Climb (lib/spirebound/first_climb.lua) and the perk waits at its chapter 8.
for _, id in ipairs({ "q1_1", "q1_temper", "q1_2", "q1_3", "q1_iron1", "q1_iron2", "q1_4", "q1_5", "q1_6" }) do
	for _, q in ipairs(SpireQuests.list) do
		if q.id == id then
			q.side, q.job = true, true
		end
	end
end

-- Outfit addons as quest rewards (roadmap 6.5c; Jay, 2026-11-25: "tibia has the base outfit, addon 1 and addon 2...
-- it'll give us more content for quests"). Two quests per class, only for that class (vocation = base vocation id:
-- 1 Arcanist, 2 Mystic, 3 Ranger, 4 Vanguard), each from a townsperson who fits the class. Addon 1 hunts a ground's
-- elite (the rare lone leader), addon 2 needs addon 1 and a harder ground. The reward unlocks the addon on both the
-- man's and the woman's body of the class outfit (ClassOutfits.giveAddon). Art approved by Jay 2026-11-25/26.
-- Levels and targets are Claude's call (Jay can veto).
for _, q in ipairs({
	{ id = "o_van1", vocation = 4, addon = 1, addonName = "the Crested Helm", giver = "Captain Dorrow", storage = 51201, killStorage = 51211,
		target = "Moonhowl", count = 1, minLevel = 14, exp = 6000,
		offer = "Every watch captain before me earned a crested helm on one beast: the great wolf the trappers call Moonhowl, leader of the Wolf Copse packs. Bring it down and the helm is yours. Will you?",
		step = "Defeat Moonhowl, the great wolf that leads the packs in Wolf Copse (west of Hearthgate, across the river): %d of %d.",
		thanks = "Moonhowl, by your own hand! Here: the Crested Helm of the watch. Wear it, Vanguard (open your outfit window)." },
	{ id = "o_van2", vocation = 4, addon = 2, addonName = "the Knight's Mantle", giver = "Captain Dorrow", storage = 51202, killStorage = 51212,
		target = "Granite Warden", count = 1, minLevel = 24, requires = "o_van1", exp = 12000,
		offer = "The mantle is for those who have held a line against stone itself. In the Old Quarry a Granite Warden still guards the ruins. Break it, and the knight's mantle is yours. Will you?",
		step = "Break the Granite Warden that guards the Old Quarry (north of Hearthgate, off the Pass Road): %d of %d.",
		thanks = "Stone gave way before you did. The Knight's Mantle: you've earned it twice over." },
	{ id = "o_ran1", vocation = 3, addon = 1, addonName = "the Hawk-Feather Hood", giver = "Hunter Brannoch", storage = 51203, killStorage = 51213,
		target = "Blackthorn", count = 1, minLevel = 14, exp = 6000,
		offer = "A ranger's hood carries the feathers of a hunt worth telling. Here's one: Blackthorn, the oldest snapping thorn in Thornsnap Hollow. Cut it down and I'll stitch you a hawk-feather hood. Will you?",
		step = "Cut down Blackthorn, the oldest thornsnap in Thornsnap Hollow (north-west of Hearthgate): %d of %d.",
		thanks = "Blackthorn's done? Then here's your Hawk-Feather Hood. The Hall will know you by it, Ranger." },
	{ id = "o_ran2", vocation = 3, addon = 2, addonName = "the Huntsman's Horn", giver = "Hunter Brannoch", storage = 51204, killStorage = 51214,
		-- AD5 (adventure design 4.5, Q71): a hunt for a named target, not a kill count. She comes out after 15 of her
		-- crossbowmen fall on Smugglers' Ridge (scripts/spirebound/addon_hunts.lua).
		target = "Deadeye Sorrel", count = 1, minLevel = 20, requires = "o_ran1", exp = 12000,
		hunt = { kind = "Bandit Crossbowman", plural = "Bandit Crossbowmen", count = 15, ground = "smugglers_ridge" },
		offer = "A crossbow ace leads the bandits on Smugglers' Ridge. They call her Deadeye Sorrel, and she only shows herself once her crew starts falling. Drop fifteen of her crossbowmen, then outshoot her, and the huntsman's horn of the Hall is yours. Will you?",
		step = "Drop 15 Bandit Crossbowmen on Smugglers' Ridge (far north-east of Hearthgate) until Deadeye Sorrel comes out, then outshoot her: %d of %d.",
		thanks = "Deadeye Sorrel, outshot! The ridge will talk about it for a season. Take the Huntsman's Horn, and blow it proud." },
	{ id = "o_arc1", vocation = 1, addon = 1, addonName = "the Orbiting Runestones", giver = "Vesper", storage = 51205, killStorage = 51215,
		target = "Prism Shardling", count = 1, minLevel = 17, exp = 7000,
		offer = "The builders' stones answer to light. In the Shard Fields lives a prism shardling, grown huge on the tower's light. Shatter it and bring me its heart: I'll set its pieces circling you. Will you?",
		step = "Shatter the Prism Shardling in the Shard Fields (south-east of Hearthgate): %d of %d.",
		thanks = "Its heart still hums. There: the Orbiting Runestones. They will follow you now, Arcanist." },
	{ id = "o_arc2", vocation = 1, addon = 2, addonName = "the Floating Grimoire", giver = "Vesper", storage = 51206, killStorage = 51216,
		-- AD5: the Page-Thief comes out after 15 hexers fall on the Bandit Road
		target = "The Page-Thief", count = 1, minLevel = 22, requires = "o_arc1", exp = 12000,
		hunt = { kind = "Hedge Hexer", plural = "Hedge Hexers", count = 15, ground = "bandit_road" },
		offer = "One hexer on the Bandit Road carries a stolen book of the builders. The others call her the Page-Thief, and she hides behind them until they start to fall. Bring down fifteen hexers, then take the book from her, and I'll bind it for you. Will you?",
		step = "Bring down 15 Hedge Hexers on the Bandit Road (north-east of Hearthgate) until the Page-Thief comes out, then take the book from her: %d of %d.",
		thanks = "Every page, and not one torn. The book is bound, and it has chosen you: the Floating Grimoire." },
	{ id = "o_mys1", vocation = 2, addon = 1, addonName = "the Antler Crown", giver = "Fisher Corwin", storage = 51207, killStorage = 51217,
		target = "Mossback Snapper", count = 1, minLevel = 14, exp = 6000,
		offer = "The marsh folk crown a healer who frees the reeds. An old mossback snapper has choked Reedmarsh for years. Free the marsh of it and I'll weave you the antler crown. Will you?",
		step = "Free Reedmarsh of the old Mossback Snapper (west of Hearthgate): %d of %d.",
		thanks = "The reeds breathe again. Here is your Antler Crown, Mystic. The marsh folk will bow when you pass." },
	{ id = "o_mys2", vocation = 2, addon = 2, addonName = "the Owl Companion", giver = "Fisher Corwin", storage = 51208, killStorage = 51218,
		-- AD5: Glasswing, the oldest shardling, stirs after 15 shardlings are calmed in the Shard Fields
		target = "Glasswing", count = 1, minLevel = 19, requires = "o_mys1", exp = 11000,
		hunt = { kind = "Field Shardling", plural = "Field Shardlings", count = 15, ground = "shard_fields" },
		offer = "The owls left the Shard Fields when the oldest shardling woke. Glasswing, the trappers call it, and it only stirs when its brood is thinned. Calm fifteen shardlings, then calm Glasswing itself, and one owl will come back to you, and stay. Will you?",
		step = "Calm 15 Field Shardlings in the Shard Fields (south-east of Hearthgate) until Glasswing stirs, then calm it: %d of %d.",
		thanks = "Listen: hoo. One came back, and it's looking at you. The Owl Companion is yours." },
}) do
	q.floor, q.side = 1, true
	q.name = "Outfit: " .. q.addonName:gsub("^the ", ""):gsub("^%l", string.upper)
	q.reward = { exp = q.exp, addon = q.addon, addonName = q.addonName }
	q.report = "Return to " .. q.giver .. " and say 'report'."
	table.insert(SpireQuests.list, q)
end

-- Quest gold goes into the backpack (Jay, 2026-11-27, Q76), weight ignored; only with no free slot does it go to the
-- bank, so a full backpack never drops the coins on the floor (party playtest hand-off P1-1).
function SpireQuests.payGold(player, gold)
	local bag, bank = SpireGive.gold(player, gold)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%d gold, %s.", gold, SpireGive.goldWhere(bag, bank)))
end

-- Pure: does this giver have outfit-addon quests for this class?
function SpireQuests.anyAddonQuest(giver, vocation)
	for _, q in ipairs(SpireQuests.list) do
		if q.giver == giver and q.addon and q.vocation == vocation then
			return true
		end
	end
	return false
end

function SpireQuests.get(id)
	for _, q in ipairs(SpireQuests.list) do
		if q.id == id then
			return q
		end
	end
end

function SpireQuests.state(player, q)
	return player:getStorageValue(q.storage)
end

function SpireQuests.progress(player, q)
	if q.kind == "collect" then
		return SpireQuests.collectedCount(player, q.collect)
	elseif q.kind == "deliver" then
		return 0
	elseif q.kind == "key" then
		return SpireStairKey.count(player)
	elseif q.kind == "chapter" or q.kind == "oath" then
		return SpireFirstClimb.progress(player, q)
	end
	return math.max(0, player:getStorageValue(q.killStorage))
end

-- Collect quests (P9): what a player has found of a set (builders' stones, the sluice), kept even before the quest is taken
function SpireQuests.collected(player, set)
	return player:kv():scoped("spirebound-collect"):get(set) or {}
end

function SpireQuests.collectedCount(player, set)
	local n = 0
	for _ in pairs(SpireQuests.collected(player, set)) do
		n = n + 1
	end
	return n
end

-- Marks one piece found; returns true if it was new. Moves a running collect quest on to "report" when it is complete.
function SpireQuests.find(player, set, piece)
	local have = SpireQuests.collected(player, set)
	if have[piece] then
		return false
	end
	have[piece] = os.time()
	player:kv():scoped("spirebound-collect"):set(set, have)
	SpireQuests.checkCollect(player)
	return true
end

-- G10 (Grok session 3): the Quest Tracker showed "0 of 3" through every kill. The engine refreshes tracked missions
-- only when a quest's own storage is written (data/libs/functions/quests.lua, Player.updateStorage), and kills are
-- counted in a second storage. Writing the same state again refreshes the count; an unchanged value sends no
-- "Your questlog has been updated" line, so there is no message per kill.
function SpireQuests.refreshTracker(player, q)
	player:setStorageValue(q.storage, player:getStorageValue(q.storage))
end

function SpireQuests.checkCollect(player)
	for _, q in ipairs(SpireQuests.list) do
		if q.kind == "collect" and SpireQuests.state(player, q) == 1 then
			local n = SpireQuests.progress(player, q)
			if n >= q.count then
				player:setStorageValue(q.storage, 2)
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, q.name .. ": done! " .. q.report)
			elseif n > 0 then
				SpireQuests.refreshTracker(player, q)
				player:sendTextMessage(MESSAGE_STATUS, string.format("%s: %d of %d.", q.name, n, q.count))
			end
		end
	end
end

-- Pure: the quest-log line for a state
function SpireQuests.logText(q, state, kills)
	if state == 1 then
		if q.kind == "deliver" then
			return q.step
		end
		if q.kind == "chapter" or q.kind == "oath" then
			return SpireFirstClimb.stepLine(q, kills)
		end
		return string.format(q.step, math.min(kills, q.count), q.count)
	elseif state == 2 then
		return q.report
	elseif state == 3 then
		return "Completed."
	end
	if q.auto then
		return string.format(q.step, math.min(kills or 0, q.count), q.count)
	end
	return "Talk to " .. (SpireQuests.whereText and SpireQuests.whereText(q.giver) or q.giver) .. "."
end

-- Pure: may this player start the quest? doneIds = set of completed quest ids
function SpireQuests.available(q, state, doneIds, ctx)
	if q.auto or (state ~= -1 and state ~= 0) then
		return false
	end
	if ctx and q.minLevel and (ctx.level or 0) < q.minLevel then
		return false
	end
	if ctx and q.requiresWeapon and not ctx.hasWeapon then
		return false
	end
	if ctx and q.vocation and ctx.vocation ~= q.vocation then -- 6.5c: a class's outfit quests are for that class
		return false
	end
	return not q.requires or doneIds[q.requires] == true
end

function SpireQuests.context(player)
	local voc = player.getVocation and player:getVocation() -- (test stand-ins may have no class)
	return { vocation = voc and voc:getBaseId() or 0, level = player:getLevel(), hasWeapon = SpireGear.earnedMain ~= nil and SpireGear.earnedMain(player, 1) ~= nil }
end

function SpireQuests.doneIds(player)
	local out = {}
	for _, q in ipairs(SpireQuests.list) do
		if SpireQuests.state(player, q) == 3 then
			out[q.id] = true
		end
	end
	return out
end

function SpireQuests.floorStoryDone(player, floor)
	if floor == 1 and SpireFirstClimb and SpireFirstClimb.CHAPTERS then -- FD1: Floor 1's story is The First Climb
		return SpireQuests.state(player, SpireFirstClimb.CHAPTERS[#SpireFirstClimb.CHAPTERS]) == 3
	end
	for _, q in ipairs(SpireQuests.list) do
		if q.floor == floor and not q.side and SpireQuests.state(player, q) ~= 3 then
			return false
		end
	end
	return true
end

-- Perks -----------------------------------------------------------------
SpirePerks = {}

function SpirePerks.get(player, floor)
	return player:kv():scoped("spirebound-perks"):get("floor" .. floor)
end

function SpirePerks.choose(player, floor, key)
	player:kv():scoped("spirebound-perks"):set("floor" .. floor, key)
	SpirePerks.apply(player)
end

-- SpirePerks.apply lives in lib/spirebound/perks.lua (roadmap R12: every perk works)

-- Shared NPC dialogue for quest givers. Returns true if it handled the message.
-- Pure: what a quest pays, in one line (FLOOR1_REVIEW.md F1-23)
local function thousands(n)
	local s = tostring(math.floor(n))
	return (s:reverse():gsub("(%d%d%d)", "%1,"):reverse():gsub("^,", ""))
end
function SpireQuests.rewardText(r)
	local parts = {}
	if r.gold then table.insert(parts, thousands(r.gold) .. " gold") end
	if r.exp then table.insert(parts, thousands(r.exp) .. " experience") end
	if r.title then table.insert(parts, "the title \"" .. r.title .. "\"") end
	if r.gear then table.insert(parts, "a piece of Floor gear") end
	if r.temper then table.insert(parts, "your weapon tempered one tier") end
	if r.addon then table.insert(parts, (r.addonName or "an outfit addon") .. " (outfit addon " .. r.addon .. ")") end
	if #parts == 0 then
		return ""
	end
	return "Reward: " .. table.concat(parts, ", ") .. "."
end

local offered = {} -- playerId -> quest id
SpireCleanup.add(function(pid) offered[pid] = nil end)
function SpireQuests.talk(npc, npcHandler, player, msg, giver)
	if msg:sub(1, 1) == "!" then
		return false -- a player command said near an NPC (e.g. !upgrade) is not talk
	end
	if SpireGear.dorrowTalk and giver == "Captain Dorrow" and SpireGear.dorrowTalk(npc, npcHandler, player, msg) then
		return true
	end
	local lower = msg:lower()
	local pid = player:getId()
	if SpireFirstClimb and SpireFirstClimb.talk and SpireFirstClimb.talk(npc, npcHandler, player, msg, giver) then
		return true -- FD1: chapter steps said to a townsperson (Agna), and every giver's line on the First Climb
	end
	if MsgContains(lower, "report") then
		for _, q in ipairs(SpireQuests.list) do
			local choice = q.choices and q.choices[giver]
			if choice and SpireQuests.state(player, q) == 1 then
				if player:getItemCount(q.item) < 1 then
					npcHandler:say("You don't have " .. q.giver .. "'s " .. ItemType(q.item):getName() .. " with you.", npc, player)
					return true
				end
				player:removeItem(q.item, 1)
				player:setStorageValue(q.storage, 3)
				local r = choice.reward
				if r.gold then SpireQuests.payGold(player, r.gold) end
				if r.exp then player:addExperience(r.exp, true) end
				if r.title then player:kv():scoped("spirebound-titles"):set(r.title, os.time()) end
				player:kv():scoped("spirebound-choices"):set(q.id, giver)
				SpireChronicle.add(player, "quest", 1)
				npcHandler:say(choice.thanks, npc, player)
				return true
			end
		end
		-- finished quests first: a giver with one quest done and another still running pays out the finished one
		local order = {}
		for _, q in ipairs(SpireQuests.list) do
			if q.giver == giver and SpireQuests.state(player, q) == 2 then
				table.insert(order, q)
			end
		end
		for _, q in ipairs(SpireQuests.list) do
			if q.giver == giver and SpireQuests.state(player, q) ~= 2 then
				table.insert(order, q)
			end
		end
		for _, q in ipairs(order) do
			if q.giver == giver then
				local st = SpireQuests.state(player, q)
				if st == 1 and q.kind == "escort" and SpireEscort and SpireEscort.arrived(player, npc) then
					SpireEscort.finish(player) -- P9b: the one you walked home is here
					player:setStorageValue(q.killStorage, 1)
					st = 2
				end
				if st == 2 then
					player:setStorageValue(q.storage, 3)
					SpireChronicle.add(player, "quest", 1)
					local thanks = q.thanks
					if (q.kind == "chapter" or q.kind == "oath") and SpireFirstClimb.onReport then
						thanks = SpireFirstClimb.onReport(player, q) or thanks -- FD1: chapter 4's choice, chapter 8's heir
					end
					if q.reward.gold then SpireQuests.payGold(player, q.reward.gold) end
					if q.reward.exp then player:addExperience(q.reward.exp, true) end -- FLOOR1_REVIEW.md F1-21: about 10 minutes of hunting
					if q.reward.title then player:kv():scoped("spirebound-titles"):set(q.reward.title, os.time()) end
					if q.reward.gear then SpireGear.give(player, q.floor, "quest") end -- R12: a reward that isn't gold
					if q.reward.temper then SpireGear.temperFor(player, q.floor) end -- gear progression: +1 tier
					if q.reward.addon then ClassOutfits.giveAddon(player, q.reward.addon) end -- 6.5c: outfit addon
					if q.id == "q1_iron2" then SpireStairKey.update(player) end
					npcHandler:say(thanks, npc, player)
					SpireQuests.markGivers(player) -- the next quest may be with someone new
					if SpireQuests.floorStoryDone(player, q.floor) then
						if q.floor ~= 1 then -- (Floor 1: Archivist Maren grants the perk, and says so herself)
							player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You finished every story quest on Floor " .. q.floor .. ". Registrar Maelis in Hearthgate can grant you a perk: say 'perk'.")
						end
					end
					return true
				elseif st == 1 then
					npcHandler:say("Not done yet: " .. SpireQuests.logText(q, st, SpireQuests.progress(player, q)), npc, player)
					return true
				end
			end
		end
		npcHandler:say("You have nothing to report to me.", npc, player)
		return true
	end
	-- 6.5c: "outfit" (or "addon") asks a giver for their outfit-addon quest straight away, past their other quests
	if MsgContains(lower, "outfit") or MsgContains(lower, "addon") then
		local mine, other = nil, nil
		local done = SpireQuests.doneIds(player)
		local ctx = SpireQuests.context(player)
		for _, q in ipairs(SpireQuests.list) do
			if q.giver == giver and q.addon then
				if q.vocation ~= ctx.vocation then
					other = other or q
				elseif not mine and SpireQuests.available(q, SpireQuests.state(player, q), done, ctx) then
					mine = q
				end
			end
		end
		if mine then
			offered[pid] = mine.id
			npcHandler:say(mine.offer .. " " .. SpireQuests.rewardText(mine.reward) .. " Say {yes} or {no}.", npc, player)
			return true
		elseif other and not SpireQuests.anyAddonQuest(giver, ctx.vocation) then
			local names = { [1] = "Arcanists", [2] = "Mystics", [3] = "Rangers", [4] = "Vanguards" }
			npcHandler:say("My outfit work is for " .. (names[other.vocation] or "another path") .. " only.", npc, player)
			return true
		elseif other or SpireQuests.anyAddonQuest(giver, ctx.vocation) then
			npcHandler:say("No outfit work for you right now. Some of it needs more experience (level 14 for the first piece), or the first piece done; finished ones I can't give twice.", npc, player)
			return true
		end
	end
	if MsgContains(lower, "quest") or MsgContains(lower, "mission") or MsgContains(lower, "help") then
		local done = SpireQuests.doneIds(player)
		for _, q in ipairs(SpireQuests.list) do
			if q.giver == giver and SpireQuests.available(q, SpireQuests.state(player, q), done, SpireQuests.context(player)) then
				offered[pid] = q.id
				local rw = SpireQuests.rewardText(q.reward)
				npcHandler:say(q.offer .. (rw ~= "" and (" " .. rw) or "") .. " Say {yes} or {no}.", npc, player)
				return true
			end
		end
		npcHandler:say("I have no work for you right now.", npc, player)
		return true
	end
	if MsgContains(lower, "yes") and offered[pid] then
		local q = SpireQuests.get(offered[pid])
		offered[pid] = nil
		player:setStorageValue(q.storage, 1)
		player:setStorageValue(q.killStorage, 0)
		if q.kind == "deliver" then
			SpireGive.item(player, q.item, 1) -- ignores carrying weight: an overloaded player still gets the parcel (P1-1)
		end
		if q.kind == "chapter" and SpireFirstClimb.onStart then
			SpireFirstClimb.onStart(player, q) -- FD1: a chapter's first item (chapter 4: Agna's marker)
		end
		npcHandler:say("Thank you! It's in your quest log.", npc, player)
		if q.kind == "collect" then
			SpireQuests.checkCollect(player) -- pieces found before the quest count
		end
		return true
	end
	if MsgContains(lower, "no") and offered[pid] then
		offered[pid] = nil
		npcHandler:say("Maybe another time.", npc, player)
		return true
	end
	return false
end

-- The Stair Key (P9, FLOOR1_REVIEW.md F1-20): the Axe-Lord's hall opens only for a climber who has helped defeat the
-- Gate Hound, helped defeat the Stonehorn Ram at the Old Watchtower, and finished Iron for the Stair (2 of 2).
-- (The review also named the Underkeep, but that is a secret and DESIGN.md 9 keeps secrets off the main path.)
SpireStairKey = {}

function SpireStairKey.pieces(player)
	return {
		hound = player:kv():scoped("spirebound"):get("boss_credit_Gate Hound") ~= nil,
		ram = SpireQuests.collected(player, "stairkey").ram ~= nil,
		iron = SpireQuests.state(player, SpireQuests.get("q1_iron2")) == 3,
	}
end

function SpireStairKey.count(player)
	local n = 0
	for _, have in pairs(SpireStairKey.pieces(player)) do
		if have then
			n = n + 1
		end
	end
	return n
end

function SpireStairKey.has(player)
	return SpireStairKey.count(player) >= 3 or player:kv():scoped("spirebound"):get("stair_key_pilot") ~= nil
end

-- Starts the quest with the first piece and finishes it with the third.
function SpireStairKey.update(player, quiet)
	local q = SpireQuests.get("k1_stairkey")
	local st, n = SpireQuests.state(player, q), SpireStairKey.count(player)
	if st == 3 or n == 0 then
		return
	end
	if n >= q.count then
		player:setStorageValue(q.storage, 3)
		player:addExperience(q.reward.exp, true)
		if quiet then
			return
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The Stair Key is whole. The Axe-Lord's hall at the top of the labyrinth will open for you.")
		player:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
		return
	end
	if st ~= 1 then
		player:setStorageValue(q.storage, 1)
	end
	if quiet then
		return
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The Stair Key: %d of 3 pieces. Your quest log says what is left.", n))
end

-- P2 (Jay's playtest 2026-11-23, "quests you can find"): where each quest giver stands, said in the Journal and the
-- NPC offer lines, and marked on the minimap. Positions match world/spirebound-npc.xml (an in-game test checks the
-- NPC really stands there); Fence Marrow is placed at start-up (scripts/spirebound/quest_objects.lua).
SpireQuests.WHERE = {
	["Guide Pell"] = { place = "the Arrival Yard, at the start of the stone path", pos = { 1276, 1347, 7 } },
	["Captain Dorrow"] = { place = "Hearthgate's north gate, outside the guardhouse", pos = { 1235, 1244, 7 } },
	["Hunter Brannoch"] = { place = "the Hunters' Hall in Hearthgate's Crown Quarter, north-east of the plaza", pos = { 1260, 1271, 7 } },
	["Vesper"] = { place = "the Hearth, upstairs at the east counter beside the depot lockers", pos = { 1245, 1283, 6 } },
	["Fisher Corwin"] = { place = "the river bank north-west of Hearthgate", pos = { 1143, 1190, 7 } },
	["Miller Agna"] = { place = "the mill on the north edge of Millcross, far to the west", pos = { 1082, 1185, 7 } },
	["Fence Marrow"] = { place = "the road just south of the Bandit Road, east of Hearthgate" },
	["Archivist Maren"] = { place = "the Monument in Hearthgate's plaza", pos = { 1229, 1277, 7 } }, -- FD1 (maps/floor1_story.py)
}

function SpireQuests.giverPos(giver)
	local w = SpireQuests.WHERE[giver]
	if w and w.pos then
		return Position(w.pos[1], w.pos[2], w.pos[3])
	end
	if giver == "Fence Marrow" and SpireQuestObjects and SpireQuestObjects.placed then
		return SpireQuestObjects.placed.marrow
	end
end

-- Pure: "about 41 steps north of the temple"
function SpireQuests.compass(from, to)
	local dx, dy = to.x - from.x, to.y - from.y
	local dist = math.max(math.abs(dx), math.abs(dy))
	if dist <= 4 then
		return "right by the temple"
	end
	local ns = (dy < 0 and -dy * 2.4 > math.abs(dx)) and "north" or ((dy > 0 and dy * 2.4 > math.abs(dx)) and "south" or "")
	local ew = (dx > 0 and dx * 2.4 > math.abs(dy)) and "east" or ((dx < 0 and -dx * 2.4 > math.abs(dy)) and "west" or "")
	local dir = ns ~= "" and ew ~= "" and (ns .. "-" .. ew) or (ns .. ew)
	return string.format("about %d steps %s of the temple", math.floor(dist / 5 + 0.5) * 5, dir)
end

-- "Captain Dorrow (Hearthgate's north gate, outside the guardhouse: about 40 steps north of the temple)"
function SpireQuests.whereText(giver)
	local w = SpireQuests.WHERE[giver]
	if not w then
		return giver
	end
	local pos, temple = SpireQuests.giverPos(giver), WorldPoints and WorldPoints.temple_hearthgate
	if pos and temple and pos.z == temple.z then
		return string.format("%s (%s: %s)", giver, w.place, SpireQuests.compass(temple, pos))
	end
	if pos and temple and math.abs(pos.z - temple.z) == 1 then   -- one level up or down (Vesper, upstairs in the Hearth)
		return string.format("%s (%s: %s, %s)", giver, w.place, pos.z < temple.z and "upstairs" or "downstairs",
			SpireQuests.compass(temple, pos))
	end
	return string.format("%s (%s)", giver, w.place)
end

-- Minimap marks on the givers who have something for this player (once per giver per character)
function SpireQuests.markGivers(player)
	local doneIds, ctx = SpireQuests.doneIds(player), SpireQuests.context(player)
	local marked = player:kv():scoped("spirebound-questmarks")
	for _, q in ipairs(SpireQuests.list) do
		local st = SpireQuests.state(player, q)
		local giver = q.giver
		if q.floor == 1 and not q.auto and (SpireQuests.available(q, st, doneIds, ctx) or st == 2) and not marked:get(giver) then
			local pos = SpireQuests.giverPos(giver)
			if pos and player.addMapMark then
				player:addMapMark(pos, MAPMARK_EXCLAMATION or 2, "Quest: " .. giver)
				marked:set(giver, os.time())
			end
		end
	end
end

-- FD1: The First Climb's eight chapters join the list here, before the client's quest catalog is built
dofile(DATA_DIRECTORY .. "/lib/spirebound/first_climb.lua")
dofile(DATA_DIRECTORY .. "/lib/spirebound/oathroom.lua") -- FD3: the Oathroom's rules and its quest-log entry
