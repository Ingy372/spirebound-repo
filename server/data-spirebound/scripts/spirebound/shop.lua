-- !shop: the donation shop. Closed until launch (SpireShop.ENABLED). Owner command /shopgrant <name>, <coins> for testing.
local function deliver(player, e)
	if e.kind == "outfit" then
		player:addOutfitAddon(e.lookType, 3)
	elseif e.kind == "mount" then
		player:addMount(e.mount)
	else
		player:addItem(e.item, 1)
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
		if not ok then
			player:sendCancelMessage(why)
			return false
		end
		SpireShop.setCoins(player, coins - e.price)
		deliver(player, e)
		if e.kind == "outfit" or e.kind == "mount" then
			SpireShop.owned(player):set(e.id, os.time())
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
