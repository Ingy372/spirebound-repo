-- The Oathroom in the game (roadmap FD3; rules: lib/spirebound/oathroom.lua; map: maps/floor1_story.py).
-- One team at a time. The run lives in memory: a restart empties the hall (everyone inside is put out at login).

local O = SpireOathroom
local P = WorldPoints
local GATE = 1772                     -- a sealed boulder door, as at the Spire's foot in the Arrival Yard
local LEVER, LEVER_PULLED = 2772, 2773
local BRAZIER = 2113
local CHEST = 116
local AID = { lever = 48201, lever_in = 48210, lectern = 48220, chest = 48230 }

O.run = O.run or nil                  -- the team inside now (nil = the hall is free)
O.runCount = O.runCount or 0
local tracked = {}                    -- monster id -> true for every monster the run made

local function inHall(pos)
	local nw, se = P.oath_nw, P.oath_se
	return nw and pos.z == nw.z and pos.x >= nw.x and pos.x <= se.x and pos.y >= nw.y and pos.y <= se.y
end
O.inHall = inHall

local function members()
	local out = {}
	for guid in pairs(O.run and O.run.team or {}) do
		local p = Player(guid)
		if p and inHall(p:getPosition()) then
			table.insert(out, p)
		end
	end
	return out
end

local function tell(text, kind)
	for _, p in ipairs(members()) do
		p:sendTextMessage(kind or MESSAGE_EVENT_ADVANCE, text)
	end
end

local function questOf()
	return O.QUEST
end

-- the quest-log line: the phase of the run you are in (or the one you reached last)
function O.progress(player)
	return SpireFirstClimb.encode(player:kv():scoped("spirebound-oath"):get("phase") or 0, 0)
end

local function setPhase(n)
	if not O.run then
		return
	end
	O.run.phase = n
	for _, p in ipairs(members()) do
		p:kv():scoped("spirebound-oath"):set("phase", n)
		local q = questOf()
		if SpireQuests.state(p, q) == 1 then
			SpireQuests.refreshTracker(p, q)
		end
	end
end

-- ---------------------------------------------------------------- gates
local function gateTiles(name)
	local top = P["oath_gate_" .. name]
	local out = {}
	if top then
		for j = 0, 2 do
			table.insert(out, Position(top.x, top.y + j, top.z))
		end
	end
	return out
end

local function closeGate(name)
	for _, pos in ipairs(gateTiles(name)) do
		local t = Tile(pos)
		if t and not t:getItemById(GATE) then
			for _, c in ipairs(t:getCreatures() or {}) do -- never shut anyone inside a gate
				c:teleportTo(P.oath_arrival or pos)
			end
			Game.createItem(GATE, 1, pos)
		end
	end
end

local function openGate(name)
	for _, pos in ipairs(gateTiles(name)) do
		local t = Tile(pos)
		local g = t and t:getItemById(GATE)
		if g then
			g:remove()
			pos:sendMagicEffect(CONST_ME_POFF)
		end
	end
end

-- ---------------------------------------------------------------- monsters
local function spawn(name, pos)
	local m = Game.createMonster(name, pos, true, true)
	if m then
		tracked[m:getId()] = true
	end
	return m
end

local function clearMonsters()
	for mid in pairs(tracked) do
		local m = Monster(mid)
		if m then
			m:remove()
		end
	end
	tracked = {}
end

local function countAlive(filter)
	local n = 0
	for mid in pairs(tracked) do
		local m = Monster(mid)
		if not m then
			tracked[mid] = nil
		elseif not filter or filter(m) then
			n = n + 1
		end
	end
	return n
end

-- ---------------------------------------------------------------- the hall's furniture (start-up and every reset)
local function setLevers()
	for i, l in ipairs(O.LEVERS) do
		local t = Tile(P["oath_lever_" .. l.id])
		local item = t and (t:getItemById(LEVER_PULLED) or t:getItemById(LEVER))
		if item then
			if item:getId() == LEVER_PULLED then
				item:transform(LEVER)
			end
			item:setActionId(AID.lever_in + i)
			item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "An old lever. Its handle is carved with a " .. l.mark .. ".")
		end
	end
