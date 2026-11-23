-- Gear progression spec 4.7: the "Next upgrade" window. The top line always names the thing and the place.
local function base(over)
	local v = { level = 15, weapon = nil, armour = nil, shards = { rough = 0, cut = 0, flawless = 0 }, steps = {},
		style = { stageName = "Ranger Mastery", level = 3, choiceReady = false }, trophies = {} }
	for k, x in pairs(over or {}) do
		v[k] = x
	end
	return v
end
local function weapon(tier)
	return { name = "Trailwarden Bow", floor = 1, tier = tier, fam = 4, power = 1.2 }
end

SpireTest.add("upgrade: below level 10 the next step is Captain Dorrow at level 10", function()
	local v = base({ level = 4, steps = { { key = "weapon", level = 10, text = "Get your weapon", where = "see Captain Dorrow at Hearthgate's north gate", done = false } } })
	SpireTest.eq(SpireUpgrade.nextLine(v), "Reach level 10, then see Captain Dorrow at Hearthgate's north gate.", "the first goal")
end)

SpireTest.add("upgrade: a ready story step comes first and says where", function()
	local v = base({ weapon = weapon(1), steps = { { key = "temper", level = 12, text = "Tempered in the Field", where = "hunt Meadow Wolves in Wolf Copse", done = false } } })
	SpireTest.eq(SpireUpgrade.nextLine(v), "Next: hunt Meadow Wolves in Wolf Copse.", "the quest step")
end)

SpireTest.add("upgrade: with no step ready, the next tier's shards and where they drop", function()
	local v = base({ weapon = weapon(1), shards = { rough = 1, cut = 0, flawless = 0 } })
	local line = SpireUpgrade.nextLine(v)
	SpireTest.eq(line:find("2 more rough Hearth Shards", 1, true) ~= nil, true, "how many: " .. line)
	SpireTest.eq(line:find("any Floor 1 hunting ground", 1, true) ~= nil, true, "where: " .. line)
	v.weapon = weapon(2)
	line = SpireUpgrade.nextLine(v)
	SpireTest.eq(line:find("cut Hearth Shards", 1, true) ~= nil and line:find("Wolf Copse", 1, true) ~= nil, true, "cut shards and where: " .. line)
	v.weapon, v.shards = weapon(1), { rough = 3, cut = 0, flawless = 0 }
	line = SpireUpgrade.nextLine(v)
	SpireTest.eq(line:find("Weaponsmith Garrick", 1, true) ~= nil, true, "enough shards: go to the smith: " .. line)
end)

SpireTest.add("upgrade: a waiting style choice is the next step", function()
	local v = base({ weapon = weapon(3), style = { stageName = "Ranger Mastery", level = 10, choiceReady = true, options = { "Marksman", "Trapper" } } })
	SpireTest.eq(SpireUpgrade.nextLine(v), "Next: choose Marksman or Trapper. Say !style to read both.", "the choice")
end)

SpireTest.add("upgrade: everything done points at Floor 2", function()
	local w = weapon(5)
	w.awakened = true
	local v = base({ weapon = w, steps = { { key = "axe_lord", level = 30, text = "x", where = "y", done = true } } })
	SpireTest.eq(SpireUpgrade.nextLine(v):find("Floor 2", 1, true) ~= nil, true, "Floor 2's weapons")
end)

SpireTest.add("upgrade: the window has its sections, hides unfound trophies and fits the width", function()
	local v = base({ weapon = weapon(2), armour = { name = "Trailwarden Greaves", tier = 1 }, steps = SpireUpgrade.sampleSteps(), trophies = {} })
	local lines = SpireUpgrade.lines(v)
	local text = table.concat(lines, "\n")
	for _, head in ipairs({ "WEAPON", "ARMOUR", "FLOOR 1 PATH", "STYLE", "TROPHIES" }) do
		SpireTest.eq(text:find(head, 1, true) ~= nil, true, "has " .. head)
	end
	SpireTest.eq(text:find("none found yet", 1, true) ~= nil, true, "no trophy names before they are found")
	for _, l in ipairs(lines) do
		SpireTest.eq(#l <= 90, true, "line fits: " .. l)
	end
	SpireTest.eq(lines[1]:sub(1, 5) == "Next:" or lines[1]:sub(1, 5) == "Reach", true, "the next step comes first")
end)
