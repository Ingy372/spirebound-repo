-- Roadmap 8.2: season remix
SpireTest.add("remix: season 1 is as designed, later seasons move mechanics and rewards", function()
	local bosses = {}
	for n, b in pairs(SpireFloorBosses) do
		bosses[n] = { fieldPattern = b.fieldPattern, bossPattern = b.bossPattern }
	end
	local p1 = SpireRemix.bossPlan(bosses, 1)
	for n, b in pairs(bosses) do
		SpireTest.eq(p1[n].fieldPattern, b.fieldPattern, "season 1 keeps floor " .. n)
	end
	local p2 = SpireRemix.bossPlan(bosses, 2)
	local changed = 0
	for n, b in pairs(bosses) do
		if p2[n].fieldPattern ~= b.fieldPattern or p2[n].bossPattern ~= b.bossPattern then
			changed = changed + 1
		end
	end
	if changed < 5 then error("season 2 should change most floors, changed " .. changed) end
	SpireTest.eq(p2[10].bossPattern, "ruin", "Azhrakkar keeps his ruin dance")
	local again = SpireRemix.bossPlan(bosses, 2)
	SpireTest.eq(again[3].bossPattern, p2[3].bossPattern, "same season, same plan (every restart)")
	-- patterns stay in their own pool: field patterns never become boss patterns
	local field = { stomp = true, root = true, lance = true, stances = true }
	for n, p in pairs(p2) do
		SpireTest.eq(field[p.fieldPattern], true, "field pattern on floor " .. n)
	end
	-- secrets: tiers move within a floor, special rewards stay
	local plan = SpireRemix.secretPlan(SpireSecrets.list, 3)
	SpireTest.eq(plan["s1"], nil, "the Underkeep secret keeps its own reward")
	local tierCount = {}
	for id, p in pairs(plan) do
		local s = SpireSecrets.get(id)
		tierCount[s.floor] = (tierCount[s.floor] or 0) + (p.tier == "large" and 1 or 0)
	end
	local orig = {}
	for _, s in ipairs(SpireSecrets.list) do
		if type(s.reward) == "table" and s.tier == "large" then
			orig[s.floor] = (orig[s.floor] or 0) + 1
		end
	end
	SpireTest.eq(tierCount[2], orig[2], "same number of large secrets on floor 2")
	SpireTest.eq(SpireRemix.shuffle({ 1, 2, 3 }, 1)[1], 1, "season 1 shuffle is identity")
end)