end

local function setBraziers(lit)
	for i = 1, 4 do
		local pos = P["oath_brazier_" .. i]
		local t = pos and Tile(pos)
		if t then
			local b = t:getItemById(BRAZIER)
			if lit and not b then
				Game.createItem(BRAZIER, 1, pos)
			elseif not lit and b then
				b:remove()
			end
		end
	end
end

local function brazierLit(i)
	local t = Tile(P["oath_brazier_" .. i])
	return t and t:getItemById(BRAZIER) ~= nil
end

function O.resetHall()
	clearMonsters()
	for _, g in ipairs(O.CLOSED_AT_START) do
		closeGate(g)
	end
	setLevers()
	setBraziers(true)
end

function O.placeFurniture()
	if not P.oath_nw then
		logger.warn("[oathroom] no Oathroom on the map")
		return
	end
	local lec = Tile(P.oath_lectern)
	if lec and not lec:getItemById(2821) then
		local book = Game.createItem(2821, 1, P.oath_lectern)
		if book then
			book:setActionId(AID.lectern)
			book:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A page of Ione Castellan's record, chained to the lectern. Use it to read it.")
		end
	end
	for i, c in ipairs(O.CHESTS) do
		local pos = P["oath_chest_" .. c.id]
		if pos and not Tile(pos):getItemById(CHEST) then
			local item = Game.createItem(CHEST, 1, pos)
			if item then
				item:setActionId(AID.chest + i)
				item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, c.name:gsub("^%l", string.upper) .. ": " .. c.text .. ". Use it to take it (one chest per character each season).")
			end
		end
	end
	local lever = Tile(P.oath_lever)
	if lever then
		local l = lever:getItemById(LEVER) or lever:getItemById(LEVER_PULLED)
		if l then
			l:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "The oath lever. Four climbers of level 30 on the four stones, then pull it.")
		end
	end
	local order = Tile(P.oath_order)
	local o = order and order:getItemById(2199)
	if o then
		o:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A stone carved with the First Climb's standing order. Use it to read it.")
	end
	O.resetHall()
end

local startup = GlobalEvent("SpireOathroomStartup")
function startup.onStartup()
	O.placeFurniture()
	return true
end
startup:register()

-- ---------------------------------------------------------------- the run
local function putOut(p, why)
	if P.oath_door_out then
		p:teleportTo(P.oath_door_out)
		P.oath_door_out:sendMagicEffect(CONST_ME_TELEPORT)
	end
	if why then
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, why)
	end
end

function O.endRun(why)
	if not O.run then
		return
	end
	for _, p in ipairs(members()) do
		putOut(p, why)
	end
	O.run = nil
	O.resetHall()
end

