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
			for _, m in ipairs({ "getAttack", "getDefense", "getArmor", "getExtraDefense", "getHitChance", "getShootRange" }) do
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
