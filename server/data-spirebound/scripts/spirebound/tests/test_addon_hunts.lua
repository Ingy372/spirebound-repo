-- Roadmap AD5: three addon quests that were kill counts are hunts for a named target (adventure design 4.5, Q71).
local H = SpireAddonHunts

local function quest(id)
	for _, q in ipairs(SpireQuests.list) do
		if q.id == id then
			return q
		end
	end
end

SpireTest.add("addon hunts: Ranger, Arcanist and Mystic addon 2 hunt a named target after 15 of its kind", function()
	for id, h in pairs(SpireAdventureData.addonHunts) do
		local q = quest(id)
		SpireTest.eq(q ~= nil and q.addon == 2, true, id .. " is an addon 2 quest")
		SpireTest.eq(q.target, h.target, id .. ": the quest counts the named target")
		SpireTest.eq(q.count, 1, id .. ": one kill of it")
		SpireTest.eq(q.hunt.kind, h.kind, id .. ": its kind")
		SpireTest.eq(q.hunt.count, 15, id .. ": comes out after 15")
		SpireTest.eq(q.hunt.ground, h.ground, id .. ": in its ground")
		SpireTest.eq(MonsterType(q.target) ~= nil, true, q.target .. " exists")
		SpireTest.eq(#SpireRoamers.spots(q.hunt.ground) > 0, true, q.target .. " has somewhere to come out")
		SpireTest.eq(q.step:find("15", 1, true) ~= nil and q.step:find((q.target:gsub("^The ", "the ")), 1, true) ~= nil, true,
			id .. ": the Journal says what to do (" .. q.step .. ")")
	end
end)

SpireTest.add("addon hunts: only kills of the kind, in the ground, while it is not out, count", function()
	SpireTest.eq(select(1, H.step(3, 15, true, true, false)), true, "a crossbowman on the ridge counts")
	SpireTest.eq(select(2, H.step(3, 15, true, true, false)), false, "the 4th does not call her yet")
	SpireTest.eq(select(2, H.step(14, 15, true, true, false)), true, "the 15th calls her out")
	SpireTest.eq(select(1, H.step(3, 15, false, true, false)), false, "a crossbowman elsewhere does not count")
	SpireTest.eq(select(1, H.step(3, 15, true, true, true)), false, "nothing counts while she is out")
	H.hook()
	SpireTest.eq(H.hooked, true, "every quest kill reaches the hunts")
end)
