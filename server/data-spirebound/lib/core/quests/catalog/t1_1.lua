-- Quest-log entry for SpireQuests "t1_1" (lib/spirebound/quests.lua holds the text and numbers).
local q = SpireQuests.get("t1_1")
return {
	name = q.name,
	startStorageId = q.storage,
	startStorageValue = 1,
	missions = {
		[1] = {
			name = q.name,
			storageId = q.storage,
			missionId = tonumber(("t1_1"):gsub("%D", "")) or 1,
			startValue = 1,
			endValue = 3,
			description = function(player)
				return SpireQuests.logText(q, SpireQuests.state(player, q), SpireQuests.progress(player, q))
			end,
		},
	},
}
