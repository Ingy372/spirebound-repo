-- Hunting tasks (DESIGN.md 15). Roadmap 2.16. One active task at a time; each task repeats once a day.
SpireTasks = {
	COOLDOWN = 20 * 3600,
	list = {
		{ id = "t_wolves", floor = 1, monster = "Meadow Wolf", count = 50, gold = 2000, points = 1 },
		{ id = "t_boars", floor = 1, monster = "Bristle Boar", count = 50, gold = 2500, points = 1 },
		{ id = "t_bandits", floor = 1, monster = "Road Bandit", count = 40, gold = 3500, points = 2 },
		{ id = "t_shards", floor = 1, monster = "Field Shardling", count = 40, gold = 3000, points = 2 },
		{ id = "t_sentinels", floor = 1, monster = "Ruin Sentinel", count = 30, gold = 4500, points = 2 },
		{ id = "t_rams", floor = 1, monster = "Stonehorn Ram", count = 25, gold = 9000, points = 3 },
		{ id = "t_toads", floor = 1, monster = "Mire Toad", count = 30, gold = 6000, points = 3 },
	},
}

function SpireTasks.get(id)
	for _, t in ipairs(SpireTasks.list) do
		if t.id == id then return t end
	end
end

-- Pure: may this task be taken now? lastDone = time it was last completed (or nil)
function SpireTasks.canTake(activeId, lastDone, now)
	if activeId then
		return false, "Finish (or {cancel}) your current task first."
	end
	if lastDone and now - lastDone < SpireTasks.COOLDOWN then
		return false, "You did that one recently. Come back tomorrow."
	end
	return true
end

function SpireTasks.scope(player)
	return player:kv():scoped("spirebound-tasks")
end
