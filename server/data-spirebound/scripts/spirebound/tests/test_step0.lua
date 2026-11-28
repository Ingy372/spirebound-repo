-- Roadmap Step 0: Jay's answers of 2026-11-27 (QUESTIONS.md). One test per task where a rule can be checked here;
-- each task is also checked in the real client (PROGRESS.md says how).

SpireTest.add("QA2: secret gear trades like other gear (Q100)", function()
	for _, g in ipairs(SpireGearData.secretGear) do
		local item = SpireGear.makeSecret(g)
		SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_DESCRIPTION):find("can't", 1, true), nil, g.id .. ": the look text no longer says it can't be traded")
		item:remove()
	end
end)

SpireTest.add("QA4: reward gold is paid in coins, largest first (Q76)", function()
	local s = SpireGive.coinStacks(12345)
	SpireTest.eq(#s, 3, "a crystal, platinum and gold stack")
	SpireTest.eq(s[1].id .. ":" .. s[1].count, "3043:1", "one crystal coin")
	SpireTest.eq(s[2].id .. ":" .. s[2].count, "3035:23", "23 platinum")
	SpireTest.eq(s[3].id .. ":" .. s[3].count, "3031:45", "45 gold")
	local total = 0
	for _, x in ipairs(SpireGive.coinStacks(2500000)) do
		SpireTest.eq(x.count <= 100, true, "no stack over 100")
		total = total + x.value
	end
	SpireTest.eq(total, 2500000, "every coin counted")
	SpireTest.eq(SpireGive.goldWhere(500, 0), "in your backpack", "all in the bag")
	SpireTest.eq(SpireGive.goldWhere(0, 500):find("bank", 1, true) ~= nil, true, "a full backpack: the bank")
	-- a real backpack on the ground stands in for the player
	local bp = Game.createItem(2854, 1, WorldPoints.temple_hearthgate)
	local p = { bank = 0 }
	function p:addItemEx(it) return bp:addItemEx(it) end
	function p:getBankBalance() return self.bank end
	function p:setBankBalance(n) self.bank = n end
	local bag, bank = SpireGive.gold(p, 345)
	SpireTest.eq(bag .. "/" .. bank, "345/0", "345 gold in the bag")
	SpireTest.eq(SpireTest.coinValue(bp), 345, "the coins are really there")
	bp:remove()
end)
