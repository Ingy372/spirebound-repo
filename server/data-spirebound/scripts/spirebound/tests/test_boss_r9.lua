-- Roadmap R9: the rest of the boss system. Credit, warnings, the calendar and the private hall's rules go through the
-- same functions the live boss events call; the private hall is checked on the real map.

local function walkable(pos)
	local t = Tile(pos)
	return t ~= nil and t:getGround() ~= nil and t:isWalkable(false, false, false, false, true)
end

SpireTest.add("boss: healers and tanks earn credit, and a token hit does not", function()
	local st, now = SpireBoss.newState(), 1000
	SpireBoss.recordHit(st, "Striker", 6000, now)
	SpireBoss.recordHit(st, "Healer", 2500, now) -- healing the fighters
	SpireBoss.recordHit(st, "Tank", 1500, now) -- half of what it soaked
	SpireBoss.recordHit(st, "Poker", 50, now) -- a token hit (0.5%)
	local names = {}
	for _, n in ipairs(SpireBoss.credited(st, now + 10)) do
		names[n] = true
	end
	SpireTest.eq(names.Striker and names.Healer and names.Tank, true, "striker, healer and tank are credited")
	SpireTest.eq(names.Poker, nil, "a 0.5% token hit is not")
end)

SpireTest.add("boss: the enrage timer follows the real headcount", function()
	local st = SpireBoss.newState()
	st.started, st.headcount = 0, 2
	local two = Floors.enrageSeconds(2)
	SpireTest.eq(SpireBoss.enrageMultiplier(st, two - 1), 1, "two players: no enrage yet")
	st.headcount = 8 -- six more arrived later in the fight
	SpireTest.eq(SpireBoss.enrageMultiplier(st, two - 1) > 1, true, "eight players: the boss enrages sooner")
	SpireTest.eq(SpireBoss.ROOM_CAP, 20, "a boss room holds 20 players at most")
end)

SpireTest.add("boss: hits that can kill give a full second of warning (Q19)", function()
	SpireTest.eq(SpireBoss.warningMs(-180), 600, "a normal hit: 0.6 s")
	SpireTest.eq(SpireBoss.warningMs(-420), 1000, "a hit that can kill: 1.0 s")
end)

SpireTest.add("boss: rewards wait for players who were offline at the kill", function()
	kv.scoped("spirebound-boss-pending"):remove("Nobody Online Here")
	SpireTest.eq(SpireBoss.grantTitle("Nobody Online Here", "Test Title"), false, "an offline player can't get it now")
	local list = kv.scoped("spirebound-boss-pending"):get("Nobody Online Here")
	SpireTest.eq(list and list[1], "Test Title", "it waits for the next login")
	kv.scoped("spirebound-boss-pending"):remove("Nobody Online Here")
end)

SpireTest.add("boss: the season calendar seals each floor's hall until its day (Q13)", function()
	local s = kv.scoped("spirebound-season")
	local old = s:get("startedAt")
	s:remove("startedAt")
	SpireTest.eq((SpireBoss.calendarOpen(1, 12345)), true, "no season started: no gate")
	s:set("startedAt", 1000000)
	SpireTest.eq((SpireBoss.calendarOpen(1, 1000000 + 86400)), false, "day 2: Floor 1's hall is still sealed")
	SpireTest.eq((SpireBoss.calendarOpen(1, 1000000 + 2 * 86400)), true, "day 3: open")
	SpireTest.eq(SpireBoss.calendarOpensAt(2), 1000000 + 8 * 86400, "Floor 2's hall six days later")
	if old then
		s:set("startedAt", old)
	else
		s:remove("startedAt")
	end
end)

SpireTest.add("boss: the private hall takes a party of 1-5 once a day, after the floor is cleared", function()
	local now = 2000000
	local m = { { name = "A" }, { name = "B" } }
	SpireTest.eq((SpireBoss.privateCheck(m, true, false, false, now)), false, "not before the first clear")
	SpireTest.eq((SpireBoss.privateCheck(m, true, true, true, now)), false, "not while another party is inside")
	SpireTest.eq((SpireBoss.privateCheck(m, false, true, false, now)), false, "the whole party must be there")
	SpireTest.eq((SpireBoss.privateCheck(m, true, true, false, now)), true, "a party of two may go in")
	local six = { {}, {}, {}, {}, {}, {} }
	SpireTest.eq((SpireBoss.privateCheck(six, true, true, false, now)), false, "six is too many")
	m[2].lockedAt = now - 19 * 3600
	SpireTest.eq((SpireBoss.privateCheck(m, true, true, false, now)), false, "one member fought 19 hours ago: locked")
	m[2].lockedAt = now - 21 * 3600
	SpireTest.eq((SpireBoss.privateCheck(m, true, true, false, now)), true, "21 hours later: free")
	local def = SpireBoss.defs["Axe-Lord of the Stair"]
	SpireTest.eq(def.private ~= nil, true, "the Axe-Lord has a private hall")
	SpireTest.eq(walkable(WorldPoints[def.private.spawn]), true, "its hall is on the map")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints[def.private.spawn]), "bossroom", "it is a boss room (no cavebot, no murderers)")
	SpireTest.eq(WorldPoints.boss_private_floor1_exit ~= nil, true, "and has a way out")
end)
