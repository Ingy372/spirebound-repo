-- Roadmap 2.11: story quests, quest log lines, perks.
SpireTest.add("quests: floor 1 story quests with a next step for every state", function()
	local n = 0
	for _, q in ipairs(SpireQuests.list) do
		if q.floor == 1 then
			n = n + 1
			for _, st in ipairs({ -1, 1, 2, 3 }) do
				local line = SpireQuests.logText(q, st, 3)
				if not line or line == "" then error(q.id .. " has no log line for state " .. st) end
			end
			if not q.kind and not MonsterType(q.target) then error(q.id .. " targets unknown monster " .. tostring(q.target)) end
		end
	end
	SpireTest.eq(n, 18, "eighteen floor 1 quests: nine story (with the weapon temper and the armour line), eight side (four not about killing: stones, sluice, flour, the Stair Key) and the tutorial quest")
	local story = 0
	for _, q in ipairs(SpireQuests.list) do
		if q.floor == 1 and not q.side then story = story + 1 end
	end
	SpireTest.eq(story, 9, "nine story quests (the perk needs only these)")
	local q3 = SpireQuests.get("q1_3")
	SpireTest.eq(SpireQuests.available(q3, -1, {}), false, "Millstone needs Bread for the Road first")
	SpireTest.eq(SpireQuests.available(q3, -1, { q1_1 = true }), true, "then it opens")
	SpireTest.eq(SpireQuests.logText(SpireQuests.get("q1_1"), 1, 4), "Hunt Bristle Boars in the boar meadow (south-west of Hearthgate): 4 of 15.", "progress line")
	SpireTest.eq(#SpireQuests.PERKS[1], 2, "pick 1 of 2 perks")
end)

SpireTest.add("quests: quest log catalog loaded", function()
	local found = 0
	for _, quest in pairs(Quests or {}) do
		if quest.name == "Bread for the Road" or quest.name == "The Lost Patrol" or quest.name == "Millstone" then
			found = found + 1
		end
	end
	SpireTest.eq(found, 3, "quests in the client quest log")
end)

-- FLOOR1_REVIEW.md F1-21: every Floor 1 quest pays experience as well
SpireTest.add("quests: every Floor 1 quest pays experience", function()
	local missing = {}
	for _, q in ipairs(SpireQuests.list) do
		if q.floor == 1 and not (q.reward.exp and q.reward.exp > 0) then
			table.insert(missing, q.id)
		end
	end
	SpireTest.eq(table.concat(missing, ","), "", "Floor 1 quests without experience")
end)

-- FLOOR1_REVIEW.md F1-23: players see what a quest pays before they take it
SpireTest.add("quests: the reward line names gold, experience, title, gear and tempering", function()
	SpireTest.eq(SpireQuests.rewardText({ gold = 600, exp = 4950 }), "Reward: 600 gold, 4,950 experience.", "gold and experience")
	SpireTest.eq(SpireQuests.rewardText({ exp = 300, title = "Millhand", gear = true, temper = true }),
		"Reward: 300 experience, the title \"Millhand\", a piece of Floor gear, your weapon tempered one tier.", "the rest")
	SpireTest.eq(SpireQuests.rewardText({}), "", "nothing to say")
end)

-- G3 (Grok playtest 2026-11-24): the Quest Tracker only shows quests the game's quest log knows
SpireTest.add("quests: every quest is in the game's quest log (so the Quest Tracker can show it)", function()
	local inLog = {}
	for _, entry in ipairs(Quests or {}) do
		inLog[entry.startStorageId] = entry.name
	end
	local missing = {}
	for _, q in ipairs(SpireQuests.list) do
		if inLog[q.storage] ~= q.name then
			table.insert(missing, q.name)
		end
	end
	SpireTest.eq(table.concat(missing, ", "), "", "quests missing from the quest log")
end)

-- P9: quests that aren't "kill N of X" (scripts/spirebound/quest_objects.lua)
SpireTest.add("quests: the builders' stones, the sluice and Fence Marrow are on the map", function()
	local p = SpireQuestObjects.placed
	for _, s in ipairs(SpireQuestObjects.STONES) do
		local pos = p["stone_" .. s.id]
		SpireTest.eq(pos ~= nil, true, "a builders' stone in " .. s.id)
		local t = pos and Tile(pos)
		SpireTest.eq(t ~= nil and t:getItemById(2199) ~= nil, true, "the stone stands in " .. s.id)
	end
	SpireTest.eq(p.sluice ~= nil, true, "the sluice levers")
	for i = 0, 2 do
		local t = p.sluice and Tile(Position(p.sluice.x + i, p.sluice.y, p.sluice.z))
		SpireTest.eq(t ~= nil and (t:getItemById(2772) or t:getItemById(2773)) ~= nil, true, "sluice lever " .. (i + 1))
	end
	SpireTest.eq(p.sluice_hint ~= nil, true, "the stone with the lever order")
	SpireTest.eq(p.marrow ~= nil, true, "Fence Marrow has a spot")
	local found = false
	for _, c in ipairs(p.marrow and Game.getSpectators(p.marrow, false, false, 1, 1, 1, 1) or {}) do
		if c:isNpc() and c:getName() == "Fence Marrow" then
			found = true
		end
	end
	SpireTest.eq(found, true, "Fence Marrow stands by the Bandit Road")
end)

SpireTest.add("quests: the sluice levers only open in the carved order", function()
	local pull = SpireQuestObjects.pull
	SpireTest.eq(pull({}, 1), "wrong", "the fish lever first is wrong")
	SpireTest.eq(pull({}, 2), "next", "the sun lever first")
	SpireTest.eq(pull({ 2 }, 3), "next", "then the reed")
	SpireTest.eq(pull({ 2, 3 }, 1), "solved", "and last the fish")
	SpireTest.eq(pull({ 2 }, 1), "wrong", "skipping the reed resets")
end)

SpireTest.add("quests: collect and delivery quests read right in the log", function()
	local stones = SpireQuests.get("l1_stones")
	SpireTest.eq(SpireQuests.logText(stones, 1, 4):find("4 of 6") ~= nil, true, "stones count in the log")
	local flour = SpireQuests.get("d1_flour")
	SpireTest.eq(SpireQuests.logText(flour, 1, 0):find("Captain Dorrow") ~= nil, true, "the delivery names where to go")
	SpireTest.eq(flour.choices["Captain Dorrow"] ~= nil and flour.choices["Fence Marrow"] ~= nil, true, "two ways to finish it")
	SpireTest.eq(SpireQuests.rewardText(flour.reward):find("Honest Carter") ~= nil, true, "the offer shows the honest reward")
end)

SpireTest.add("quests: the Stair Key guards the Axe-Lord's hall door", function()
	local door, back = SpireStairKey.door, SpireStairKey.back
	SpireTest.eq(door ~= nil and back ~= nil, true, "the door and the way back are known")
	local hall = WorldPoints.boss_room_floor1_nw
	local se = WorldPoints.boss_room_floor1_se
	SpireTest.eq(door.x >= hall.x and door.x <= se.x and door.y >= hall.y and door.y <= se.y and door.z == hall.z, true, "the door is inside the hall")
	local t = Tile(back)
	SpireTest.eq(t ~= nil and t:isWalkable(false, false, false, false, true), true, "the way back is open floor")
	local key = SpireQuests.get("k1_stairkey")
	SpireTest.eq(SpireQuests.available(key, -1, {}, { level = 100 }), false, "nobody offers the key: it starts by itself")
	SpireTest.eq(SpireQuests.logText(key, -1, 0):find("Gate Hound") ~= nil, true, "the log says what the pieces are")
	SpireTest.eq(MonsterType("Stonehorn Ram") ~= nil, true, "the Stonehorn Ram exists")
end)
