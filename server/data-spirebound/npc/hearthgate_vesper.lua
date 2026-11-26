-- Vesper, the Info Broker (DESIGN.md 8.1). Buys secrets and makes them public.
local npcName = "Vesper"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "Vesper, the information broker"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 2010, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0 }
npcConfig.flags = { floorchange = false }
npcConfig.voices = { interval = 20000, chance = 30, { text = "Everything has a price. Especially what nobody else knows." } }

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local lower = msg:lower()
	if lower == "hi" or lower == "hello" or lower == "hey" then -- G11: a second greeting while already talking
		local text = VesperGreeting(SpireQuests.state(player, SpireQuests.get("l1_stones")), SpireQuests.collected(player, "builders"))
		npcHandler:say((text:gsub("|PLAYERNAME|", player:getName())), npc, player)
		return true
	end
	if lower == "secrets" or lower == "mine" then
		local names = {}
		for _, s in ipairs(SpireSecrets.foundList(player)) do
			local by = SpireSecrets.publicBy(s.id)
			table.insert(names, s.name .. (by and " (public)" or (" (unsold, " .. SpireSecrets.payout(s) .. " gold)")))
		end
		npcHandler:say(#names == 0 and "You haven't found anything yet. Go and look." or ("You know of: " .. table.concat(names, ", ") .. ". Say {sell} and the name to sell one."), npc, player)
		return true
	end
	if lower == "list" or lower == "board" then
		local lines = {}
		for _, s in ipairs(SpireSecrets.list) do
			local by = SpireSecrets.publicBy(s.id)
			if by then
				table.insert(lines, s.name .. " (Floor " .. s.floor .. "): " .. s.hint)
			end
		end
		npcHandler:say(#lines == 0 and "Nobody has sold me anything yet." or table.concat(lines, " | "), npc, player)
		return true
	end
	local name = lower:match("^sell%s+(.+)$")
	if name then
		for _, s in ipairs(SpireSecrets.list) do
			if s.name:lower() == name then
				local ok, why = SpireSecrets.canSell(SpireSecrets.hasFound(player, s.id), SpireSecrets.publicBy(s.id))
				if not ok then
					npcHandler:say(why, npc, player)
					return true
				end
				local pay = SpireSecrets.payout(s)
				SpireSecrets.markPublic(s.id, player:getName())
				player:setBankBalance(player:getBankBalance() + pay)
				player:kv():scoped("spirebound-informant"):set(s.id, os.time())
				npcHandler:say("A pleasure. " .. pay .. " gold, straight to your bank.", npc, player)
				Game.broadcastMessage(string.format("%s has sold word of %s on Floor %d! Ask Vesper in Hearthgate for directions.", player:getName(), s.name, s.floor), MESSAGE_EVENT_ADVANCE)
				return true
			end
		end
		npcHandler:say("I don't know a secret by that name.", npc, player)
		return true
	end
	SpireQuests.talk(npc, npcHandler, player, msg, npcName) -- P9: The Builders' Stones
	return true
end

-- G11 (Grok session 3): with her stones quest running, a second "hi" gave the whole broker speech again, in one long
-- bubble that overlapped itself. Now she greets by where you are with the quest, in short lines.
local GREET = "Ah, |PLAYERNAME|. Found a secret? Say {secrets}, {sell} <name> or {list}. I also pay for old stories: ask for a {quest}."
local STONE_PLACES = { boar_meadow = "Boar Meadow", wolf_copse = "Wolf Copse", reed_marsh = "Reedmarsh",
	thornsnap_hollow = "Thornsnap Hollow", shard_fields = "the Shard Fields", burrow_hills = "the Burrow Hills" }

-- Pure: Vesper's greeting for a quest state (-1/0 not taken, 1 running, 2 ready, 3 done) and the stones read so far
function VesperGreeting(state, found)
	if state == 2 then
		return "|PLAYERNAME|! All six stones read? Say {report} and tell me the story."
	elseif state == 1 then
		local left = {}
		for _, id in ipairs({ "boar_meadow", "wolf_copse", "reed_marsh", "thornsnap_hollow", "shard_fields", "burrow_hills" }) do
			if not found[id] then
				table.insert(left, STONE_PLACES[id])
			end
		end
		return string.format("Back, |PLAYERNAME|? %d of 6 stones read. Still to find: %s.", 6 - #left, table.concat(left, ", "))
	end
	return GREET
end

npcHandler:setMessage(MESSAGE_GREET, GREET)
npcHandler:setCallback(CALLBACK_GREET, function(npc, player)
	local q = SpireQuests.get("l1_stones")
	npcHandler:setMessage(MESSAGE_GREET, VesperGreeting(SpireQuests.state(player, q), SpireQuests.collected(player, "builders")))
	return true
end)
-- G11: the engine's greeting ignores "hi" from someone already talking to her (she said nothing). Her own greeting
-- keywords come first: talking already -> the short progress line again; otherwise the normal greeting.
local function vesperHi(npc, player, message)
	if npcHandler:checkInteraction(npc, player) then
		local text = VesperGreeting(SpireQuests.state(player, SpireQuests.get("l1_stones")), SpireQuests.collected(player, "builders"))
		npcHandler:say((text:gsub("|PLAYERNAME|", player:getName())), npc, player)
	else
		npcHandler:onGreet(npc, player, message)
	end
	return true
end
keywordHandler:addKeyword({ "hi", callback = FocusModule.messageMatcher }, vesperHi)
keywordHandler:addKeyword({ "hello", callback = FocusModule.messageMatcher }, vesperHi)
npcHandler:setMessage(MESSAGE_FAREWELL, "Keep your eyes open.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
