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

-- Pure: percent of the way to the next familiarity level (0-99), or nil when maxed (FLOOR1_REVIEW.md F1-41)
function SpireGear.famProgress(points, floor)
	local T = SpireGearData.FAMILIARITY_POINTS[floor] or SpireGearData.FAMILIARITY_POINTS[1]
	local lvl = SpireGear.famLevel(points, floor)
	if lvl >= #T then
		return nil
	end
	local from, to = lvl == 0 and 0 or T[lvl], T[lvl + 1]
	return math.floor(((points or 0) - from) / (to - from) * 100)
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
		local pct = SpireGear.famProgress(s.famPoints, d.floor)
		if pct then
			text = text .. string.format(" (%d%% to the next)", pct)
		end
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

-- Pure: does this kill drop a shard? chance per kill, kills since the last shard of this grade, a roll in [0, 1).
-- Pity (FLOOR1_REVIEW.md F1-42): at three times the expected wait the shard is guaranteed.
function SpireGear.shardRoll(chance, sinceLast, roll)
	return roll < chance or sinceLast >= math.floor(3 / chance)
end

-- ---------------------------------------------------------------- the Weaponsmith (spec 4.4, 4.5)
-- A wallet is { count(id), remove(id, n), money(), pay(n) }: a player's (SpireGear.playerWallet) or a test's.
function SpireGear.playerWallet(player)
	return {
		count = function(id) return player:getItemCount(id) end,
		remove = function(id, n) return player:removeItem(id, n) end,
		money = function() return player:getMoney() + player:getBankBalance() end,
		pay = function(n) return player:removeMoneyBank(n) end,
	}
end

local function shardName(id, n)
	local names = SpireGearData.tokenNames[id]
	return n == 1 and names[1] or names[2]
end

-- What the next tier costs: ok, { tier, shard, count, gold } or false, message (nothing is taken here)
function SpireGear.upgradeCheck(item, wallet)
	local s, d = SpireGear.state(item), SpireGear.defOf(item)
	if not s then
		return false, "That is not Spirebound gear."
	end
	if s.shop then
		return false, "Starter gear from the shop cannot be upgraded. A Spirebound weapon can: Captain Dorrow gives one at level 10."
	end
	if s.tier >= SpireGearData.MAX_TIER then
		return false, item:getName() .. " is already at its best: tier " .. SpireGearData.MAX_TIER .. "."
	end
	local tokens = SpireGearData.tokens[d.floor]
	local cost = SpireGearData.TIER_COST[s.tier + 1]
	local shard, need, gold = tokens[cost.grade], SpireGearData.SHARDS_PER_TIER, cost.gold * d.floor
	local have = wallet.count(shard)
	if have < need then
		return false, string.format("Tier %d needs %d %s and %d gold; you have %d. %s", s.tier + 1, need, shardName(shard, need),
			gold, have, SpireGearData.tokenWhere[shard])
	end
	if wallet.money() < gold then
		return false, string.format("Tier %d costs %d gold as well as the shards.", s.tier + 1, gold)
	end
	return true, { tier = s.tier + 1, shard = shard, count = need, gold = gold }
end

function SpireGear.upgradeWith(item, wallet)
	local ok, cost = SpireGear.upgradeCheck(item, wallet)
	if not ok then
		return false, cost
	end
	if not wallet.pay(cost.gold) then
		return false, "You could not pay the fee."
	end
	wallet.remove(cost.shard, cost.count)
	SpireGear.setState(item, { tier = cost.tier })
	return true, string.format("Done: %s is now tier %d.", item:getName(), cost.tier)
end

-- Remake a weapon in another family of its class and floor: tier kept, familiarity 0. Returns the new item or nil, message.
function SpireGear.reforgeWith(item, family, wallet, into)
	local s, d = SpireGear.state(item), SpireGear.defOf(item)
	if not s or d.kind ~= "weapon" or s.shop then
		return nil, "Only a Spirebound weapon can be reforged."
	end
	local target = nil
	for _, w in pairs(defs) do
		if not w.shop and w.kind == "weapon" and w.vocation == d.vocation and w.floor == d.floor and w.source == "main" and w.family == family then
			target = w
		end
	end
	if not target or target.id == d.id then
		return nil, "I can't reforge it into that. Your class's families on this floor: " .. SpireGear.familiesOf(d.vocation, d.floor) .. "."
	end
	local fee = SpireGearData.REFORGE_FEE * d.floor
	if wallet.money() < fee or not wallet.pay(fee) then
		return nil, string.format("A reforge costs %d gold.", fee)
	end
	local new = SpireGear.make(into, target.id)
	if not new then
		return nil, "You have no room for the new weapon."
	end
	SpireGear.setState(new, { tier = s.tier, awakened = s.awakened })
	item:remove()
	return new, string.format("Reforged into %s, tier %d. Its familiarity starts again.", new:getName(), s.tier)
