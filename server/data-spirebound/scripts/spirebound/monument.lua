-- P12 (FLOOR1_REVIEW.md F1-65): leaderboards in town. The Monument's statue on Hearth Plaza shows the top
-- climbers and the Memorial (the same lists as the Journal's Top and Memorial tabs, !top and !memorial).
function SpireMonumentText()
	local _, top = SpireJournal.top()
	local _, fallen = SpireJournal.memorial()
	local lines = { "THE MONUMENT", "", "Top climbers:" }
	for _, l in ipairs(top) do
		table.insert(lines, l)
	end
	table.insert(lines, "")
	local season = SpireSeason.current()
	local done = SpireChronicle.finishers(season)
	table.insert(lines, string.format("The Spire Chronicle of Season %d, finished by:", season))
	table.insert(lines, #done > 0 and table.concat(done, ", ") or "no one yet.")
	table.insert(lines, "")
	-- adventure layer 4.3: the season's first finders (never where)
	local firsts = SpireFinds and SpireFinds.allFirsts() or {}
	table.insert(lines, string.format("First finders of Season %d:", season))
	if #firsts == 0 then
		table.insert(lines, "  no one yet. The tower keeps its secrets.")
	else
		for _, l in ipairs(SpireFinds.firstLines(firsts, 25)) do
			table.insert(lines, l)
		end
	end
	table.insert(lines, "")
	table.insert(lines, "The Memorial (Death Game):")
	for _, l in ipairs(fallen) do
		table.insert(lines, l)
	end
	return table.concat(lines, "\n")
end

local statue = Action()
function statue.onUse(player, item)
	player:showTextDialog(item:getId(), SpireMonumentText():sub(1, 4000))
	return true
end
local m = WorldPoints.monument
if m then
	statue:position(Position(m.x, m.y - 1, m.z))
	statue:register()
end

-- P7 (FLOOR1_REVIEW.md F1-01): the first-clears stone at the foot of the Spire in the Arrival Yard
function SpireFirstClearsText()
	local lines = { "THE FIRST TO OPEN EACH FLOOR", "" }
	for n = 1, Floors.LAUNCH_FLOORS do
		local rec = Floors.get(n)
		local who = rec.credit and #rec.credit > 0 and table.concat(rec.credit, ", ", 1, math.min(5, #rec.credit))
		if who then
			table.insert(lines, string.format("Floor %d: %s", n, who))
		else
			table.insert(lines, string.format("Floor %d: no one yet.", n))
			break
		end
	end
	table.insert(lines, "")
	local top = Floors.highestOpen()
	table.insert(lines, Floors.raceLine(top, Floors.get(top)))
	return table.concat(lines, "\n")
end

local firstClears = Action()
function firstClears.onUse(player, item)
	player:showTextDialog(item:getId(), SpireFirstClearsText())
	return true
end
if WorldPoints.yard_first_clears then
	firstClears:position(WorldPoints.yard_first_clears)
	firstClears:register()
end

-- N3 (FLOOR1_REVIEW.md F1-50): the notice board on Hearth Plaza. Use it to read what is going on in the tower
-- right now: the floor race, the beacon, this weekend's bonus, the biggest bounties. Each part is guarded, so one broken
-- system never blanks the board.
function SpireNoticeText()
	local lines = { "HEARTHGATE NOTICE BOARD", "" }
	local function part(f)
		local ok, out = pcall(f)
		if ok and out then
			if type(out) ~= "table" then
				out = { out, nil }
			end
			for _, l in ipairs(out) do
				table.insert(lines, l)
			end
			table.insert(lines, "")
		end
	end
	part(function()
		local top = Floors.highestOpen()
		return Floors.raceLine(top, Floors.get(top))
	end)
	part(function()
		return SpireBeacons.statusLine(1, SpireBeacons.get(1), os.time())
	end)
	part(function()
		local w = SpireEvents.currentWeekend()
		return w and ("This weekend: " .. w.name .. "!") or "Weekend bonus: none today. Every Saturday and Sunday brings one."
	end)
	part(function()
		local out = { "Wanted (the biggest bounties):" }
		for i, b in ipairs(SpireBounty.list()) do
			if i > 3 then break end
			table.insert(out, string.format("  %s: %d gold", b.name or "?", b.total))
		end
		if #out == 1 then
			table.insert(out, "  nobody. The roads are safe, for now.")
		end
		return out
	end)
	part(function() -- adventure layer 4.2: rare finds of the last week, newest first
		local out = { "Recent finds:" }
		for i, e in ipairs(SpireFinds.board()) do
			if i > 8 then break end
			table.insert(out, string.format("  %s %s", os.date("%d %b", e.at), e.text))
		end
		if #out == 1 then
			table.insert(out, "  nothing yet this week. Somebody has to be first.")
		end
		return out
	end)
	part(function() -- adventure layer 4.3: first finds of this season
		local out = { "First finds this season:" }
		for _, l in ipairs(SpireFinds.firstLines(SpireFinds.allFirsts(), 6)) do
			table.insert(out, l)
		end
		if #out == 1 then
			table.insert(out, "  none yet. Every secret, hidden beast and elite still waits for its first finder.")
		end
		return out
	end)
	table.insert(lines, "Say !arena for the arena, !beacon for the beacons, !top for the climbers, !finds for your discoveries.")
	return table.concat(lines, "\n")
end

local notice = Action()
function notice.onUse(player, item)
	player:showTextDialog(item:getId(), SpireNoticeText():sub(1, 4000))
	return true
end
if WorldPoints.hearth_notice_board then
	notice:position(WorldPoints.hearth_notice_board)
	notice:register()
end