-- the Captain's hall: waves for three minutes; a monster on the line starts the hall again
local function captainTick(runId)
	local r = O.run
	if not r or r.id ~= runId or r.phase ~= 0 then
		return
	end
	local now = os.time()
	if #members() == 0 then
		O.endRun()
		return
	end
	if now - r.holdStart < O.HOLD then
		if now >= r.nextWave then
			r.wave = r.wave + 1
			local kinds = O.WAVES[(r.wave - 1) % #O.WAVES + 1]
			local c = P.oath_captain_spawn
			for i, name in ipairs(kinds) do
				spawn(name, Position(c.x + (i % 2), c.y - 1 + i, c.z))
			end
			r.nextWave = now + O.WAVE_EVERY
			if r.wave == 1 then
				tell("The Captain's hall: the garrison comes down the corridor. Hold the line for three minutes: let none of them past the marked line behind you!")
			end
		end
	elseif countAlive() == 0 then
		openGate("g1")
		tell("The line held. The Captain's gate opens. The Scout's hall: split into two pairs and read the carving at the entrance.")
		local spots = { north_a = P.oath_lever_l1, south_a = P.oath_lever_l2, north_b = P.oath_lever_l3, south_b = P.oath_lever_l4 }
		for room, name in pairs(O.SCOUT_GUARDS) do
			local s = spots[room]
			if s then
				spawn(name, Position(s.x - 2, s.y + (s.y < P.oath_arrival.y and 1 or -1), s.z))
			end
		end
		setPhase(1)
		return
	end
	addEvent(captainTick, 1000, runId)
end

function O.lineBroken(monster)
	local r = O.run
	if not r or r.phase ~= 0 or not tracked[monster:getId()] then
		return
	end
	clearMonsters()
	r.holdStart, r.nextWave, r.wave = os.time() + 8, os.time() + 8, 0
	tell("The line is broken! The garrison falls back. Hold it again, from the start, in 8 seconds.")
end

-- the timer and the watch over who is still inside
local function watch(runId)
	local r = O.run
	if not r or r.id ~= runId then
		return
	end
	if os.time() - r.started >= O.TIME_LIMIT then
		O.endRun("The oath hall's 25 minutes are up. The stones push you back out to the quarry.")
		return
	end
	if #members() == 0 then
		O.endRun()
		return
	end
	local left = O.TIME_LIMIT - (os.time() - r.started)
	if left <= 300 and not r.warned then
		r.warned = true
		tell("Five minutes left in the oath hall.")
	end
	addEvent(watch, 5000, runId)
end

function O.start(team)
	O.runCount = O.runCount + 1
	O.run = { id = O.runCount, team = {}, started = os.time(), phase = 0, holdStart = os.time() + 10,
		nextWave = os.time() + 10, wave = 0, pulled = 0, path = O.makePath(math.random), cleared = false }
	O.resetHall()
	for _, p in ipairs(team) do
		O.run.team[p:getGuid()] = true
		p:teleportTo(P.oath_arrival)
		p:kv():scoped("spirebound-oath"):set("phase", 0)
		local q = questOf()
		local season = SpireSeason and SpireSeason.current() or 1
		if p:kv():scoped("spirebound-oath"):get("season") ~= season then
			p:setStorageValue(q.storage, 1) -- the quest log follows the run (once a chest is taken this season, it stays done)
			p:setStorageValue(q.killStorage, 0)
		end
	end
	P.oath_arrival:sendMagicEffect(CONST_ME_TELEPORT)
	tell("You are inside the First Climb's oath hall. 25 minutes. In 10 seconds the garrison comes down the corridor: hold the line in front of the gate behind you.")
	addEvent(captainTick, 1000, O.run.id)
	addEvent(watch, 5000, O.run.id)
end

-- ---------------------------------------------------------------- the door in the quarry
local doorLever = Action()
function doorLever.onUse(player, item)
	if O.run and #members() == 0 then
		O.endRun()
	end
	local tiles, team = {}, {}
	for i = 1, O.TEAM do
		local t = Tile(P["oath_tile_" .. i])
		local c = t and t:getTopCreature()
		local p = c and c:getPlayer()
		if p then
			tiles[i] = { level = p:getLevel(), name = p:getName() }
			table.insert(team, p)
		else
			tiles[i] = false
		end
	end
	local ok, why = O.entryCheck(tiles, O.run ~= nil)
	item:transform(item:getId() == LEVER and LEVER_PULLED or LEVER)
	if not ok then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, why)
		return true
	end
	O.start(team)
	return true
end
doorLever:aid(AID.lever)
doorLever:register()

-- the line in the Captain's hall: five tiles across the corridor
local line = MoveEvent()
function line.onStepIn(creature, item, position, fromPosition)
	if creature:isMonster() then
		O.lineBroken(creature)
	end
	return true
end
if P.oath_line then
	for j = 0, 4 do
		line:position(Position(P.oath_line.x, P.oath_line.y + j, P.oath_line.z))
	end
	line:register()
end

-- the Scout's levers
local levers = Action()
function levers.onUse(player, item)
	local r = O.run
	local i = item:getActionId() - AID.lever_in
	local l = O.LEVERS[i]
	if not r or not l or not r.team[player:getGuid()] then
		return true
	end
	if item:getId() == LEVER_PULLED then
		player:sendTextMessage(MESSAGE_STATUS, "This lever is already pulled.")
		return true
	end
	local res = O.leverResult(r.pulled, i)
	if res == "wrong" then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The %s lever won't move. The carving at the entrance says %s comes first.", l.mark, O.LEVERS[r.pulled + 1].mark))
		return true
	end
	item:transform(LEVER_PULLED)
	r.pulled = r.pulled + 1
	openGate(l.opens)
	tell(string.format("The %s lever: a door opens on the other side (%d of 4).", l.mark, r.pulled))
	if res == "last" then
		openGate("ng2")
		openGate("sg2")
		tell("All four levers. The Keeper's hall: read the book on the lectern, then walk the rune floor.")
		setPhase(2)
	end
	return true
