-- Roadmap FD2 (a feature per Floor 1 ground) and FD5 (Town Works).
local F = SpireFeatures

SpireTest.add("ground features: every Floor 1 ground has one, and its spots are on the map", function()
	local have = {}
	for _, f in ipairs(SpireDepthData.features) do
		have[f.id] = true
	end
	for _, g in ipairs(SpireWilds.grounds) do
		if (WorldPoints["camp_" .. g.id] or { x = 9999 }).x < 2000 then
			SpireTest.eq(have[g.id], true, g.id .. " has a feature")
		end
	end
	SpireTest.eq(have.apex_watchtower, true, "the Old Watchtower has one")
	for _, name in ipairs({ "feat_bell", "feat_howl", "feat_poster", "feat_lift_winch", "feat_lift_top", "feat_signal",
		"feat_ballista", "feat_cache", "feat_nightfish", "feat_lily_1", "feat_tide_1", "feat_vine_1_1", "feat_mole_2" }) do
		SpireTest.eq(WorldPoints[name] ~= nil, true, name .. " is on the map")
	end
	SpireTest.eq(F.place() >= 15, true, "the feature objects are tagged")
	local bellAid = 0
	for _, it in ipairs(Tile(WorldPoints.feat_bell):getItems() or {}) do
		if it:getId() == 2117 then
			bellAid = it:getActionId()
		end
	end
	SpireTest.eq(bellAid, F.AID.bell, "the bell rings")
	for _, n in ipairs({ "Elder Sproutling", "Nest Queen", "Bandit Lieutenant" }) do
		SpireTest.eq(MonsterType(n) ~= nil, true, n .. " exists")
	end
	SpireTest.eq(ItemType(9218):getName(), "Lieutenant's Badge", "the badge's name")
end)

SpireTest.add("ground features: the rules (tide, chimes, vines, cool-downs)", function()
	SpireTest.eq(F.tideLow(0, 1800, 600), true, "low at the start of a half hour")
	SpireTest.eq(F.tideLow(900, 1800, 600), false, "high in the middle")
	local o = F.windOrder(12345)
	SpireTest.eq(#o, 4, "four notes")
	SpireTest.eq(F.chimeStep(o, { o[1] }), "more", "right so far")
	SpireTest.eq(F.chimeStep(o, { o[2] }), "wrong", "a wrong note")
	SpireTest.eq(F.chimeStep(o, { o[1], o[2], o[3], o[4] }), "done", "all four")
	local up = F.pickVines(7, 0.5, math.random)
	local n = 0
	for _ in pairs(up) do
		n = n + 1
	end
	SpireTest.eq(n >= 1 and n <= 6, true, "some vine walls stand, never all")
	local cool = {}
	SpireTest.eq(F.ready(cool, "a", 100), true, "free at first")
	cool.a = 200
	local ok, left = F.ready(cool, "a", 150)
	SpireTest.eq(ok == false and left == 50, true, "then cooling down")
	-- the lilies and the tide swap their tiles and back
	F.liliesUp(true)
	SpireTest.eq(Tile(WorldPoints.feat_lily_1):getGround():getId(), 17238, "a lily pad at night")
	F.liliesUp(false)
	SpireTest.eq(Tile(WorldPoints.feat_lily_1):getGround():getId() ~= 17238, true, "water again by day")
	F.tideSet(true)
	SpireTest.eq(Tile(WorldPoints.feat_tide_1):getGround():getId(), 104, "a sandbar at low tide")
	F.tideSet(false)
	SpireTest.eq(Tile(WorldPoints.feat_tide_1):getGround():getId() ~= 104, true, "water at high tide")
	SpireTest.eq(F.vineWalls() > 0, true, "vine walls grow")
end)

SpireTest.add("town works: sizes, the daily cap and the pieces", function()
	SpireTest.eq(SpireWorks.size(1, 1), 20000, "five testers: the smallest project")
	SpireTest.eq(SpireWorks.size(1, 100), 400000, "a hundred accounts: four days of 1,000 each")
	SpireTest.eq(SpireWorks.size(5, 100) > SpireWorks.size(1, 100), true, "later projects are bigger")
	local ok, cap = SpireWorks.allowed(20000, 4000, 3000)
	SpireTest.eq(ok == 1000 and cap == 5000, true, "the daily cap stops one account")
	SpireTest.eq(SpireWorks.coinValue(3035, 3), 300, "platinum counts as 100")
	SpireTest.eq(SpireWorks.coinValue(3577, 1), nil, "meat is no money")
	local r = SpireWorks.ranked({ a = { name = "B", amount = 5 }, b = { name = "A", amount = 9 } })
	SpireTest.eq(r[1].name, "A", "the top giver first")
	for i = 1, 5 do
		SpireTest.eq(#(SpireWorksPieces[i] or {}) > 0, true, "project " .. i .. " has pieces")
	end
	SpireTest.eq(WorldPoints.works_board ~= nil and Tile(WorldPoints.works_board) ~= nil, true, "the Works Board stands in the Hearth")
end)
