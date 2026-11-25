-- Floor Beacons in the game (rules: lib/spirebound/beacons.lua; DESIGN.md 3.6; roadmap M1).
-- Fire bowls in each town (points beacon_<floor>_<slot>), Ember drops, the experience and loot bonus, the faster apex
-- spawn with all four fires lit, announcements, !beacon, the HUD line, and GM /beacon for tests.

local B = SpireBeacons

-- keep each bowl's look (lit or empty) in step with the stored state
local function syncBowls(floor, now)
	local rec = B.get(floor)
	for i = 1, B.SLOTS do
		local p = WorldPoints["beacon_" .. floor .. "_" .. i]
		local tile = p and Tile(p)
		if tile then
			local want = B.isLit(rec, i, now) and B.LIT or B.UNLIT
			local other = want == B.LIT and B.UNLIT or B.LIT
			local item = tile:getItemById(other)
			if item then
				item:transform(want)
			end
		end
	end
end
B.syncBowls = syncBowls

-- the HUD: {t="beacon", n=floor, lit, mins} whenever a player's floor or its fires change
local lastHud = {}
local function hudFor(player, now, force)
	local n = Floors.at(player:getPosition())
	local rec = n > 0 and B.get(n) or { slots = {} }
	local lit = n > 0 and B.litCount(rec, now) or 0
	local left = B.nextOut(rec, now)
	local mins = left and math.ceil(left / 60) or 0
	local key = n .. ":" .. lit .. ":" .. mins -- the minutes count down on the label
	if force or lastHud[player:getId()] ~= key then
		lastHud[player:getId()] = key
		SpireClient.send(player, { t = "beacon", n = n, lit = lit, slots = B.SLOTS, mins = mins })
	end
end
B.hudFor = hudFor

-- Lights bowl i on a floor for this player, taking one Ember. Returns true when lit.
function B.lightBy(player, floor, i)
	if B.isLit(B.get(floor), i, os.time()) then -- a burning bowl says how long it burns, Ember or not
		player:sendCancelMessage(select(2, B.canLight(B.get(floor), i, 0, os.time())))
		return false
	end
	if player:getItemCount(B.EMBER) < 1 then
		player:sendCancelMessage("The bowl is cold. A Beacon Ember would light it: field bosses, elites and hidden beasts drop them.")
		return false
	end
	if not Floors.isOpen(floor) then
		player:sendCancelMessage("This floor is still sealed.")
		return false
	end
	local guild = player:getGuild()
	local now = os.time()
	local ok, why = B.light(floor, i, player:getName(), guild and guild:getId() or 0, now)
	if not ok then
		player:sendCancelMessage(why)
		return false
	end
	player:removeItem(B.EMBER, 1)
	SpireChronicle.add(player, "beacon", 1)
	syncBowls(floor, now)
	local p = WorldPoints["beacon_" .. floor .. "_" .. i]
	if p then
		p:sendMagicEffect(CONST_ME_FIREAREA)
	end
	local rec = B.get(floor)
	local lit = B.litCount(rec, now)
	Game.broadcastMessage(string.format("%s lit a fire on the Floor %d Beacon! Everyone hunting on Floor %d gets +%d%% experience and loot for the next hour (%d of %d fires lit)%s",
		player:getName(), floor, floor, math.floor(lit * B.XP_PER_SLOT * 100 + 0.5), lit, B.SLOTS,
		lit >= B.SLOTS and ". All four burn: the apex spawn refills fast!" or "."), MESSAGE_EVENT_ADVANCE)
	logger.info("[Spirebound] beacon floor {} slot {} lit by {}", floor, i, player:getName())
	for _, pl in ipairs(Game.getPlayers()) do
		hudFor(pl, now)
	end
	return true
end

-- using a bowl (with an Ember in the backpack), or using an Ember on a bowl
local bowl = Action()
function bowl.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local floor, i = B.slotAt(item:getPosition())
	if not floor then
		return false
	end
	B.lightBy(player, floor, i)
	return true
end
for floor = 1, 10 do
	for i = 1, B.SLOTS do
		local p = WorldPoints["beacon_" .. floor .. "_" .. i]
		if p then
			bowl:position(p)
		end
	end
end
bowl:register()

local ember = Action()
function ember.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if not target or not target.isItem or not target:isItem() then
		player:sendCancelMessage("Use the Ember on a fire bowl of a town's Beacon.")
		return true
	end
	local floor, i = B.slotAt(target:getPosition())
	if not floor then
		player:sendCancelMessage("Use the Ember on a fire bowl of a town's Beacon.")
		return true
	end
	B.lightBy(player, floor, i)
	return true
end
ember:id(B.EMBER)
ember:register()

-- the bonus: experience and loot for kills on a floor with lit fires
local xp = EventCallback("SpireBeaconXp")
function xp.playerOnGainExperience(player, target, exp, rawExp)
	if target and target:isMonster() then
		local f = B.xpFactor(Floors.at(player:getPosition()))
		if f > 1 then
			return math.floor(exp * f)
		end
	end
	return exp
end
xp:register()

