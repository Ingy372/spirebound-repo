-- Cooking on the hub fires (roadmap FD4; docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.4).
-- No bench, no window, no recipe list: use a raw ingredient on a fire and it cooks; use a second ingredient on a cooked
-- dish while you stand at the fire and it becomes a combined dish, if that pair is a recipe. Eating a dish feeds you and
-- gives one small, slow comfort out of a fight (never damage, defence, experience or loot). One dish at a time.
-- A combined dish used on a fire is set down as a feast: the cook's party eat from it and the comfort lasts twice as long.
-- The first time a character makes a dish it goes in their Cookbook (a row group on the Discoveries page).
-- Numbers: tools/gen_depth.py (depth_data.lua). The game side: scripts/spirebound/cooking.lua and the foods override.
SpireCooking = SpireCooking or { active = {} }

local C = SpireDepthData.cooking
SpireCooking.byId, SpireCooking.byItem, SpireCooking.byRaw, SpireCooking.byPair = {}, {}, {}, {}
for _, d in ipairs(C.dishes) do
	SpireCooking.byId[d.id] = d
	SpireCooking.byItem[d.item] = d
	if d.raw then
		SpireCooking.byRaw[d.raw] = d
	end
end
for _, d in ipairs(C.dishes) do
	if d.base then
		SpireCooking.byPair[d.base .. ":" .. d.add] = d
	end
end
SpireCooking.FIRE = {}
for _, id in ipairs(C.fires) do
	SpireCooking.FIRE[id] = true
end

-- ---------------------------------------------------------------- pure
function SpireCooking.isIngredient(itemId)
	return C.ingredients[itemId] ~= nil
end

function SpireCooking.isDish(itemId)
	return SpireCooking.byItem[itemId] ~= nil
end

-- Pure: what does using `itemId` on a fire make? -> dish or nil, reason
function SpireCooking.cookResult(itemId)
	local d = SpireCooking.byRaw[itemId]
	if d then
		return d
	end
	if C.ingredients[itemId] then
		return nil, "alone"
	end
	return nil, "not_food"
end

-- Pure: using ingredient `addId` on the dish `dishItemId` -> combined dish or nil
function SpireCooking.combineResult(dishItemId, addId)
	local base = SpireCooking.byItem[dishItemId]
	if not base then
		return nil
	end
	return SpireCooking.byPair[base.id .. ":" .. addId]
end

-- Pure: seconds a dish lasts, alone or from a feast
function SpireCooking.duration(d, feast)
	return math.floor(d.minutes * 60 * (feast and C.feastMult or 1))
end

-- Pure: the titles reached with `n` of `total` dishes found
function SpireCooking.titlesFor(n, total)
	local out = {}
	for _, t in ipairs(C.titles) do
		if (t[1] and n >= t[1]) or (not t[1] and n >= total) then
			table.insert(out, t[2])
		end
	end
	return out
end

-- Pure: one line about a comfort, for the eat message and !dish
function SpireCooking.comfortLine(d)
	local c = d.comfort
	if c == "regen" then
		return string.format("you heal %d health every %d seconds out of a fight", d.amount, C.tick)
	elseif c == "mana" then
		return string.format("you regain %d mana every %d seconds out of a fight", d.amount, C.tick)
	elseif c == "cap" then
		return string.format("you can carry %d oz more", d.amount)
	elseif c == "light" then
		return "a warm light goes with you"
	elseif c == "townspeed" then
		return "you walk faster in town and other safe places"
	end
	return c
end

-- Pure: a fire item id?
function SpireCooking.isFireId(id)
	return SpireCooking.FIRE[id] == true
end

-- A fire on this tile, or next to `pos` within the reach (returns its position)
function SpireCooking.fireAt(pos)
	local tile = pos and Tile(pos)
	if not tile then
		return nil
	end
	local g = tile:getGround()
	if g and SpireCooking.FIRE[g:getId()] then
		return pos
	end
	for _, it in ipairs(tile:getItems() or {}) do
		if SpireCooking.FIRE[it:getId()] then
			return pos
		end
	end
	return nil
end

function SpireCooking.fireNear(pos, reach)
	reach = reach or C.reach
	for dx = -reach, reach do
		for dy = -reach, reach do
			local p = Position(pos.x + dx, pos.y + dy, pos.z)
			if SpireCooking.fireAt(p) then
				return p
			end
		end
	end
	return nil
