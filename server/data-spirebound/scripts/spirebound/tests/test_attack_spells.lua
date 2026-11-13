-- Jay's playtest (2026-11-13): Rangers and Vanguards get attack spells from level 8, registered with the game.
SpireTest.add("spells: every vocation has an attack spell at level 8", function()
	for voc = 1, 4 do
		local found = nil
		for _, row in ipairs(SpireSpells.list) do
			if (row.kind == "attack_target" or row.kind == "attack_area") and row.level <= 8 and type(row.voc) == "table" then
				for _, v in ipairs(row.voc) do
					if v == voc then found = row end
				end
			end
		end
		SpireTest.eq(found ~= nil, true, "vocation " .. voc .. " has an attack spell by level 8")
		SpireTest.eq(Spell(found.name) ~= nil, true, found.name .. " is a real spell in the game")
	end
end)
