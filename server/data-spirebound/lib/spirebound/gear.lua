-- Gear and weapon progression rules (docs/superpowers/specs/2026-11-23-gear-progression-design.md).
-- Data: lib/spirebound/gear_data.lua (tools/gen_gear.py). A weapon's tier, familiarity and awakening are stored on
-- the item (custom attributes), so they survive trades, the depot and restarts. Weapon power is a damage multiplier.
SpireGear = SpireGear or {}

local A_ID, A_TIER, A_FAM, A_AWAKE = "sb_gear", "sb_tier", "sb_fam", "sb_awake"

local defs = {}
for _, w in ipairs(SpireGearData.weapons) do
	defs[w.id] = { id = w.id, kind = "weapon", name = w.name, floor = w.floor, vocation = w.vocation, family = w.family,
		source = w.source, base = w.base, awakenedName = w.awakenedName, perk = w.perk, perkValue = w.perkValue,
		attack = w.attack, defense = w.defense, scale = w.scale }
end
for _, a in ipairs(SpireGearData.armour) do
	defs[a.id] = { id = a.id, kind = "armour", name = a.name, floor = a.floor, vocation = a.vocation, source = a.source,
		base = a.base, bonus = a.bonus }
end
for voc, s in pairs(SpireGearData.shop) do
	defs[s.weapon.id] = { id = s.weapon.id, kind = "weapon", shop = true, name = s.weapon.name, floor = 1, vocation = voc,
		base = s.weapon.base, bonus = s.weapon.bonus, attack = s.weapon.attack, defense = s.weapon.defense }
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

-- ---------------------------------------------------------------- rare-drop weapon perks (spec 4.5; review B4-2)
-- Pure: the line on the item
function SpireGear.perkText(perk, value)
	local pct = math.floor(value * 100 + 0.5)
	if perk == "life_leech" then
		return string.format("Rare: %d%% of the damage you deal returns as health", pct)
	elseif perk == "mana_leech" then
		return string.format("Rare: %d%% of the damage you deal returns as mana", pct)
	elseif perk == "crit" then
		return string.format("Rare: %d%% of your hits strike for %d%% more", pct, math.floor(SpireGearData.CRIT_BONUS * 100 + 0.5))
	elseif perk == "heal" then
		return string.format("Rare: your healing is %d%% stronger", pct)
	end
	return ""
end

-- Pure: what a hit of this size (a positive number) becomes with a perk. roll is in [0, 1).
-- Returns the new size, health given back, mana given back.
function SpireGear.perkHit(perk, value, size, roll)
	if perk == "crit" and roll < value then
		return math.floor(size * (1 + SpireGearData.CRIT_BONUS) + 0.5), 0, 0
	elseif perk == "life_leech" then
		return size, math.floor(size * value + 0.5), 0
	elseif perk == "mana_leech" then
		return size, 0, math.floor(size * value + 0.5)
	end
	return size, 0, 0
end

-- Pure: multiplier on healing done
function SpireGear.perkHealFactor(perk, value)
	return perk == "heal" and (1 + value) or 1
end

-- The perk of the rare weapon in this player's hand (only for its own class, like the damage bonus)
function SpireGear.perkOf(player)
	local item, d = SpireGear.mainWeapon(player)
	if d and d.perk and d.vocation == player:getVocation():getBaseId() then
		return d.perk, d.perkValue
	end
end

-- A player's own hit on a monster (called from the monsters' damage event). The amount can arrive negative or
-- positive: work on its size and keep the sign. Leeched health and mana arrive a moment later, never inside the event.
function SpireGear.onDealtPerk(attacker, target, amount)
	local player = attacker and attacker:getPlayer()
	if not player or amount == 0 then
		return amount
	end
	local perk, value = SpireGear.perkOf(player)
	if not perk then
		return amount
	end
	local sign = amount < 0 and -1 or 1
	local size, life, mana = SpireGear.perkHit(perk, value, math.abs(amount), math.random())
	if size > math.abs(amount) then
		target:getPosition():sendMagicEffect(CONST_ME_CRITICAL_DAMAGE)
	end
	if life > 0 or mana > 0 then
		local cap = target:getHealth() -- an overkill gives back no more than the monster had
		life, mana = math.min(life, cap), math.min(mana, cap)
		addEvent(function(pid, hp, mp)
			local p = Player(pid)
			if p and hp > 0 then
				p:addHealth(hp)
			end
			if p and mp > 0 then
				p:addMana(mp)
			end
		end, 50, player:getId(), life, mana)
	end
	return sign * size