end

-- ---------------------------------------------------------------- the Cookbook
local function book(player)
	return player:kv():scoped("spirebound-cookbook")
end

function SpireCooking.knows(player, id)
	return book(player):get(id) ~= nil
end

function SpireCooking.count(player)
	local n = 0
	for _, d in ipairs(C.dishes) do
		if SpireCooking.knows(player, d.id) then
			n = n + 1
		end
	end
	return n
end

-- First time this character made the dish: the Cookbook row, the titles. Returns true the first time.
function SpireCooking.learn(player, d)
	if SpireCooking.knows(player, d.id) then
		return false
	end
	book(player):set(d.id, os.time())
	if SpireDiscoveries then
		SpireDiscoveries.mark(player, "cookbook", d.id)
	end
	local n = SpireCooking.count(player)
	for _, title in ipairs(SpireCooking.titlesFor(n, #C.dishes)) do
		local titles = player:kv():scoped("spirebound-titles")
		if not titles:get(title) then
			titles:set(title, os.time())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. title .. ".")
		end
	end
	return true
end

-- ---------------------------------------------------------------- cooking (drop things on a fire)
-- Food in the client is "use", never "use with", so cooking is done the old Tibia way: drop the ingredient on the fire.
local function dishOnTile(tile, wantId)
	for _, it in ipairs(tile:getItems() or {}) do
		if it:getId() == wantId and not it:getCustomAttribute("feast_owner") then
			return it
		end
	end
end

-- A combined dish this ingredient makes with a dish already lying on the fire's tile
local function combinePartner(tile, addId)
	for _, it in ipairs(tile:getItems() or {}) do
		local base = SpireCooking.byItem[it:getId()]
		if base and not it:getCustomAttribute("feast_owner") then
			local d = SpireCooking.byPair[base.id .. ":" .. addId]
			if d then
				return it, d
			end
		end
	end
end

local function praise(player, d, n, first, combined)
	local what = n > 1 and (n .. " " .. d.name .. (d.name:sub(-1) == "s" and "" or "s")) or ((d.name:match("^[AEIOU]") and "an " or "a ") .. d.name)
	local tail = combined and " Use it while it lies on the fire to set it out as a feast for your party, or pick it up to eat later."
		or " Pick it up and eat it, or drop a second ingredient on it while it is on the fire."
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You cook %s.%s%s", what,
		first and " It is new in your Cookbook!" or "", tail))
end

-- A player dropped `item` (any count) at `pos`. Returns true when it cooked (or explained why not).
function SpireCooking.onDrop(player, item, pos)
	if not item or not pos or pos.x == CONTAINER_POSITION then
		return false
	end
	local id = item:getId()
	if not SpireCooking.isIngredient(id) then
		return false
	end
	local fire = SpireCooking.fireAt(pos)
	if not fire then
		return false
	end
	local tile = Tile(fire)
	-- the item the engine hands over can be the stack left behind in the backpack (a part of a stack was dropped):
	-- cook what really lies on the fire
	local onFire
	for _, it in ipairs(tile:getItems() or {}) do
		if it:getId() == id then
			onFire = it
			break
		end
	end
	if not onFire then
		return false
	end
	item = onFire
	-- a second ingredient on a dish that lies on the fire: the combined dish
	local base, d = combinePartner(tile, id)
	if base then
		local n = math.min(item:getCount(), base:getCount())
		item:remove(n)
		base:remove(n)
		Game.createItem(d.item, n, fire)
		fire:sendMagicEffect(CONST_ME_HITBYFIRE)
		praise(player, d, n, SpireCooking.learn(player, d), true)
		return true
	end
	local cooked, why = SpireCooking.cookResult(id)
	if not cooked then
		if why == "alone" then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format(
				"The %s does not cook well on its own. Cook something on the fire first, then drop the %s on it.",
				ItemType(id):getName(), ItemType(id):getName()))
			return true
		end
		return false
	end
	local n = item:getCount()
	item:transform(cooked.item, n)
	fire:sendMagicEffect(CONST_ME_HITBYFIRE)
	praise(player, cooked, n, SpireCooking.learn(player, cooked), false)
	return true
end

