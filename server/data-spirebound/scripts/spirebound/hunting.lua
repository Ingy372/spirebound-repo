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

-- New characters (no path, no difficulty, never seen the yard) start in the Arrival Yard.
local STORAGE_YARD = 50900
local login = CreatureEvent("SpireHuntLogin")
function login.onLogin(player)
	player:registerEvent("SpireHuntAdvice")
	if player:getVocation():getId() == 0 and Difficulty.get(player) == Difficulty.NONE and player:getStorageValue(STORAGE_YARD) ~= 1 then
		player:setStorageValue(STORAGE_YARD, 1)
		local yard = Town(50)
		if yard then
			player:setTown(yard)
			player:teleportTo(yard:getTemplePosition())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Welcome to Spirebound. Follow the stone path east; Guide Pell will help you. Say !guide for a letter of first steps.")
		end
	end
	return true
end
login:register()
