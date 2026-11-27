-- Archivist Maren: tells The First Climb, Floor 1's story, at the Monument (roadmap FD1; lib/spirebound/first_climb.lua).
-- Placed by maps/floor1_story.py beside the Monument.
local npcName = "Archivist Maren"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the keeper of Hearthgate's records"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
local l = { 138, 58, 77, 77, 115, 0 } -- a robed townswoman in archive grey and ink blue (own art wished for in ART_REQUESTS.md)
npcConfig.outfit = { lookType = l[1], lookHead = l[2], lookBody = l[3], lookLegs = l[4], lookFeet = l[5], lookAddons = l[6] }
npcConfig.flags = { floorchange = false }

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

local FC = SpireFirstClimb

local function current(player)
	return FC.current(function(q) return SpireQuests.state(player, q) end)
end

local perkOffer = {} -- player id -> true while choosing the Floor 1 perk
SpireCleanup.add(function(pid) perkOffer[pid] = nil end)

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local lower = msg:lower()
	local pid = player:getId()
	-- the Floor 1 perk (DESIGN 8.3): chosen here at the end of the First Climb (the Registrar stays in the Arrival
	-- Yard, which climbers cannot go back into)
	local opts = SpireQuests.PERKS[1]
	if perkOffer[pid] then
		for _, o in ipairs(opts) do
			if MsgContains(lower, o.name:lower()) or MsgContains(lower, (o.key:gsub("_", " "))) then
				perkOffer[pid] = nil
				SpirePerks.choose(player, 1, o.key)
				npcHandler:say("Then it's written in the archive, under your name: " .. o.name .. ".", npc, player)
				return true
			end
		end
	end
	if MsgContains(lower, "perk") then
		if SpirePerks.get(player, 1) then
			npcHandler:say("Your Floor 1 perk is already written down.", npc, player)
		elseif SpireQuests.floorStoryDone(player, 1) then
			perkOffer[pid] = true
			npcHandler:say(string.format("For the Heir to the First Climb: choose one, {%s} (%s) or {%s} (%s).", opts[1].name, opts[1].text, opts[2].name, opts[2].text), npc, player)
		else
			npcHandler:say("The Floor 1 perk is for whoever follows the First Climb to the end of their trail, chapter 8.", npc, player)
		end
		return true
	end
	if MsgContains(lower, "wish") or MsgContains(lower, "spire") or MsgContains(lower, "summit") then
		npcHandler:say(FC.PREMISE, npc, player)
		return true
	end
	if MsgContains(lower, "names") or MsgContains(lower, "monument") or MsgContains(lower, "climb") or MsgContains(lower, "story") then
		if FC.isHeir(player) then
			npcHandler:say("Their names are back on the Monument, for you at least: read it. The First Climb went on, above us. Maybe you'll find them on the next floor.", npc, player)
		else
			npcHandler:say("Forty-one climbers went up the stair before Hearthgate was even a town. The First Climb. Their names were chiselled off the Monument, and I mean to put them back. Ask me for a {quest}.", npc, player)
		end
		return true
	end
	-- "quest" when the next chapter waits on a level: say when, not "no work"
	if MsgContains(lower, "quest") or MsgContains(lower, "mission") or MsgContains(lower, "help") then
		local q, st = current(player)
		if q and (st == -1 or st == 0) and q.minLevel and player:getLevel() < q.minLevel then
			local done = SpireQuests.doneIds(player)
			if not q.requires or done[q.requires] then
				npcHandler:say(string.format("The next part of the First Climb's trail, \"%s\", is rough going. Come back when you reach level %d.", q.name:gsub("^.-: ", ""), q.minLevel), npc, player)
				return true
			end
		end
	end
	if SpireQuests.talk(npc, npcHandler, player, msg, npcName) then
		return true
	end
	npcHandler:say("Ask me about the {first climb}, the {Summit Wish}, a {quest}, or {report} when you've found something.", npc, player)
	return true
end

local GREET = "Welcome to the Monument, |PLAYERNAME|. I keep Hearthgate's records, and its oldest mystery: the {first climb}. Ask for a {quest}, or {report} what you've found."
local GREET_READY = "|PLAYERNAME|! You've found something, I can see it on your face. Say {report}."
npcHandler:setMessage(MESSAGE_GREET, GREET)
npcHandler:setCallback(CALLBACK_GREET, function(npc, player)
	local q, st = current(player)
	npcHandler:setMessage(MESSAGE_GREET, (q and st == 2) and GREET_READY or GREET)
	return true
end)
npcHandler:setMessage(MESSAGE_FAREWELL, "Mind the old stones, climber.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
