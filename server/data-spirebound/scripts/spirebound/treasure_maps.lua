-- Treasure maps in the game (roadmap AD5). Rules: lib/spirebound/treasure_maps.lua; numbers: tools/gen_adventure.py.
local D = SpireAdventureData
local T = SpireTreasure

local function spotOf(item)
	local key = item:getCustomAttribute("dig")
	return key and T.byKey[key] or nil, key
end

-- Give a map its spot (the first time it is read): fixed from then on, and written on the map for whoever holds it
local function assign(item)
	local s = T.spots[math.random(#T.spots)]
	item:setCustomAttribute("dig", s.key)
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "The map reads: \"" .. s.clue .. "\"")
	return s
end

local readMap = Action()
function readMap.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if #T.spots == 0 then
		player:sendCancelMessage("The map is too faded to read.")
		return true
	end
	local s, key = spotOf(item)
	if not s then
		if key then -- (the map changed and this spot is gone): give it a new one
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The old marks have washed out, but new ones show through.")
		end
		s = assign(item)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You smooth out the tattered map. " .. s.clue
			.. " (Use the map again once you are in " .. SpireRoamers.groundTitle(s.gid) .. ": it tells you how close you are.)")
		return true
	end
	local here = player:getPosition()
	if SpireRoamers.groundAt(here) == s.gid and here.z == s.pos.z then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, T.hint(s.pos.x - here.x, s.pos.y - here.y))
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The map reads: \"" .. s.clue .. "\"")
	end
	return true
end
readMap:id(D.mapItem)
readMap:register()

local function findMap(player, key)
	local bag = player:getSlotItem(CONST_SLOT_BACKPACK)
	local function scan(c)
		for i = 0, c:getSize() - 1 do
			local it = c:getItem(i)
			if it then
				if it:getId() == D.mapItem and it:getCustomAttribute("dig") == key then
					return it
				end
				if it:isContainer() then
					local f = scan(it)
					if f then return f end
				end
			end
		end
	end
	for slot = CONST_SLOT_FIRST, CONST_SLOT_LAST do
		local it = player:getSlotItem(slot)
		if it and it:getId() == D.mapItem and it:getCustomAttribute("dig") == key then
			return it
		end
	end
	return bag and bag:isContainer() and scan(bag) or nil
end

-- The dig. Returns what came up, for the tests: { gold, shards, ember, keepsake, guards }
function T.dig(player, s, rolls)
	rolls = rolls or {}
	local r = function(k) return rolls[k] or math.random() end
	local out = { gold = T.gold(s.gid, r("gold")), shards = 0, guards = 0 }
	local pos = s.pos
	pos:sendMagicEffect(CONST_ME_POFF)
	player:setBankBalance(player:getBankBalance() + out.gold)
	local parts = { string.format("%d gold (paid into your bank)", out.gold) }
	if r("shard") < D.digShardChance then
		out.shards = r("shards") < 0.5 and 1 or 2
		SpireGive.reward(player, D.cut, out.shards)
		table.insert(parts, string.format("%d cut Hearth Shard%s", out.shards, out.shards == 1 and "" or "s"))
	end
	if r("ember") < D.digEmber then
		out.ember = true
		SpireGive.reward(player, D.ember, 1)
		table.insert(parts, "a Beacon Ember")
	end
	local k = player:kv():scoped("spirebound-treasure")
	local since = (k:get("since") or 0) + 1
	if SpireGear.shardRoll(D.keepsakeChance, since, r("keepsake")) then
		local i = T.pickKeepsake(T.keepsakes(player), function(n) return math.random(n) end)
		local ks = D.treasureKeepsakes[i]
		out.keepsake = ks.id
		k:set("since", 0)
		k:set("keepsake_" .. ks.id, os.time())
		SpireGive.reward(player, ks.item, 1)
		table.insert(parts, "and a keepsake: " .. ks.name .. "!")
		pos:sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
		if SpireFinds and SpireFinds.announce then
			SpireFinds.announce("keepsake", { player }, ks.name, SpireRoamers.groundTitle(s.gid))
		else
			Game.broadcastMessage(string.format("%s dug up %s!", player:getName(), ks.name), MESSAGE_EVENT_ADVANCE)
		end
		if SpireDiscoveries and SpireDiscoveries.mark then
			SpireDiscoveries.mark(player, "keepsake", ks.id)
		end
	else
		k:set("since", since)
	end
	local dug = T.dug(player) + 1
	k:set("dug", dug)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You dig up a buried stash: " .. table.concat(parts, ", ") .. ".")
	if dug == D.digTitle[1] then
		player:kv():scoped("spirebound-titles"):set(D.digTitle[2], os.time())
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%d treasure maps dug: you earned the title %s.", dug, D.digTitle[2]))
	end
	if r("guards") < D.digGuardChance then
		local n = r("count") < 0.5 and 2 or 3
		local name = D.digs[s.gid].guard
		for i = 1, n do
			local m = Game.createMonster(name, pos, true, false)
			if m then
				out.guards = out.guards + 1
				m:getPosition():sendMagicEffect(CONST_ME_GROUNDSHAKER)
			end
		end
		if out.guards > 0 then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The stash had guards! Something climbs out of the hole.")
		end
	end
	return out
end

-- The shovel: on a dig spot with the matching map, dig; anywhere else, the ordinary shovel
local function wrapShovel()
	if T.wrapped or not onUseShovel then
		return
	end
	T.wrapped = true
	local plain = onUseShovel
	onUseShovel = function(player, item, fromPosition, target, toPosition, isHotkey)
		local pos = toPosition
		if type(pos) == "table" or type(pos) == "userdata" then
			local s = pos.x and T.spotAt(Position(pos.x, pos.y, pos.z))
			if s then
				local map = findMap(player, s.key)
				if map then
					map:remove(1)
					T.dig(player, s)
					return true
				end
				-- a dig spot, but no map for it: nothing to find (and say so, or it looks broken)
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You dig a little, but find only roots and stones.")
				Position(pos.x, pos.y, pos.z):sendMagicEffect(CONST_ME_POFF)
				return true
			end
		end
		return plain(player, item, fromPosition, target, toPosition, isHotkey)
	end
end

local startup = GlobalEvent("SpireTreasureStartup")
function startup.onStartup()
	local n = T.place()
	logger.info("[Spirebound] treasure maps: {} dig spots placed", n)
	wrapShovel()
	if SpireDiscoveries and SpireDiscoveries.register then
		for _, k in ipairs(D.treasureKeepsakes) do
			SpireDiscoveries.register("keepsake", k.id, k.name, 1)
		end
	end
	return true
end
startup:register()

-- GM: /treasure map | /treasure spots | /treasure goto <n>
local gm = TalkAction("/treasure")
function gm.onSay(player, words, param)
	local cmd, n = param:match("^%s*(%a*)%s*(%d*)")
	if cmd == "map" then
		player:addItem(D.mapItem, 1)
	elseif cmd == "goto" and tonumber(n) and T.spots[tonumber(n)] then
		player:teleportTo(T.spots[tonumber(n)].pos)
	else
		local lines = {}
		for i, s in ipairs(T.spots) do
			table.insert(lines, string.format("%d %s %s: %s", i, s.key, s.pos:toString(), s.clue))
		end
		player:showTextDialog(D.mapItem, #lines > 0 and table.concat(lines, "\n") or "No dig spots placed.")
	end
	return false
end
gm:separator(" ")
gm:groupType("god")
gm:register()
