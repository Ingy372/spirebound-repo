-- Story quest kill tracking and perk re-application at login.
local kill = CreatureEvent("SpireQuestKill")
function kill.onKill(player, target)
	if not target or not target:isMonster() or target:getMaster() then
		return true
	end
	local name = target:getName()
	for _, q in ipairs(SpireQuests.list) do
		if q.target == name and SpireQuests.state(player, q) == 1 then
			local n = SpireQuests.progress(player, q) + 1
			player:setStorageValue(q.killStorage, n)
			if n >= q.count then
				player:setStorageValue(q.storage, 2)
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, q.name .. ": done! " .. q.report)
			elseif n % 5 == 0 or q.count <= 5 then
				player:sendTextMessage(MESSAGE_STATUS, string.format("%s: %d of %d.", q.name, n, q.count))
			end
		end
	end
	return true
end
kill:register()

local login = CreatureEvent("SpireQuestLogin")
function login.onLogin(player)
	player:registerEvent("SpireQuestKill")
	SpirePerks.apply(player)
	return true
end
login:register()