end

-- Pure: does this kill drop a rare weapon, and for which class? `own` is the looter's class (1-4), chanceRoll and
-- classRoll are in [0, 1). The looter's own class is DROP_OWN_CLASS_WEIGHT times as likely as each other class.
function SpireGear.rareDrop(monsterName, own, chanceRoll, classRoll)
	local floor = nil
	for f, list in pairs(SpireGearData.dropFrom) do
		for _, n in ipairs(list) do
			if n == monsterName then
				floor = f
			end
		end
	end
	if not floor or chanceRoll >= SpireGearData.DROP_CHANCE then
		return nil
	end
	local w = SpireGearData.DROP_OWN_CLASS_WEIGHT
	local total = 0
	for voc = 1, 4 do
		total = total + (voc == own and w or 1)
	end
	local at, pick = classRoll * total, 4
	for voc = 1, 4 do
		at = at - (voc == own and w or 1)
		if at < 0 then
			pick = voc
			break
		end
	end
	return SpireGear.find(pick, floor, "drop", "weapon")
end

-- Pure: the attack written on a melee weapon of this definition at a tier (nil: the base item's own attack)
function SpireGear.attackOf(d, tier)
	if not d or not d.attack then
		return nil
	end
	return d.attack + (d.shop and 0 or (tier or 0) * SpireGearData.MELEE_ATTACK_PER_TIER)
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
		awakened = (tonumber(item:getCustomAttribute(A_AWAKE)) or 0) == 1,
		scale = d.scale } -- adventure layer: a rare weapon's own picture may be a stronger base item, scaled back
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
		if d.perk then
			text = text .. ". " .. SpireGear.perkText(d.perk, d.perkValue)
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
	if d.kind == "weapon" and d.attack then
		-- melee weapons carry their own attack and defence (Floor 1 review B4-1): one value per floor for sword, axe
		-- and mace alike, +1 attack per tier, so no shop sword out-damages the barracks' weapon
		item:setAttribute(ITEM_ATTRIBUTE_ATTACK, SpireGear.attackOf(d, s.tier))
		item:setAttribute(ITEM_ATTRIBUTE_DEFENSE, d.defense)
	end
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, describe(item, d, s))
	return true
end

-- A new piece that is not anywhere yet (the caller places it)
function SpireGear.create(id)
	local d = defs[id]
	local item = d and Game.createItem(d.base, 1)
	if not item then
		return nil
	end
	item:setCustomAttribute(A_ID, d.id)
	SpireGear.setState(item, { tier = 0, famPoints = 0, awakened = false })
	return item
end

