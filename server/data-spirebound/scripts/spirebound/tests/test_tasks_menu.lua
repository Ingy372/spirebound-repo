-- Jay's playtest 2026-11-13: right-clicking coins changes them up; every floor's taskmaster has a task menu.

-- A stand-in player: real items in a real backpack on the ground, real KV storage under a test name.
local function fakePlayer(pos, tag)
	local bp = Game.createItem(2854, 1, pos) -- backpack
	local store = { scoped = function(_, name) return kv.scoped("spiretest-" .. tag .. "-" .. name) end }
	local p = { bp = bp, money = 0, msgs = {} }
	function p:addItem(id, n) return bp:addItem(id, n) end
	function p:addMoney(n) self.money = self.money + n return true end
	function p:sendCancelMessage(m) table.insert(self.msgs, m) end
	function p:sendTextMessage(_, m) table.insert(self.msgs, m) end
	function p:getPosition() return pos end
	function p:kv() return store end
	return p
end

local function count(bp, id)
	local n = 0
	for i = 0, bp:getSize() - 1 do
		local it = bp:getItem(i)
		if it and it:getId() == id then n = n + it:getCount() end
	end
	return n
end

SpireTest.add("coins: using a stack changes it up, the rest stays", function()
	local p = fakePlayer(WorldPoints.temple_hearthgate, "coins")
	local gold = p.bp:addItem(ITEM_GOLD_COIN, 100)
	p.bp:addItem(ITEM_GOLD_COIN, 50) -- second stack: 100 + 50 would merge, so check counts by total
	SpireTest.eq(SpireCoins.use(p, gold), true, "using gold works")
	SpireTest.eq(count(p.bp, ITEM_PLATINUM_COIN), 1, "100 gold became 1 platinum")
	SpireTest.eq(count(p.bp, ITEM_GOLD_COIN), 50, "50 gold left over")
	local plat = p.bp:addItem(ITEM_PLATINUM_COIN, 99)
	plat = nil
	for i = 0, p.bp:getSize() - 1 do
		local it = p.bp:getItem(i)
		if it and it:getId() == ITEM_PLATINUM_COIN then plat = it end
	end
	SpireTest.eq(plat:getCount(), 100, "platinum stacked to 100")
	SpireCoins.use(p, plat)
	SpireTest.eq(count(p.bp, ITEM_CRYSTAL_COIN), 1, "100 platinum became 1 crystal")
	SpireTest.eq(count(p.bp, ITEM_PLATINUM_COIN), 0, "no platinum left")
	SpireTest.eq(SpireCoins.split(250), 2, "250 gold makes 2 platinum")
	SpireTest.eq(select(2, SpireCoins.split(250)), 50, "and leaves 50")
	p.bp:remove()
end)

local function masterPosition(name)
	local npc = Npc(name)
	return npc and npc:getPosition()
end

SpireTest.add("tasks: every floor's taskmaster stands in town with only that floor's monsters", function()
	for n = 1, 10 do
		local name = SpireTasks.MASTERS[n]
		local pos = masterPosition(name)
		if not pos then error(name .. " is not on the map") end
		SpireTest.eq(Floors.at(pos), n, name .. " stands on Floor " .. n)
		local list = SpireTasks.forFloor(n)
		SpireTest.eq(#list >= 8, true, "Floor " .. n .. " has a full menu")
		for _, t in ipairs(list) do
			local mt = MonsterType(t.monster)
			if not mt then error(t.id .. ": no monster " .. t.monster) end
			if (mt.isRewardBoss and mt:isRewardBoss()) or t.monster == "Pen Rat" then error(t.id .. " is not a hunting monster") end
		end
	end
	SpireTest.eq(#SpireTasks.forFloor(1), 25, "Floor 1 offers all 25 huntable monsters")
end)

SpireTest.add("tasks: take, hunt, report through Taskmaster Rhen's menu", function()
	local pos = masterPosition("Taskmaster Rhen")
	local p = fakePlayer(Position(pos.x, pos.y + 1, pos.z), "menu")
	local s = SpireTasks.scope(p)
	for _, t in ipairs(SpireTasks.list) do s:remove("done_" .. t.id) end
	s:remove("active")
	s:set("points", 0)
	local m = SpireTasks.menu(p, 1)
	SpireTest.eq(m.master, "Taskmaster Rhen", "menu is Rhen's")
	SpireTest.eq(#m.list, 25, "25 tasks listed")
	SpireTest.eq(m.active, false, "no task yet")
	SpireTest.eq(m.list[1].look[1] > 0, true, "the menu shows the monster's look")
	SpireTest.eq((SpireTasks.take(p, "t2_hornedgrazer")), false, "Rhen doesn't give Floor 2 tasks")
	SpireTest.eq((SpireTasks.take(p, "t1_meadowwolf")), true, "take Meadow Wolf")
	SpireTest.eq((SpireTasks.take(p, "t1_bristleboar")), false, "one task at a time")
	SpireTest.eq((SpireTasks.report(p)), false, "can't report before the hunt")
	local t = SpireTasks.get("t1_meadowwolf")
	s:set("kills", t.count)
	m = SpireTasks.menu(p, 1)
	SpireTest.eq(m.active.kills, t.count, "menu shows the hunt done")
	SpireTest.eq((SpireTasks.report(p)), true, "report it")
	SpireTest.eq(p.money, t.gold, "paid the task's gold")
	SpireTest.eq(s:get("points"), t.points, "task points added")
	for _, row in ipairs(SpireTasks.menu(p, 1).list) do
		if row.id == "t1_meadowwolf" then SpireTest.eq(row.status, "wait", "done today: waits until tomorrow") end
	end
	SpireTest.eq(SpireTasks.get("t_wolves").id, "t1_meadowwolf", "an old task id still counts")
	local far = fakePlayer(WorldPoints.temple_hearthgate, "far")
	SpireTest.eq((SpireTasks.take(far, "t1_fieldrat")), false, "no taking tasks away from a taskmaster")
	for _, t2 in ipairs(SpireTasks.list) do s:remove("done_" .. t2.id) end
	s:remove("points")
	p.bp:remove()
	far.bp:remove()
end)
