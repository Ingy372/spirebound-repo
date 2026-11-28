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

SpireTest.add("QA17: Rangers can take a Trailwarden Spear from Dorrow (Q88)", function()
	SpireTest.eq(SpireGear.familiesOf(3, 1):find("spear", 1, true) ~= nil, true, "Dorrow offers a spear: " .. SpireGear.familiesOf(3, 1))
	local d = SpireGear.mainFor(3, 1, "spear")
	SpireTest.eq(d and d.name, "Trailwarden Spear", "the spear")
	local b = Game.createItem(2853, 1, WorldPoints.temple_hearthgate)
	local item = SpireGear.make(b, d.id)
	SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_ATTACK), 25, "attack 25 at tier 0")
	SpireGear.setState(item, { tier = 2 })
	SpireTest.eq(item:getAttribute(ITEM_ATTRIBUTE_ATTACK), 27, "+1 per tier")
	SpireTest.eq(ItemType(d.base):getWeaponType() == WEAPON_DISTANCE or ItemType(d.base):getWeaponType() == WEAPON_MISSILE, true, "a thrown-and-returning distance weapon")
	b:remove()
end)

SpireTest.add("QA19: one guild takes at most 10 of the 20 first-kill places (Q91)", function()
	local list, guilds = {}, {}
	for i = 1, 12 do -- twelve of one guild did the most damage
		table.insert(list, { name = "G" .. i, amount = 1000 - i })
		guilds["G" .. i] = 7
	end
	for i = 1, 12 do -- twelve others
		table.insert(list, { name = "O" .. i, amount = 500 - i })
	end
	local names = Floors.rankCreditCapped(list, function(n) return guilds[n] end, 10)
	SpireTest.eq(#names, 20, "twenty places")
	local g = 0
	for _, n in ipairs(names) do
		if guilds[n] then g = g + 1 end
	end
	SpireTest.eq(g, 10, "ten of them for the big guild")
	SpireTest.eq(names[11], "O1", "the next place goes to the best fighter outside it")
	SpireTest.eq(#Floors.rankCredit(list), 20, "uncapped ranking still gives 20 (later bosses)")
	-- through the boss's own credit rule
	local st = SpireBoss.newState()
	for _, c in ipairs(list) do
		SpireBoss.recordHit(st, c.name, c.amount, 100)
	end
	local credit = SpireBoss.credited(st, 100, 0, function(n) return guilds[n] end, 10)
	SpireTest.eq(#credit, 20, "the boss credits 20")
	SpireTest.eq(credit[11], "O1", "with the guild capped at 10")
end)

SpireTest.add("QA18: crowd events wait for players; world events and weekend bonuses don't (Q59)", function()
	-- the boot test runs with nobody online: a world event still starts
	local fishing
	for _, k in ipairs(SpireEvents.KINDS) do
		if k.id == "fishing" then fishing = k end
	end
	local before = SpireEvents.active
	SpireEvents.start(fishing, 1)
	SpireTest.eq(SpireEvents.active and SpireEvents.active.kind.id, "fishing", "a world event runs with nobody online")
	SpireEvents.active = before
	SpireTest.eq(SpireEvents.weekendBonus(7, 1) ~= nil, true, "the weekend bonus goes by the calendar alone")
	-- the crowd ones wait
	SpireTest.eq((SpireArena.start({ order = { 1 }, players = { [1] = {} }, kind = next(SpireArena.KINDS) }, os.time())), false, "an arena event needs 4 fighters")
	SpireTest.eq(SpireSiege.MIN_GUILDS >= 2 and SpireSiege.MIN_MEMBERS >= 2, true, "the Siege needs two guilds of two")
end)

SpireTest.add("QA11: the engine's free blessing ends after level 7 (Q80)", function()
	SpireTest.eq(configManager.getNumber(configKeys.ADVENTURERSBLESSING_LEVEL), 7, "adventurer's blessing up to level 7")
end)

SpireTest.add("WA1: familiarity belongs to the character who earned it", function()
	SpireTest.eq(SpireGear.bondChange(nil, 5), "adopt", "an old weapon with no bond is adopted, nothing reset")
	SpireTest.eq(SpireGear.bondChange(5, 5), "keep", "your own weapon keeps its familiarity")
	SpireTest.eq(SpireGear.bondChange(5, 6), "reset", "another character's starts again")
end)

SpireTest.add("WA5: retune moves tiers minus one", function()
	local t, s = SpireGear.retunePlan(4, 1)
	SpireTest.eq(t .. "/" .. s, "3/0", "tier 4 into a tier 1: 3, and the source back to 0")
	SpireTest.eq((SpireGear.retunePlan(2, 3)), 3, "never below the target's own")
end)

SpireTest.add("WA5: a fighter dead at the kill: the most familiar weapon of theirs is awakened", function()
	local rows = {
		{ id = "axe", floor = 1, awakened = false, bond = 7, fam = 100 },
		{ id = "sword", floor = 1, awakened = false, bond = 7, fam = 9000 },
		{ id = "bow", floor = 1, awakened = false, bond = 8, fam = 99999 },      -- someone else's familiarity
		{ id = "old", floor = 1, awakened = true, bond = 7, fam = 50000 },       -- already awakened
		{ id = "f2", floor = 2, awakened = false, bond = 7, fam = 70000 },       -- another floor's
	}
	SpireTest.eq(SpireGear.pickLate(rows, 1, 7).id, "sword", "the sword: most familiar, bonded to them")
	SpireTest.eq(SpireGear.pickLate({}, 1, 7), nil, "no weapon: nothing")
end)

SpireTest.add("ST1: monsters build resistance to holds; off-hand strikes; control bonus", function()
	local rec = {}
	SpireTest.eq(SpireSpells.monsterHold(rec, 100, false), 1, "first hold: full")
	SpireTest.eq(SpireSpells.monsterHold(rec, 105, false), 0.5, "second within 10 s: half")
	SpireTest.eq(SpireSpells.monsterHold(rec, 107, false), 0, "third: nothing")
	SpireTest.eq(SpireSpells.monsterHold(rec, 112, false), 0, "and immune for 10 s")
	SpireTest.eq(SpireSpells.monsterHold(rec, 118, false), 1, "after that, full again")
	local boss = {}
	SpireTest.eq(SpireSpells.monsterHold(boss, 100, true), 1, "a boss can be held once")
	SpireTest.eq(SpireSpells.monsterHold(boss, 125, true), 0, "then is immune for 30 s")
	SpireTest.eq(SpireSpells.monsterHold(boss, 131, true), 1, "and again after")
	SpireTest.eq(SpireOffhand.strike(100, 20, 13, 0.5, false), 33, "a 100 hit: the dirk strikes 100 x 13/20 x 50%")
	SpireTest.eq(SpireOffhand.strike(100, 20, nil, 0.5, false), 0, "no blade: no strike")
	SpireTest.eq(SpireOffhand.strike(100, 30, nil, 0.3, true), 30, "a two-hander gets the share of the hit")
	SpireTest.eq(SpireOffhand.strike(100, 20, 13, 0, false), 0, "not a Reaver: nothing")
	local dirk = SpireOffhand.create("climbers_dirk")
	SpireTest.eq(SpireOffhand.attackOf(dirk), 13, "the dirk carries attack 13")
	SpireTest.eq(ItemType(SpireOffhand.BASE):getWeaponType() ~= WEAPON_SWORD, true, "its base is no weapon, so it fits beside one")
	dirk:remove()
end)
