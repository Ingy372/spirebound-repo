-- Roadmap 7.2: the shop never sells power and nothing in it can be gambled
SpireTest.add("shop: closed by default; every item is a cosmetic with no combat stats", function()
	SpireTest.eq(SpireShop.ENABLED, false, "shop closed until launch")
	local seen = {}
	for _, e in ipairs(SpireShop.catalog) do
		if seen[e.id] then error("duplicate id " .. e.id) end
		seen[e.id] = true
		if not SpireShop.KINDS[e.kind] then error(e.id .. ": kind " .. tostring(e.kind) .. " is not allowed in the shop") end
		if e.price <= 0 then error(e.id .. ": needs a price") end
		if e.item then
			if SpireShop.isGold(e.item) then error(e.id .. " sells gold") end
			local it = ItemType(e.item)
			if not it or it:getId() == 0 or not it:isPickupable() then error(e.id .. ": not a real takeable item") end
			for _, m in ipairs({ "getAttack", "getDefense", "getArmor", "getExtraDefense" }) do
				if it[m] and (it[m](it) or 0) ~= 0 then
					error(string.format("%s has %s = %s: shop items must never have combat stats", e.id, m, tostring(it[m](it))))
				end
			end
			if it:getWeaponType() ~= 0 then error(e.id .. " is a weapon or shield") end
		end
	end
	SpireTest.eq(SpireShop.isShopItem(2779), true, "shop item recognised")
	SpireTest.eq(SpireShop.isShopItem(3031), false, "gold is not a shop item")
	SpireTest.eq(SpireShop.canBuy(10, SpireShop.catalog[1]), false, "too poor")
	SpireTest.eq(SpireShop.canBuy(1000, SpireShop.catalog[1]), true, "can afford")
end)

-- Gear progression spec 4.9: starter gear that Floor 1 weapons outgrow, and the shop-only Mastery Respec
SpireTest.add("shop: the starter set is outclassed by the Floor 1 weapon at tier 2", function()
	local set = SpireShop.get("starter_set")
	SpireTest.eq(set ~= nil and set.kind, "gear", "the starter set is in the catalog")
	for voc = 1, 4 do
		local s = SpireGearData.shop[voc]
		SpireTest.eq(SpireGear.power({ shop = true, vocation = voc }) < SpireGear.power({ floor = 1, tier = 2, fam = 0 }), true,
			"vocation " .. voc .. ": shop weapon below a tier 2 Floor 1 weapon")
		SpireTest.eq(SpireGear.def(s.weapon.id).shop, true, "vocation " .. voc .. ": shop weapon cannot be upgraded")
	end
	local respec = SpireShop.get("mastery_respec")
	SpireTest.eq(respec ~= nil and respec.kind, "respec", "the respec is in the catalog")
	SpireTest.eq(respec.item, SpireShop.RESPEC_ITEM, "it is the respec scroll")
	SpireTest.eq(ItemType(SpireShop.RESPEC_ITEM):getName(), "Mastery Respec Scroll", "with its own name")
end)

SpireTest.add("shop: the respec scroll comes from the shop and nowhere else", function()
	local id = SpireShop.RESPEC_ITEM
	for _, mt in pairs(Game.getMonsterTypes()) do
		for _, l in ipairs(mt:getLoot()) do
			if l.itemId == id then
				error(mt:getName() .. " drops the respec scroll")
			end
		end
	end
	for _, q in ipairs(SpireQuests.list) do
		for _, it in ipairs(q.reward.items or {}) do
			SpireTest.eq(it[1] ~= id, true, q.id .. " does not reward it")
		end
	end
	for _, s in ipairs(SpireSecrets.list) do
		if type(s.reward) == "table" then
			for _, it in ipairs(s.reward.items or {}) do
				SpireTest.eq(it[1] ~= id, true, s.id .. " does not reward it")
			end
		end
	end
end)
