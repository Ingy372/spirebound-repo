-- House commands (DESIGN.md 7.5). Plain chat commands so they work in any client:
--   !buyhouse                      (face a free house's doorway)        -- core override with the head-start rule
--   !portal set / !portal          set your house portal spot (3 times ever) / travel there from inside your house
--   !summon <boss name>            Summoning Circle: spend a Boss Sigil inside a house of 30+ tiles
--   !dice <amount> <high|low>      bet against the owner of a licensed Fortune Hall you're standing in
--   !fortune license               buy a Fortune Hall license for your house
--   !openhouse                     open your house to everyone for 2 hours

local function inOwnHouse(player)
	local tile = Tile(player:getPosition())
	local house = tile and tile:getHouse()
	if house and house:getOwnerGuid() == player:getGuid() then
		return house
	end
	return nil
end

local function nearBossRoom(pos)
	for name, p in pairs(WorldPoints) do
		if (name:find("^boss_room") or name == "pass_arena") and p.z == pos.z and pos:getDistance(p) <= SpireHouses.PORTAL_BOSS_DISTANCE then
			return true
		end
	end
	return false
end

-- !portal ----------------------------------------------------------------
local portal = TalkAction("!portal")
function portal.onSay(player, words, param)
	local s = player:kv():scoped("spirebound-house")
	if param:lower():find("set") then
		local used = s:get("portalChanges") or 0
		if SpireHouses.portalChangesLeft(used) <= 0 then
			player:sendCancelMessage("Your portal key is worn out. It can only be set " .. SpireHouses.PORTAL_CHANGES .. " times.")
			return false
		end
		local pos = player:getPosition()
		local tile = Tile(pos)
		local isSecret = SpireSecrets.byPos[pos.x .. ":" .. pos.y .. ":" .. pos.z] ~= nil
		local ok, why = SpireHouses.portalTargetAllowed(SpirePvP.zoneAt(pos), nearBossRoom(pos), isSecret, tile and tile:getHouse() ~= nil)
		if not ok then
			player:sendCancelMessage(why)
			return false
		end
		s:set("portalChanges", used + 1)
		s:set("portal", { x = pos.x, y = pos.y, z = pos.z })
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Portal set here. %d change(s) left, ever.", SpireHouses.portalChangesLeft(used + 1)))
		pos:sendMagicEffect(CONST_ME_TELEPORT)
		return false
	end
	if not inOwnHouse(player) then
		player:sendCancelMessage("Use the portal from inside your own house.")
		return false
	end
	local dest = s:get("portal")
	if not dest then
		player:sendCancelMessage("Set a destination first: stand there and say !portal set")
		return false
	end
	if player:isPzLocked() then
		player:sendCancelMessage("You can't use the portal right after a fight.")
		return false
	end
	local to = Position(dest.x, dest.y, dest.z)
	player:getPosition():sendMagicEffect(CONST_ME_TELEPORT)
	player:teleportTo(to)
	to:sendMagicEffect(CONST_ME_TELEPORT)
	return false
end
portal:separator(" ")
portal:groupType("normal")
portal:register()

-- !summon ----------------------------------------------------------------
local summon = TalkAction("!summon")
function summon.onSay(player, words, param)
	local house = inOwnHouse(player)
	if not house then
		player:sendCancelMessage("The Summoning Circle only works inside your own house.")
		return false
	end
	if #house:getTiles() < SpireHouses.SUMMON_MIN_SIZE then
		player:sendCancelMessage("Your house is too small for a Summoning Circle (" .. SpireHouses.SUMMON_MIN_SIZE .. " tiles needed).")
		return false
	end
	local name = param:gsub("^%s+", ""):gsub("%s+$", "")
	local def = nil
	for bossName, d in pairs(SpireBoss.defs) do
		if bossName:lower() == name:lower() then
			def, name = d, bossName
		end
	end
	if not def then
		player:sendCancelMessage("Say !summon followed by the name of a boss you hold a sigil for.")
		return false
	end
	local sigils = player:kv():scoped("spirebound-sigils")
	local have = sigils:get(name) or 0
	if have <= 0 then
		player:sendCancelMessage("You have no " .. name .. " sigil. Sigils come from defeating bosses.")
		return false
	end
	local m = Game.createMonster(name, player:getPosition(), true, true)
	if not m then
		player:sendCancelMessage("There isn't enough room here.")
		return false
	end
	-- a private copy: no first-clear credit (it never gets a fight record), normal loot
	sigils:set(name, have - 1)
	m:say("You summoned me? Foolish.", TALKTYPE_MONSTER_YELL)
	logger.info("[Spirebound] {} summoned {} in house {}", player:getName(), name, house:getName())
	return false
end
summon:separator(" ")
summon:groupType("normal")
summon:register()

-- !fortune license / !dice ------------------------------------------------
local fortune = TalkAction("!fortune")
function fortune.onSay(player, words, param)
	local house = inOwnHouse(player)
	if not house then
		player:sendCancelMessage("Stand in your own house to buy a Fortune Hall license.")
		return false
	end
	local key = "license_" .. house:getId()
	local hk = kv.scoped("spirebound-fortune")
	if hk:get(key) == player:getGuid() then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your house is already a Fortune Hall.")
		return false
	end
	if not player:removeMoneyBank(SpireHouses.LICENSE_COST) then
		player:sendCancelMessage("A Fortune Hall license costs " .. SpireHouses.LICENSE_COST .. " gold.")
		return false
	end
	hk:set(key, player:getGuid())
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your house is now a Fortune Hall. Players inside can bet with !dice <amount> high|low. Gold only; the hall keeps 5%.")
	return false
end
fortune:separator(" ")
fortune:groupType("normal")
fortune:register()

local dice = TalkAction("!dice")
function dice.onSay(player, words, param)
	local tile = Tile(player:getPosition())
	local house = tile and tile:getHouse()
	local ownerGuid = house and kv.scoped("spirebound-fortune"):get("license_" .. house:getId())
	if not house or not ownerGuid or ownerGuid ~= house:getOwnerGuid() then
		player:sendCancelMessage("You need to be inside a licensed Fortune Hall.")
		return false
	end
	local amount, call = param:lower():match("(%d+)%s+(%a+)")
	amount = tonumber(amount)
	if not amount or (call ~= "high" and call ~= "low") then
		player:sendCancelMessage("Say: !dice <amount> high   (4-6 wins)   or   !dice <amount> low   (1-3 wins)")
		return false
	end
	if amount < 100 or amount > SpireHouses.DICE_MAX_BET then
		player:sendCancelMessage("Bets are 100 to " .. SpireHouses.DICE_MAX_BET .. " gold.")
		return false
	end
	local host = Player(ownerGuid)
	if not host then
		player:sendCancelMessage("The hall's owner must be online to cover bets.")
		return false
	end
	if host == player then
		player:sendCancelMessage("You can't bet against yourself.")
		return false
	end
	local win, cut = SpireHouses.dicePayout(amount)
	if host:getBankBalance() < win then
		player:sendCancelMessage("The house can't cover that bet right now.")
		return false
	end
	if player:getBankBalance() < amount then
		player:sendCancelMessage("You don't have that much gold in the bank. (Bets are gold only.)")
		return false
	end
	player:setBankBalance(player:getBankBalance() - amount)
	host:setBankBalance(host:getBankBalance() + amount)
	local roll = math.random(6)
	player:getPosition():sendMagicEffect(CONST_ME_CRAPS)
	if SpireHouses.diceWins(call, roll) then
		host:setBankBalance(host:getBankBalance() - win)
		player:setBankBalance(player:getBankBalance() + win)
		player:say(string.format("rolled a %d and wins %d gold!", roll, win), TALKTYPE_MONSTER_SAY)
	else
		player:say(string.format("rolled a %d and loses %d gold.", roll, amount), TALKTYPE_MONSTER_SAY)
	end
	logger.info("[Spirebound] dice: {} bet {} {} in {}'s hall, roll {}", player:getName(), amount, call, host:getName(), roll)
	return false
end
dice:separator(" ")
dice:groupType("normal")
dice:register()

-- !openhouse --------------------------------------------------------------
local openhouse = TalkAction("!openhouse")
function openhouse.onSay(player, words, param)
	local house = inOwnHouse(player)
	if not house then
		player:sendCancelMessage("Stand in your own house.")
		return false
	end
	house:setAccessList(GUEST_LIST, "*")
	kv.scoped("spirebound-openhouse"):set(tostring(house:getId()), os.time() + SpireHouses.OPEN_HOUSE_TIME)
	Game.broadcastMessage(string.format("%s's house \"%s\" is open to visitors for the next 2 hours!", player:getName(), house:getName()), MESSAGE_EVENT_ADVANCE)
	local hid = house:getId()
	addEvent(function()
		local h = House(hid)
		if h then
			h:setAccessList(GUEST_LIST, "")
		end
	end, SpireHouses.OPEN_HOUSE_TIME * 1000)
	return false
end
openhouse:groupType("normal")
openhouse:register()

-- Boss sigils: every credited player of a boss kill earns one (bosses_floor1.lua calls this)
function SpireHouses.awardSigil(name, bossName)
	local p = Player(name)
	if p then
		local s = p:kv():scoped("spirebound-sigils")
		s:set(bossName, (s:get(bossName) or 0) + 1)
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned a Boss Sigil: " .. bossName .. ". Use it in a house Summoning Circle (!summon).")
	end
end
