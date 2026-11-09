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
		if q.floor == floor and SpireQuests.state(player, q) ~= 3 then
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

function SpirePerks.apply(player)
	player:removeCondition(CONDITION_ATTRIBUTES, CONDITIONID_DEFAULT, 4501)
	player:removeCondition(CONDITION_HASTE, CONDITIONID_DEFAULT, 4502)
	local p1 = SpirePerks.get(player, 1)
	if p1 == "thick_skin" then
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, 4501)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		c:setParameter(CONDITION_PARAM_STAT_MAXHITPOINTSPERCENT, 105)
		player:addCondition(c)
	elseif p1 == "light_step" then
		local c = Condition(CONDITION_HASTE)
		c:setParameter(CONDITION_PARAM_SUBID, 4502)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		c:setParameter(CONDITION_PARAM_SPEED, 10)
		player:addCondition(c)
	end
end

-- Shared NPC dialogue for quest givers. Returns true if it handled the message.
local offered = {} -- playerId -> quest id
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
				npcHandler:say(q.offer .. " ({yes} or {no})", npc, player)
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
