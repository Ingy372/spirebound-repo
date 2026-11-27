-- Roadmap AD4: rare roaming monsters (adventure design 4.4).
local R = SpireRoamers

SpireTest.add("roamers: four, one per band, each a real monster with spots in every one of its grounds", function()
	SpireTest.eq(#R.list(), 4, "four roamers")
	for _, r in ipairs(R.list()) do
		SpireTest.eq(MonsterType(r.name) ~= nil, true, r.name .. " exists")
		SpireTest.eq(r.purse > 0, true, r.name .. " carries a purse")
		for _, gid in ipairs(r.grounds) do
			local spots = R.spots(gid)
			SpireTest.eq(#spots > 0, true, r.name .. " has a spot in " .. gid)
			local gate = WorldPoints["gate_" .. gid]
			for _, s in ipairs(spots) do
				if gate then
					SpireTest.eq(math.max(math.abs(s.x - gate.x), math.abs(s.y - gate.y)) >= 8, true, gid .. ": spot 8+ tiles from the gate")
				end
				for _, c in ipairs(SpireWilds.caves) do
					local inside = s.z == c.z and s.x >= c.x1 and s.x <= c.x2 and s.y >= c.y1 and s.y <= c.y2
					SpireTest.eq(inside, false, gid .. ": spot not in a party cave")
				end
			end
		end
	end
end)

SpireTest.add("roamers: the wait is 25 to 45 minutes, the rules for spots, coins and the keepsake", function()
	SpireTest.eq(R.delay(0), 1500, "shortest wait")
	SpireTest.eq(R.delay(1), 2700, "longest wait")
	SpireTest.eq(R.spotOk({ x = 100, y = 100, z = 7 }, { x = 104, y = 100 }, {}), false, "4 tiles from the gate: no")
	SpireTest.eq(R.spotOk({ x = 100, y = 100, z = 7 }, { x = 108, y = 100 }, {}), true, "8 tiles from the gate: yes")
	SpireTest.eq(R.spotOk({ x = 100, y = 100, z = 8 }, nil, { { x1 = 90, y1 = 90, x2 = 110, y2 = 110, z = 8 } }), false, "in a party cave: no")
	SpireTest.eq(R.spotOk({ x = 100, y = 100, z = 7 }, nil, { { x1 = 90, y1 = 90, x2 = 110, y2 = 110, z = 8 } }), true, "above the cave: yes")
	local plat, gold = R.coins(1780)
	SpireTest.eq(plat, 17, "1780 gold = 17 platinum")
	SpireTest.eq(gold, 80, "and 80 gold")
	SpireTest.eq(R.keepsakeRoll(0, 0.03), true, "a 3% roll under 4%: keepsake")
	SpireTest.eq(R.keepsakeRoll(10, 0.5), false, "an ordinary kill: no keepsake")
	SpireTest.eq(R.keepsakeRoll(75, 0.99), true, "pity: sure at three times the expected wait (75 kills)")
end)

SpireTest.add("roamers: one comes out at a real spot of its grounds and is gone again", function()
	local m, why = R.spawn("frenzied_boar")
	SpireTest.eq(m ~= nil, true, "the Frenzied Boar came out (" .. tostring(why) .. ")")
	local cur = R.current
	SpireTest.eq(cur and (cur.ground == "boar_meadow" or cur.ground == "burrow_hills"), true, "in one of its grounds")
	local again = R.spawn("pale_stag")
	SpireTest.eq(again, nil, "only one roamer at a time")
	m:remove()
	R.current = nil
	local p, why2 = R.spawn("paymaster")
	SpireTest.eq(p ~= nil, true, "the Paymaster came out (" .. tostring(why2) .. ")")
	SpireTest.eq(#R.current.guards, 2, "with his two guards")
	for _, cid in ipairs(R.current.guards) do
		local g = Creature(cid)
		if g then g:remove() end
	end
	p:remove()
	R.current = nil
end)
