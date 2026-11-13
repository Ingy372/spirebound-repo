-- Hunting tasks (DESIGN.md 15). Roadmap 2.16. One active task at a time; each task repeats once a day.
-- Every floor has its own taskmaster with a task menu (Jay, 2026-11-13); the tasks themselves are generated
-- into tasks_floors.lua by tools/balance.py: one per monster that spawns on that floor.
SpireTasks = {
	COOLDOWN = 20 * 3600,
	NEAR = 4, -- how close to a taskmaster the menu's buttons work
	list = {}, -- filled by tasks_floors.lua
	-- the taskmaster of each floor (Floor 1: Jay's name, 2-10: Claude's call, Jay can veto)
	MASTERS = {
		[1] = "Taskmaster Rhen", [2] = "Taskmaster Doral", [3] = "Taskmaster Ilsa", [4] = "Taskmaster Varn",
		[5] = "Taskmaster Kesh", [6] = "Taskmaster Brenna", [7] = "Taskmaster Otho", [8] = "Taskmaster Sigra",
		[9] = "Taskmaster Marlo", [10] = "Taskmaster Quillan",
	},
	-- task ids from before the full menu, so a task someone already took keeps counting
	RENAMED = {
		t_wolves = "t1_meadowwolf", t_boars = "t1_bristleboar", t_bandits = "t1_roadbandit", t_shards = "t1_fieldshardling",
		t_sentinels = "t1_ruinsentinel", t_rams = "t1_stonehornram", t_toads = "t1_miretoad",
	},
}

function SpireTasks.get(id)
	id = SpireTasks.RENAMED[id] or id
	for _, t in ipairs(SpireTasks.list) do
		if t.id == id then return t end
	end
end

function SpireTasks.forFloor(n)
	local out = {}
	for _, t in ipairs(SpireTasks.list) do
		if t.floor == n then table.insert(out, t) end
	end
	return out
end

function SpireTasks.floorOfMaster(name)
	for n, m in pairs(SpireTasks.MASTERS) do
		if m == name then return n end
	end
end

-- Pure: may this task be taken now? lastDone = time it was last completed (or nil)
function SpireTasks.canTake(activeId, lastDone, now)
	if activeId then
		return false, "Finish your current task first, or cancel it."
	end
	if lastDone and now - lastDone < SpireTasks.COOLDOWN then
		return false, "You did that one recently. Come back tomorrow."
	end
	return true
end

function SpireTasks.scope(player)
	return player:kv():scoped("spirebound-tasks")
end

-- The taskmaster standing near the player (name and floor), or nil
function SpireTasks.nearMaster(player)
	local pos = player:getPosition()
	for _, c in ipairs(Game.getSpectators(pos, false, false, SpireTasks.NEAR, SpireTasks.NEAR, SpireTasks.NEAR, SpireTasks.NEAR)) do
		if c:isNpc() then
			local n = SpireTasks.floorOfMaster(c:getName())
			if n then return c:getName(), n end
		end
	end
end

-- Take a task (from a taskmaster's menu or chat). Returns ok, message.
function SpireTasks.take(player, id)
	local t = SpireTasks.get(id)
	local master, floor = SpireTasks.nearMaster(player)
	if not master then return false, "Stand next to a taskmaster to take a task." end
	if not t or t.floor ~= floor then return false, master .. " has no such task." end
	local s = SpireTasks.scope(player)
	local ok, why = SpireTasks.canTake(s:get("active"), s:get("done_" .. t.id), os.time())
	if not ok then return false, why end
	s:set("active", t.id)
	s:set("kills", 0)
	return true, string.format("Hunt %d %ss, then come back to any taskmaster and report.", t.count, t.monster)
end

-- Hand in a finished task at any taskmaster. Returns ok, message.
function SpireTasks.report(player)
	if not SpireTasks.nearMaster(player) then return false, "Report to a taskmaster." end
	local s = SpireTasks.scope(player)
	local t = SpireTasks.get(s:get("active"))
	if not t then return false, "You have no task." end
	local kills = s:get("kills") or 0
	if kills < t.count then return false, string.format("Not yet: %d of %d %ss.", kills, t.count, t.monster) end
	s:remove("active")
	s:set("kills", 0)
	s:set("done_" .. t.id, os.time())
	s:set("points", (s:get("points") or 0) + t.points)
	player:addMoney(t.gold)
	return true, string.format("Good work. %d gold and %d task point%s (you have %d).", t.gold, t.points, t.points > 1 and "s" or "", s:get("points"))
end

function SpireTasks.cancel(player)
	local s = SpireTasks.scope(player)
	if not s:get("active") then return false, "You have no task." end
	s:remove("active")
	s:set("kills", 0)
	return true, "Task dropped."
end

-- The menu a taskmaster shows (sent to the client as {t="tasks", ...})
function SpireTasks.menu(player, floor)
	local s = SpireTasks.scope(player)
	local now = os.time()
	local activeTask = SpireTasks.get(s:get("active"))
	local rows = {}
	for _, t in ipairs(SpireTasks.forFloor(floor)) do
		local last = s:get("done_" .. t.id)
		local wait = last and math.max(0, SpireTasks.COOLDOWN - (now - last)) or 0
		local status = (activeTask and activeTask.id == t.id) and "active" or (wait > 0 and "wait" or "open")
		local look = { 0, 0, 0, 0, 0 } -- the monster's outfit, so the window can show it
		local mt = MonsterType(t.monster)
		local o = mt and mt:outfit()
		if o then
			look = { o.lookType or 0, o.lookHead or 0, o.lookBody or 0, o.lookLegs or 0, o.lookFeet or 0 }
		end
		table.insert(rows, { id = t.id, monster = t.monster, count = t.count, gold = t.gold, points = t.points, status = status, wait = wait, look = look })
	end
	local active = nil
	if activeTask then
		active = { id = activeTask.id, monster = activeTask.monster, count = activeTask.count, kills = math.min(s:get("kills") or 0, activeTask.count), floor = activeTask.floor, gold = activeTask.gold, points = activeTask.points }
	end
	return {
		t = "tasks", master = SpireTasks.MASTERS[floor], floor = floor, points = s:get("points") or 0,
		list = rows, active = active or false,
	}
end