end

function SpireGear.familiesOf(vocation, floor)
	local out = {}
	for _, w in ipairs(SpireGearData.weapons) do
		if w.vocation == vocation and w.floor == floor and w.source == "main" then
			table.insert(out, w.family)
		end
	end
	return table.concat(out, ", ")
end

-- Every item the player carries (slots and nested containers)
function SpireGear.carried(player)
	local out = {}
	local function walk(item)
		table.insert(out, item)
		if item:isContainer() then
			for i = 0, item:getSize() - 1 do
				walk(item:getItem(i))
			end
		end
	end
	for slot = CONST_SLOT_FIRST, CONST_SLOT_LAST do
		local it = player:getSlotItem(slot)
		if it then
			walk(it)
		end
	end
	return out
end

-- ---------------------------------------------------------------- the Floor 1 path (spec 4.5)
-- Pure: what Captain Dorrow says about the barracks' weapon: "no_class", "too_low", "offer" or "has"
SpireGear.MAIN_LEVEL = 10
function SpireGear.dorrowOffer(level, vocation, earnedId)
	if not SpireGearData.style[vocation] then
		return "no_class"
	end
	if earnedId then
		return "has"
	end
	if level < SpireGear.MAIN_LEVEL then
		return "too_low"
	end
	return "offer"
end

-- Pure: the main weapon of a family for a vocation and floor
function SpireGear.mainFor(vocation, floor, family)
	for _, d in pairs(defs) do
		if not d.shop and d.kind == "weapon" and d.source == "main" and d.vocation == vocation and d.floor == floor and d.family == family then
			return d
		end
	end
end

-- +1 tier, free (the temper quest)
function SpireGear.temper(item)
	local s = SpireGear.state(item)
	if not s or s.shop or s.tier >= SpireGearData.MAX_TIER then
		return false
	end
	SpireGear.setState(item, { tier = s.tier + 1 })
	return true
end

-- The awakening (the floor boss): its new name and final base power, once
function SpireGear.awaken(item)
	local s, d = SpireGear.state(item), SpireGear.defOf(item)
	if not s or s.shop or d.kind ~= "weapon" or s.awakened then
		return false
	end
	SpireGear.setState(item, { awakened = true })
	return true
end

-- Pure: what a credited fighter gets from a Floor 1 boss
SpireGear.BOSS_REWARDS = { ["Gate Hound"] = { shards = 3, grade = "cut", floor = 1 }, ["Axe-Lord of the Stair"] = { awaken = 1 } }
function SpireGear.bossReward(boss, hadShards)
	local r = SpireGear.BOSS_REWARDS[boss]
	if not r then
		return {}
	end
	return { shards = r.shards and (hadShards and 0 or r.shards) or 0, grade = r.grade, floor = r.floor, awaken = r.awaken }
end

-- A Floor n weapon the player holds or carries (the one in hand first)
function SpireGear.floorWeapon(player, floor)
	local item, d = SpireGear.mainWeapon(player)
	if item and d.floor == floor and not d.shop then
		return item
	end
	for _, it in ipairs(SpireGear.carried(player)) do
		local dd = SpireGear.defOf(it)
		if dd and dd.kind == "weapon" and dd.floor == floor and not dd.shop then
			return it
		end
	end
end

function SpireGear.temperFor(player, floor)
	local item = SpireGear.floorWeapon(player, floor)
	if item and SpireGear.temper(item) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, item:getName() .. " is tempered: tier " .. SpireGear.state(item).tier .. ".")
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Bring your Floor 1 weapon next time and it will be tempered.")
	end
end

-- Give every credited fighter its boss reward (public and private kills alike)
function SpireGear.grantBoss(boss, creditNames)
	if not SpireGear.BOSS_REWARDS[boss] then
		return
	end
	for _, name in ipairs(creditNames) do
		local p = Player(name)
		if p then
			local k = p:kv():scoped("spirebound")
			local flag = "boss_credit_" .. boss
			local plan = SpireGear.bossReward(boss, k:get(flag) ~= nil)
			k:set(flag, os.time())
			if boss == "Gate Hound" and SpireStairKey then
				SpireStairKey.update(p) -- one piece of the Stair Key
			end
			if plan.shards > 0 then
				p:addItem(SpireGearData.tokens[plan.floor][plan.grade], plan.shards)
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s leaves you %d %s.", boss, plan.shards, SpireGearData.tokenNames[SpireGearData.tokens[plan.floor][plan.grade]][2]))
			end
			if plan.awaken then
				local item = SpireGear.floorWeapon(p, 1)
				if item and SpireGear.awaken(item) then
					p:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
					p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your weapon awakens: " .. item:getName() .. "!")
				elseif not item then
					p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Carry a Floor 1 weapon when you defeat the " .. boss .. " to awaken it.")
				end
			end
		end
	end
end
