-- Gear and weapon progression rules (docs/superpowers/specs/2026-11-23-gear-progression-design.md).
-- Data: lib/spirebound/gear_data.lua (tools/gen_gear.py). A weapon's tier, familiarity and awakening are stored on
-- the item (custom attributes), so they survive trades, the depot and restarts. Weapon power is a damage multiplier.
SpireGear = SpireGear or {}

local A_ID, A_TIER, A_FAM, A_AWAKE = "sb_gear", "sb_tier", "sb_fam", "sb_awake"

local defs = {}
for _, w in ipairs(SpireGearData.weapons) do
	defs[w.id] = { id = w.id, kind = "weapon", name = w.name, floor = w.floor, vocation = w.vocation, family = w.family,
		source = w.source, base = w.base, awakenedName = w.awakenedName, perk = w.perk, perkValue = w.perkValue }
end
for _, a in ipairs(SpireGearData.armour) do
	defs[a.id] = { id = a.id, kind = "armour", name = a.name, floor = a.floor, vocation = a.vocation, source = a.source,
		base = a.base, bonus = a.bonus }
end
for voc, s in pairs(SpireGearData.shop) do
	defs[s.weapon.id] = { id = s.weapon.id, kind = "weapon", shop = true, name = s.weapon.name, floor = 1, vocation = voc,
		base = s.weapon.base, bonus = s.weapon.bonus }
	defs[s.armour.id] = { id = s.armour.id, kind = "armour", shop = true, name = s.armour.name, floor = 1, vocation = voc,
		base = s.armour.base, bonus = s.armour.bonus }
end
SpireGear.defs = defs

function SpireGear.def(id)
	return defs[id]
end

-- Pure: familiarity level (0-10) for raw points on a weapon of this floor
function SpireGear.famLevel(points, floor)
	local T = SpireGearData.FAMILIARITY_POINTS[floor] or SpireGearData.FAMILIARITY_POINTS[1]
	local lvl = 0
	for i, need in ipairs(T) do
		if (points or 0) >= need then
			lvl = i
		end
	end
	return lvl
end

-- Pure: damage multiplier of a weapon state { floor, tier, fam, awakened, shop }
function SpireGear.power(s)
	if not s then
		return 1
	end
	if s.shop then
		local voc = s.vocation or 3
		return 1 + SpireGearData.shop[voc].weapon.bonus
	end
	local f = SpireGearData.floor[s.floor]
	return (1 + f.base + (s.tier or 0) * f.step + (s.awakened and f.awaken or 0)) * (1 + SpireGearData.FAM_BONUS * (s.fam or 0))
end

function SpireGear.defOf(item)
	if not item then
		return nil
	end
	local id = item:getCustomAttribute(A_ID)
	return id and defs[id] or nil
end

-- The item's state, or nil for an item that is not Spirebound gear
function SpireGear.state(item)
	local d = SpireGear.defOf(item)
	if not d then
		return nil
	end
	local points = tonumber(item:getCustomAttribute(A_FAM)) or 0
	return { id = d.id, kind = d.kind, floor = d.floor, vocation = d.vocation, shop = d.shop or false,
		tier = tonumber(item:getCustomAttribute(A_TIER)) or 0, famPoints = points,
		fam = d.kind == "weapon" and not d.shop and SpireGear.famLevel(points, d.floor) or 0,
		awakened = (tonumber(item:getCustomAttribute(A_AWAKE)) or 0) == 1 }
end

local function describe(item, d, s)
	if d.shop then
		return "Climber's starter gear (shop). It cannot be upgraded."
	end
	local name = d.kind == "weapon" and "weapon" or "armour"
	local text = string.format("Spirebound %s, Floor %d. Tier %d/%d", name, d.floor, s.tier, SpireGearData.MAX_TIER)
	if d.kind == "weapon" then
		text = text .. string.format(", familiarity %d/10: %+d%% damage", s.fam, math.floor((SpireGear.power(s) - 1) * 100 + 0.5))
		if s.awakened then
			text = text .. ". Awakened"
		end
	end
	return text .. "."
end

-- Write the state onto the item and refresh its name, armour and description. Fields left out keep their value.
function SpireGear.setState(item, new)
	local d = SpireGear.defOf(item)
	if not d then
		return false
	end
	if not d.shop then
		if new.tier ~= nil then
			item:setCustomAttribute(A_TIER, math.max(0, math.min(SpireGearData.MAX_TIER, new.tier)))
		end
		if new.famPoints ~= nil then
			item:setCustomAttribute(A_FAM, math.floor(new.famPoints))
		end
		if new.awakened ~= nil then
			item:setCustomAttribute(A_AWAKE, new.awakened and 1 or 0)
		end
	end
	local s = SpireGear.state(item)
	item:setAttribute(ITEM_ATTRIBUTE_NAME, (s.awakened and d.awakenedName) or d.name)
	if d.kind == "armour" then
		local step = d.shop and 0 or SpireGearData.floor[d.floor].armorStep
		item:setAttribute(ITEM_ATTRIBUTE_ARMOR, ItemType(d.base):getArmor() + d.bonus + s.tier * step)
	end
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, describe(item, d, s))
	return true
end

-- Make a piece by its id into a player or a container
function SpireGear.make(into, id)
	local d = defs[id]
	if not d then
		return nil
	end
	local item = into:addItem(d.base, 1)
	if not item then
		return nil
	end
	item:setCustomAttribute(A_ID, d.id)
	SpireGear.setState(item, { tier = 0, famPoints = 0, awakened = false })
	return item
end

-- The Spirebound weapon in the player's hands (left or right), or nil
function SpireGear.mainWeapon(player)
	for _, slot in ipairs({ CONST_SLOT_LEFT, CONST_SLOT_RIGHT }) do
		local item = player:getSlotItem(slot)
		local d = SpireGear.defOf(item)
		if d and d.kind == "weapon" then
			return item, d
		end
	end
	return nil
end

-- Pure: the rare drop / armour / main weapon definitions for a vocation and floor
function SpireGear.find(vocation, floor, source, kind)
	for _, d in pairs(defs) do
		if not d.shop and d.vocation == vocation and d.floor == floor and d.source == source and (not kind or d.kind == kind) then
			return d
		end
	end
end

-- Give a player the piece for its vocation (used by quest rewards)
function SpireGear.give(player, floor, source)
	local d = SpireGear.find(player:getVocation():getBaseId(), floor, source)
	if not d then
		return nil
	end
	local item = SpireGear.make(player, d.id)
	if item then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You received " .. d.name .. ".")
	end
	return item
end
