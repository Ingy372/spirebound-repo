-- Roadmap 2.5 / 2.6: bounties and consent wars.
SpireTest.add("bounty: who may collect", function()
	local target = { guid = 1, ip = 111, guildId = 5, partyId = 9, partiedRecently = { [7] = true } }
	SpireTest.eq((SpireBounty.validClaimer(target, { guid = 2, ip = 222, guildId = 6 })), true, "stranger collects")
	SpireTest.eq((SpireBounty.validClaimer(target, { guid = 3, ip = 111, guildId = 6 })), false, "same IP refused")
	SpireTest.eq((SpireBounty.validClaimer(target, { guid = 4, ip = 444, guildId = 5 })), false, "same guild refused")
	SpireTest.eq((SpireBounty.validClaimer(target, { guid = 5, ip = 555, guildId = 0, partyId = 9 })), false, "same party refused")
	SpireTest.eq((SpireBounty.validClaimer(target, { guid = 7, ip = 777, guildId = 0 })), false, "recent party partner refused")
	SpireTest.eq(SpireBounty.fine(100, 50000), 50000, "fine limited by bank")
	SpireTest.eq(SpireBounty.fine(100, 500000), 100000, "fine = level x 1000")
end)

SpireTest.add("bounty: board stores and clears", function()
	SpireBounty.clear(999999)
	SpireBounty.add(999999, "Testvillain", 5000, "A")
	SpireTest.eq(SpireBounty.add(999999, "Testvillain", 2500, "B"), 7500, "bounties add up")
	local found = false
	for _, b in ipairs(SpireBounty.list()) do
		if b.name == "Testvillain" then found = true end
	end
	SpireTest.eq(found, true, "bounty shows on the board")
	SpireBounty.clear(999999)
	SpireTest.eq(SpireBounty.get(999999).total, 0, "cleared")
end)

SpireTest.add("war: terms and 7-day cooldown", function()
	SpireTest.eq((SpireWar.validTerms(7, 0)), true, "7 days, no kill limit")
	SpireTest.eq((SpireWar.validTerms(0, 0)), false, "0 days refused")
	SpireTest.eq((SpireWar.validTerms(15, 0)), false, "15 days refused")
	SpireTest.eq(SpireWar.cooldownOver(0, 1000000), true, "never fought")
	SpireTest.eq(SpireWar.cooldownOver(1000000 - 3 * 86400, 1000000), false, "fought 3 days ago")
	SpireTest.eq(SpireWar.cooldownOver(1000000 - 8 * 86400, 1000000), true, "fought 8 days ago")
end)
