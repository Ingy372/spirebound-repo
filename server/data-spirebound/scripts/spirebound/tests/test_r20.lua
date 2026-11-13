-- Roadmap R20: small fixes.
SpireTest.add("r20: per-player memory is forgotten at logout", function()
	SpireTest.eq(#SpireCleanup.fns >= 5, true, "the scripts that keep per-player tables registered a cleanup")
	SpirePvP.damage[777001] = { [5] = { { 1, 1 } } }
	SpireCleanup.run(-1, 777001)
	SpireTest.eq(SpirePvP.damage[777001], nil, "a logged-out player's damage record is gone")
end)

SpireTest.add("r20: the Rapid Respawn weekend fills every ground and brings extra groups back faster", function()
	local found = false
	for _, w in ipairs(SpireEvents.WEEKEND) do
		found = found or w.id == "respawn"
	end
	SpireTest.eq(found, true, "Rapid Respawn is one of the weekend bonuses")
	local g = SpireCrowd.ground("burrow_hills")
	SpireCrowd.grounds[g.id] = nil
	SpireCrowd.forceRapid = true
	local state = SpireCrowd.update(g, 7000000, 0, function() return true end)
	SpireCrowd.forceRapid = nil
	SpireCrowd.grounds[g.id] = nil
	SpireTest.eq(state, "packed", "with nobody there, the ground still counts as packed")
end)

SpireTest.add("r20: the Derby pays a winner who logged off", function()
	db.query("UPDATE `players` SET `balance` = 0 WHERE `name` = 'Test Ranger'")
	SpireEvents.payDerby("Test Ranger")
	local r = db.storeQuery("SELECT `balance` FROM `players` WHERE `name` = 'Test Ranger'")
	local bal = r and Result.getNumber(r, "balance") or 0
	if r then Result.free(r) end
	SpireTest.eq(bal, 50000, "50,000 gold reach the offline winner's bank")
	local list = kv.scoped("spirebound-boss-pending"):get("Test Ranger") or {}
	SpireTest.eq(list[#list], "Derby Champion", "the title waits for the next login")
	kv.scoped("spirebound-boss-pending"):remove("Test Ranger")
	db.query("UPDATE `players` SET `balance` = 0 WHERE `name` = 'Test Ranger'")
end)
