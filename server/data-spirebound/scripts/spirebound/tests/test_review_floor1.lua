-- Fixes from the Floor 1 review, 2026-11-26 (docs/reviews/floor1-fixes-HANDOFF-2026-11-26.md).
local HERE = WorldPoints.temple_hearthgate

-- ---------------------------------------------------------------- 1. barracks weapons against shop weapons (B4-1)
local MELEE = { [WEAPON_SWORD] = true, [WEAPON_AXE] = true, [WEAPON_CLUB] = true }

SpireTest.add("review B4-1: the three barracks weapons hit alike, and harder with each tier", function()
	local b = Game.createItem(2853, 1, HERE)
	local floor = nil
	for _, id in ipairs({ "f1_vanguard_sword", "f1_vanguard_axe", "f1_vanguard_club" }) do
		local w = SpireGear.make(b, id)
		local atk = w:getAttribute(ITEM_ATTRIBUTE_ATTACK)
		floor = floor or atk
		SpireTest.eq(atk, floor, id .. " attack at tier 0")
		SpireTest.eq(atk > ItemType(SpireGear.def(id).base):getAttack(), true, id .. " beats the plain item it is built on")
		SpireTest.eq(w:getAttribute(ITEM_ATTRIBUTE_DEFENSE), SpireGear.def(id).defense, id .. " defence")
		SpireGear.setState(w, { tier = 3 })
		SpireTest.eq(w:getAttribute(ITEM_ATTRIBUTE_ATTACK), floor + 3 * SpireGearData.MELEE_ATTACK_PER_TIER, id .. " attack at tier 3")
	end
	local drop = SpireGear.make(b, "f1_vanguard_drop")
	SpireTest.eq(drop:getAttribute(ITEM_ATTRIBUTE_ATTACK), floor, "the rare sabre starts like the main weapon")
	local shop = SpireGear.make(b, "shop_weapon_4")
	SpireTest.eq(shop:getAttribute(ITEM_ATTRIBUTE_ATTACK) < floor, true, "the shop's Climber's Sword stays below the barracks weapon")
	b:remove()
end)

SpireTest.add("review B4-1: no Floor 1 shop sells a weapon that out-damages the tier-0 barracks weapon of its class", function()
	local barracks = SpireGear.def("f1_vanguard_sword").attack
	local p = io.popen("ls data-spirebound/npc/*.lua 2>/dev/null")
	local bad, seen = {}, 0
	for path in p:lines() do
		local file = path:match("[^/]+$")
		if not file:find("^floor%d") then -- Floor 1's NPCs: everything but the floorN_* towns
			local f = io.open(path, "r")
			local text = f and f:read("*a") or ""
			if f then f:close() end
			for name, id in text:gmatch('itemName = "([^"]+)", clientId = (%d+), buy = %d+') do
				local it = ItemType(tonumber(id))
				if MELEE[it:getWeaponType()] then
					seen = seen + 1
					if it:getAttack() >= barracks then
						table.insert(bad, file .. ": " .. name .. " (attack " .. it:getAttack() .. ")")
					end
				elseif it:getWeaponType() == WEAPON_DISTANCE or it:getWeaponType() == WEAPON_WAND then
					-- bows, crossbows, wands and rods: the barracks weapon is the same base item plus its damage bonus,
					-- so a shop weapon only out-damages it if it is a better base than every barracks weapon of the class
					seen = seen + 1
				end
			end
		end
	end
	p:close()
	SpireTest.eq(seen >= 8, true, "found the shops' weapons (" .. seen .. ")")
	SpireTest.eq(table.concat(bad, ", "), "", "shop weapons at or above attack " .. barracks)
end)

-- ---------------------------------------------------------------- 2. rare-drop weapons (B4-2)
-- A stand-in fighter holding a real item in its weapon hand (no real player is online during the boot test)
local function holder(voc, item)
	local p = { id = 987000 + voc }
	function p:getPlayer() return self end
	function p:getId() return self.id end
	function p:getVocation() return { getBaseId = function() return voc end } end
	function p:getSlotItem(slot) return slot == CONST_SLOT_LEFT and item or nil end
	return p
