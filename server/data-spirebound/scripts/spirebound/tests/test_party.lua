-- Roadmap 1.16: party bonus per member (DESIGN.md 7.1).
SpireTest.add("party: shared xp bonus beats solo", function()
	if not SpirePartyShare then
		error("SpirePartyShare missing: core override events/scripts/party.lua not loaded")
	end
	SpireTest.eq(SpirePartyShare(1000, 1, 1), 1000, "solo")
	-- 3 players, 2 vocations: 1000 * (1 + 0.6 + 0.1) / 3 = 566.67 -> 567 each
	SpireTest.eq(SpirePartyShare(1000, 3, 2), 567, "3 players, 2 vocations")
	-- 4 players, 4 vocations: 1000 * (1 + 0.9 + 0.3) / 4 = 550
	SpireTest.eq(SpirePartyShare(1000, 4, 4), 550, "4 players, 4 vocations")
	SpireTest.eq(SPIRE_PARTY_MAX, 6, "party cap")
end)
