-- Story quests and floor perks (DESIGN.md 8.3). Roadmap 2.11.
-- Every quest shows its next step in the client's quest log (lib/core/quests/catalog/q*.lua read from here).
-- Storage values: -1 not started, 1 hunting, 2 ready to report, 3 done.

SpireQuests = {
	list = {
		{ id = "q1_1", floor = 1, name = "Bread for the Road", giver = "Miller Agna", storage = 50101, killStorage = 50111,
			target = "Bristle Boar", count = 15, reward = { gold = 600 },
			offer = "The inn is out of meat and the climbers are hungry. Hunt 15 bristle boars in the meadow south-west of Hearthgate. Will you?",
			step = "Hunt Bristle Boars in the boar meadow (south-west of Hearthgate): %d of %d.",
			report = "Return to Miller Agna in Millcross and say 'report'.",
			thanks = "Wonderful! The stew pot will be full for a week. Here's 600 gold." },
		{ id = "q1_2", floor = 1, name = "The Lost Patrol", giver = "Captain Dorrow", storage = 50102, killStorage = 50112,
			target = "Bandit Captain", count = 2, reward = { gold = 1200 },
			offer = "My patrol never came back from the bandit road in the east. Two bandit captains run that road. Bring them down?",
			step = "Defeat Bandit Captains on the bandit road (east of Hearthgate): %d of %d.",
			report = "Return to Captain Dorrow at Hearthgate's north gate and say 'report'.",
			thanks = "Then my men are avenged. Take this, 1,200 gold, and my thanks." },
		{ id = "q1_3", floor = 1, name = "Millstone", giver = "Miller Agna", storage = 50103, killStorage = 50113,
			target = "Thornsnap", count = 20, reward = { gold = 900, title = "Millhand" }, requires = "q1_1",
			offer = "Thornsnaps have overgrown the old mill road in the hollow north of town. Clear 20 of them so the millstones can come through?",
			step = "Clear Thornsnaps in the thornsnap hollow (north-west of Hearthgate): %d of %d.",
			report = "Return to Miller Agna in Millcross and say 'report'.",
			thanks = "The road's clear! You've earned the name Millhand, and 900 gold." },
		-- R12: a hand-written quest line whose reward is gear for your path, not gold
		{ id = "q1_iron1", floor = 1, side = true, name = "Iron for the Stair (1 of 2)", giver = "Hunter Brannoch", storage = 50131, killStorage = 50132,
			target = "Burrow Mole", count = 25, reward = { gold = 200 },
			offer = "The Hall's armourer wants mole claws for rivets: they never rust. Twenty-five moles from Burrow Hills, north-east of town. Will you?",
			step = "Hunt Burrow Moles in Burrow Hills (north-east of Hearthgate): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "Good claws. Here's a little for the walk. Ask me for a quest again: the armourer has one more request." },
		{ id = "q1_iron2", floor = 1, side = true, name = "Iron for the Stair (2 of 2)", giver = "Hunter Brannoch", storage = 50133, killStorage = 50134,
			target = "Road Bandit", count = 30, reward = { gear = true }, requires = "q1_iron1",
			offer = "The rivets need iron, and the bandits east of town stole a cartload of it. Take back thirty bandits' worth of it. The armourer will make you something for your path.",
			step = "Defeat Road Bandits on the Bandit Road (east of Hearthgate): %d of %d.",
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
			target = "Pen Rat", count = 3, reward = { gold = 100 },
			offer = "Let's find out what you can do. The rat pen is just along the path: defeat three of its rats. Ready?",
			step = "Defeat the rats in the pen along the stone path: %d of %d.",
			report = "Return to Guide Pell at the start of the path and say 'report'.",
			thanks = "Well fought! Here are 100 gold. Now follow the path to the Registrar. Say 'hunt' to me any time you wonder where to fight next." },
		-- more of the Hearthgate ladder (each one sends you to the next step: see BESTIARY.md)
		{ id = "q1_4", floor = 1, name = "Wasp Nest", giver = "Captain Dorrow", storage = 50104, killStorage = 50114,
			target = "Meadow Wasp", count = 12, reward = { gold = 500 },
			offer = "Wasps have nested in the fields just north of the gate, and they sting my guards. Clear out 12 of them?",
			step = "Kill Meadow Wasps in the Waspgrass Fields (just north of Hearthgate): %d of %d.",
			report = "Return to Captain Dorrow at Hearthgate's north gate and say 'report'.",
			thanks = "Quiet at last. Here is 500 gold for your trouble." },
		{ id = "q1_5", floor = 1, name = "Pelts for the Hall", giver = "Hunter Brannoch", storage = 50105, killStorage = 50115,
			target = "Meadow Wolf", count = 20, reward = { gold = 1200 },
			offer = "The Hunters' Hall needs wolf pelts. The wolves of the Copse, across the river beside Millcross, will do. Twenty of them. Will you hunt them?",
			step = "Kill Meadow Wolves in the Wolf Copse (west, across the river): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall (north of the plaza) and say 'report'.",
			thanks = "Fine pelts. The Hall pays 1,200 gold, and I have more work if you want it." },
		{ id = "q1_6", floor = 1, name = "Quarry Watch", giver = "Hunter Brannoch", storage = 50106, killStorage = 50116,
			target = "Ruin Archer", count = 10, reward = { gold = 2500, title = "Quarrywatch" }, requires = "q1_5",
			offer = "Archers have taken the Old Quarry, north of town, and our scouts cannot pass. Bring down ten of them. A long walk, and a real fight. Ready?",
			step = "Kill Ruin Archers in the Old Quarry (north of Hearthgate): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "The scouts can pass again. You have earned the title Quarrywatch and 2,500 gold." },
		-- side quests: they pay well but do not block the Floor 1 perk
		{ id = "s1_1", floor = 1, side = true, name = "Snapper Season", giver = "Fisher Corwin", storage = 50107, killStorage = 50117,
			target = "Reed Snapper", count = 15, reward = { gold = 1500 },
			offer = "Snappers are tearing my nets in the marsh across the river. Thin them out: fifteen. I'll pay what I can.",
			step = "Kill Reed Snappers in Reedmarsh (south-west, across the river): %d of %d.",
			report = "Return to Fisher Corwin at the Fisher's Huts and say 'report'.",
			thanks = "My nets will last the season. Take 1,500 gold." },
		{ id = "s1_2", floor = 1, side = true, name = "Mole Hills", giver = "Miller Agna", storage = 50108, killStorage = 50118,
			target = "Burrow Mole", count = 15, reward = { gold = 1000 }, requires = "q1_1",
			offer = "Moles from the Burrow Hills are digging up the grain road. Fifteen of them should discourage the rest. Will you?",
			step = "Kill Burrow Moles in the Burrow Hills (north-east of Hearthgate): %d of %d.",
			report = "Return to Miller Agna in Millcross and say 'report'.",
			thanks = "The road is whole again. Here's 1,000 gold." },
		{ id = "s1_3", floor = 1, side = true, name = "The Alpha", giver = "Hunter Brannoch", storage = 50109, killStorage = 50119,
			target = "Grey Alpha", count = 1, reward = { gold = 1800 }, requires = "q1_5",
			offer = "One Grey Alpha leads every wolf pack, and it calls its wolves when hurt. Kill one and I will pay you well. Interested?",
			step = "Kill a Grey Alpha in the Wolf Copse: %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "An Alpha! That is a hunter's work. 1,800 gold." },
		{ id = "s1_4", floor = 1, side = true, name = "Shard Hunt", giver = "Hunter Brannoch", storage = 50110, killStorage = 50120,
			target = "Field Shardling", count = 20, reward = { gold = 2200 }, requires = "s1_3",
			offer = "The Shard Fields, south-east of the city, are filling with shardlings. Twenty of them, if you can stand their sting. Are you in?",
			step = "Kill Field Shardlings in the Shard Fields (south-east of Hearthgate): %d of %d.",
			report = "Return to Hunter Brannoch in the Hunters' Hall and say 'report'.",
			thanks = "Twenty shardlings. You are becoming a real climber. 2,200 gold." },
	},
	PERKS = {
		[1] = {
			{ key = "thick_skin", name = "Thick Skin", text = "+5% maximum health" },
			{ key = "light_step", name = "Light Step", text = "+10 movement speed" },
		},
	},
}

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
	return math.max(0, player:getStorageValue(q.killStorage))
end

-- Pure: the quest-log line for a state
function SpireQuests.logText(q, state, kills)
	if state == 1 then
		return string.format(q.step, math.min(kills, q.count), q.count)
	elseif state == 2 then
		return q.report
	elseif state == 3 then
		return "Completed."
	end
	return "Talk to " .. q.giver .. "."
end

-- Pure: may this player start the quest? doneIds = set of completed quest ids
function SpireQuests.available(q, state, doneIds)
	if state ~= -1 and state ~= 0 then
		return false
	end
	return not q.requires or doneIds[q.requires] == true
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
local offered = {} -- playerId -> quest id
SpireCleanup.add(function(pid) offered[pid] = nil end)
function SpireQuests.talk(npc, npcHandler, player, msg, giver)
	local lower = msg:lower()
	local pid = player:getId()
	if MsgContains(lower, "report") then
		for _, q in ipairs(SpireQuests.list) do
			if q.giver == giver then
				local st = SpireQuests.state(player, q)
				if st == 2 then
					player:setStorageValue(q.storage, 3)
					if q.reward.gold then player:addMoney(q.reward.gold) end
					if q.reward.title then player:kv():scoped("spirebound-titles"):set(q.reward.title, os.time()) end
					if q.reward.gear then SpireGear.give(player, q.floor, "quest") end -- R12: a reward that isn't gold
					npcHandler:say(q.thanks, npc, player)
					if SpireQuests.floorStoryDone(player, q.floor) then
						player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You finished every story quest on Floor " .. q.floor .. ". Registrar Maelis in Hearthgate can grant you a perk: say 'perk'.")
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
	if MsgContains(lower, "quest") or MsgContains(lower, "mission") or MsgContains(lower, "help") then
		local done = SpireQuests.doneIds(player)
		for _, q in ipairs(SpireQuests.list) do
			if q.giver == giver and SpireQuests.available(q, SpireQuests.state(player, q), done) then
				offered[pid] = q.id
				npcHandler:say(q.offer .. " Say {yes} or {no}.", npc, player)
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
		npcHandler:say("Thank you! It's in your quest log.", npc, player)
		return true
	end
	if MsgContains(lower, "no") and offered[pid] then
		offered[pid] = nil
		npcHandler:say("Maybe another time.", npc, player)
		return true
	end
	return false
end
