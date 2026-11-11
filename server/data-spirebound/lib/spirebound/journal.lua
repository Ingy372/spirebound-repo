-- The Journal window (roadmap 6.1): secret list, fishing log, quest log, hunting task, leaderboards.
-- The client asks {t="journal", tab="secrets"}; the server answers {t="journal", tab, title, lines={...}}.
-- Every builder below returns plain text lines, so the window and the tests share one source.
SpireJournal = {
	TABS = { "secrets", "fishing", "quests", "task", "top", "memorial" },
	MAX_LINES = 120,
}

local function titleCase(s)
	return (s:gsub("^%l", string.upper))
end

-- Pure: one secret's row. found = bool.
function SpireJournal.secretLine(secret, found)
	local tier = titleCase(secret.tier)
	if found then
		return string.format("[x] Floor %d - %s (%s) - found", secret.floor, secret.name, tier)
	end
	local night = secret.night and " (night only)" or ""
	return string.format("[ ] Floor %d - %s (%s)%s: %s", secret.floor, "???", tier, night, secret.hint)
end

function SpireJournal.secrets(player)
	local lines, found = {}, 0
	for _, s in ipairs(SpireSecrets.list) do
		local f = SpireSecrets.hasFound(player, s.id)
		if f then
			found = found + 1
		end
		table.insert(lines, SpireJournal.secretLine(s, f))
	end
	table.insert(lines, 1, string.format("You have found %d of %d secrets. Sell what you know to the Info Broker in Hearthgate.", found, #SpireSecrets.list))
	return "Secrets", lines
end

-- Pure: fishing rows. log = function(id) -> {count, best} or nil
function SpireJournal.fishingLines(tables, log)
	local lines, kinds, total = {}, 0, 0
	for floor = 1, 99 do
		local t = tables[floor]
		if t then
			table.insert(lines, "Floor " .. floor)
			for _, f in ipairs(t) do
				if not f.junk and not f.treasure then
					total = total + 1
					local e = log(f.id)
					if e and e.count > 0 then
						kinds = kinds + 1
						table.insert(lines, string.format("  [x] %s - caught %d, best %.2f kg", f.name, e.count, e.best or 0))
					else
						table.insert(lines, "  [ ] ???" .. (f.night and " (only caught at night)" or ""))
					end
				end
			end
		end
	end
	table.insert(lines, 1, string.format("Fish kinds in your log: %d of %d.", kinds, total))
	return lines
end

function SpireJournal.fishing(player)
	local log = SpireFishing.log(player)
	return "Fishing log", SpireJournal.fishingLines(SpireFishing.tables, function(id)
		return log:get(id)
	end)
end

-- Quest rows for a player: started and finished quests, then ones they could start.
function SpireJournal.quests(player)
	local active, ready, done, open = {}, {}, {}, {}
	local doneIds = SpireQuests.doneIds(player)
	for _, q in ipairs(SpireQuests.list) do
		local state = SpireQuests.state(player, q)
		local label = string.format("Floor %d - %s (from %s)", q.floor, q.name, q.giver)
		if state == 3 then
			table.insert(done, label .. ": completed")
		elseif state == 1 or state == 2 then
			table.insert(state == 2 and ready or active, label .. ": " .. SpireQuests.logText(q, state, SpireQuests.progress(player, q)))
		elseif SpireQuests.available(q, state, doneIds) then
			table.insert(open, label .. ": talk to " .. q.giver .. ".")
		end
	end
	local lines = {}
	local function add(head, list)
		if #list > 0 then
			table.insert(lines, head)
			for _, l in ipairs(list) do
				table.insert(lines, "  " .. l)
			end
		end
	end
	add("Ready to report", ready)
	add("In progress", active)
	add("Available", open)
	add("Completed", done)
	if #lines == 0 then
		table.insert(lines, "No quests yet. Talk to the people of Hearthgate.")
	end
	return "Quests", lines
end

function SpireJournal.task(player)
	local s = SpireTasks.scope(player)
	local id = s:get("active")
	local t = id and SpireTasks.get(id)
	if not t then
		return "Hunting task", { "No active task. Ask Taskmaster Ren in Hearthgate." }
	end
	local n = s:get("kills") or 0
	local lines = { string.format("%s: %d of %d defeated.", t.monster, math.min(n, t.count), t.count) }
	table.insert(lines, n >= t.count and "Report to Taskmaster Ren." or string.format("Reward: %d gold, %d task point%s.", t.gold, t.points, t.points == 1 and "" or "s"))
	return "Hunting task", lines
end

function SpireJournal.top()
	return "Top climbers", SpireBoards.rankLines(SpireBoards.rows(), nil, SpireBoards.TOP)
end

function SpireJournal.memorial()
	local lines = SpireBoards.memorialLines(SpireBoards.memorial())
	if #lines == 0 then
		lines = { "No names yet. May it stay that way." }
	end
	return "The Memorial", lines
end

-- Build the reply for a tab; nil if the tab is unknown.
function SpireJournal.build(player, tab)
	local title, lines
	if tab == "secrets" then
		title, lines = SpireJournal.secrets(player)
	elseif tab == "fishing" then
		title, lines = SpireJournal.fishing(player)
	elseif tab == "quests" then
		title, lines = SpireJournal.quests(player)
	elseif tab == "task" then
		title, lines = SpireJournal.task(player)
	elseif tab == "top" then
		title, lines = SpireJournal.top()
	elseif tab == "memorial" then
		title, lines = SpireJournal.memorial()
	else
		return nil
	end
	while #lines > SpireJournal.MAX_LINES do
		table.remove(lines)
	end
	return { t = "journal", tab = tab, title = title, lines = lines }
end

function SpireJournal.tabFromRequest(buffer)
	if not buffer:find('"t"%s*:%s*"journal"') then
		return nil
	end
	return buffer:match('"tab"%s*:%s*"(%a+)"')
end