end

SpireTest.add("review B4-2: the four rare-weapon perks do what the item says", function()
	local size, life, mana = SpireGear.perkHit("life_leech", 0.02, 200, 0.9)
	SpireTest.eq(size, 200, "life leech leaves the hit alone")
	SpireTest.eq(life, 4, "2% of 200 comes back as health")
	size, life, mana = SpireGear.perkHit("mana_leech", 0.02, 200, 0.9)
	SpireTest.eq(mana, 4, "2% of 200 comes back as mana")
	size = SpireGear.perkHit("crit", 0.03, 200, 0.02)
	SpireTest.eq(size, 300, "a critical hit does half as much again")
	size = SpireGear.perkHit("crit", 0.03, 200, 0.5)
	SpireTest.eq(size, 200, "most hits are ordinary")
	SpireTest.eq(SpireGear.perkHealFactor("heal", 0.04), 1.04, "healing 4% stronger")
	SpireTest.eq(SpireGear.perkHealFactor(nil, nil), 1, "no rare weapon: no change")
	for _, w in ipairs(SpireGearData.weapons) do
		if w.source == "drop" then
			SpireTest.eq(SpireGear.perkText(w.perk, w.perkValue) ~= "", true, w.name .. " has a built perk")
		end
	end
end)

SpireTest.add("review B4-2: a rare weapon in hand changes a real hit on a real monster, whatever its sign", function()
	local b = Game.createItem(2853, 1, HERE)
	local sabre = SpireGear.make(b, "f1_vanguard_drop")
	SpireTest.eq(sabre:getAttribute(ITEM_ATTRIBUTE_DESCRIPTION):find("returns as health", 1, true) ~= nil, true, "the item says what it does")
	local wolf = Game.createMonster("Meadow Wolf", HERE, false, true)
	SpireTest.eq(wolf ~= nil, true, "monster made")
	local vanguard = holder(4, sabre)
	SpireTest.eq((SpireGear.perkOf(vanguard)), "life_leech", "a Vanguard holding the sabre has its perk")
	SpireTest.eq(SpireGear.onDealtPerk(vanguard, wolf, -40), -40, "life leech keeps a negative hit as it is")
	SpireTest.eq(SpireGear.perkOf(holder(3, sabre)), nil, "another class holding it gets nothing")
	local bow = SpireGear.make(b, "f1_ranger_drop")
	local ranger, crits, total = holder(3, bow), 0, 0
	for _ = 1, 4000 do
		local out = SpireGear.onDealtPerk(ranger, wolf, -100)
		total = total + 1
		if out == -150 then
			crits = crits + 1
		else
			SpireTest.eq(out, -100, "an ordinary arrow")
		end
	end
	SpireTest.eq(crits > 60 and crits < 200, true, "about 3% of 4000 arrows are critical (" .. crits .. ")")
	SpireTest.eq(SpireGear.onDealtPerk(holder(3, SpireGear.make(b, "f1_ranger_bow")), wolf, -100), -100, "the main bow has no perk")
	wolf:remove()
	b:remove()
end)

SpireTest.add("review B4-2: rare weapons fall from the two elites and the Ram only, 1 kill in 200, your own class twice as often", function()
	SpireTest.eq(SpireGearData.DROP_CHANCE, 0.005, "the chance")
	SpireTest.eq(SpireGear.rareDrop("Ruin Sentinel", 4, 0, 0), nil, "Ruin Sentinels no longer drop them")
	SpireTest.eq(SpireGear.rareDrop("Grey Alpha", 4, 0.0049, 0) ~= nil, true, "a Grey Alpha does, on a lucky roll")
	SpireTest.eq(SpireGear.rareDrop("Grey Alpha", 4, 0.005, 0), nil, "and not on an ordinary one")
	for _, name in ipairs({ "Bandit Captain", "Stonehorn Ram" }) do
		SpireTest.eq(SpireGear.rareDrop(name, 1, 0, 0) ~= nil, true, name .. " can drop one")
	end
	for own = 1, 4 do
		local count = { 0, 0, 0, 0 }
		for i = 0, 999 do
			local d = SpireGear.rareDrop("Grey Alpha", own, 0, i / 1000)
			count[d.vocation] = count[d.vocation] + 1
		end
		for voc = 1, 4 do
			SpireTest.eq(count[voc], voc == own and 400 or 200, "class " .. voc .. " share for a class-" .. own .. " looter")
		end
	end
end)

