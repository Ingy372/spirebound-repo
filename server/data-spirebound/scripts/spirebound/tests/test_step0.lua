-- Roadmap Step 0: Jay's answers of 2026-11-27 (QUESTIONS.md). One test per task where a rule can be checked here;
-- each task is also checked in the real client (PROGRESS.md says how).

SpireTest.add("QA2: secret gear trades like other gear (Q100)", function()
	for _, g in ipairs(SpireGearData.secretGear) do
		local item = SpireGear.makeSecret(g)
		SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_DESCRIPTION):find("can't", 1, true), nil, g.id .. ": the look text no longer says it can't be traded")
		item:remove()
	end
end)

SpireTest.add("QA4: reward gold is paid in coins, largest first (Q76)", function()
	local s = SpireGive.coinStacks(12345)
	SpireTest.eq(#s, 3, "a crystal, platinum and gold stack")
	SpireTest.eq(s[1].id .. ":" .. s[1].count, "3043:1", "one crystal coin")
	SpireTest.eq(s[2].id .. ":" .. s[2].count, "3035:23", "23 platinum")
	SpireTest.eq(s[3].id .. ":" .. s[3].count, "3031:45", "45 gold")
	local total = 0
	for _, x in ipairs(SpireGive.coinStacks(2500000)) do
		SpireTest.eq(x.count <= 100, true, "no stack over 100")
		total = total + x.value
	end
	SpireTest.eq(total, 2500000, "every coin counted")
	SpireTest.eq(SpireGive.goldWhere(500, 0), "in your backpack", "all in the bag")
	SpireTest.eq(SpireGive.goldWhere(0, 500):find("bank", 1, true) ~= nil, true, "a full backpack: the bank")
	-- a real backpack on the ground stands in for the player
	local bp = Game.createItem(2854, 1, WorldPoints.temple_hearthgate)
	local p = { bank = 0 }
	function p:addItemEx(it) return bp:addItemEx(it) end
	function p:getBankBalance() return self.bank end
	function p:setBankBalance(n) self.bank = n end
	local bag, bank = SpireGive.gold(p, 345)
	SpireTest.eq(bag .. "/" .. bank, "345/0", "345 gold in the bag")
	SpireTest.eq(SpireTest.coinValue(bp), 345, "the coins are really there")
	bp:remove()
end)

SpireTest.add("QA9: upgraded gear needs a level to wear (Q86)", function()
	SpireTest.eq(SpireGear.levelFor(1, 2), 0, "tier 2: no level")
	SpireTest.eq(SpireGear.levelFor(1, 3), 20, "tier 3: level 20")
	SpireTest.eq(SpireGear.levelFor(1, 4), 25, "tier 4: level 25")
	SpireTest.eq(SpireGear.levelFor(1, 5), 30, "tier 5: level 30")
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local item = SpireGear.make(b, "f1_vanguard_sword")
	SpireGear.setState(item, { tier = 5 })
	SpireTest.eq((SpireGear.canWield(item, 8)), false, "a level 8 can't wear a tier 5")
	SpireTest.eq(select(2, SpireGear.canWield(item, 8)), 30, "it needs 30")
	SpireTest.eq((SpireGear.canWield(item, 30)), true, "a level 30 can")
	SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_DESCRIPTION):find("needs level 30", 1, true) ~= nil, true, "the look text says so")
	SpireTest.eq((SpireGear.canWield(Game.createItem(3031, 1), 1)), true, "ordinary items need nothing")
	SpireTest.eq(SpireGear.isWornSlot({ x = 0xFFFF, y = CONST_SLOT_LEFT, z = 0 }), true, "the weapon hand is worn")
	SpireTest.eq(SpireGear.isWornSlot({ x = 0xFFFF, y = CONST_SLOT_BACKPACK, z = 0 }), false, "the backpack slot is not")
	SpireTest.eq(SpireGear.isWornSlot({ x = 0xFFFF, y = 0x40, z = 0 }), false, "a container is not")
	-- the Weaponsmith won't make a tier you can't wear yet
	SpireGear.setState(item, { tier = 2 })
	local w = { count = function() return 9 end, remove = function() return true end, money = function() return 99999 end,
		pay = function() return true end, level = function() return 15 end }
	local ok, msg = SpireGear.upgradeCheck(item, w)
	SpireTest.eq(ok, false, "level 15 can't have tier 3 made")
	SpireTest.eq(msg:find("level 20", 1, true) ~= nil, true, "and is told the level: " .. tostring(msg))
	w.level = function() return 20 end
	SpireTest.eq((SpireGear.upgradeCheck(item, w)), true, "level 20 can")
	b:remove()
