-- Roadmap 6.5c: Season Path
SpireTest.add("season path: goals reset by period, points unlock cosmetic tiers", function()
	local t0 = 1700000000
	local st = {}
	local earned = SpirePath.advance(st, "kill", 299, t0)
	SpireTest.eq(earned, 0, "not yet")
	local e2, fin = SpirePath.advance(st, "kill", 1, t0)
	SpireTest.eq(e2, 10, "daily hunt done: +10")
	SpireTest.eq(fin[1].id, "d_hunt", "the daily goal finished")
	SpireTest.eq(SpirePath.advance(st, "kill", 300, t0), 0, "done once per day")
	SpireTest.eq(SpirePath.advance(st, "kill", 300, t0 + 86400), 10, "next day counts again")
	SpireTest.eq(SpirePath.advance(st, "secret", 1, t0), 40, "weekly secret: +40")
	SpireTest.eq(SpirePath.advance(st, "secret", 1, t0 + 3600), 0, "once per week")
	SpireTest.eq(st.points, 60, "points add up")
	SpireTest.eq(SpirePath.periodOf("week", 0), 0, "week 0 contains 1970-01-01")
	SpireTest.eq(SpirePath.periodOf("week", 4 * 86400), 1, "Monday 1970-01-05 starts week 1")
	SpireTest.eq(SpirePath.tierFor(99), 0, "tier 0")
	SpireTest.eq(SpirePath.tierFor(250), 2, "tier 2")
	SpireTest.eq(SpirePath.tierFor(999999), #SpirePath.REWARDS, "capped")
	for i, r in ipairs(SpirePath.REWARDS) do
		if r.item then
			local it = ItemType(r.item)
			if not it or it:getId() == 0 or not it:isPickupable() then
				error("reward " .. i .. " is not a takeable item: " .. tostring(r.item))
			end
		elseif not r.title then
			error("reward " .. i .. " has no item or title")
		end
	end
	SpireTest.eq(#SpirePath.lines(st, t0), #SpirePath.GOALS, "one line per goal")
end)
