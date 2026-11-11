-- Local test characters (server/sql/dev_accounts.sql): on first login give them a difficulty and a
-- starter kit, the way the Registrar would. Does nothing for any other character.
local SEEDED = {
	["Test Vanguard"] = { mode = Difficulty.NORMAL, kit = { { 3264, 1 }, { 3412, 1 } } },
	["Test Ranger"] = { mode = Difficulty.NORMAL, kit = { { 3350, 1 }, { 3447, 200 }, { 3277, 2 } } },
	["Test Arcanist"] = { mode = Difficulty.NORMAL, kit = { { 3074, 1 } } },
	["Test Mystic"] = { mode = Difficulty.NORMAL, kit = { { 3066, 1 } } },
	["Test Hardcore"] = { mode = Difficulty.HARDCORE, kit = { { 3264, 1 }, { 3412, 1 } } },
}
local COMMON = { { 3361, 1 }, { 3355, 1 }, { 3559, 1 }, { 3552, 1 }, { 3582, 5 }, { 266, 20 }, { 268, 20 }, { 3003, 1 }, { 3457, 1 } }

local login = CreatureEvent("SpireDevSeedLogin")
function login.onLogin(player)
	local seed = SEEDED[player:getName()]
	if seed and Difficulty.get(player) == Difficulty.NONE then
		Difficulty.set(player, seed.mode)
		for _, list in ipairs({ seed.kit, COMMON }) do
			for _, entry in ipairs(list) do
				player:addItem(entry[1], entry[2])
			end
		end
		player:addMoney(10000)
	end
	return true
end
login:register()

-- Gamemasters (group 4 and up) run fast so they can cross the map while testing. Speed resets at every
-- login, so this applies every time. Change GM_SPEED_BONUS to taste (a normal level-30 player is ~170).
local GM_SPEED_BONUS = 600
local gmSpeed = CreatureEvent("SpireGmSpeedLogin")
function gmSpeed.onLogin(player)
	if player:getGroup():getId() >= 4 then
		player:changeSpeed(GM_SPEED_BONUS)
	end
	return true
end
gmSpeed:register()
