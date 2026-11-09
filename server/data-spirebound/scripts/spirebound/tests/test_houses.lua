-- Phase 3: houses.
SpireTest.add("houses: head start, portal rules, dice", function()
	local now = 1000000
	local rec = { untilTime = now + 3600, credited = { "Hero" }, cap = 5, sold = 0 }
	SpireTest.eq((SpireHouses.headStartAllows(rec, "Hero", now)), true, "credited may buy")
	SpireTest.eq((SpireHouses.headStartAllows(rec, "Late", now)), false, "others wait")
	SpireTest.eq((SpireHouses.headStartAllows(rec, "Late", now + 3600)), true, "after the hour anyone may buy")
	rec.sold = 5
	SpireTest.eq((SpireHouses.headStartAllows(rec, "Hero", now)), false, "cap reached")
	SpireTest.eq((SpireHouses.headStartAllows(nil, "Anyone", now)), true, "no head start running")
	SpireTest.eq((SpireHouses.portalTargetAllowed("open", false, false, false)), true, "a field is fine")
	SpireTest.eq((SpireHouses.portalTargetAllowed("bossroom", false, false, false)), false, "boss rooms refused")
	SpireTest.eq((SpireHouses.portalTargetAllowed("deadzone", false, false, false)), false, "deadzones refused")
	SpireTest.eq((SpireHouses.portalTargetAllowed("open", true, false, false)), false, "near a boss refused")
	SpireTest.eq((SpireHouses.portalTargetAllowed("open", false, true, false)), false, "secret tiles refused")
	SpireTest.eq(SpireHouses.portalChangesLeft(2), 1, "one change left")
	SpireTest.eq(SpireHouses.portalChangesLeft(3), 0, "4th change refused")
	local win, cut = SpireHouses.dicePayout(1000)
	SpireTest.eq(win, 1900, "winner gets 2x minus 5%")
	SpireTest.eq(cut, 100, "100 gold destroyed")
	SpireTest.eq(SpireHouses.diceWins("high", 4), true, "4 is high")
	SpireTest.eq(SpireHouses.diceWins("low", 4), false, "4 is not low")
end)

SpireTest.add("houses: houses loaded with doorways, house spells use our words", function()
	local n = 0
	for _, h in ipairs(Game.getHouses()) do
		n = n + 1
		local entry = h:getExitPosition()
		if not Tile(entry) then error(h:getName() .. " has no entry tile") end
	end
	if n < 9 then error("only " .. n .. " houses") end
	SpireTest.eq(Spell("House Guest List") ~= nil, true, "house guest list spell")
end)
