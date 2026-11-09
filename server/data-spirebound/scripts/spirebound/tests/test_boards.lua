-- Roadmap 6.2: Memorial and leaderboards
SpireTest.add("boards: Memorial order and leaderboard filters", function()
	local lines = SpireBoards.memorialLines({
		Ana = { level = 40, vocation = "Ranger", cause = "a wolf", time = 100 },
		Bo = { level = 90, vocation = "Mystic", cause = "Old Tusk", time = 50 },
	})
	SpireTest.eq(#lines, 2, "two names")
	SpireTest.eq(lines[1]:sub(1, 9), "1. Bo, le", "highest level first")
	local rows = {
		{ name = "A", level = 120, vocation = "Vanguard", mode = 1 },
		{ name = "B", level = 110, vocation = "Arcanist", mode = 3, retired = true },
		{ name = "C", level = 100, vocation = "Ranger", mode = 3 },
		{ name = "D", level = 90, vocation = "Mystic", mode = 2 },
	}
	local all = SpireBoards.rankLines(rows, nil)
	SpireTest.eq(#all, 4, "everyone listed")
	SpireTest.eq(all[2], "2. B, level 110 Arcanist (Death Game) [fallen]", "fallen Death Game marked")
	local dg = SpireBoards.rankLines(rows, 3)
	SpireTest.eq(#dg, 2, "Death Game board")
	SpireTest.eq(dg[2], "2. C, level 100 Ranger", "ranked within the board")
	SpireTest.eq(#SpireBoards.rankLines(rows, nil, 2), 2, "limit")
	SpireTest.eq(type(SpireBoards.rows()), "table", "reads the database")
	SpireTest.eq(type(SpireBoards.memorial()), "table", "reads the Memorial")
end)
