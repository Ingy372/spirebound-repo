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
			else
				SpireQuests.refreshTracker(player, q)
				if n % 5 == 0 or q.count <= 5 then
					player:sendTextMessage(MESSAGE_STATUS, string.format("%s: %d of %d.", q.name, n, q.count))
				end
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
	SpireQuests.markGivers(player) -- P2: "!" on the minimap where a quest waits
	-- G3 (Grok playtest, 2026-11-24: Pell's quest never showed in the Quest Tracker): the tracker only lists missions
	-- the player picked by hand unless "auto-track new quests" is on, and it starts off. Turn both auto options on
	-- once per character (the player can still switch them off in the tracker).
	local qt = player:kv():scoped("quest-tracker")
	if player.setQuestTrackerOption and qt:get("auto-track-new-quests") == nil then
		player:setQuestTrackerOption("autoTrackNewQuests", true)
		player:setQuestTrackerOption("autoUntrackCompletedQuests", true)
	end
	return true
end
login:register()
