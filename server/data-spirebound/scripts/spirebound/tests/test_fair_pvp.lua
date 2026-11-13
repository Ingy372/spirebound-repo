-- Roadmap R7: fair PvP credit. The damage records are written by SpirePvP.noteDamage, the same call the real
-- onHealthChange event makes; the death handler then asks SpirePvP.participants / bountyShares, tested here.

local function walkable(pos)
	local t = Tile(pos)
	return t ~= nil and t:getGround() ~= nil and t:isWalkable(false, false, false, false, true)
end

SpireTest.add("fair pvp: everyone with meaningful damage takes part in a kill, not only the last hit", function()
	local v, now, hp = 201, 900000, 1000
	SpirePvP.damage[v] = nil
	SpirePvP.noteDamage(v, 11, 400, now - 20) -- the real fighter
	SpirePvP.noteDamage(v, 12, 150, now - 10) -- a helper (15%)
	SpirePvP.noteDamage(v, 13, 30, now - 5) -- a 3% poke
	SpirePvP.noteDamage(v, 14, 500, now - 90) -- too long ago
	local parts = SpirePvP.participants(v, 15, hp, now) -- 15 lands the killing blow
	local got = {}
	for _, p in ipairs(parts) do
		got[p.guid] = p.damage
	end
	SpireTest.eq(got[11], 400, "the main attacker takes part")
	SpireTest.eq(got[12], 150, "a 15% helper takes part")
	SpireTest.eq(got[13], nil, "a 3% poke does not")
	SpireTest.eq(got[14], nil, "damage older than a minute does not")
	SpireTest.eq(got[15], 0, "the killing blow always takes part")
	SpireTest.eq(parts[1].guid, 11, "most damage first")
	SpirePvP.damage[v] = nil
end)

SpireTest.add("fair pvp: the outnumbered shield counts only outsiders who did real damage", function()
	local v, now, hp = 202, 910000, 1000
	SpirePvP.damage[v] = nil
	SpirePvP.noteDamage(v, 21, 80, now - 2) -- outsider, real
	SpirePvP.noteDamage(v, 22, 60, now - 3) -- outsider, real
	SpirePvP.noteDamage(v, 23, 10, now - 3) -- outsider, a tap
	SpirePvP.noteDamage(v, 24, 300, now - 1) -- the victim's own party member
	local outsider = function(g)
		return g ~= 24
	end
	SpireTest.eq(SpirePvP.outnumberedCount(v, hp, now, outsider), 2, "two real outside attackers")
	SpireTest.eq(SpirePvP.outnumberedCount(v, hp, now + 20, outsider), 0, "old hits stop counting")
	SpirePvP.damage[v] = nil
end)

SpireTest.add("fair pvp: bounties are shared by damage among those who may claim them", function()
	local parts = { { guid = 31, damage = 600 }, { guid = 32, damage = 300 }, { guid = 33, damage = 100 } }
	local shares = SpirePvP.bountyShares(10000, parts, function(g)
		return g ~= 33 -- 33 partied with the target yesterday
	end)
	SpireTest.eq(shares[31], 6666, "two thirds to the main attacker")
	SpireTest.eq(shares[32], 3334, "a third to the helper")
	SpireTest.eq(shares[33], nil, "a recent party partner gets nothing")
	local target = { guid = 1, ip = 1, guildId = 0, partyId = nil, partiedRecently = { [5] = true } }
	SpireTest.eq((SpireBounty.validClaimer(target, { guid = 5, ip = 2, guildId = 0 })), false, "the partner rule is wired into the claim check")
	SpirePvP.notePartners({ 9001, 9002 }, os.time())
	SpireTest.eq(SpirePvP.partnersOf(9001, os.time())[9002], true, "joining a party records partners")
	SpireTest.eq(SpirePvP.partnersOf(9001, os.time() + 25 * 3600)[9002], nil, "after 24 hours they are free again")
	kv.scoped("spirebound-partners"):remove("9001")
	kv.scoped("spirebound-partners"):remove("9002")
end)

SpireTest.add("fair pvp: healing a skulled player drops your protection for five minutes", function()
	local now = 920000
	SpirePvP.noteAid(41, now)
	SpireTest.eq(SpirePvP.aiding(41, now + 299), true, "still exposed after 4:59")
	SpireTest.eq(SpirePvP.aiding(41, now + 301), false, "protected again after 5 minutes")
	local a = { level = 80, skull = SKULL_NONE }
	SpireTest.eq((SpirePvP.canAttack(a, { level = 20, skull = SKULL_NONE }, "open")), false, "a level 20 is normally protected")
	SpireTest.eq((SpirePvP.canAttack(a, { level = 20, skull = SKULL_NONE, aidedSkull = true }, "open")), true, "a level 20 healer of a murderer is not")
end)

SpireTest.add("fair pvp: murderers wake in the Outlaw Camp, outside every town", function()
	local p = WorldPoints.outlaw_camp
	SpireTest.eq(p ~= nil and walkable(p), true, "the Outlaw Camp is on the map")
	SpireTest.eq(SpirePvP.zoneAt(p), "open", "it is not in a town or a Guarded zone")
end)