-- ---------------------------------------------------------------- eating
local function store(player)
	return player:kv():scoped("spirebound-dish")
end

function SpireCooking.current(player)
	local a = SpireCooking.active[player:getId()]
	if a and a["until"] > os.time() then
		return a
	end
	return nil
end

local function dropCap(player, a)
	if a and a.cap and a.cap > 0 then
		player:setCapacity(math.max(0, player:getCapacity() - a.cap))
		a.cap = 0
	end
end

-- End the comfort (expired, or another dish eaten)
function SpireCooking.stop(player, silent)
	local a = SpireCooking.active[player:getId()]
	if a then
		dropCap(player, a)
		if a.comfort == "light" then
			player:removeCondition(CONDITION_LIGHT, CONDITIONID_DEFAULT, 72)
		end
		if a.comfort == "townspeed" then
			player:removeCondition(CONDITION_HASTE, CONDITIONID_DEFAULT, 72)
		end
	end
	SpireCooking.active[player:getId()] = nil
	store(player):remove("now")
	if a and not silent then
		player:sendTextMessage(MESSAGE_STATUS, "The comfort of your " .. (SpireCooking.byId[a.id] and SpireCooking.byId[a.id].name or "dish") .. " has worn off.")
	end
end

local function apply(player, d, untilT, capApplied)
	local a = { id = d.id, comfort = d.comfort, amount = d.amount, ["until"] = untilT, cap = capApplied or 0 }
	if d.comfort == "cap" and a.cap == 0 then
		local add = d.amount * 100 -- the engine counts capacity in hundredths of an oz
		player:setCapacity(player:getCapacity() + add)
		a.cap = add
	elseif d.comfort == "light" then
		local cond = Condition(CONDITION_LIGHT, CONDITIONID_DEFAULT)
		cond:setParameter(CONDITION_PARAM_SUBID, 72)
		cond:setParameter(CONDITION_PARAM_LIGHT_LEVEL, d.amount)
		cond:setParameter(CONDITION_PARAM_LIGHT_COLOR, 215)
		cond:setParameter(CONDITION_PARAM_TICKS, math.max(1, untilT - os.time()) * 1000)
		player:addCondition(cond)
	end
	SpireCooking.active[player:getId()] = a
	store(player):set("now", { id = d.id, ["until"] = untilT, cap = a.cap })
	return a
end

-- Eat a dish (alone or from a feast). The item is removed by the caller.
function SpireCooking.eat(player, d, feast)
	SpireCooking.stop(player, true)
	local secs = SpireCooking.duration(d, feast)
	apply(player, d, os.time() + secs)
	player:feed(d.food * 12)
	player:say(feast and "Mmm, a feast!" or "Mmm.", TALKTYPE_MONSTER_SAY)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You eat the %s%s: for %d minutes %s.", d.name,
		feast and " from the feast" or "", math.floor(secs / 60), SpireCooking.comfortLine(d)))
	return true
end

-- Login: bring back a comfort that has not run out (the capacity bonus is already in the saved capacity)
function SpireCooking.restore(player)
	local now = store(player):get("now")
	if not now then
		return
	end
	local d = SpireCooking.byId[now.id]
	if not d or now["until"] <= os.time() then
		if now.cap and now.cap > 0 then
			player:setCapacity(math.max(0, player:getCapacity() - now.cap))
		end
		store(player):remove("now")
		return
	end
	apply(player, d, now["until"], now.cap)
end

-- One comfort tick for a player (every C.tick seconds)
function SpireCooking.tick(player)
	local a = SpireCooking.active[player:getId()]
	if not a then
		return
	end
	if a["until"] <= os.time() then
		SpireCooking.stop(player)
		return
	end
	local fighting = player:hasCondition(CONDITION_INFIGHT)
	if a.comfort == "regen" and not fighting and player:getHealth() < player:getMaxHealth() then
		-- quietly (addHealth prints "You were healed" every tick)
		player:setHealth(math.min(player:getMaxHealth(), player:getHealth() + a.amount))
	elseif a.comfort == "mana" and not fighting and player:getMana() < player:getMaxMana() then
		player:addMana(a.amount) -- (the engine has no setMana; addMana says nothing)
	elseif a.comfort == "townspeed" then
		local tile = Tile(player:getPosition())
		if tile and tile:hasFlag(TILESTATE_PROTECTIONZONE) then
			local cond = Condition(CONDITION_HASTE, CONDITIONID_DEFAULT)
			cond:setParameter(CONDITION_PARAM_SUBID, 72)
			cond:setParameter(CONDITION_PARAM_TICKS, (C.tick + 1) * 1000)
			cond:setParameter(CONDITION_PARAM_SPEED, a.amount)
			player:addCondition(cond)
		end
	end