end
for i = 1, #O.LEVERS do
	levers:aid(AID.lever_in + i)
end
levers:register()

-- the Keeper's lectern and rune floor
local lectern = Action()
function lectern.onUse(player, item)
	local r = O.run
	if not r then
		player:showTextDialog(item:getId(), "The page is blank until the oath is sworn again.")
		return true
	end
	player:showTextDialog(item:getId(), O.pathText(r.path))
	return true
end
lectern:aid(AID.lectern)
lectern:register()

local runes = MoveEvent()
function runes.onStepIn(creature, item, position, fromPosition)
	local p = creature:getPlayer()
	local r = O.run
	if not p or not r then
		return true
	end
	local row = position.x - P.oath_runes.x + 1
	local lane = position.y - P.oath_runes.y + 1
	if O.safe(r.path, row, lane) then
		if row == O.RUNE_ROWS and r.phase < 3 then
			setPhase(3)
			tell("Across the Keeper's floor. The Healer's hall lies ahead: the Oathkeeper heals from his four braziers. Stand beside one to put it out.")
		end
		return true
	end
	local dmg = O.runeDamage(p:getHealth(), p:getMaxHealth())
	if dmg > 0 then
		p:addHealth(-dmg)
	end
	position:sendMagicEffect(CONST_ME_ENERGYHIT)
	p:teleportTo(P.oath_rune_back)
	p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The rune flares under your foot and throws you back. That was not the safe stone.")
	return true
end
if P.oath_runes then
	for i = 0, O.RUNE_ROWS - 1 do
		for j = 0, O.RUNE_LANES - 1 do
			runes:position(Position(P.oath_runes.x + i, P.oath_runes.y + j, P.oath_runes.z))
		end
	end
	runes:register()
end

-- the Healer's hall: the Oathkeeper wakes when the first climber steps through the gate after the runes
local function bossTick(runId)
	local r = O.run
	if not r or r.id ~= runId or not r.boss then
		return
	end
	local b = Monster(r.boss)
	if not b then
		return
	end
	local lit = 0
	for i = 1, 4 do
		if brazierLit(i) then
			lit = lit + 1
		end
	end
	if lit > 0 and b:getHealth() < b:getMaxHealth() then
		b:addHealth(math.floor(b:getMaxHealth() * O.BRAZIER_HEAL * lit))
		b:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	end
	if os.time() >= (r.relight or 0) then
		r.relight = os.time() + O.RELIGHT_EVERY
		for i = 1, 4 do
			if not brazierLit(i) then
				Game.createItem(BRAZIER, 1, P["oath_brazier_" .. i])
				tell("A brazier flares up again beside the Oathkeeper.", MESSAGE_STATUS)
				break
			end
		end
	end
	addEvent(bossTick, 2000, runId)
end

local wake = MoveEvent()
function wake.onStepIn(creature, item, position, fromPosition)
	local r = O.run
	if not creature:isPlayer() or not r or r.boss or r.phase < 3 then
		return true
	end
	local name = MonsterType(O.BOSS) and O.BOSS or O.BOSS_STANDIN
	setBraziers(true)
	local b = spawn(name, P.oath_boss)
	if b then
		r.boss = b:getId()
		b:registerEvent("SpireOathkeeper")
		b:setSkull(SKULL_NONE)
		r.relight = os.time() + O.RELIGHT_EVERY
		tell("The Oathkeeper rises: \"Hold the stair. The oath is kept.\"")
		addEvent(bossTick, 2000, r.id)
	end
	return true
end
local g3 = P.oath_gate_g3
if g3 then
	for j = 0, 2 do
		wake:position(Position(g3.x + 1, g3.y + j, g3.z))
	end
	wake:register()
