-- P12 (FLOOR1_REVIEW.md F1-65): leaderboards in town. The Monument's statue in the Hearth Square shows the top
-- climbers and the Memorial (the same lists as the Journal's Top and Memorial tabs, !top and !memorial).
function SpireMonumentText()
	local _, top = SpireJournal.top()
	local _, fallen = SpireJournal.memorial()
	local lines = { "THE MONUMENT", "", "Top climbers:" }
	for _, l in ipairs(top) do
		table.insert(lines, l)
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