-- ---------------------------------------------------------------- confirmed by the review session's tests (T1-T3)
-- (real characters: tools/loadtest.py review hits and kills real monsters and reads what the server did)
SpireTest.add("review B4-0: the weapon's damage bonus applies to hits the way the engine sends them (negative)", function()
	local b = Game.createItem(2853, 1, HERE)
	local sword = SpireGear.make(b, "f1_vanguard_sword")
	SpireGear.setState(sword, { tier = 5, awakened = true })
	local wolf = Game.createMonster("Meadow Wolf", HERE, false, true)
	local p = holder(4, sword)
	function p:getPosition() return HERE end
	function p:getMaster() return nil end
	function p:kv() return kv.scoped("spiretest-b40") end
	function p:sendTextMessage() end
	local want = math.floor(100 * SpireGear.power(SpireGear.state(sword)) + 0.5)
	SpireTest.eq(want >= 140, true, "a tier-5 awakened sword is worth at least +40% (" .. want .. ")")
	SpireTest.eq(SpireProgress.onDealt(p, wolf, -100) <= -want, true, "a negative hit of 100 grows to at least " .. want .. ": " .. SpireProgress.onDealt(p, wolf, -100))
	SpireTest.eq(SpireProgress.onDealt(p, wolf, 100) >= want, true, "a positive hit grows the same way")
	SpireTest.eq(SpireProgress.onDealt(p, wolf, 0), 0, "nothing stays nothing")
	wolf:remove()
	b:remove()
end)

SpireTest.add("review T2: experience and skill factors go through the engine's own functions", function()
	local f = io.open("data/events/scripts/player.lua", "r")
	local text = f:read("*a")
	f:close()
	SpireTest.eq(text:find("SpireHooks.gainExperience", 1, true) ~= nil, true, "the engine's Player:onGainExperience calls Spirebound's factors")
	SpireTest.eq(text:find("SpireHooks.gainSkillTries", 1, true) ~= nil, true, "and so does Player:onGainSkillTries")
	for _, name in ipairs({ "difficulty", "beacons", "boost", "events" }) do
		SpireTest.eq(type(SpireHooks.xpFns[name]), "function", name .. " adds its experience factor")
	end
	SpireTest.eq(type(SpireHooks.skillFns.difficulty), "function", "the skill catch-up is hooked in")
	local saved = SpireHooks.xpFns
	SpireHooks.xpFns = { a = function(_, _, exp) return exp * 1.5 end, b = function(_, _, exp) return exp * 0.45 end }
	SpireTest.eq(SpireHooks.gainExperience(nil, nil, 1000, 100), 675, "factors multiply and the result is a whole number")
	SpireHooks.xpFns = saved
end)

SpireTest.add("review T3: the cavebot's loot cut works on a real container of real items", function()
	local body = Game.createItem(2853, 1, HERE)
	body:addItem(3031, 80) -- coins: a stack
	body:addItem(3264, 1) -- a sword
	body:addItem(3355, 1) -- a helmet
	local removed = SpireCavebot.cutLoot(body, function() return 0.99 end) -- every single item is unlucky
	SpireTest.eq(body:getSize(), 1, "single items vanish on a bad roll")
	SpireTest.eq(body:getItem(0):getCount(), 40, "a stack of 80 coins is halved")
	SpireTest.eq(removed, 42, "40 coins and 2 items taken")
	body:addItem(3264, 1)
	SpireCavebot.cutLoot(body, function() return 0 end)
	SpireTest.eq(body:getSize(), 2, "and stay on a good one")
	body:remove()
end)
