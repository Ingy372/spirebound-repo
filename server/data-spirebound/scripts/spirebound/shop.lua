-- !shop: the donation shop. Closed until launch (SpireShop.ENABLED). Owner command /shopgrant <name>, <coins> for testing.
local function findHouse(name)
	for _, h in ipairs(Game.getHouses()) do
		if h:getName() == name then
			return h
		end
	end
end

function SpireShop.giveStarterSet(player)
	local set = SpireGearData.shop[player:getVocation():getBaseId()]
	if not set then
		return false
	end
	SpireGear.make(player, set.weapon.id)
	SpireGear.make(player, set.armour.id)
	return true
end

local function deliver(player, e)
	if e.kind == "house" then
		local h = findHouse(e.house)
		h:setHouseOwner(player:getGuid())
		return
	end
	if e.kind == "gear" then
		SpireShop.giveStarterSet(player)
	elseif e.kind == "outfit" then
		player:addOutfitAddon(e.lookType, 3)
	elseif e.kind == "mount" then
		player:addMount(e.mount)
	else
		SpireGive.reward(player, e.item, 1) -- never onto the floor
	end
end

local login = CreatureEvent("SpireShopLogin")
function login.onLogin(player)
	if SpireShop.ENABLED then
		-- outfits and mounts bought on any character follow the account
		local owned = SpireShop.owned(player)
		for _, e in ipairs(SpireShop.catalog) do
			if owned:get(e.id) and e.kind == "outfit" then
				player:addOutfitAddon(e.lookType, 3)
			elseif owned:get(e.id) and e.kind == "mount" then
				player:addMount(e.mount)
			end
		end
		-- review S-1: furniture and decorations bought in an earlier season come back to the season's first character
		local bought, deliveredSeason = SpireShop.bought(player)
		local back = SpireShop.toRedeliver(bought, deliveredSeason, SpireSeason.current())
		if #back > 0 then
			local inbox = player:getStoreInbox()
			local names = {}
			for _, r in ipairs(back) do
				for _ = 1, r.count do
					local it = Game.createItem(r.entry.item, 1)
					if it and not (inbox and inbox:addItemEx(it, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR) then
						SpireGive.reward(player, r.entry.item, 1)
					end
				end
				table.insert(names, r.count .. "x " .. r.entry.name)
			end
			SpireShop.markDelivered(player)
			logger.info("[Spirebound] shop: {} got last season's items back ({})", player:getName(), table.concat(names, ", "))
			addEvent(function(pid)
				local p = Player(pid)
				if p then
					p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "A new season: the shop items your account owns are back in your Store Inbox ("
						.. table.concat(names, ", ") .. ").")
				end
			end, 3000, player:getId())
		end
	end
	return true
end
login:register()

local cmd = TalkAction("!shop")
function cmd.onSay(player, words, param)
	if not SpireShop.ENABLED then
		player:sendTextMessage(MESSAGE_STATUS, "The shop opens when Spirebound launches. It sells cosmetics and house decorations only: never power.")
		return false
	end
	local buy = param:lower():match("^buy%s+(%S+)$")
	if buy then
		local e = SpireShop.get(buy)
		local coins = SpireShop.coinsOf(player)
		local ok, why = SpireShop.canBuy(coins, e)
		if ok and e.kind == "house" then
			local h = findHouse(e.house)
			if not h then
				ok, why = false, "That house is not on this map."
			else
				ok, why = SpireShop.houseAvailable(h:getOwnerGuid(), player:getHouse() ~= nil, player:getAccountId(),
					SpireShop.manorLast(), SpireSeason.current(), kv.scoped("spirebound-season"):get("startedAt") or 0, os.time())
			end
		end
		if not ok then
			player:sendCancelMessage(why)
			return false
		end
		SpireShop.setCoins(player, coins - e.price)
		deliver(player, e)
		SpireSave.now("shop purchase") -- R8: a bought item is never lost to a crash
		if e.kind == "outfit" or e.kind == "mount" then
			SpireShop.owned(player):set(e.id, os.time())
		elseif SpireShop.REDELIVER[e.kind] then
			SpireShop.noteBought(player, e.id) -- review S-1: it comes back next season
		elseif e.kind == "house" then
			SpireShop.setManorLast(player:getAccountId())
		end
		logger.info("[Spirebound] shop: {} bought {} for {}", player:getName(), e.id, e.price)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You bought " .. e.name .. ".")
		return false
	end
	local lines = { SpireShop.CURRENCY .. ": " .. SpireShop.coinsOf(player), "Say !shop buy <name> to buy.", "" }
	for _, e in ipairs(SpireShop.catalog) do
		table.insert(lines, SpireShop.line(e))
	end
	player:showTextDialog(2821, table.concat(lines, "\n"))
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()

local grant = TalkAction("/shopgrant")
function grant.onSay(player, words, param)
	local name, n = param:match("^(.-)%s*,%s*(%d+)$")
	local target = name and Player(name)
	if not target then
		player:sendCancelMessage("/shopgrant <online player>, <coins>")
		return false
	end
	SpireShop.setCoins(target, SpireShop.coinsOf(target) + tonumber(n))
	player:sendTextMessage(MESSAGE_ADMINISTRATOR, "Gave " .. n .. " " .. SpireShop.CURRENCY .. " to " .. target:getName() .. ".")
	return false
end
grant:separator(" ")
grant:groupType("god")
grant:register()

-- GM testing while the shop is closed: /givegear <online player>, shop|respec
local give = TalkAction("/givegear")
function give.onSay(player, words, param)
	local name, what = param:match("^(.-)%s*,%s*(%a+)$")
	local target = name and Player(name)
	if not target or (what ~= "shop" and what ~= "respec") then
		player:sendCancelMessage("/givegear <online player>, shop|respec")
		return false
	end
	if what == "shop" then
		SpireShop.giveStarterSet(target)
	else
		target:addItem(SpireShop.RESPEC_ITEM, 1)
	end
	player:sendTextMessage(MESSAGE_ADMINISTRATOR, "Gave " .. what .. " gear to " .. target:getName() .. ".")
	return false
end
give:separator(" ")
give:groupType("god")
give:register()

-- Using the Mastery Respec Scroll
local scroll = Action()
function scroll.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local ok, msg = SpireStyle.respec(player, os.time())
	player:sendTextMessage(ok and MESSAGE_EVENT_ADVANCE or MESSAGE_STATUS, msg)
	if ok then
		item:remove(1)
		player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	end
	return true
end
scroll:id(SpireShop.RESPEC_ITEM)
scroll:register()