local loot = EventCallback("SpireBeaconLoot")
function loot.monsterOnDropLoot(monster, corpse)
	local owner = Player(corpse:getCorpseOwner())
	local mType = monster:getType()
	if not owner or not mType or monster:getMaster() then
		return
	end
	local bonus = B.lootBonus(Floors.at(monster:getPosition()))
	if bonus > 0 and corpse:isContainer() then
		corpse:addLoot(mType:generateLootRoll({ factor = bonus, gut = false }, {}, owner))
	end
	-- Embers
	local n = B.embersFor(monster:getName(), math.random, SpireFloorBosses)
	if n > 0 then
		if corpse:isContainer() then
			corpse:addItem(B.EMBER, n)
		else
			owner:addItem(B.EMBER, n)
		end
		corpse:getPosition():sendMagicEffect(CONST_ME_FIREATTACK)
		owner:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s Beacon Ember%s smoulder%s in the remains! Light a fire bowl in town with it.",
			n == 1 and "A" or tostring(n), n == 1 and "" or "s", n == 1 and "s" or ""))
	end
end
loot:register()

-- the fourth fire: extra apex monsters near the heart of the apex spawn, back soon after they die
local apexAlive = {} -- floor -> { [k] = creature id }
local apexReady = {} -- floor -> { [k] = os.time() when it may return }
local function apexPoint(floor)
	return floor == 1 and WorldPoints.apex_watchtower or WorldPoints["f" .. floor .. "_apex"]
end
function B.apexTick(floor, now)
	local alive, ready = apexAlive[floor] or {}, apexReady[floor] or {}
	apexAlive[floor], apexReady[floor] = alive, ready
	local fast = B.apexFast(floor, now)
	local spawned = 0
	for k = 1, B.APEX_EXTRA do
		local c = alive[k] and Creature(alive[k])
		if alive[k] and (not c or c:isRemoved() or c:getHealth() <= 0) then
			alive[k] = nil
			ready[k] = now + B.APEX_RETURN
		end
		if fast and not alive[k] and now >= (ready[k] or 0) then
			local pos, name = apexPoint(floor), B.APEX[floor]
			local m = pos and name and Game.createMonster(name, pos, true, false)
			if m then
				alive[k] = m:getId()
				spawned = spawned + 1
			end
		elseif not fast and alive[k] and c then
			c:remove() -- the fires went out: the extras melt away
			alive[k] = nil
		end
	end
	return spawned
end
function B.apexExtras(floor)
	local n = 0
	for _, cid in pairs(apexAlive[floor] or {}) do
		local c = Creature(cid)
		if c and not c:isRemoved() then
			n = n + 1
		end
	end
	return n
end

-- every 10 seconds: bowls, fires going out, the apex extras, the HUD
local wasLit = {} -- floor -> { [i] = true }
local tick = GlobalEvent("SpireBeaconTick")
function tick.onThink(interval)
	local now = os.time()
	for floor = 1, Floors.highestOpen() do
		local rec = B.get(floor)
		wasLit[floor] = wasLit[floor] or {}
		local out = 0
		for i = 1, B.SLOTS do
			local lit = B.isLit(rec, i, now)
			if wasLit[floor][i] and not lit then
				out = out + 1
			end
			wasLit[floor][i] = lit or nil
		end
		if out > 0 then -- one line, however many went out together
			Game.broadcastMessage(string.format("%s on the Floor %d Beacon %s gone out (%d of %d still burn).", out == 1 and "A fire" or (out .. " fires"),
				floor, out == 1 and "has" or "have", B.litCount(rec, now), B.SLOTS), MESSAGE_EVENT_ADVANCE)
		end
		syncBowls(floor, now)
		B.apexTick(floor, now)
	end
	for _, p in ipairs(Game.getPlayers()) do
		hudFor(p, now)
	end
	return true
end
tick:interval(10000)
tick:register()

local startup = GlobalEvent("SpireBeaconStartup")
function startup.onStartup()
	local now = os.time()
	for floor = 1, 10 do
		syncBowls(floor, now)
	end
	return true
end
startup:register()

local login = CreatureEvent("SpireBeaconLogin")
function login.onLogin(player)
	addEvent(function(pid)
		local p = Player(pid)
		if p then
			hudFor(p, os.time(), true)
		end
	end, 1500, player:getId())
	return true
end
login:register()

-- !beacon: the state of this floor's Beacon (or every open floor's from town-less places)
local status = TalkAction("!beacon")
function status.onSay(player, words, param)
	local now = os.time()
	local n = Floors.at(player:getPosition())
	local lines = {}
	for floor = 1, Floors.highestOpen() do
		if n == 0 or floor == n then
			table.insert(lines, B.statusLine(floor, B.get(floor), now))
		end
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, table.concat(lines, "\n"))
	return false
end
status:separator(" ")
status:groupType("normal")
status:register()

-- GM: /beacon light <floor> [slot] [name] | /beacon clear <floor> | /beacon ember [count]
local gm = TalkAction("/beacon")
function gm.onSay(player, words, param)
	local args = param:split(" ")
	local now = os.time()
	if args[1] == "ember" then
		player:addItem(B.EMBER, tonumber(args[2]) or 1)
	elseif args[1] == "light" and tonumber(args[2]) then
		local floor = tonumber(args[2])
		local rec = B.get(floor)
		local slot = tonumber(args[3])
		if not slot then
			for i = 1, B.SLOTS do
				if not B.isLit(rec, i, now) then
					slot = i
					break
				end
			end
		end
		local ok, why = B.light(floor, slot or 1, args[4] or player:getName(), 0, now)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, ok and "Lit." or why)
		syncBowls(floor, now)
	elseif args[1] == "clear" and tonumber(args[2]) then
		B.put(tonumber(args[2]), { slots = {} })
		syncBowls(tonumber(args[2]), now)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Beacon cleared.")
	else
		player:sendCancelMessage("Usage: /beacon light <floor> [slot] [name] | /beacon clear <floor> | /beacon ember [count]")
	end
	return false
end
gm:separator(" ")
gm:groupType("god")
gm:register()
