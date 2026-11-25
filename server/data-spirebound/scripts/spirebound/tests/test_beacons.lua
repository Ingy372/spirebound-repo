-- Roadmap M1: Floor Beacons (lib/spirebound/beacons.lua, scripts/spirebound/beacons.lua).
local B = SpireBeacons

SpireTest.add("beacons: four fires, the guild cap and the hour", function()
	local floor, t0 = 1, os.time()
	B.put(floor, { slots = {} })
	SpireTest.eq(B.xpFactor(floor, t0), 1, "dark Beacon: no bonus")
	SpireTest.eq(B.lootBonus(floor, t0), 0, "dark Beacon: no loot bonus")
	SpireTest.eq(select(1, B.light(floor, 1, "Ann", 7, t0)), true, "a guild member lights fire 1")
	SpireTest.eq(select(1, B.light(floor, 1, "Bob", 0, t0)), false, "a burning fire can't be lit again")
	SpireTest.eq(select(1, B.light(floor, 2, "Cid", 7, t0)), true, "the same guild lights fire 2")
	local ok, why = B.light(floor, 3, "Dee", 7, t0)
	SpireTest.eq(ok, false, "a third fire for the same guild is refused")
	SpireTest.eq(why:find("guild") ~= nil, true, "the refusal names the guild cap")
	SpireTest.eq(select(1, B.light(floor, 3, "Eve", 0, t0)), true, "a player without a guild lights fire 3")
	SpireTest.eq(select(1, B.light(floor, 4, "Fay", 9, t0)), true, "another guild lights fire 4")
	SpireTest.eq(B.litCount(B.get(floor), t0), 4, "all four burn")
	SpireTest.eq(math.abs(B.xpFactor(floor, t0) - 1.20) < 1e-9, true, "+20% experience with four fires")
	SpireTest.eq(math.abs(B.lootBonus(floor, t0) - 0.20) < 1e-9, true, "+20% loot roll with four fires")
	SpireTest.eq(B.apexFast(floor, t0), true, "four fires: the apex refills fast")
	SpireTest.eq(B.statusLine(floor, B.get(floor), t0):find("Ann") ~= nil, true, "the status names who lit")
	SpireTest.eq(B.xpFactor(2, t0), 1, "another floor gets nothing")
	SpireTest.eq(B.litCount(B.get(floor), t0 + B.DURATION + 1), 0, "after an hour every fire is out")
	SpireTest.eq(B.apexFast(floor, t0 + B.DURATION + 1), false, "and the apex is back to normal")
	B.put(floor, { slots = {} })
end)

SpireTest.add("beacons: who drops Embers", function()
	local always = function() return 0 end
	local never = function() return 0.99 end
	SpireTest.eq(B.embersFor("Gate Hound", never, SpireFloorBosses), B.FIELD_BOSS_EMBERS, "Floor 1's field boss always drops Embers")
	SpireTest.eq(B.embersFor("Horn Brute", never, SpireFloorBosses), B.FIELD_BOSS_EMBERS, "Floor 2's field boss too")
	SpireTest.eq(B.embersFor("Old Tusk", never, SpireFloorBosses), B.MINIBOSS_EMBERS, "a hidden mini-boss drops one")
	SpireTest.eq(B.embersFor("Grey Alpha", always, SpireFloorBosses), 1, "an elite can drop one")
	SpireTest.eq(B.embersFor("Grey Alpha", never, SpireFloorBosses), 0, "but not always")
	SpireTest.eq(B.embersFor("Herd Bull", always, SpireFloorBosses), 1, "Floor 2's elite can drop one")
	SpireTest.eq(B.embersFor("Stonehorn Ram", always, SpireFloorBosses), 1, "an apex monster rarely drops one")
	SpireTest.eq(B.embersFor("Field Rat", always, SpireFloorBosses), 0, "a rat never does")
	SpireTest.eq(ItemType(B.EMBER):getName(), "Beacon Ember", "the Ember has its own name")
end)

SpireTest.add("beacons: every open floor's town has four fire bowls on the map", function()
	for floor = 1, 10 do
		for i = 1, B.SLOTS do
			local p = WorldPoints["beacon_" .. floor .. "_" .. i]
			SpireTest.eq(p ~= nil, true, "point beacon_" .. floor .. "_" .. i)
			local tile = Tile(p)
			SpireTest.eq(tile ~= nil and (tile:getItemById(B.UNLIT) ~= nil or tile:getItemById(B.LIT) ~= nil), true,
				"fire bowl " .. i .. " on floor " .. floor)
			local f, s = B.slotAt(p)
			SpireTest.eq(f == floor and s == i, true, "the bowl knows its floor and slot")
		end
	end
	SpireTest.eq(Floors.at(WorldPoints.beacon_1_1), 1, "Floor 1's Beacon stands on Floor 1")
end)

SpireTest.add("beacons: lit fires show on the bowls and fill the apex spawn", function()
	local floor, now = 1, os.time()
	B.put(floor, { slots = {} })
	for i = 1, B.SLOTS do
		B.light(floor, i, "Tester", 0, now)
	end
	B.syncBowls(floor, now)
	SpireTest.eq(Tile(WorldPoints.beacon_1_1):getItemById(B.LIT) ~= nil, true, "a lit bowl shows fire")
	local spawned = B.apexTick(floor, now)
	SpireTest.eq(spawned, B.APEX_EXTRA, "four fires: the extra apex monsters arrive")
	SpireTest.eq(B.apexExtras(floor), B.APEX_EXTRA, "and they are alive")
	B.put(floor, { slots = {} })
	B.syncBowls(floor, now)
	SpireTest.eq(Tile(WorldPoints.beacon_1_1):getItemById(B.UNLIT) ~= nil, true, "a cold bowl is empty again")
	B.apexTick(floor, now)
	SpireTest.eq(B.apexExtras(floor), 0, "fires out: the extras melt away")
end)
