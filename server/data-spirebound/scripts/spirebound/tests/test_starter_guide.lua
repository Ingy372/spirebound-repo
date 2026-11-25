-- Starter letter and !spells list (playtest 2026-11-11)

SpireTest.add("guide: the letter names the first steps and fits in a letter", function()
	local text = SpireGuide.TEXT
	SpireTest.eq(#text < 1000, true, "letter text is under the 1023-character limit")
	for _, word in ipairs({ "Journal", "Millcross", "Gate Hound", "Vesper", "!spells" }) do
		SpireTest.eq(text:find(word, 1, true) ~= nil, true, "letter mentions " .. word)
	end
end)

SpireTest.add("guide: !spells lists only the vocation's own spells, marking what is learned", function()
	local lines = SpireGuide.spellLines(1, 8) -- Arcanist at level 8
	local joined = table.concat(lines, "\n")
	SpireTest.eq(joined:find("Kindle", 1, true) ~= nil, true, "shared spell listed")
	SpireTest.eq(joined:find("Kindle[^\n]*learned") ~= nil, true, "level 8 spell is learned at level 8")
	SpireTest.eq(joined:find("Second Wind", 1, true) == nil, true, "a Vanguard spell is not listed for an Arcanist")
	SpireTest.eq(joined:find("Arc Beam[^\n]*level 23") ~= nil, true, "level 23 spell is shown as locked at level 8")
	SpireTest.eq(joined:find("Wayfinder[^\n]*level 10") ~= nil, true, "shared spells show the Arcanist's own level")
end)

SpireTest.add("guide: !spells keeps style abilities apart and never calls them learned without the style (C2)", function()
	local joined = table.concat(SpireGuide.spellLines(3, 8, nil), "\n") -- Ranger, level 8, no style progress
	SpireTest.eq(joined:find("Farshot[^\n]*learned") == nil, true, "a path ability is not learned at level 8")
	SpireTest.eq(joined:find("Last Light[^\n]*learned") == nil, true, "a final-style ability is not learned at level 8")
	SpireTest.eq(joined:find("Style abilities", 1, true) ~= nil, true, "style abilities have their own section")
	SpireTest.eq(joined:find("Piercing Shot[^\n]*learned") ~= nil, true, "the level-1 spell is still learned")
	local view = SpireStyle.view(3, 999999, "marksman", nil, nil)
	SpireTest.eq(SpireGuide.ownsStyle({ style = 2, path = "marksman" }, view), SpireStyle.hasAbilityPure(view, 2), "the chosen path's ability follows the style tree")
	SpireTest.eq(SpireGuide.ownsStyle({ style = 2, path = "trapper" }, view), false, "another path's ability is not owned")
end)
