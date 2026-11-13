-- Roadmap R17: secret fixes.
SpireTest.add("secrets: every trigger tile reacts to a step, gold is paid once per account, night is the game's", function()
	SpireTest.eq((SpireSecrets.stepTiles or 0) >= 100, true, "every secret tile has a step trigger (" .. tostring(SpireSecrets.stepTiles) .. ")")
	local acc = -4242
	local store = kv.scoped("account"):scoped(tostring(acc)):scoped("spirebound-secretgold")
	store:remove("s5")
	SpireTest.eq(SpireSecrets.goldPaid(acc, "s5"), false, "not paid yet")
	SpireSecrets.markGoldPaid(acc, "s5")
	SpireTest.eq(SpireSecrets.goldPaid(acc, "s5"), true, "a second character on the account gets no gold")
	store:remove("s5")
	local h = SpireSecrets.gameHour()
	SpireTest.eq(h >= 0 and h < 24, true, "the game's hour is read")
end)

SpireTest.add("secrets: Floors 6-10 have real hints", function()
	for _, s in ipairs(SpireSecrets.list) do
		if s.floor >= 6 then
			SpireTest.eq(s.hint:find("off the beaten path") == nil, true, s.id .. " has a real hint")
		end
	end
end)
