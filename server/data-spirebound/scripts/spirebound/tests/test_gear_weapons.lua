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

-- Task 4: Hearth Shards and the Weaponsmith (spec 4.4, 4.5)
local function wallet(counts, gold)
	local w = { counts = counts, gold = gold, taken = {}, paid = 0 }
	function w.count(id) return w.counts[id] or 0 end
	function w.remove(id, n) w.counts[id] = (w.counts[id] or 0) - n; w.taken[id] = (w.taken[id] or 0) + n; return true end
	function w.money() return w.gold end
	function w.pay(n) w.gold = w.gold - n; w.paid = w.paid + n; return true end
	return w
end
local T1 = SpireGearData.tokens[1]

SpireTest.add("shards: every Floor 1 monster but the yard rats drops rough shards; harder ones drop cut", function()
	SpireTest.eq(SpireGearData.shardMonsters["Pen Rat"], nil, "no shards from the Arrival Yard")
	SpireTest.eq(SpireGearData.shardMonsters["Field Rat"].rough, true, "a field rat drops rough")
	SpireTest.eq(SpireGearData.shardMonsters["Field Rat"].cut, nil, "but not cut")
	SpireTest.eq(SpireGearData.shardMonsters["Ruin Sentinel"].cut, true, "the quarry drops cut")
	SpireTest.eq(SpireGearData.shardMonsters["Grey Alpha"].flawless, true, "an elite drops flawless")
	SpireTest.eq(ItemType(T1.rough):getName(), "rough Hearth Shard", "the item carries its name")
end)

SpireTest.add("weaponsmith: an upgrade takes exactly three shards and the fee", function()
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local item = SpireGear.make(b, "f1_ranger_bow")
	local w = wallet({ [T1.rough] = 4 }, 10000)
	local ok = SpireGear.upgradeWith(item, w)
	SpireTest.eq(ok, true, "tier 0 -> 1 with 3 rough")
	SpireTest.eq(SpireGear.state(item).tier, 1, "now tier 1")
	SpireTest.eq(w.taken[T1.rough], 3, "three shards taken")
	SpireTest.eq(w.paid, SpireGearData.TIER_COST[1].gold, "the fee paid")
	b:remove()
end)

SpireTest.add("weaponsmith: refusals take nothing and say what is missing", function()
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local item = SpireGear.make(b, "f1_ranger_bow")
	SpireGear.setState(item, { tier = 2 })
	local w = wallet({ [T1.rough] = 9 }, 99999)
	local ok, msg = SpireGear.upgradeWith(item, w)
	SpireTest.eq(ok, false, "tier 3 needs cut shards")
	SpireTest.eq(msg:find("cut Hearth Shard", 1, true) ~= nil and msg:find("Wolf Copse", 1, true) ~= nil, true, "names the shard and where: " .. msg)
	SpireTest.eq(w.paid + (w.taken[T1.rough] or 0), 0, "nothing taken")
	ok = SpireGear.upgradeWith(item, wallet({ [T1.cut] = 3 }, 0))
	SpireTest.eq(ok, false, "no gold, no upgrade")
	SpireGear.setState(item, { tier = 5 })
	ok, msg = SpireGear.upgradeWith(item, wallet({ [T1.flawless] = 3 }, 99999))
	SpireTest.eq(ok, false, "tier 5 is the top")
	local f2 = SpireGear.make(b, "f2_ranger_main")
	SpireTest.eq((SpireGear.upgradeWith(f2, wallet({ [T1.rough] = 3 }, 99999))), false, "Floor 1 shards do not fit Floor 2 gear")
	local shop = SpireGear.make(b, "shop_weapon_3")
	SpireTest.eq((SpireGear.upgradeWith(shop, wallet({ [T1.rough] = 3 }, 99999))), false, "shop gear cannot be upgraded")
	b:remove()
end)

SpireTest.add("weaponsmith: a reforge keeps the tier and starts familiarity again", function()
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local item = SpireGear.make(b, "f1_ranger_bow")
	SpireGear.setState(item, { tier = 3, famPoints = SpireGearData.FAMILIARITY_POINTS[1][7] })
	local w = wallet({}, 99999)
	local new = SpireGear.reforgeWith(item, "crossbow", w, b)
	local s = SpireGear.state(new)
	SpireTest.eq(s.id .. "/" .. s.tier .. "/" .. s.fam, "f1_ranger_crossbow/3/0", "crossbow, tier 3, familiarity 0")
	SpireTest.eq(w.paid, SpireGearData.REFORGE_FEE, "the reforge fee")
	SpireTest.eq((SpireGear.reforgeWith(new, "axe", wallet({}, 99999), b)), nil, "not another class's family")
	b:remove()
end)

-- FLOOR1_REVIEW.md F1-42: a pity counter so a hunter never goes far past the expected wait without a shard
SpireTest.add("shards: the pity counter guarantees a shard at three times the expected wait", function()
	local c = SpireGearData.SHARD_CHANCE.rough
	local cap = math.floor(3 / c)
	SpireTest.eq(SpireGear.shardRoll(c, 0, 0.999), false, "an unlucky roll early gives nothing")
	SpireTest.eq(SpireGear.shardRoll(c, 0, c / 2), true, "a lucky roll gives a shard")
	SpireTest.eq(SpireGear.shardRoll(c, cap - 1, 0.999), false, "just short of the cap: still the dice")
	SpireTest.eq(SpireGear.shardRoll(c, cap, 0.999), true, "at the cap: guaranteed")
end)
