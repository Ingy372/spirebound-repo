-- Roadmap 1.16: party bonus per member (DESIGN.md 7.1).
SpireTest.add("party: shared xp bonus beats solo", function()
	if not SpirePartyShare then
		error("SpirePartyShare missing: core override events/scripts/party.lua not loaded")
	end
	SpireTest.eq(SpirePartyShare(1000, 1, 1), 1000, "solo")
	-- S1b (2026-11-26): +50% per extra member. 3 players, 2 vocations: 1000 * (1 + 1.0 + 0.1) / 3 = 700 each
	SpireTest.eq(SpirePartyShare(1000, 3, 2), 700, "3 players, 2 vocations")
	-- 4 players, 4 vocations: 1000 * (1 + 1.5 + 0.3) / 4 = 700
	SpireTest.eq(SpirePartyShare(1000, 4, 4), 700, "4 players, 4 vocations")
	SpireTest.eq(SPIRE_PARTY_MAX, 8, "party cap (S4: 8, so a large-group ground fits in one party)")
end)
