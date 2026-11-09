-- Roadmap 2.1 - 2.4: PvP rules (DESIGN.md 6).
SpireTest.add("pvp: zone tiers from the map", function()
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.temple_hearthgate), "town", "temple")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.camp_starter_west), "guarded", "starter field")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.apex_watchtower), "contested", "apex approach")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.boss_room_floor1), "bossroom", "boss room")
	SpireTest.eq(SpirePvP.zoneAt(WorldPoints.camp_shard_fields), "open", "a normal camp")
end)

SpireTest.add("pvp: newbie and level-range protection", function()
	local function can(al, vl, zone, extra)
		local v = { level = vl, skull = SKULL_NONE }
		for k, x in pairs(extra or {}) do v[k] = x end
		return (SpirePvP.canAttack({ level = al, skull = SKULL_NONE }, v, zone))
	end
	SpireTest.eq(can(200, 40, "open"), false, "level 40 is protected")
	SpireTest.eq(can(40, 200, "open"), false, "a level 40 can't attack either")
	SpireTest.eq(can(200, 40, "bossroom"), true, "no newbie protection in boss rooms")
	SpireTest.eq(can(200, 139, "open"), false, "level 200 can't start on 139")
	SpireTest.eq(can(200, 140, "open"), true, "140 is in range")
	SpireTest.eq(can(200, 139, "open", { attackedMeRecently = true }), true, "can fight back")
	SpireTest.eq(can(200, 139, "open", { skull = SKULL_RED }), true, "murderers are never protected")
	SpireTest.eq(can(200, 100, "contested"), true, "no level range in Contested")
	SpireTest.eq(can(200, 150, "town"), false, "never in town")
	SpireTest.eq(can(200, 150, "open", { sanctuaryVsMyGuild = true }), false, "sanctuary")
end)

SpireTest.add("pvp: unjust kill weights and skulls", function()
	SpireTest.eq(SpirePvP.unjustWeight(100, 90, "open", false), 1, "normal")
	SpireTest.eq(SpirePvP.unjustWeight(100, 90, "guarded", false), 3, "guarded counts triple")
	SpireTest.eq(SpirePvP.unjustWeight(100, 60, "open", false), 2, "bully doubles")
	SpireTest.eq(SpirePvP.unjustWeight(100, 90, "open", true), 2, "death game victim doubles")
	SpireTest.eq(SpirePvP.unjustWeight(100, 90, "contested", false), 0, "contested never counts")
	local now = 10000000
	local function frags(n, age)
		local t = {}
		for i = 1, n do table.insert(t, { t = now - age, w = 1 }) end
		return t
	end
	SpireTest.eq(SpirePvP.skullFor(frags(2, 100), now), nil, "2 kills today: no red")
	SpireTest.eq(SpirePvP.skullFor(frags(3, 100), now), SKULL_RED, "3 today: red")
	SpireTest.eq(SpirePvP.skullFor(frags(5, 3 * 86400), now), SKULL_RED, "5 this week: red")
	SpireTest.eq(SpirePvP.skullFor(frags(6, 100), now), SKULL_BLACK, "6 today: black")
	SpireTest.eq(SpirePvP.skullFor(frags(4, 40 * 86400), now), nil, "old kills expire")
	SpireTest.eq(SpirePvP.deathLossMultiplier(SKULL_RED), 2, "red death costs double")
end)

SpireTest.add("pvp: outnumbered shield and guild sanctuary", function()
	SpireTest.eq(SpirePvP.outnumberedReduction(2), 0, "2 attackers: fair fight")
	SpireTest.eq(SpirePvP.outnumberedReduction(3), 10, "3 attackers")
	SpireTest.eq(SpirePvP.outnumberedReduction(4), 20, "4 attackers")
	SpireTest.eq(SpirePvP.outnumberedReduction(10), 40, "capped at 40%")
	local now = 100000
	SpireTest.eq(SpirePvP.sanctuaryDue({ now - 100 }, now), false, "one kill")
	SpireTest.eq(SpirePvP.sanctuaryDue({ now - 100, now - 5 * 3600 }, now), true, "two kills in 6 hours")
	SpireTest.eq(SpirePvP.sanctuaryDue({ now - 100, now - 7 * 3600 }, now), false, "outside the window")
	SpireTest.eq(SpirePvP.cursor(SKULL_NONE), "green", "clean cursor")
	SpireTest.eq(SpirePvP.cursor(SKULL_WHITE), "orange", "aggressor cursor")
end)
