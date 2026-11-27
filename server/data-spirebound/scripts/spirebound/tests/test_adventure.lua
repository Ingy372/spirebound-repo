-- Adventure layer (docs/superpowers/specs/2026-11-27-adventure-layer-design.md): the seam Session B calls, and AD1-AD3, AD6, AD7.
SpireTest.add("adventure: find lines read right and never give a place away", function()
	local L = SpireFinds.line
	SpireTest.eq(L("rare_weapon", { "Ana" }, { item = "Copsewood Bow", from = "Grey Alpha" }), "Ana found a Copsewood Bow on a Grey Alpha!", "rare weapon")
	SpireTest.eq(L("rare_weapon", { "Ana" }, { item = "Ironbark Staff", from = "Old Bristleback" }), "Ana found an Ironbark Staff on an Old Bristleback!", "a/an")
	SpireTest.eq(L("fish", { "Bo" }, { name = "Old Whiskers", kg = 17.43 }), "Bo landed Old Whiskers (17.4 kg)!", "fish")
	SpireTest.eq(L("secret", {}, nil, 1), "Someone has found a secret on Floor 1.", "secret: the floor only")
	SpireTest.eq(L("secret", {}, nil, "Wolf Copse"), "Someone has found a secret on Floor 1.", "secret: a ground name is never used")
	SpireTest.eq(L("roamer_seen", {}, "Goldback Toad", "Millcross"), "A Goldback Toad has been sighted in Millcross!", "no article for a town")
	SpireTest.eq(L("beast", {}, nil, 1), "A hidden beast has fallen somewhere on Floor 1.", "beast")
	SpireTest.eq(L("roamer_seen", {}, "Frenzied Boar", "Boar Meadow"), "A Frenzied Boar has been sighted in the Boar Meadow!", "sighted")
	SpireTest.eq(L("roamer_seen", {}, "The Paymaster", "Bandit Road"), "The Paymaster has been sighted in the Bandit Road!", "sighted, the")
	SpireTest.eq(L("roamer_killed", { "Ana", "Bo", "Cy" }, "The Paymaster"), "Ana, Bo and Cy brought down the Paymaster!", "killed")
	SpireTest.eq(L("roamer_killed", { "Ana", false }, "Frenzied Boar"), "Ana and one other brought down the Frenzied Boar!", "an anonymous name")
	SpireTest.eq(L("keepsake", { false }, "Smuggler's Lantern"), "Someone dug up a Smuggler's Lantern!", "anonymous finder")
	SpireTest.eq(SpireFinds.mayShout(100, 110), false, "20 second gap")
	SpireTest.eq(SpireFinds.mayShout(100, 120), true, "after the gap")
	local old = { { at = 0, text = "old" }, { at = 1000000, text = "new" } }
	SpireTest.eq(#SpireFinds.prune(old, 1000000 + 3600), 1, "a week on the board")
	SpireTest.eq(SpireFinds.firstTitle(2), "First Finder", "1-2 firsts")
	SpireTest.eq(SpireFinds.firstTitle(3), "Trailblazer", "3 firsts")
	SpireTest.eq(SpireFinds.firstTitle(6), "Pathbreaker", "6 firsts")
end)

SpireTest.add("adventure: announce goes to the board and is rate-limited", function()
	local saved, last = kv.scoped("spirebound-finds"):get("board"), SpireFinds.lastLine
	SpireFinds.clearBoard()
	SpireFinds.lastLine = 0
	local _, shout1 = SpireFinds.announce("keepsake", { "Tester One" }, "Ruin Idol")
	local _, shout2 = SpireFinds.announce("keepsake", { "Tester Two" }, "Bandit Banner")
	SpireTest.eq(shout1, true, "first line shouted")
	SpireTest.eq(shout2, false, "second line within 20 s: board only")
	SpireTest.eq(#SpireFinds.board(), 2, "both on the board")
	SpireTest.eq(SpireFinds.board()[1].text, "Tester Two dug up a Bandit Banner!", "newest first")
	if saved then kv.scoped("spirebound-finds"):set("board", saved) else SpireFinds.clearBoard() end
	SpireFinds.lastLine = last
end)

SpireTest.add("adventure: Discoveries registry counts, milestones and rows", function()
	local rows = { { category = "secret", id = "a", name = "A" }, { category = "secret", id = "b", name = "B" },
		{ category = "fish", id = "c", name = "C" }, { category = "fish", id = "d", name = "D" } }
	local per, got, total = SpireDiscoveries.counts(rows, function(r) return r.id == "a" end)
	SpireTest.eq(got, 1, "one found"); SpireTest.eq(total, 4, "four rows"); SpireTest.eq(per.secret.got, 1, "per category")
	SpireTest.eq(#SpireDiscoveries.reached(1, 1, 4), 1, "25%: the first milestone")
	SpireTest.eq(#SpireDiscoveries.reached(1, 4, 4), 3, "100%: all three")
	SpireTest.eq(SpireDiscoveries.rowLine({ name = "X" }, nil, nil), "  [ ] ???", "unfound")
	SpireTest.eq(SpireDiscoveries.rowLine({ name = "X" }, nil, "Boar Meadow"), "  [ ] ??? (rumoured: Boar Meadow)", "rumoured")
	SpireTest.eq(SpireDiscoveries.rowLine({ name = "X" }, true, nil), "  [x] X", "found, no date")
	-- the real Floor 1 registry (filled at start-up)
	local f1 = SpireDiscoveries.floorRows(1)
	local cats = {}
	for _, r in ipairs(f1) do cats[r.category] = (cats[r.category] or 0) + 1 end
	if (cats.secret or 0) < 13 then error("secrets on the page: " .. tostring(cats.secret)) end
	SpireTest.eq(cats.elite, 6, "six elites"); SpireTest.eq(cats.fish, 7, "seven fish"); SpireTest.eq(cats.stone, 6, "six stones")
	if (cats.beast or 0) < 4 then error("hidden beasts: " .. tostring(cats.beast)) end
	if (cats.chest or 0) < 10 then error("ground chests: " .. tostring(cats.chest)) end
end)

SpireTest.add("adventure: auras and keepsakes exist and can be shown", function()
	for _, a in ipairs(SpireAuras.LIST) do
		for _, fx in ipairs(a.effects) do
			if type(fx) ~= "number" then error(a.id .. " has a missing effect") end
		end
	end
	SpireTest.eq(SpireAuras.match("dyers drift").id, "dyers_drift", "match by name")
	SpireTest.eq(SpireAuras.match("trail").id, "trailblazers_wake", "match by start")
	SpireTest.eq(SpireAuras.match("nothing"), nil, "no match")
	for _, k in ipairs(SpireKeepsakes.LIST) do
		local it = ItemType(k.item)
		if not it or it:getId() == 0 or not it:isPickupable() then error(k.id .. ": placeholder item " .. k.item .. " can't be carried") end
	end
	SpireTest.eq(SpireFinds.lookText("Ana", { title = "Underkeeper", trophies = { "Old Tusk's Tusk" }, secrets = 7, firsts = 3 }),
		"Ana: Title: Underkeeper. Trophies: Old Tusk's Tusk. Secrets found: 7. First finder (3).", "look line")
	SpireTest.eq(SpireFinds.lookText("Bo", { trophies = {}, secrets = 0, firsts = 0 }), nil, "nothing to show")
end)

SpireTest.add("adventure AD2: secrets pay a purse and keepsakes; riddles name no place", function()
	SpireTest.eq(SpireSecrets.purse(1), 1000, "Floor 1 purse (Jay: always a medium gold reward)")
	local gear, banned = 0, { "Hearthgate", "Millcross", "Vesper", "north", "south", "east", "west", "Floor" }
	for _, g in ipairs(SpireWilds.grounds) do table.insert(banned, (g.title:gsub("^The ", ""))) end
	for _, s in ipairs(SpireSecrets.list) do
		if s.floor == 1 and type(s.reward) == "table" and s.reward.gear then gear = gear + 1 end
		if s.floor == 1 then
			for _, word in ipairs(banned) do
				if s.hint:lower():find(word:lower(), 1, true) then error(s.id .. "'s riddle names " .. word) end
			end
		end
	end
	SpireTest.eq(gear + 1, 3, "three gear secrets on Floor 1 (two from the table, the shrine's pendant from its fight)")
	for _, g in ipairs(SpireGearData.secretGear) do
		SpireTest.eq(SpireGear.SECRET_SLOTS[g.slot] ~= nil, true, g.id .. " is a ring, amulet or boots")
		local item = SpireGear.makeSecret(g)
		SpireTest.eq(SpireGear.secretOf(item).id, g.id, g.id .. " made and recognised")
		SpireTest.eq(item:getName(), g.name, g.id .. " named")
		item:remove()
	end
	local t = SpireGear.secretTotals(SpireGearData.secretGear)
	SpireTest.eq(t.speed, 5, "boots speed"); SpireTest.eq(t.skill, 1, "signet skill")
	-- the Journal never shows a riddle by default, nor a tier
	local line = SpireJournal.secretLine(SpireSecrets.get("s3"), false, false)
	SpireTest.eq(line, "[ ] Floor 1 - ???", "unfound secret row")
end)

SpireTest.add("adventure AD7: rumours pick the band, never secrets or beasts; bottles hold a riddle", function()
	local c = { { row = { id = "a" }, lo = 1, hi = 10, ground = "A" }, { row = { id = "b" }, lo = 20, hi = 30, ground = "B" } }
	SpireTest.eq(SpireRumours.pick(c, 25, 0.5).row.id, "b", "in band")
	SpireTest.eq(SpireRumours.pick(c, 15, 0.1).row.id, "a", "closest band when none fits")
	SpireTest.eq(SpireRumours.ready(nil, 100), true, "first rumour")
	SpireTest.eq(SpireRumours.ready(100, 100 + 3600), false, "one a day")
	SpireTest.eq(SpireRumours.CATEGORIES.secret, nil, "never secrets (Jay, 2026-11-27)")
	SpireTest.eq(SpireRumours.CATEGORIES.beast, nil, "never hidden beasts")
	SpireTest.eq(SpireRumours.line("elite", "Wolf Copse", 0), "Hunters whisper that something bigger than the rest leads the beasts of the Wolf Copse.", "words")
	local s = SpireRumours.bottlePick(SpireSecrets.list, function(id) return id ~= "s4" end, function() return false end, 0.3)
	SpireTest.eq(s and s.id, "s4", "the bottle picks an unfound secret")
	SpireTest.eq(SpireRumours.bottlePick(SpireSecrets.list, function() return true end, function() return false end, 0.3), nil, "none left")
	local bottle = false
	for _, f in ipairs(SpireFishing.tables[1]) do if f.bottle then bottle = f.weight == 1 end end
	SpireTest.eq(bottle, true, "a message bottle at weight 1 on the Floor 1 table")
	-- every rumour category on Floor 1 has somewhere to point
	for name, gid in pairs(SpireRumours.ELITE_GROUND) do
		local ok = false
		for _, g in ipairs(SpireWilds.grounds) do if g.id == gid then ok = true end end
		if not ok then error(name .. " points at a missing ground " .. gid) end
	end
	for _, f in ipairs(SpireTownsfolk) do
		if not f.name then error("townsperson without a name") end
	end
end)

SpireTest.add("adventure AD6: the Journal has a Discoveries tab", function()
	SpireTest.eq(SpireJournal.tabFromRequest('{"t":"journal","tab":"discoveries"}'), "discoveries", "request parse")
	local found = false
	for _, t in ipairs(SpireJournal.TABS) do if t == "discoveries" then found = true end end
	SpireTest.eq(found, true, "listed")
end)
