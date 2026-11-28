-- Roadmap AD5: treasure maps (adventure design 4.5).
local T, D = SpireTreasure, SpireAdventureData

local function ensurePlaced()
	if #T.spots == 0 then
		T.place()
	end
end

SpireTest.add("treasure maps: 24 dig spots on open ground in the level 12-30 grounds, each by a real landmark", function()
	ensurePlaced()
	SpireTest.eq(#T.spots, 24, "24 dig spots")
	for i, s in ipairs(T.spots) do
		SpireTest.eq(SpireRoamers.groundAt(s.pos), s.gid, s.key .. " lies in its ground")
		local t = Tile(s.pos)
		SpireTest.eq(t ~= nil and t:isWalkable(false, false, false, false, true), true, s.key .. " can be walked on")
		SpireTest.eq(s.landmark ~= nil, true, s.key .. " has a landmark")
		local gate = WorldPoints["gate_" .. s.gid]
		SpireTest.eq(math.max(math.abs(s.pos.x - gate.x), math.abs(s.pos.y - gate.y)) >= 8, true, s.key .. " is 8+ tiles from the gate")
		for j = i + 1, #T.spots do
			local o = T.spots[j]
			SpireTest.eq(math.max(math.abs(o.pos.x - s.pos.x), math.abs(o.pos.y - s.pos.y)) >= 8 or o.pos.z ~= s.pos.z, true, s.key .. " and " .. o.key .. " are apart")
		end
		SpireTest.eq(s.clue:find(SpireRoamers.groundTitle(s.gid), 1, true) == 1, true, s.key .. "'s clue starts with the ground")
	end
end)

SpireTest.add("treasure maps: the warmer/colder help, gold and keepsake rules", function()
	SpireTest.eq(T.hint(0, 0), "Right here! Dig with a shovel.", "on the spot")
	SpireTest.eq(T.hint(1, -1), "Right here! Dig with a shovel.", "a step away counts")
	SpireTest.eq(T.hint(0, -3), "Very close now, just to the north.", "very close")
	SpireTest.eq(T.hint(8, 0), "Close. Keep going east.", "close")
	SpireTest.eq(T.hint(30, -25), "Far to the north-east.", "far")
	local g = D.digs.bandit_road.gold
	SpireTest.eq(T.gold("bandit_road", 0), g[1], "5 minutes of the Bandit Road")
	SpireTest.eq(T.gold("bandit_road", 1), g[2], "10 minutes of the Bandit Road")
	local first = T.pickKeepsake({ smugglers_lantern = true, bandit_banner = true, ruin_idol = true, captains_sea_chest = true, climbers_compass = true }, function() return 1 end)
	SpireTest.eq(D.treasureKeepsakes[first].id, "wardwright_tablet", "a lucky dig gives a keepsake you lack")
end)

SpireTest.add("treasure maps: the map, the shovel and the keepsakes are real items with their own names", function()
	SpireTest.eq(ItemType(D.mapItem):getName(), "Tattered map", "the map's name")
	SpireTest.eq(ItemType(D.mapItem):isPickupable(), true, "the map can be carried (and traded)")
	SpireTest.eq(ItemType(D.shovel):isPickupable(), true, "a shovel can be carried")
	for _, k in ipairs(D.treasureKeepsakes) do
		SpireTest.eq(ItemType(k.item):getName(), k.name, k.id .. " is named")
		SpireTest.eq(ItemType(k.item):isPickupable(), true, k.name .. " can be carried home")
	end
	for _, r in ipairs(D.roamers) do
		SpireTest.eq(ItemType(r.keepsake):getName(), r.keepsakeName, r.id .. "'s keepsake is named")
		SpireTest.eq(ItemType(r.keepsake):isPickupable(), true, r.keepsakeName .. " can be carried home")
	end
	SpireTest.eq(onUseShovel ~= nil and T.wrapped == true, true, "the shovel knows about dig spots")
end)

SpireTest.add("treasure maps: a dig pays gold, counts toward the title and can raise guards", function()
	ensurePlaced()
	local s = T.byKey["bandit_road:1"]
	SpireTest.eq(s ~= nil, true, "a Bandit Road spot")
	local pos = s.pos
	local bp = Game.createItem(2854, 1, WorldPoints.temple_hearthgate)
	local store = { scoped = function(_, name) return kv.scoped("spiretest-dig-" .. name) end }
	kv.scoped("spiretest-dig-spirebound-treasure"):remove("dug")
	kv.scoped("spiretest-dig-spirebound-treasure"):remove("since")
	local p = { money = 0, msgs = {} }
	function p:addItemEx(it) return bp:addItemEx(it) end
	function p:getBankBalance() return self.money end
	function p:setBankBalance(n) self.money = n return true end
	function p:sendTextMessage(_, m) table.insert(self.msgs, m) end
	function p:getName() return "Digtest" end
	function p:kv() return store end
	local out = T.dig(p, s, { gold = 0, shard = 0, shards = 0, ember = 0, keepsake = 0, guards = 0, count = 0 })
	SpireTest.eq(SpireTest.coinValue(bp), D.digs.bandit_road.gold[1], "the gold went into the backpack (Q76)")
	SpireTest.eq(p.money, 0, "not the bank")
	SpireTest.eq(out.shards, 1, "a cut shard")
	SpireTest.eq(out.ember, true, "an ember")
	SpireTest.eq(out.keepsake ~= nil, true, "a keepsake")
	SpireTest.eq(out.guards, 2, "two guards rose")
	SpireTest.eq(T.dug(p), 1, "one map dug")
	for _, c in ipairs(Game.getSpectators(pos, false, false, 3, 3, 3, 3)) do
		if c:isMonster() and c:getName() == D.digs.bandit_road.guard then
			c:remove()
		end
	end
	bp:remove()
	kv.scoped("spiretest-dig-spirebound-treasure"):remove("dug")
end)
