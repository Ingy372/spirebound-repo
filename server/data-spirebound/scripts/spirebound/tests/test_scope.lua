-- Roadmap R13: the friends test is Floors 1-2 only; arena, siege and shop are off (the Season Path is on since 2026-11-23).
SpireTest.add("scope: the friends test seals Floors 3-10 and switches off the extras", function()
	local store = kv.scoped("spirebound-scope")
	local old = store:get("friendsTest")
	local rec, rec1 = Floors.get(2), Floors.get(1)
	local had, had1 = rec.bossDeadAt, rec1.bossDeadAt
	local function restore() -- always, even when a check fails: this state is saved in the database
		rec.bossDeadAt, rec1.bossDeadAt = had, had1
		kv.scoped("spirebound-floors"):set("floor-2", rec)
		kv.scoped("spirebound-floors"):set("floor-1", rec1)
		if old == nil then
			store:remove("friendsTest")
		else
			store:set("friendsTest", old)
		end
	end
	local ok, err = pcall(function()
		store:set("friendsTest", true)
		rec.bossDeadAt = had or os.time()
		rec1.bossDeadAt = had1 or os.time()
		kv.scoped("spirebound-floors"):set("floor-2", rec)
		kv.scoped("spirebound-floors"):set("floor-1", rec1)
		SpireTest.eq(Floors.isOpen(2), true, "Floor 2 can open")
		SpireTest.eq(Floors.isOpen(3), false, "Floor 3 stays sealed even after Floor 2's boss falls")
		SpireTest.eq(SpireArena.open("lms"), false, "no arena event can start")
		SpireTest.eq(SpireSiege.open(), false, "no siege can start")
		SpireTest.eq(SpireScope.off("seasonpath"), false, "the Season Path is on (2026-11-23: testers should try the daily and weekly goals)")
		SpireTest.eq(SpireShop.ENABLED, false, "the shop is off")
		store:set("friendsTest", false)
		SpireTest.eq(Floors.isOpen(3), true, "at launch scope, Floor 3 opens after Floor 2's boss")
	end)
	restore()
	if not ok then
		error(err, 0)
	end
end)

SpireTest.add("scope: every Floor 2 camp monster has its own trick", function()
	local seen = {}
	for _, name in ipairs({ "Horned Grazer", "Ridge Cat", "Dust Strider", "Hill Cutthroat", "Blight Wasp" }) do
		local mt = MonsterType(name)
		SpireTest.eq(mt ~= nil and #mt:getAttackList() >= 2, true, name .. " has an attack besides its bite")
	end
end)