end

-- putting a brazier out: stand on the tile beside it (toward the middle of the hall) for a few seconds
local douse = MoveEvent()
function douse.onStepIn(creature, item, position, fromPosition)
	local p = creature:getPlayer()
	if not p or not O.run or not O.run.boss then
		return true
	end
	local idx
	for i = 1, 4 do
		local b = P["oath_brazier_" .. i]
		if b and b.x == position.x and math.abs(b.y - position.y) == 1 then
			idx = i
		end
	end
	if not idx or not brazierLit(idx) then
		return true
	end
	p:sendTextMessage(MESSAGE_STATUS, "You smother the brazier: hold still...")
	addEvent(function(pid, i, x, y, z)
		local pl = Player(pid)
		if not pl then
			return
		end
		local pp = pl:getPosition()
		if pp.x ~= x or pp.y ~= y or pp.z ~= z or not brazierLit(i) then
			return
		end
		local t = Tile(P["oath_brazier_" .. i])
		local b = t and t:getItemById(BRAZIER)
		if b then
			b:remove()
			P["oath_brazier_" .. i]:sendMagicEffect(CONST_ME_POFF)
		end
		local c = Condition(CONDITION_PARALYZE)
		c:setParameter(CONDITION_PARAM_TICKS, O.DOUSE_STUN)
		c:setFormula(-0.9, 0, -0.9, 0)
		pl:addCondition(c)
		if CONDITION_PACIFIED then
			local pc = Condition(CONDITION_PACIFIED)
			pc:setParameter(CONDITION_PARAM_TICKS, O.DOUSE_STUN)
			pl:addCondition(pc)
		end
		pl:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The brazier goes out, and the smoke leaves you reeling for a few seconds.")
	end, O.DOUSE_SECONDS * 1000, p:getId(), idx, position.x, position.y, position.z)
	return true
end
for i = 1, 4 do
	local b = P["oath_brazier_" .. i]
	if b then
		douse:position(Position(b.x, b.y + (i <= 2 and 1 or -1), b.z))
	end
end
if P.oath_brazier_1 then
	douse:register()
end

local bossDeath = CreatureEvent("SpireOathkeeper")
function bossDeath.onDeath(creature)
	local r = O.run
	if not r or r.boss ~= creature:getId() then
		return true
	end
	r.cleared, r.boss = true, nil
	openGate("g4")
	setBraziers(true) -- FD3b: they light the hall (without them it went pitch dark and two Pilots lost their way)
	local team = members()
	for _, p in ipairs(team) do
		p:kv():scoped("spirebound-oath"):set("cleared_run", os.time())
		r.clearedBy = r.clearedBy or {}
		r.clearedBy[p:getGuid()] = true
	end
	setPhase(4)
	tell("The Oathkeeper falls: \"...the oath... is kept.\" The last gate opens. Each of you may take ONE chest, once this season. Everyone will see which you chose.")
	if SpireDiscoveries and SpireDiscoveries.mark then
		for _, p in ipairs(team) do
			pcall(SpireDiscoveries.mark, p, "deed", "oathroom")
		end
	end
	if SpireFinds and SpireFinds.first and SpireFinds.first("deed", "oathroom", team, "The Oathroom") then
		local names = {}
		for _, p in ipairs(team) do
			table.insert(names, p:getName())
			p:kv():scoped("spirebound-titles"):set("Oathbreaker of the Season", os.time())
		end
		Game.broadcastMessage(table.concat(names, ", ") .. " are the first team this season to break the Oathkeeper in the oath hall under the Old Quarry.", MESSAGE_STATUS)
	end
	return true
end
bossDeath:register()

-- ---------------------------------------------------------------- the chests
local CHOSEN = "spirebound-oath"

local function takeCaptain(player)
	local item = SpireGear.floorWeapon and SpireGear.floorWeapon(player, 1)
	local s = item and SpireGear.state(item)
	if not s or s.shop or s.tier >= SpireGearData.MAX_TIER then
		return false, "The Captain's chest tempers a Floor 1 weapon you carry, below the top tier. Carry one and open it again."
	end
	SpireGear.setState(item, { tier = s.tier + 1 })
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, item:getName() .. " is tempered one tier: tier " .. (s.tier + 1) .. ".")
	return true
