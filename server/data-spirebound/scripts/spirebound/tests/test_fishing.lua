-- Roadmap 2.9: fishing.
SpireTest.add("fishing: catch table, night fish, bite chance", function()
	SpireTest.eq(SpireFishing.roll(1, false, 0).id, "hearth_minnow", "lowest roll")
	local nightSeen, daySeen = false, false
	for i = 0, 999 do
		local r = i / 1000
		if SpireFishing.roll(1, true, r).id == "moonscale_eel" then nightSeen = true end
		if SpireFishing.roll(1, false, r).id == "moonscale_eel" then daySeen = true end
	end
	SpireTest.eq(nightSeen, true, "eel bites at night")
	SpireTest.eq(daySeen, false, "eel never bites by day")
	SpireTest.eq(SpireFishing.biteChance(10), 25, "low skill floor")
	SpireTest.eq(SpireFishing.biteChance(200), 70, "high skill cap")
	SpireTest.eq(SpireFishing.fishKinds(1), 7, "7 kinds of fish on floor 1")
	SpireTest.eq(SpireFishing.titleFor(5), "Angler", "angler title")
	SpireTest.eq(SpireFishing.BITE_WINDOW, 3, "3 seconds to react")
	local t = systemTime()
	if type(t) ~= "number" or t < 1000000000000 then
		error("systemTime() is not milliseconds: " .. tostring(t))
	end
end)