end

-- ---------------------------------------------------------------- feasts
-- Use a combined dish lying on a fire: it is laid out as a feast (four servings, ten minutes, for the cook's party)
function SpireCooking.setFeast(player, dishItem, firePos)
	local d = SpireCooking.byItem[dishItem:getId()]
	if not d then
		return false
	end
	if not d.base then
		return false -- a plain dish on a fire is simply eaten
	end
	if dishItem:getCount() > 1 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Lay out one dish at a time: pick the others up first.")
		return true
	end
	dishItem:setCustomAttribute("feast_owner", player:getGuid())
	dishItem:setCustomAttribute("feast_left", C.feastServings)
	dishItem:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, string.format("A feast laid out by %s for their party: %d servings.", player:getName(), C.feastServings))
	firePos:sendMagicEffect(CONST_ME_GIFT_WRAPS)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format(
		"You lay the %s out by the fire as a feast. You and your party can each eat from it (%d servings) for the next %d minutes, and it lasts twice as long as eating alone.",
		d.name, C.feastServings, C.feastMinutes))
	local pos = Position(firePos.x, firePos.y, firePos.z)
	local itemId, guid = d.item, player:getGuid()
	addEvent(function()
		local t = Tile(pos)
		for _, it in ipairs(t and t:getItems() or {}) do
			if it:getId() == itemId and it:getCustomAttribute("feast_owner") == guid then
				it:remove()
				pos:sendMagicEffect(CONST_ME_POFF)
				return
			end
		end
	end, C.feastMinutes * 60 * 1000)
	return true
end

-- Pure-ish: may this player eat from a feast set by `ownerGuid`?
function SpireCooking.mayEatFeast(player, ownerGuid)
	if player:getGuid() == ownerGuid then
		return true
	end
	local party = player:getParty()
	if not party then
		return false
	end
	local members = party:getMembers() or {}
	table.insert(members, party:getLeader())
	for _, m in ipairs(members) do
		if m and m:getGuid() == ownerGuid then
			return true
		end
	end
	return false
end

-- Use a feast lying by a fire. Returns true when handled.
function SpireCooking.eatFeast(player, item)
	local owner = item:getCustomAttribute("feast_owner")
	local d = SpireCooking.byItem[item:getId()]
	if not owner or not d then
		return false
	end
	if not SpireCooking.mayEatFeast(player, owner) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "This feast was set down for another party.")
		return true
	end
	local fedKey = "feast_fed_" .. player:getGuid()
	if item:getCustomAttribute(fedKey) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You have already had your share of this feast.")
		return true
	end
	SpireCooking.eat(player, d, true)
	item:setCustomAttribute(fedKey, 1)
	local left = (item:getCustomAttribute("feast_left") or 1) - 1
	if left <= 0 then
		item:getPosition():sendMagicEffect(CONST_ME_POFF)
		item:remove()
	else
		item:setCustomAttribute("feast_left", left)
		item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, string.format("A feast by the fire: %d servings left.", left))
	end
	return true
end

-- ---------------------------------------------------------------- using a dish (from the foods override)
-- Returns true when cooking handled this use; false lets the ordinary food script eat it.
function SpireCooking.onUse(player, item, fromPosition)
	local d = SpireCooking.byItem[item:getId()]
	if not d then
		return false
	end
	local onTile = fromPosition and fromPosition.x ~= CONTAINER_POSITION
	if onTile then
		if item:getCustomAttribute("feast_owner") then
			return SpireCooking.eatFeast(player, item)
		end
		local fire = SpireCooking.fireAt(Position(fromPosition.x, fromPosition.y, fromPosition.z))
		if fire and d.base and SpireCooking.setFeast(player, item, fire) then
			return true
		end
	end
	SpireCooking.eat(player, d, false)
	item:remove(1)
	return true
end