end

local function takeScout(player)
	local bag = Game.createItem(5801, 1)
	if not bag then
		return false, "The chest is stuck. Try again."
	end
	bag:setAttribute(ITEM_ATTRIBUTE_NAME, "Oathbound Pack")
	bag:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A backpack from the First Climb's oath hall. Only those who broke the Oathkeeper carry one.")
	if player:addItemEx(bag, false, INDEX_WHEREEVER, FLAG_NOLIMIT) ~= RETURNVALUE_NOERROR then
		bag:remove()
		return false, "You have no room for the pack. Make room and open the chest again."
	end
	return true
end

local function takeKeeper(player)
	SpireQuests.payGold(player, O.KEEPER_GOLD)
	return true
end

local function takeHealer(player)
	if SpireAuras and SpireAuras.give then
		SpireAuras.give(player, "oathkeepers_mantle")
	end
	return true
end

local TAKE = { captain = takeCaptain, scout = takeScout, keeper = takeKeeper, healer = takeHealer }

local chests = Action()
function chests.onUse(player, item)
	local c = O.CHESTS[item:getActionId() - AID.chest]
	local r = O.run
	if not c then
		return false
	end
	local k = player:kv():scoped(CHOSEN)
	local season = SpireSeason and SpireSeason.current() or 1
	local ok, why = O.mayTake(r and r.clearedBy and r.clearedBy[player:getGuid()], k:get("season"), season)
	if not ok then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, why)
		return true
	end
	local done, err = TAKE[c.id](player)
	if not done then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, err)
		return true
	end
	k:set("season", season)
	k:set("chest", c.id)
	item:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
	local q = O.QUEST
	player:setStorageValue(q.storage, 3)
	player:addExperience(q.reward.exp, true)
	SpireChronicle.add(player, "quest", 1)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You take " .. c.name .. ": " .. c.text .. ". Step on the light in the corner to leave.")
	return true
end
for i = 1, #O.CHESTS do
	chests:aid(AID.chest + i)
end
chests:register()

-- ---------------------------------------------------------------- the look line, the aura, the Discoveries row
SpireFinds = SpireFinds or {}
SpireFinds.LOOK_EXTRAS = SpireFinds.LOOK_EXTRAS or {}
table.insert(SpireFinds.LOOK_EXTRAS, function(target)
	local k = target:kv():scoped(CHOSEN)
	local id = k:get("chest")
	if not id then
		return nil
	end
	for _, c in ipairs(O.CHESTS) do
		if c.id == id then
			return "Oathroom: took " .. c.name .. "."
		end
	end
end)

if SpireAuras and SpireAuras.LIST and not SpireAuras.get("oathkeepers_mantle") then
	table.insert(SpireAuras.LIST, { id = "oathkeepers_mantle", name = "Oathkeeper's Mantle", every = 4,
		effects = { CONST_ME_HOLYAREA or 40, CONST_ME_MAGIC_BLUE or 2 } })
end

if SpireDiscoveries and SpireDiscoveries.ORDER then
	local present = false
	for _, c in ipairs(SpireDiscoveries.ORDER) do
		present = present or c == "deed"
	end
	if not present then
		table.insert(SpireDiscoveries.ORDER, "deed")
	end
	SpireDiscoveries.LABEL.deed = "Deeds"
	SpireDiscoveries.sources = SpireDiscoveries.sources or {}
	SpireDiscoveries.sources.deed = function(player, id)
		if id == "oathroom" then
			return player:kv():scoped(CHOSEN):get("cleared_run") and 1 or nil
		end
	end
	SpireDiscoveries.register("deed", "oathroom", "The Oathroom: broke the Oathkeeper", 1)
end

-- ---------------------------------------------------------------- leaving: death, logout, the exits
local login = CreatureEvent("SpireOathroomLogin")
function login.onLogin(player)
	if inHall(player:getPosition()) and not (O.run and O.run.team[player:getGuid()]) then
		putOut(player, "The oath hall let you out while you were away.")
	end
	return true
end
login:register()
