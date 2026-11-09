-- House fixtures (DESIGN.md 7.5, roadmap 3.5):
--   !trophies           inside any house: the owner's Trophy Hall (bosses beaten, first date, kills)
--   !mannequin save|wear <1-3>   inside your house: store or put on an outfit (outfit, colours, addons, mount)
--   !pond               inside a house: the fish collection; !pond stock (owner) adds every fish kind you've caught
--   !pond bait          owner, once a day: worms bred by the pond
--   !warroom            inside a house owned by a guildmate: your guild's active wars
-- Workshop bench and garden: waiting for crafting/cooking (not in the game yet; noted in DESIGN.md).

local function houseHere(player)
	local tile = Tile(player:getPosition())
	return tile and tile:getHouse()
end

local function ownerKv(house)
	return kv.scoped("player"):scoped(tostring(house:getOwnerGuid()))
end

local function isOwner(player, house)
	return house:getOwnerGuid() == player:getGuid()
end

local trophies = TalkAction("!trophies")
function trophies.onSay(player, words, param)
	local house = houseHere(player)
	if not house or house:getOwnerGuid() == 0 then
		player:sendCancelMessage("Stand inside a house to see its Trophy Hall.")
		return false
	end
	local lines = SpireHouses.trophyLines(SpireHouses.trophiesOf(house:getOwnerGuid()))
	player:showTextDialog(2821, "Trophy Hall of " .. house:getName() .. "\n\n" .. (#lines > 0 and table.concat(lines, "\n") or "No bosses beaten yet."))
	return false
end
trophies:separator(" ")
trophies:groupType("normal")
trophies:register()

function SpireHouses.trophiesOf(guid)
	local store = kv.scoped("player"):scoped(tostring(guid)):scoped("spirebound-trophies")
	local out = {}
	for _, boss in ipairs(store:keys() or {}) do
		out[boss] = store:get(boss)
	end
	return out
end

local mannequin = TalkAction("!mannequin")
function mannequin.onSay(player, words, param)
	local house = houseHere(player)
	if not house or not isOwner(player, house) then
		player:sendCancelMessage("Mannequins stand in your own house.")
		return false
	end
	local action, slot = param:lower():match("(%a+)%s*(%d*)")
	slot = tonumber(slot) or 1
	if slot < 1 or slot > SpireHouses.MANNEQUIN_SLOTS then
		player:sendCancelMessage("Mannequins 1 to " .. SpireHouses.MANNEQUIN_SLOTS .. ".")
		return false
	end
	local store = player:kv():scoped("spirebound-mannequins")
	if action == "save" then
		local o = player:getOutfit()
		store:set(tostring(slot), { lookType = o.lookType, lookHead = o.lookHead, lookBody = o.lookBody, lookLegs = o.lookLegs,
			lookFeet = o.lookFeet, lookAddons = o.lookAddons, lookMount = o.lookMount or 0 })
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Mannequin " .. slot .. " now wears your outfit.")
	elseif action == "wear" then
		local o = store:get(tostring(slot))
		if not o then
			player:sendCancelMessage("Mannequin " .. slot .. " is bare.")
			return false
		end
		if not player:hasOutfit(o.lookType, o.lookAddons) then
			player:sendCancelMessage("You no longer have that outfit.")
			return false
		end
		player:setOutfit(o)
		player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "!mannequin save <1-3> stores your outfit, !mannequin wear <1-3> puts it on.")
	end
	return false
end
mannequin:separator(" ")
mannequin:groupType("normal")
mannequin:register()

local pond = TalkAction("!pond")
function pond.onSay(player, words, param)
	local house = houseHere(player)
	if not house or house:getOwnerGuid() == 0 then
		player:sendCancelMessage("Stand inside a house to see its pond.")
		return false
	end
	local store = ownerKv(house):scoped("spirebound-pond")
	local stocked = store:get("fish") or {}
	local p = param:lower()
	if p == "stock" then
		if not isOwner(player, house) then
			player:sendCancelMessage("Only the owner stocks the pond.")
			return false
		end
		local log = SpireFishing.log(player)
		local added = 0
		for _, floorTable in pairs(SpireFishing.tables) do
			for _, f in ipairs(floorTable) do
				if not f.junk and not f.treasure and (log:get(f.id) or { count = 0 }).count > 0 and not stocked[f.id] then
					stocked[f.id] = f.name
					added = added + 1
				end
			end
		end
		store:set("fish", stocked)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, added > 0 and ("You released " .. added .. " new kinds of fish into your pond.") or "Your pond already has every kind you've caught.")
	elseif p == "bait" then
		if not isOwner(player, house) then
			player:sendCancelMessage("Only the owner collects bait.")
			return false
		end
		local kinds = 0
		for _ in pairs(stocked) do
			kinds = kinds + 1
		end
		local today = math.floor(os.time() / 86400)
		local n = SpireHouses.pondBait(kinds, store:get("baitDay"), today)
		if n == 0 then
			player:sendCancelMessage("The pond has no more bait today.")
			return false
		end
		store:set("baitDay", today)
		player:addItem(SpireFishing.WORM, n)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You collect " .. n .. " worms from the pond's edge.")
	else
		local names = {}
		for _, name in pairs(stocked) do
			table.insert(names, name)
		end
		table.sort(names)
		player:showTextDialog(2821, "The pond of " .. house:getName() .. "\n\n" .. (#names > 0 and table.concat(names, "\n") or "Empty. The owner can '!pond stock' every fish kind they've caught.")
			.. "\n\nOwner: '!pond bait' once a day for worms.")
	end
	return false
end
pond:separator(" ")
pond:groupType("normal")
pond:register()

local warroom = TalkAction("!warroom")
function warroom.onSay(player, words, param)
	local house = houseHere(player)
	local guild = player:getGuild()
	if not guild then
		player:sendCancelMessage("You are not in a guild.")
		return false
	end
	local ownerGuild = 0
	if house and house:getOwnerGuid() > 0 then
		local g = db.storeQuery("SELECT `guild_id` FROM `guild_membership` WHERE `player_id` = " .. house:getOwnerGuid())
		if g then
			ownerGuild = Result.getNumber(g, "guild_id")
			Result.free(g)
		end
	end
	if ownerGuild ~= guild:getId() then
		player:sendCancelMessage("The war board hangs in your guild's houses (a house owned by a guildmate).")
		return false
	end
	local lines = {}
	local q = db.storeQuery("SELECT `name1`, `name2`, `status`, `started`, `ended` FROM `guild_wars` WHERE (`guild1` = " .. guild:getId() .. " OR `guild2` = " .. guild:getId() .. ") AND `status` IN (0, 1) ORDER BY `started` DESC LIMIT 20")
	if q then
		repeat
			local status = Result.getNumber(q, "status") == 1 and "at war" or "declared, waiting for an answer"
			table.insert(lines, string.format("%s vs %s - %s", Result.getString(q, "name1"), Result.getString(q, "name2"), status))
		until not Result.next(q)
		Result.free(q)
	end
	player:showTextDialog(2821, "War Room of " .. guild:getName() .. "\n\n" .. (#lines > 0 and table.concat(lines, "\n") or "No wars. Guildwarden Sela in Hearthgate handles declarations."))
	return false
end
warroom:separator(" ")
warroom:groupType("normal")
warroom:register()
