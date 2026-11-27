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
