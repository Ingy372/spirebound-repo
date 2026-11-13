-- Calls every registered cleanup when a player logs out (roadmap R20). Rules: lib/spirebound/cleanup.lua.
local logout = CreatureEvent("SpireCleanupLogout")
function logout.onLogout(player)
	SpireCleanup.run(player:getId(), player:getGuid())
	return true
end
logout:register()

local login = CreatureEvent("SpireCleanupLogin")
function login.onLogin(player)
	player:registerEvent("SpireCleanupLogout")
	return true
end
login:register()
