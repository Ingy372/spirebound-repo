-- Roadmap 8.1: season reset (archive, account legacy, safe wipe SQL).
SpireTest.add("season: archive copies titles to the account and the Hall of Seasons", function()
	local guid, acc = -77, -77
	local pk = kv.scoped("player"):scoped(tostring(guid))
	pk:scoped("spirebound-titles"):set("Test Climber", os.time())
	pk:scoped("spirebound"):set("difficulty", 3)
	local rec = SpireSeason.archivePlayer(guid, acc, "Season Tester", 88, 4, 99)
	SpireTest.eq(rec.level, 88, "record keeps the level")
	SpireTest.eq(rec.titles[1], "Test Climber", "record keeps the title")
	local hall = kv.scoped("hall-of-seasons"):scoped("season-99"):get("Season Tester")
	SpireTest.eq(hall and hall.name, "Season Tester", "Hall of Seasons has the character")
	local legacy = SpireSeason.accountKv(acc):get("titles") or {}
	SpireTest.eq(legacy["Test Climber"], 99, "account keeps the title")
	SpireTest.eq(legacy["Deathbound (Season 99)"], 99, "Death Game earns Deathbound")
	SpireTest.eq(SpireSeason.accountKv(acc):get("seasons"), 1, "season count goes up")
	pcall(function()
		pk:scoped("spirebound-titles"):remove("Test Climber")
		pk:scoped("spirebound"):remove("difficulty")
		kv.scoped("hall-of-seasons"):scoped("season-99"):remove("Season Tester")
		SpireSeason.accountKv(acc):remove("titles")
		SpireSeason.accountKv(acc):remove("explored")
		SpireSeason.accountKv(acc):remove("seasons")
	end)
end)

SpireTest.add("season: the wipe never touches accounts or the Hall of Seasons", function()
	for _, sql in ipairs(SpireSeason.wipeStatements()) do
		local low = sql:lower()
		if low:find("`accounts`") or low:find("'account%.") or low:find("hall%-of%-seasons") or low:find("group_id` >= 4") then
			error("unsafe wipe statement: " .. sql)
		end
	end
	SpireTest.eq(SpireSeason.current() >= 1, true, "season number is set")
end)