-- Make a piece by its id into a player or a container.
-- Party playtest 2026-11-26 (hand-off P1-1): a plain player:addItem drops the item on the floor when the player is over
-- their carrying limit, so quest armour and the barracks weapon silently lay at the player's feet and decayed. For a
-- player the piece now ignores carrying weight (like the starter kit, lib/spirebound/give.lua); if the backpack has no
-- free slot either, it goes to the Store Inbox (always carried, never on the floor). Second result: "bag" or "inbox".
function SpireGear.make(into, id)
	local d = defs[id]
	if not d then
		return nil
	end
	if into.isPlayer and into:isPlayer() then
		local item = SpireGear.create(id)
		if not item then
			return nil
		end
		if into:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
			return item, "bag"
		end
		local inbox = into.getStoreInbox and into:getStoreInbox()
		if inbox and inbox:addItemEx(item, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
			into:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your backpack is full: " .. item:getName() .. " was put in your Store Inbox (the box in your equipment).")
			return item, "inbox"
		end
		item:remove()
		return nil
	end
	if into.getCapacity and into:getSize() >= into:getCapacity() then
		return nil -- a full container (asking the engine anyway logs an error)
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
	local item, where = SpireGear.make(player, d.id)
	if item and where == "bag" then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You received " .. d.name .. ". It is in your backpack: drag it onto your character to wear it.")
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
		refund = function(n) player:setBankBalance(player:getBankBalance() + n) end,
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
		if wallet.refund then
			wallet.refund(fee) -- review item 10: the fee was kept when the new weapon could not be made
		end
		return nil, "You have no room for the new weapon. Your fee is back in your bank."
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
	-- the Store Inbox too: a reward that found no room waits there (SpireGear.make)
	local inbox = player.getStoreInbox and player:getStoreInbox()
	if inbox then
		for i = 0, inbox:getSize() - 1 do
			walk(inbox:getItem(i))
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

-- +1 tier, free (the temper quest). Only a raw weapon (below tier 2): review item 10, it could be saved to skip tier 5.
SpireGear.TEMPER_BELOW = 2
function SpireGear.temper(item)
	local s = SpireGear.state(item)
	if not s or s.shop or s.tier >= SpireGearData.MAX_TIER or s.tier >= SpireGear.TEMPER_BELOW then
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
	elseif item and SpireGear.state(item) and SpireGear.state(item).tier >= SpireGear.TEMPER_BELOW then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, item:getName() .. " is already past raw steel (tier 2 or more): the field temper adds nothing to it.")
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Bring your Floor 1 weapon next time and it will be tempered.")
	end
end

-- Give every credited fighter its boss reward (public and private kills alike). A fighter who died during the fight
-- (or logged out) is not in the game at the kill: the reward waits and arrives when they next log in (2026-11-26: two
-- test characters who fell before the Axe-Lord died lost their awakening).
local PENDING = "spirebound-boss-pending"

function SpireGear.grantBoss(boss, creditNames)
	if not SpireGear.BOSS_REWARDS[boss] then
		return
	end
	for _, name in ipairs(creditNames) do
		local p = Player(name)
		if p then
			SpireGear.giveBossReward(p, boss)
		else
			local waiting = kv.scoped(PENDING):get(name)
			kv.scoped(PENDING):set(name, (waiting and (waiting .. ";") or "") .. boss)
		end
	end
end

function SpireGear.collectPending(p)
	local waiting = kv.scoped(PENDING):get(p:getName())
	if not waiting then
		return
	end
	kv.scoped(PENDING):remove(p:getName())
	for boss in tostring(waiting):gmatch("[^;]+") do
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You fell before the " .. boss .. " did, but your party finished the fight: your share is here.")
		SpireGear.giveBossReward(p, boss)
	end
end

function SpireGear.giveBossReward(p, boss)
	do
		do
			local k = p:kv():scoped("spirebound")
			local flag = "boss_credit_" .. boss
			local plan = SpireGear.bossReward(boss, k:get(flag) ~= nil)
			k:set(flag, os.time())
			if boss == "Gate Hound" and SpireStairKey then
				SpireStairKey.update(p) -- one piece of the Stair Key
			end
			if plan.shards > 0 then
				SpireGive.reward(p, SpireGearData.tokens[plan.floor][plan.grade], plan.shards)
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

-- ---------------------------------------------------------------- secret gear (adventure layer 4.1)
-- A ring, an amulet or boots that only a secret gives (SpireGearData.secretGear, tools/gen_gear.py). Given to its
-- finder at first, then trades, drops, stores and sells like other gear (Jay, Q100). Bonuses work while worn.
local A_SECRET = "sb_secret"
SpireGear.SECRET_SLOTS = { feet = CONST_SLOT_FEET, necklace = CONST_SLOT_NECKLACE, ring = CONST_SLOT_RING }

function SpireGear.secretDef(id)
	for _, g in ipairs(SpireGearData.secretGear or {}) do
		if g.id == id then
			return g
		end
	end
end

function SpireGear.secretOf(item)
	if not item or not item.getCustomAttribute then
		return nil
	end
	local id = item:getCustomAttribute(A_SECRET)
	return id and SpireGear.secretDef(id) or nil
end

