-- Roadmap 1.14b: spells to level 50, unlocked by level, per vocation.
SpireTest.add("spells: every row up to level 50 registers, with its level", function()
	local count = 0
	for _, row in ipairs(SpireSpells.list) do
		local s = Spell(row.name)
		if not s then
			error(row.name .. " not registered")
		end
		count = count + 1
	end
	if count < 40 then
		error("only " .. count .. " spells")
	end
end)

SpireTest.add("spells: each vocation gets 8 shared + its own, nothing from others", function()
	local per = { 0, 0, 0, 0 }
	for _, row in ipairs(SpireSpells.list) do
		for v = 1, 4 do
			if row.level <= 50 and SpireSpells.allowed(row, v) then
				per[v] = per[v] + 1
			end
		end
	end
	SpireTest.eq(per[4], 15, "vanguard spells to level 50")
	SpireTest.eq(per[3], 16, "ranger spells to level 50")
	SpireTest.eq(per[1], 17, "arcanist spells to level 50")
	SpireTest.eq(per[2], 18, "mystic spells to level 50")
	local voc0 = 0
	for _, row in ipairs(SpireSpells.list) do
		if SpireSpells.allowed(row, 0) then
			voc0 = voc0 + 1
		end
	end
	SpireTest.eq(voc0, 0, "no vocation yet: no spells")
	local names = {}
	for _, r in ipairs(SpireSpells.unlockedAt(14, 1)) do
		names[r.name] = true
	end
	SpireTest.eq(names["Mana Ward"] and names["Hearth Ration"] and names["Quickstep"] and not names["Thorn Strike"], true, "arcanist level 14 unlocks")
end)

SpireTest.add("spells: no ammo conjuring, damage buffs math", function()
	for _, row in ipairs(SpireSpells.list) do
		if row.kind == "conjure" and (row.item == 3447 or row.item == 3446 or row.item == 3277) then
			error(row.name .. " conjures ammunition")
		end
	end
	SpireTest.eq(SpireBuffs.apply(100, 30, 0), 70, "30% reduction")
	SpireTest.eq(SpireBuffs.apply(100, 0, 10), 110, "10% mark")
	SpireTest.eq(SpireBuffs.apply(100, 10, 10), 99, "both")
end)

SpireTest.add("vocations: weapons and runes use Spirebound vocation names", function()
	local wand = ItemType(3074)
	if wand.getVocationString and wand:getVocationString() ~= "" then
		local v = wand:getVocationString():lower()
		if not v:find("arcanist") then
			error("wand of vortex vocations: " .. v)
		end
	end
end)

SpireTest.add("spells: about 20 per vocation including Lost Arts", function()
	local per, lost = { 0, 0, 0, 0 }, { 0, 0, 0, 0 }
	for _, row in ipairs(SpireSpells.list) do
		for v = 1, 4 do
			if SpireSpells.allowed(row, v) then
				per[v] = per[v] + 1
				if row.lostArt then lost[v] = lost[v] + 1 end
			end
		end
	end
	for v = 1, 4 do
		if per[v] < 19 then error("vocation " .. v .. " has only " .. per[v] .. " spells") end
		SpireTest.eq(lost[v], 2, "lost arts for vocation " .. v)
	end
	local row = { lostArt = 5 }
	SpireTest.eq(SpireSpells.knowsLostArt(row, function(f) return false end), false, "not yet earned")
	SpireTest.eq(SpireSpells.knowsLostArt(row, function(f) return f == 5 end), true, "earned on floor 5")
	for _, r in ipairs(SpireSpells.unlockedAt(100, 1)) do
		if r.lostArt then error("Lost Arts must not unlock by level") end
	end
end)
