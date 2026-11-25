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