-- true if the item is secret gear or holds some (a bag with the boots in it)
function SpireGear.holdsSecret(item)
	if SpireGear.secretOf(item) then
		return true
	end
	if item and item.isContainer and item:isContainer() then
		for _, inner in ipairs(item:getItems(true) or {}) do
			if SpireGear.secretOf(inner) then
				return true
			end
		end
	end
	return false
end

function SpireGear.makeSecret(g)
	local item = Game.createItem(g.base, 1)
	if not item then
		return nil
	end
	item:setCustomAttribute(A_SECRET, g.id)
	item:setAttribute(ITEM_ATTRIBUTE_NAME, g.name)
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, SpireGear.secretText(g))
	return item
end

-- Jay, 2026-11-27 (Q100): "secret gear can be traded." Only a secret makes one, but once found it is ordinary gear.
function SpireGear.secretText(g)
	return "Secret: " .. g.text .. " while worn. Only a hidden secret gives this."
end

-- Once per character. Returns true when given (or already owned).
function SpireGear.giveSecretGear(player, id)
	local g = SpireGear.secretDef(id)
	if not g then
		return false
	end
	local k = player:kv():scoped("spirebound-secret-gear")
	if k:get(id) then
		return true
	end
	local item = SpireGear.makeSecret(g)
	if not item then
		return false
	end
	local slot = SpireGear.SECRET_SLOTS[g.slot]
	local ok = (slot and not player:getSlotItem(slot) and player:addItemEx(item, false, slot, FLAG_NOLIMIT) == RETURNVALUE_NOERROR)
		or player:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR
	if not ok then
		local inbox = player.getStoreInbox and player:getStoreInbox()
		ok = inbox and inbox:addItemEx(item, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR
	end
	if not ok then
		item:remove()
		return false
	end
	k:set(id, os.time())
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You found %s! %s while worn. Only a secret gives this; keep it, trade it or sell it.", g.name, g.text))
	player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW or CONST_ME_GIFT_WRAPS)
	SpireGear.applySecret(player)
	return true
end

-- Pure: totals of worn secret gear rows
function SpireGear.secretTotals(rows)
	local t = { speed = 0, health = 0, mana = 0, skill = 0 }
	for _, g in ipairs(rows) do
		for k in pairs(t) do
			t[k] = t[k] + (g[k] or 0)
		end
	end
	return t
end

local SECRET_SUBID = 4610
local secretSpeed = {}
SpireCleanup.add(function(pid) secretSpeed[pid] = nil end)

function SpireGear.wornSecrets(player)
	local out = {}
	for _, slot in pairs(SpireGear.SECRET_SLOTS) do
		local g = SpireGear.secretOf(player:getSlotItem(slot))
		if g and SpireGear.SECRET_SLOTS[g.slot] == slot then
			table.insert(out, g)
		end
	end
	return out
end

function SpireGear.applySecret(player)
	local t = SpireGear.secretTotals(SpireGear.wornSecrets(player))
	player:removeCondition(CONDITION_ATTRIBUTES, CONDITIONID_DEFAULT, SECRET_SUBID)
	if t.health > 0 or t.mana > 0 or t.skill > 0 then
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, SECRET_SUBID)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		if t.health > 0 then
			c:setParameter(CONDITION_PARAM_STAT_MAXHITPOINTSPERCENT, 100 + math.floor(t.health * 100 + 0.5))
		end
		if t.mana > 0 then
			c:setParameter(CONDITION_PARAM_STAT_MAXMANAPOINTSPERCENT, 100 + math.floor(t.mana * 100 + 0.5))
		end
		if t.skill > 0 then
			local voc = player:getVocation():getBaseId()
			if voc == 3 then
				c:setParameter(CONDITION_PARAM_SKILL_DISTANCE, t.skill)
			elseif voc == 4 then
				c:setParameter(CONDITION_PARAM_SKILL_MELEE, t.skill) -- sword, axe and club
			else
				c:setParameter(CONDITION_PARAM_STAT_MAGICPOINTS, t.skill)
			end
		end
		player:addCondition(c)
	end
	local pid = player:getId()
	local had = secretSpeed[pid] or 0
	if t.speed ~= had then
		player:changeSpeed(t.speed - had)
		secretSpeed[pid] = t.speed
	end
	return t
end
