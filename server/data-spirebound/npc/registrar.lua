-- The Registrar: end of the Arrival Yard. New characters pick a vocation and a difficulty here
-- (DESIGN.md 5.1, 5.4). Later the Registrar also lets characters step DOWN a difficulty.
local npcName = "Registrar Maelis"

local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the Registrar of Hearthgate"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 141, lookHead = 41, lookBody = 72, lookLegs = 39, lookFeet = 76, lookAddons = 0 }
npcConfig.flags = { floorchange = false }

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)

npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

-- Vocation ids follow server/core-overrides/XML/vocations.xml
local VOCATIONS = {
-- Each pitch says how the path plays, how hard it is and its first spells (Grok playtest, 2026-11-24: "one line each
-- is too thin for the biggest choice a new player makes"). Claude's call, Jay can veto.
	vanguard = { id = 4, text = "Vanguards hold the front line with sword, axe or club and a shield. The toughest path and the simplest to learn: walk up to a monster and hit it. Your first spells: heavy strike, and second wind to heal yourself from level 4. Strong alone, and every group wants one in front." },
	ranger = { id = 3, text = "Rangers strike from afar with bow, crossbow or spear. Keep your distance and keep moving; you will buy arrows as you go. Your first spells: piercing shot, and field dressing to heal from level 4. Good alone and in a group; a little harder to play than a vanguard." },
	arcanist = { id = 1, text = "Arcanists wield wands and fill the field with fire and lightning. The hardest hitters and the most fragile: kill things before they reach you. Your first spells: ember strike, and mending spark to heal from level 4. The trickiest path to start with, and the best against crowds." },
	mystic = { id = 2, text = "Mystics wield rods, heal their allies and command nature. Steady and hard to kill, with the best healing in the tower; every group wants one. Your first spells: frost strike, and dewfall to heal from level 4. A good first path if you like to stay alive." },
}

local FIRST_SPELLS = SpireClient.FIRST_SPELLS -- each path's first attack spell and heal (lib/spirebound/client_link.lua)
local PRACTICE_CLUB = 3270 -- handed out in the Arrival Yard (scripts/spirebound/hunting.lua)

-- Starter kits (client item ids, Tibia 15.11)
local KITS = {
	[4] = { { 3264, 1 }, { 3412, 1 } }, -- sword, wooden shield
	[3] = { { 3350, 1 }, { 3277, 2 } }, -- bow and spears; the arrows come inside a quiver (giveKit below)
	[1] = { { 3074, 1 } }, -- wand of vortex
	[2] = { { 3066, 1 } }, -- snakebite rod
}
local COMMON_KIT = { { 3361, 1 }, { 3355, 1 }, { 3559, 1 }, { 3552, 1 }, { 3582, 5 }, { 266, 5 }, { 268, 5 }, { 3003, 1 }, { 3457, 1 }, { 2920, 1 } }
-- leather armor, leather helmet, leather legs, leather boots, ham, health/mana potions, rope, shovel
-- the armour goes on straight away (Grok session 3: every new character walked about with it in the backpack)
local TOOLS = { [3003] = true, [3457] = true, [2920] = true } -- rope, shovel, torch: one is enough
local WEAR = { [3361] = CONST_SLOT_ARMOR, [3355] = CONST_SLOT_HEAD, [3559] = CONST_SLOT_LEGS, [3552] = CONST_SLOT_FEET }

local MODES = {
	["normal"] = { id = Difficulty.NORMAL, text = "Normal: the tower's usual rules. Death costs experience, as it always has." },
	["hardcore"] = { id = Difficulty.HARDCORE, text = "Hardcore: deaths cost half again as much, but you earn 25% more experience and 15% more loot." },
	["death game"] = { id = Difficulty.DEATHGAME, text = "Death Game: if a monster or the tower kills you, this character is gone for good. In return: 50% more experience, 30% more loot, and honours no one else can earn. Another player can never end you this way." },
}

local chosen = {} -- playerId -> { voc = id, mode = id }

local function giveKit(player, vocId)
	-- Take back the yard's practice club and put the path's weapon in the hand, so the skill bar on the right shows
	-- this path's skills at once (Grok playtest, 2026-11-24: a Mystic still held the club and saw club skills).
	while player:removeItem(PRACTICE_CLUB, 1) do end
	-- Weapons first, then the Ranger's quiver straight into the shield hand, then armour worn and the rest in the
	-- backpack. Nothing is limited by carrying weight (SpireGive): a level 3 Ranger once lost its quiver to the floor
	-- because the kit was too heavy (Grok session 3).
	SpireGive.withRoom(player, function()
		for i, entry in ipairs(KITS[vocId] or {}) do
			local slot = (i == 1 and CONST_SLOT_LEFT) or (vocId == 4 and i == 2 and CONST_SLOT_RIGHT) or nil
			SpireGive.item(player, entry[1], entry[2], slot)
		end
		if vocId == 3 then
			SpireQuiver.give(player, 100) -- a bow only fires from a quiver in the shield hand (Jay's playtest, 2026-11-13)
		end
		for _, entry in ipairs(COMMON_KIT) do
			-- tools the yard already gave (rope, shovel, torch) are not given twice (C3, Claude's playtest 2026-11-25)
			if not (TOOLS[entry[1]] and player:getItemCount(entry[1]) > 0) then
				SpireGive.item(player, entry[1], entry[2], WEAR[entry[1]])
			end
		end
	end)
	if SpireGuide then
		SpireGuide.giveLetter(player) -- lore and first steps
	end
end

local function greetCallback(npc, player)
	if Difficulty.get(player) == Difficulty.NONE then
		npcHandler:setMessage(MESSAGE_GREET, "Welcome to Hearthgate, |PLAYERNAME|. Before you climb, choose your path: {vanguard}, {ranger}, {arcanist} or {mystic}?")
	else
		npcHandler:setMessage(MESSAGE_GREET, "Back again, |PLAYERNAME|? If the tower weighs too heavy, I can let you {step down} to an easier way of living.")
	end
	return true
end

local function creatureSayCallback(npc, player, type, msg)
	local pid = player:getId()
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local topic = npcHandler:getTopic(pid)
	local lower = msg:lower()

	if Difficulty.get(player) == Difficulty.NONE then
		for key, voc in pairs(VOCATIONS) do
			if MsgContains(lower, key) and topic <= 1 then
				chosen[pid] = { voc = voc.id }
				npcHandler:say(voc.text .. " Will you walk the path of the " .. key .. "? {yes} or {no}?", npc, player)
				npcHandler:setTopic(pid, 1)
				return true
			end
		end
		if topic == 1 and MsgContains(lower, "yes") then
			npcHandler:say("Good. Now choose how you will live in the tower. {normal}: a death costs you some experience. {hardcore}: deaths cost more, but you earn more. {death game}: one death to a monster and this character is gone for good, for the biggest rewards. Say one to hear the details. You may always step down later, but never up.", npc, player)
			npcHandler:setTopic(pid, 2)
			return true
		end
		if topic == 2 or topic == 3 then
			for key, mode in pairs(MODES) do
				if MsgContains(lower, key) and not (key == "normal" and MsgContains(lower, "death")) then
					chosen[pid].mode = mode.id
					npcHandler:say(mode.text .. " Is that your choice? {yes} or {no}?", npc, player)
					npcHandler:setTopic(pid, 3)
					return true
				end
			end
		end
		if topic == 3 and MsgContains(lower, "yes") and chosen[pid] and chosen[pid].mode then
			local c = chosen[pid]
			if not Difficulty.set(player, c.mode) then
				npcHandler:say("Something is wrong with your papers. Speak to a gamemaster.", npc, player)
				return true
			end
			player:setVocation(Vocation(c.voc))
			giveKit(player, c.voc)
			player:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
			npcHandler:say(string.format("It is written: %s, %s. One last step before Hearthgate: the Proving, below us. Climb well.", player:getVocation():getName(), Difficulty.names[c.mode]), npc, player)
			-- Confirm in the Server Log too: the speech bubble is easy to miss (Grok playtest, 2026-11-24)
			local first = FIRST_SPELLS[c.voc]
			SpireClient.seedSpellBar(player, true)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You are now %s %s, living by the %s rules.", player:getVocation():getName():match("^[AEIOUaeiou]") and "an" or "a", player:getVocation():getName(), Difficulty.names[c.mode]))
			if first then
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Your attack spell: %s. Click a monster to target it, then say the words (it is on your action bar too). At level 4 you learn %s, which heals you. Say !spells for the full list.", first[1], first[2])) -- F1-02
			end
			player:setTown(Town(1)) -- the Arrival Yard was only the starting town
			-- G2: the tutorial goes on in the Proving (scripts/spirebound/proving.lua), then on to Hearthgate
			local proving = WorldPoints.proving_arrival
			player:teleportTo(proving and Position(proving.x, proving.y, proving.z) or Town(1):getTemplePosition())
			player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
			if proving then -- the hall's rats come straight at you (Grok session 2: "unannounced")
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The Proving. A few rats live in this hall and will come for you: try your attack spell on them. Your spells are on the action bar; the row of buttons at the bottom of the screen holds your weapon skills (Ctrl+1, 2, 3, or click them), which come with the weapon in your hand. Warden Ketta can heal you.")
			end
			chosen[pid] = nil
			npcHandler:setTopic(pid, 0)
			return true
		end
		-- "no" to a mode goes back to the modes, not all the way to the paths (Grok session 2)
		if topic == 3 and MsgContains(lower, "no") then
			npcHandler:say("Then choose how you will live: {normal}, {hardcore} or {death game}?", npc, player)
			npcHandler:setTopic(pid, 2)
			return true
		end
		if MsgContains(lower, "no") then
			npcHandler:say("Then choose again: {vanguard}, {ranger}, {arcanist} or {mystic}?", npc, player)
			npcHandler:setTopic(pid, 0)
			return true
		end
		return true
	end

	-- Floor perks (DESIGN.md 8.3): one choice per floor, after all of that floor's story quests
	if MsgContains(lower, "perk") then
		for floor = 1, Floors.LAUNCH_FLOORS do
			local opts = SpireQuests.PERKS[floor]
			if opts and SpireQuests.floorStoryDone(player, floor) and not SpirePerks.get(player, floor) then
				npcHandler:say(string.format("Floor %d perk. Choose one: {%s} (%s) or {%s} (%s).", floor, opts[1].name, opts[1].text, opts[2].name, opts[2].text), npc, player)
				npcHandler:setTopic(pid, 100 + floor)
				return true
			end
		end
		npcHandler:say("No perk is waiting for you. Perks come from finishing every story quest on a floor.", npc, player)
		return true
	end
	if topic > 100 and topic <= 100 + Floors.LAUNCH_FLOORS then
		local floor = topic - 100
		for _, o in ipairs(SpireQuests.PERKS[floor] or {}) do
			if MsgContains(lower, o.name:lower()) then
				SpirePerks.choose(player, floor, o.key)
				npcHandler:say("It is written: " .. o.name .. ".", npc, player)
				npcHandler:setTopic(pid, 0)
				return true
			end
		end
	end

	-- Already registered: stepping down
	local current = Difficulty.get(player)
	if MsgContains(lower, "step down") then
		local options = {}
		for key, mode in pairs(MODES) do
			if Difficulty.canChange(current, mode.id) then
				table.insert(options, "{" .. key .. "}")
			end
		end
		if #options == 0 then
			npcHandler:say("You already live by the gentlest rules the tower has.", npc, player)
		else
			npcHandler:say("You may step down to " .. table.concat(options, " or ") .. ". This can never be undone.", npc, player)
			npcHandler:setTopic(pid, 10)
		end
		return true
	end
	if topic == 10 then
		for key, mode in pairs(MODES) do
			if MsgContains(lower, key) and not (key == "normal" and MsgContains(lower, "death")) and Difficulty.canChange(current, mode.id) then
				chosen[pid] = { mode = mode.id }
				npcHandler:say("Step down to " .. Difficulty.names[mode.id] .. " forever? {yes} or {no}?", npc, player)
				npcHandler:setTopic(pid, 11)
				return true
			end
		end
	end
	if topic == 11 and MsgContains(lower, "yes") and chosen[pid] then
		Difficulty.set(player, chosen[pid].mode)
		npcHandler:say("It is written. You now live by the " .. Difficulty.names[chosen[pid].mode] .. " rules.", npc, player)
		chosen[pid] = nil
		npcHandler:setTopic(pid, 0)
		return true
	end
	return true
end

npcHandler:setCallback(CALLBACK_GREET, greetCallback)
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:setMessage(MESSAGE_FAREWELL, "May the tower be kind to you.")
npcHandler:setMessage(MESSAGE_WALKAWAY, "Come back when you are ready to choose.")
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
