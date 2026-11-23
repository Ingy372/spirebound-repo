-- Gear progression (docs/superpowers/specs/2026-11-23-gear-progression-design.md 4.3-4.5): weapon tier and
-- familiarity live on the item; weapon power is a damage multiplier.
local function bag()
	return Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
end

SpireTest.add("gear: familiarity levels follow the floor's thresholds", function()
	local T = SpireGearData.FAMILIARITY_POINTS[1]
	SpireTest.eq(SpireGear.famLevel(0, 1), 0, "no points")
	SpireTest.eq(SpireGear.famLevel(T[1] - 1, 1), 0, "just short of the first threshold")
	SpireTest.eq(SpireGear.famLevel(T[1], 1), 1, "first threshold")
	SpireTest.eq(SpireGear.famLevel(T[10] * 5, 1), 10, "capped at 10")
end)

SpireTest.add("gear: weapon power follows the generator's formula", function()
	local f = SpireGearData.floor[1]
	local function near(a, b, what)
		SpireTest.eq(math.abs(a - b) < 0.0001, true, what .. " (" .. a .. " vs " .. b .. ")")
	end
	near(SpireGear.power({ floor = 1, tier = 0, fam = 0 }), 1 + f.base, "a new Floor 1 weapon")
	near(SpireGear.power({ floor = 1, tier = 5, fam = 10, awakened = true }), (1 + f.base + 5 * f.step + f.awaken) * 1.15, "maxed")
	near(SpireGear.power({ floor = 1, shop = true, tier = 3, fam = 10 }), 1 + SpireGearData.shop[3].weapon.bonus, "shop gear ignores tier and familiarity")
end)

SpireTest.add("gear: tier and familiarity live on the item and survive a copy", function()
	local b = bag()
	local w = SpireGear.make(b, "f1_ranger_bow")
	SpireTest.eq(w ~= nil and w:getName(), "Trailwarden Bow", "made with its own name")
	SpireGear.setState(w, { tier = 2, famPoints = SpireGearData.FAMILIARITY_POINTS[1][6] })
	local copy = w:clone()
	local s = SpireGear.state(copy)
	SpireTest.eq(s.id, "f1_ranger_bow", "id kept")
	SpireTest.eq(s.tier, 2, "tier kept")
	SpireTest.eq(s.fam, 6, "familiarity kept")
	SpireTest.eq(s.floor, 1, "floor known")
	SpireTest.eq(copy:getAttribute(ITEM_ATTRIBUTE_DESCRIPTION):find("Tier 2/5", 1, true) ~= nil, true, "description shows the tier")
	SpireTest.eq(SpireGear.state(Game.createItem(3264, 1, WorldPoints.temple_hearthgate)), nil, "an ordinary sword has no state")
	copy:remove()
	b:remove()
end)

SpireTest.add("gear: shop pieces are marked and have no tiers", function()
	local b = bag()
	local s = SpireGear.make(b, "shop_weapon_3")
	SpireTest.eq(SpireGear.state(s).shop, true, "marked as shop gear")
	SpireTest.eq(s:getName(), "Climber's Bow", "shop name")
	local a = SpireGear.make(b, "f1_ranger_armour")
	SpireTest.eq(a:getAttribute(ITEM_ATTRIBUTE_ARMOR), ItemType(3372):getArmor() + 2, "armour bonus")
	SpireGear.setState(a, { tier = 2 })
	SpireTest.eq(a:getAttribute(ITEM_ATTRIBUTE_ARMOR), ItemType(3372):getArmor() + 2 + 2 * SpireGearData.floor[1].armorStep, "armour tiers add armour")
	b:remove()
end)
