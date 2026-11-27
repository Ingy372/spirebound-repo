-- Roadmap FD4: cooking on the hub fires (lib/spirebound/cooking.lua).
local C = SpireDepthData.cooking

SpireTest.add("cooking: recipes, combinations and feasts follow the table", function()
	SpireTest.eq(#C.dishes >= 10 and #C.dishes <= 15, true, "about twelve dishes")
	SpireTest.eq(SpireCooking.cookResult(3582).id, "boar_roast", "ham cooks into a Boar Roast")
	local d, why = SpireCooking.cookResult(5902)
	SpireTest.eq(d == nil and why == "alone", true, "honeycomb does not cook alone")
	SpireTest.eq(select(2, SpireCooking.cookResult(3031)), "not_food", "gold is no food")
	SpireTest.eq(SpireCooking.combineResult(SpireCooking.byId.boar_roast.item, 3728).id, "hunters_roast", "roast + truffle")
	SpireTest.eq(SpireCooking.combineResult(SpireCooking.byId.boar_roast.item, 3588), nil, "roast + berries is no recipe")
	local stew = SpireCooking.byId.hunters_roast
	SpireTest.eq(SpireCooking.duration(stew, true), 2 * SpireCooking.duration(stew, false), "a feast lasts twice as long")
	local t = SpireCooking.titlesFor(5, #C.dishes)
	SpireTest.eq(#t == 1 and t[1] == "Camp Cook", true, "five dishes: Camp Cook")
	SpireTest.eq(#SpireCooking.titlesFor(#C.dishes, #C.dishes), 2, "all dishes: Hearth Cook too")
	for _, dd in ipairs(C.dishes) do
		SpireTest.eq(ItemType(dd.item):getName(), dd.name, dd.id .. "'s item carries its name")
		SpireTest.eq(ItemType(dd.item):isPickupable(), true, dd.id .. " can be carried")
	end
	SpireTest.eq(ItemType(3728):getName(), "truffle", "the truffle's name")
end)

SpireTest.add("cooking: every hunting ground's hub has a fire to cook on", function()
	local missing = {}
	for _, g in ipairs(SpireWilds.grounds) do
		local camp = WorldPoints["camp_" .. g.id]
		if camp and camp.x < 2000 then
			if not SpireCooking.fireNear(camp, 4) then
				table.insert(missing, g.id)
			end
		end
	end
	SpireTest.eq(table.concat(missing, ","), "", "grounds with no fire by the hub")
end)

SpireTest.add("cooking: a dish's comfort and its capacity bonus come and go", function()
	local store, cap, conds = {}, 40000, {}
	local p = { }
	function p:getId() return 990001 end
	function p:getGuid() return 990001 end
	function p:kv() return { scoped = function() return { get = function(_, k) return store[k] end, set = function(_, k, v) store[k] = v end, remove = function(_, k) store[k] = nil end } end } end
	function p:getCapacity() return cap end
	function p:setCapacity(v) cap = v end
	function p:addCondition(c) table.insert(conds, c) end
	function p:removeCondition() end
	function p:feed() end
	function p:say() end
	function p:sendTextMessage() end
	SpireCooking.eat(p, SpireCooking.byId.boar_roast, false)
	SpireTest.eq(cap, 40000 + 40 * 100, "a Boar Roast adds 40 oz")
	SpireCooking.eat(p, SpireCooking.byId.grilled_minnow, false)
	SpireTest.eq(cap, 40000, "the next dish takes the old bonus away (one dish at a time)")
	SpireTest.eq(store.now.id, "grilled_minnow", "the dish is remembered")
	SpireCooking.stop(p, true)
	SpireTest.eq(store.now, nil, "and forgotten when it ends")
	SpireCooking.active[990001] = nil
end)
