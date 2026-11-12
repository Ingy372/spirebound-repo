-- !hunt, level-up advice and the Arrival Yard start (Jay, 2026-11-11: "players need a sense of direction").
-- The rules live in lib/spirebound/hunting_guide.lua (generated from maps/floor1_plan.py, see BESTIARY.md).
local hunt = TalkAction("!hunt")
function hunt.onSay(player, words, param)
	player:sendTextMessage(MESSAGE_STATUS, SpireHunt.advice(player:getLevel()))
	return false
end
hunt:separator(" ")
hunt:groupType("normal")
hunt:register()

-- When a level takes you past the ground you were using, say where to go next.
local advance = CreatureEvent("SpireHuntAdvice")
function advance.onAdvance(player, skill, oldLevel, newLevel)
	if skill ~= SKILL_LEVEL then
		return true
	end
	local before, after = SpireHunt.recommend(oldLevel), SpireHunt.recommend(newLevel)
	local was, now = before.xp and before.xp.id, after.xp and after.xp.id
	if was ~= now or (before.money and before.money.id) ~= (after.money and after.money.id) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Level " .. newLevel .. "! " .. SpireHunt.advice(newLevel))
	end
	return true
end
advance:register()

-- A short hint at a few early levels, once each.
local HINTS = {
	[2] = "Level 2! Your health and mana grow with every level. Keep fighting: the first levels come fast.",
	[5] = "Level 5! Visit the shops along Hearthgate's north wall: Armorer Hesta, Weaponsmith Garrick, Alchemist Ivo for potions and Fletcher Tamsin for arrows. Say 'hi' and then 'trade' to a merchant.",
	[8] = "Level 8! You have learned your first spells. Say !spells to read them, and say a spell's words to cast it.",
	[10] = "Level 10! Quest givers are waiting: Captain Dorrow at the north gate, Hunter Brannoch in the Hunters' Hall, Miller Agna in Millcross. Press J to see your quest log.",
	[20] = "Level 20! You can be promoted at the Ascendancy in Hearthgate, and you can buy a house.",
}
local hints = CreatureEvent("SpireLevelHints")
function hints.onAdvance(player, skill, oldLevel, newLevel)
	if skill ~= SKILL_LEVEL then
		return true
	end
	for level = oldLevel + 1, newLevel do
		if HINTS[level] then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, HINTS[level])
		end
	end
	return true
end
hints:register()

-- New characters (no path, no difficulty, never seen the yard) start in the Arrival Yard.
local STORAGE_YARD = 50900
local login = CreatureEvent("SpireHuntLogin")
function login.onLogin(player)
	player:registerEvent("SpireHuntAdvice")
	player:registerEvent("SpireLevelHints")
	if player:getVocation():getId() == 0 and Difficulty.get(player) == Difficulty.NONE and player:getStorageValue(STORAGE_YARD) ~= 1 then
		player:setStorageValue(STORAGE_YARD, 1)
		local yard = Town(50)
		if yard then
			player:setTown(yard)
			player:teleportTo(yard:getTemplePosition())
			-- a practice club so the first rats aren't fought bare-handed (2026-11-12 playthrough); the Registrar
			-- gives the real starter kit for your path at the end of the yard
			player:addItem(3270, 1, true, 1, CONST_SLOT_LEFT)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Welcome to Spirebound. Follow the stone path east; Guide Pell will help you. Say !guide for a letter of first steps.")
		end
	end
	return true
end
login:register()