end)

SpireTest.add("QA10: a gold respec at the Weaponsmith, dearer each time (Q87)", function()
	local tag = "respec" .. os.time()
	local store = function(name) return kv.scoped("spiretest-" .. tag .. "-" .. name) end
	local p = {}
	function p:kv() return { scoped = function(_, name) return store(name) end } end
	local w = { gold = 100000, paid = 0 }
	w.money = function() return w.gold end
	w.pay = function(n) w.gold = w.gold - n; w.paid = w.paid + n; return true end
	w.refund = function(n) w.gold = w.gold + n end
	local ok = SpireGear.respecForGold(p, w, 1000)
	SpireTest.eq(ok, false, "no style chosen: nothing to undo")
	SpireTest.eq(w.paid, 0, "and nothing paid")
	store("spirebound"):set("style_path", "reaver")
	local msg
	ok, msg = SpireGear.respecForGold(p, w, 1000)
	SpireTest.eq(ok, true, "first respec: " .. tostring(msg))
	SpireTest.eq(w.paid, 10000, "10,000 gold")
	SpireTest.eq(store("spirebound"):get("style_path"), nil, "the style is undone")
	store("spirebound"):set("style_path", "bulwark")
	SpireTest.eq((SpireGear.respecForGold(p, w, 2000)), false, "the 7-day wait still holds")
	ok = SpireGear.respecForGold(p, w, 1000 + SpireStyle.RESPEC_WAIT)
	SpireTest.eq(ok, true, "a week later")
	SpireTest.eq(w.paid, 30000, "the second costs 20,000")
	SpireTest.eq(SpireGear.respecPrice(2), 40000, "the third 40,000")
end)

SpireTest.add("QA16: the cavebot doesn't work in the starter grounds, or on Floor 1 in launch week (Q60)", function()
	SpireTest.eq(SpireCavebot.banReasonAt(WorldPoints.camp_starter_west, 0, false), "starter", "the Ratwarren: never")
	SpireTest.eq(SpireCavebot.banReasonAt(Position(1156, 1370, 7), 0, false), nil, "Boar Meadow after launch week: allowed")
	SpireTest.eq(SpireCavebot.banReasonAt(Position(1156, 1370, 7), 0, true), "launch", "Boar Meadow in launch week: not")
	SpireTest.eq(SpireCavebot.banReasonAt(WorldPoints.temple_hearthgate, 0, true), "launch", "anywhere on Floor 1 in launch week (even town)")
	SpireTest.eq(SpireCavebot.factorFor(true, true), 0, "banned: nothing")
	SpireTest.eq(SpireCavebot.factorFor(true, false), SpireCavebot.XP, "elsewhere: the usual cut")
	SpireTest.eq(SpireCavebot.factorFor(false, true), 1, "not botting: full rewards")
	-- a real corpse: a banned botter's kill leaves nothing in it
	local body = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	body:addItem(3031, 40)
	body:addItem(3577, 1)
	SpireTest.eq(SpireCavebot.cutLoot(body, nil, 0), 41, "every coin and item removed")
	SpireTest.eq(body:getSize(), 0, "the body is empty")
	body:remove()
end)

SpireTest.add("QA16: three game windows per computer (Q53)", function()
	SpireTest.eq(SpireWindows.allowed(2), true, "a third window may join")
	SpireTest.eq(SpireWindows.allowed(3), false, "a fourth may not")
end)
