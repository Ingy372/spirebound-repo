-- Story quest kill tracking and perk re-application at login.
-- One kill of a monster by this name counts for this player's running kill quests
function SpireQuests.countKill(player, name)
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
end

local kill = CreatureEvent("SpireQuestKill")
function kill.onKill(player, target)
	if not target or not target:isMonster() or target:getMaster() then
		return true
	end
	local name = target:getName()
	for _, member in ipairs(SpireProgress.killCredit("quest", player, target)) do -- the whole party nearby (P1-3)
		SpireQuests.countKill(member, name)
		if SpireFirstClimb and SpireFirstClimb.onKill then
			SpireFirstClimb.onKill(member, target) -- FD1: chapter 3's thornsnaps, chapter 5's pages
		end
	end
	return true
end
kill:register()

function SpireQuests.autolootDefault(player)
	local k = player:kv():scoped("spirebound")
	if not Features or k:get("autoloot-default") ~= nil then
		return false
	end
	k:set("autoloot-default", 1)
	if player:getFeature(Features.AutoLoot) == nil then
		player:setFeature(Features.AutoLoot, 1)
		return true
	end
	return false
end

local login = CreatureEvent("SpireQuestLogin")
function login.onLogin(player)
	player:registerEvent("SpireQuestKill")
	SpirePerks.apply(player)
	SpireQuests.markGivers(player) -- P2: "!" on the minimap where a quest waits
	-- G3 (Grok playtest, 2026-11-24: Pell's quest never showed in the Quest Tracker): the tracker only lists missions
	-- the player picked by hand unless "auto-track new quests" is on, and it starts off. Turn both auto options on
	-- once per character (the player can still switch them off in the tracker).
	-- Party playtest 2026-11-26 (hand-off P1-4): Canary only autoloots after !autoloot on, and nothing said so: new
	-- players left every coin in the bodies. Switch it on once per character; !autoloot off still turns it off.
	SpireQuests.autolootDefault(player)
	local qt = player:kv():scoped("quest-tracker")
	if player.setQuestTrackerOption and qt:get("auto-track-new-quests") == nil then
		player:setQuestTrackerOption("autoTrackNewQuests", true)
		player:setQuestTrackerOption("autoUntrackCompletedQuests", true)
	end
	return true
end
login:register()
