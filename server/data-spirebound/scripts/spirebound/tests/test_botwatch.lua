-- Roadmap R15: the server spots hunting on one spot, whatever the client says.
SpireTest.add("bots: ten minutes of kills without moving counts as botting; walking clears it", function()
	local rec, t = {}, 100000
	local here = { x = 100, y = 100, z = 7 }
	SpireCavebot.notePos(rec, here, t)
	for i = 1, 6 do
		SpireCavebot.noteKill(rec, t + i * 90)
		SpireCavebot.notePos(rec, { x = 101, y = 100, z = 7 }, t + i * 90) -- shuffling one tile is still "standing"
	end
	SpireTest.eq(SpireCavebot.standingBot(rec, t + 599), false, "not before 10 minutes")
	SpireTest.eq(SpireCavebot.standingBot(rec, t + 601), true, "10 minutes on one spot with kills: botting")
	SpireCavebot.notePos(rec, { x = 104, y = 100, z = 7 }, t + 610)
	SpireTest.eq(SpireCavebot.standingBot(rec, t + 611), false, "walking away clears it")
	local idle = {}
	SpireCavebot.notePos(idle, here, t)
	SpireTest.eq(SpireCavebot.standingBot(idle, t + 3600), false, "standing still without hunting is just resting")
end)
