-- Roadmap AD5: the Smugglers' Vault (s14) and the Sealed Cut (s15), each with a hidden beast and a trophy.
local H = SpireHidden

SpireTest.add("hidden places: two new secrets with a beast and a trophy each, on the map", function()
	for _, row in ipairs({ { "s14", "ironpurse", "Ironpurse" }, { "s15", "the_unfinished", "The Unfinished" } }) do
		local sid, tid, boss = row[1], row[2], row[3]
		local s = SpireSecrets.get(sid)
		SpireTest.eq(s ~= nil and s.floor == 1, true, sid .. " is a Floor 1 secret")
		SpireTest.eq(s.hint:find("Vault", 1, true) == nil and s.hint:find("Quarry", 1, true) == nil, true, sid .. "'s hint is a riddle")
		local t = SpireTrophies.get(tid)
		SpireTest.eq(t ~= nil and t.secret == sid and t.boss == boss, true, tid .. " is woken at " .. sid)
		SpireTest.eq(MonsterType(boss) ~= nil, true, boss .. " exists")
		SpireTest.eq(WorldPoints["secret_" .. sid] ~= nil and WorldPoints[t.spawn] ~= nil, true, sid .. " and its beast are on the map")
	end
	for _, name in ipairs({ "vault_grate", "vault_entry", "vault_exit", "sealed_cut_mouth", "sealed_cut_entry", "sealed_cut_exit" }) do
		local p = WorldPoints[name]
		SpireTest.eq(p ~= nil and Tile(p) ~= nil, true, name .. " is on the map")
	end
end)

SpireTest.add("hidden places: the grate, the sealed mouth and the three marked stones are ready to use", function()
	SpireHidden.place()
	SpireTest.eq(Tile(WorldPoints.vault_grate):getGround():getActionId(), 47160, "the grate takes a Vault Key")
	SpireTest.eq(Tile(WorldPoints.sealed_cut_mouth):getTopTopItem():getActionId(), 47161, "the rubble takes the rubbings")
	for _, gid in ipairs(H.RUBBING_GROUNDS) do
		local p = H.marks[gid]
		SpireTest.eq(p ~= nil and SpireRoamers.groundAt(p) == gid, true, "a marked stone stands in " .. gid)
		SpireTest.eq(ItemType(H.RUBBINGS[gid]):isPickupable(), true, gid .. "'s rubbing can be carried")
	end
	SpireTest.eq(ItemType(H.KEY):getName(), "Vault Key", "the key's name")
end)

SpireTest.add("hidden places: the trophies' bonuses and the rubbing rules", function()
	SpireTest.eq(H.goldBonus({ ironpurse = 1 }), 0.02, "Ironpurse's Tally: +2% gold")
	SpireTest.eq(H.armourBonus({ the_unfinished = 1 }), 1, "Unfinished Hand: +1 armour")
	SpireTest.eq(H.goldBonus({}), 0, "no trophy, no bonus")
	SpireTest.eq(H.armoured(-40, 1), -39, "a 40 hit becomes 39")
	SpireTest.eq(H.armoured(-1, 1), 0, "a 1 hit does nothing")
	local have = { [H.RUBBINGS.old_quarry] = 1, [H.RUBBINGS.shard_fields] = 1 }
	local missing = H.missingRubbings(function(id) return have[id] or 0 end)
	SpireTest.eq(#missing == 1 and missing[1] == "fallen_bastion", true, "the Bastion's rubbing is missing")
	SpireTest.eq(type(SpireTrophies.state("ironpurse")), "string", "Ironpurse is ready (not resting) at start-up")
end)
