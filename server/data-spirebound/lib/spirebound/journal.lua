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
		return "Hunting task", { "No active task. Ask Taskmaster Rhen in Hearthgate." }
	end
	local n = s:get("kills") or 0
	local lines = { string.format("%s: %d of %d defeated.", t.monster, math.min(n, t.count), t.count) }
	table.insert(lines, n >= t.count and "Report to Taskmaster Rhen." or string.format("Reward: %d gold, %d task point%s.", t.gold, t.points, t.points == 1 and "" or "s"))
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

-- "How do I..." (R11): the questions new players ask most, answered in a line each
SpireJournal.HOWTO = {
	"How do I attack? Click a monster in the Battle List (Ctrl+B), or right-click it and choose Attack.",
	"How do I loot? Right-click the body and drag what you want into your backpack. !autoloot can do it for you.",
	"How do I heal? Drink a health potion, or use your path's healing spell (say !spells). Rest in town to regain health.",
	"Where do I hunt? Say !hunt: it names the best ground for your level, and the signposts on the roads point the way.",
	"How do Rangers use arrows? Put them in a quiver and wear the quiver in your shield hand: the bow fires from it. Fletcher Tamsin sells both.",
	"How do sword skills work? Hold the right weapon and press Shift+1..6. Opener, then Link, then Finisher for a combo.",
	"Where do I learn spells? Nobody sells them: you learn them on your own as you level. Say !spells for the list.",
	"Where is my gold? At Banker Tolliver in the Hearth. Say balance, deposit or withdraw. The account vault is shared by your characters.",
	"How do I sell loot? Trader Osric in the Hearth buys what monsters drop. Players pay more on the market (any depot locker).",
	"What are hunting tasks? Every town has a taskmaster (Floor 1: Taskmaster Rhen) with a task menu of that floor's monsters. Each task pays gold and task points once a day. Spend points with !taskshop.",
	"How do I get home fast? A temple teleport scroll (Runewright Mael, 300 gold) takes you to your temple outside a fight.",
	"What is a secret? Hidden places on every floor. Find one and sell word of it to Vesper, the Info Broker, or keep it.",
	"Why can't I attack that player? Players below level 50 are protected, and so are players far below your level.",
	"How do floors open? When anyone beats a floor's boss, the way up opens for the whole server.",
}

function SpireJournal.howto()
	local copy = {}
	for i, l in ipairs(SpireJournal.HOWTO) do
		copy[i] = l
	end
	return "How do I...", copy -- a copy: the reply is translated in place
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
	elseif tab == "howto" then
		title, lines = SpireJournal.howto()
	else
		return nil
	end
	if type(player.getGuid) == "function" then
		title = SpireI18n.t(player, title)
		for i, l in ipairs(lines) do
			lines[i] = SpireI18n.t(player, l)
		end
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
