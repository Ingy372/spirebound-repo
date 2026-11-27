-- The Journal window (roadmap 6.1): secret list, fishing log, quest log, hunting task, leaderboards.
-- The client asks {t="journal", tab="secrets"}; the server answers {t="journal", tab, title, lines={...}}.
-- Every builder below returns plain text lines, so the window and the tests share one source.
SpireJournal = {
	TABS = { "upgrade", "secrets", "discoveries", "fishing", "quests", "task", "top", "memorial" },
	MAX_LINES = 120,
}

local function titleCase(s)
	return (s:gsub("^%l", string.upper))
end

-- Pure: one secret's row. found = bool; riddle = true when this character may read the riddle (the secret was sold,
-- or a message bottle gave it). Jay, 2026-11-27: riddles are the only hints, and nothing else points at a secret:
-- no tier (gear secrets pay Vesper's large tier), no "night only".
function SpireJournal.secretLine(secret, found, riddle)
	if found then
		return string.format("[x] Floor %d - %s - found", secret.floor, secret.name)
	end
	if riddle then
		return string.format("[ ] Floor %d - ???: \"%s\"", secret.floor, secret.hint)
	end
	return string.format("[ ] Floor %d - ???", secret.floor)
end

function SpireJournal.secrets(player)
	local lines, found = {}, 0
	for _, s in ipairs(SpireSecrets.list) do
		local f = SpireSecrets.hasFound(player, s.id)
		if f then
			found = found + 1
		end
		local riddle = SpireSecrets.publicBy(s.id) ~= nil or (player.kv and SpireSecrets.holdsRiddle(player, s.id))
		table.insert(lines, SpireJournal.secretLine(s, f, riddle))
	end
	table.insert(lines, 1, string.format("You have found %d of %d secrets. Riddles come from Vesper's list of sold secrets and from bottles in the water. Sell what you find to Vesper, or keep it.", found, #SpireSecrets.list))
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
			local rw = SpireQuests.rewardText(q.reward)
			table.insert(state == 2 and ready or active, label .. ": " .. SpireQuests.logText(q, state, SpireQuests.progress(player, q)) .. (rw ~= "" and (" " .. rw) or ""))
		elseif SpireQuests.available(q, state, doneIds, SpireQuests.context(player)) then
			local rw = SpireQuests.rewardText(q.reward)
			table.insert(open, label .. ": talk to " .. SpireQuests.whereText(q.giver) .. "." .. (rw ~= "" and (" " .. rw) or ""))
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
	add("Bring a group", SpireJournal.GROUP_LINES) -- review A5-1: say plainly where a party is needed
	return "Quests", lines
end

SpireJournal.GROUP_LINES = {
	"The Stair Key needs two fights you cannot win alone: the Gate Hound in the Pass (3 or more players) and the Stonehorn Ram at the Old Watchtower (a party of 4).",
	"Party grounds: the Smugglers' Cellar under the Bandit Road, the Old Watchtower, and the party caves under the grounds (2 to 4 players). The Bandit Road itself can be hunted alone.",
	"The Lost Patrol (Captain Dorrow) is for a party of four, and the Axe-Lord of the Stair for 4 to 6.",
}

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
	"How do I loot? Autoloot is on: what you kill drops straight into your backpack. Say !autoloot off to loot by hand.",
	"How do I heal? Drink a health potion, or use your path's healing spell (say !spells). Rest in town to regain health.",
	"Where do I hunt? Say !hunt: it names the best ground for your level, and the signposts on the roads point the way.",
	"How do Rangers use arrows? Put them in a quiver and wear the quiver in your shield hand: the bow fires from it. Fletcher Tamsin sells both.",
	"How do sword skills work? Hold the right weapon and press Ctrl+1..6 (or click them). Opener, then Link, then Finisher for a combo.",
	"Where do I learn spells? Nobody sells them: you learn them on your own as you level. Say !spells for the list.",
	"Where is my gold? Looted coins go straight to your bank (Banker Tolliver in the Hearth: say balance). Shops take what you pay from it.",
	"How do we share gold in a party? At any banker say transfer, then the amount and the name (e.g. transfer 200 to Fern).",
	"My backpack is too heavy! Sell meat and ham to Innkeeper Roan, loot to Trader Osric, and deposit coins at the bank.",
	"How do I sell loot? Trader Osric in the Hearth buys what monsters drop. Players pay more on the market (any depot locker).",
	"What are hunting tasks? Every town has a taskmaster (Floor 1: Taskmaster Rhen) with a task menu of that floor's monsters. Each task pays gold and task points once a day. Spend points with !taskshop.",
	"How do I get home fast? An Amber Waycrystal (Runewright Mael) takes you to Hearthgate, or to the gate of a hunting ground you have the level for. Hold still 3 seconds; not in a fight.",
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
	if tab == "upgrade" then
		if type(player.getGuid) ~= "function" then
			return nil
		end
		title, lines = "Next upgrade", SpireUpgrade.lines(SpireUpgrade.viewFor(player))
	elseif tab == "secrets" then
		title, lines = SpireJournal.secrets(player)
	elseif tab == "discoveries" then -- adventure layer 4.6 (also !finds)
		if type(player.getGuid) ~= "function" then
			return nil
		end
		title, lines = "Floor 1 Discoveries", SpireDiscoveries.lines(player, 1)
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
	elseif tab == "chronicle" then -- roadmap M3
		if type(player.getAccountId) ~= "function" then
			return nil
		end
		local acc = player:getAccountId()
		title, lines = "Spire Chronicle", SpireChronicle.lines(SpireChronicle.get(acc), SpireSeason.current(), SpireChronicle.legacyCount(acc))
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
