-- Quest-log entry for SpireQuests "s1_2" (lib/spirebound/quests.lua holds the text and numbers).
local q = SpireQuests.get("s1_2")
return {
	name = q.name,
	startStorageId = q.storage,
	startStorageValue = 1,
	missions = {
		[1] = {
			name = q.name,
			storageId = q.storage,
			missionId = tonumber(("s1_2"):gsub("%D", "")) or 1,
			startValue = 1,
			endValue = 3,
			description = function(player)
				return SpireQuests.logText(q, SpireQuests.state(player, q), SpireQuests.progress(player, q))
			end,
		},
	},
}
