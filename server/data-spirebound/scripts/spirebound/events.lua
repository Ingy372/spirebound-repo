-- World events every 3 hours, the weekly Fishing Derby, and the weekend bonus announcements.

local FLOOR1_POINTS = { apex = "apex_watchtower", camp = "camp_wolf_copse" }
local function floorPoint(n, key)
	if n == 1 then
		return WorldPoints[FLOOR1_POINTS[key]]
	end
	return WorldPoints["f" .. n .. "_" .. ({ apex = "apex", camp = "camp2" })[key]]
end

local function eliteOf(n)
	if n == 1 then
		return "Grey Alpha"
	end
	return SpireFloorBosses[n] and SpireFloorBosses[n].elite or "Grey Alpha"
end

local function apexOf(n)
	local apex = { [1] = "Stonehorn Ram", [2] = "Mesa Wyrmling", [3] = "Grove Hydraling", [4] = "Siege Beast", [5] = "Undying Champion",
		[6] = "Pyre Wyrm", [7] = "Shard Hydra", [8] = "Hoarfrost Wyrm", [9] = "Treasure Devourer", [10] = "Lapis Wyrm" }
	return apex[n]
end

local spawned = {}

local function startEvent(kind, floor)
	SpireEvents.active = { kind = kind, floor = floor, untilTime = os.time() + kind.minutes * 60 }
	Game.broadcastMessage(string.format(kind.text, floor), MESSAGE_EVENT_ADVANCE)
	spawned = {}
	local function add(name, pos, n)
		for _ = 1, n do
			local m = pos and Game.createMonster(name, pos, true, false)
			if m then
				table.insert(spawned, m:getId())
			end
		end
	end
	if kind.id == "frenzy" then
		add(apexOf(floor), floorPoint(floor, "apex"), 6)
	elseif kind.id == "incursion" then
		add(eliteOf(floor), floorPoint(floor, "camp"), 4)
	elseif kind.id == "champion" then
		add(eliteOf(floor), floorPoint(floor, "camp"), 1)
		local champ = spawned[#spawned] and Creature(spawned[#spawned])
		if champ then
			champ:setMaxHealth(champ:getMaxHealth() * 6)
			champ:addHealth(champ:getMaxHealth())
			champ:say("I am the Wandering Champion! Who dares?", TALKTYPE_MONSTER_YELL)
		end
	end
	logger.info("[Spirebound] world event {} on floor {}", kind.id, floor)
	addEvent(function()
		Game.broadcastMessage(kind.name .. " on Floor " .. floor .. " has ended.", MESSAGE_EVENT_ADVANCE)
		for _, id in ipairs(spawned) do
			local c = Creature(id)
			if c then
				c:remove()
			end
		end
		spawned = {}
		SpireEvents.active = nil
	end, kind.minutes * 60 * 1000)
end
SpireEvents.start = startEvent

-- Every 3 hours: announce, then start 10 minutes later
local scheduler = GlobalEvent("SpireWorldEvents")
function scheduler.onThink(interval)
	local kind, floor = SpireEvents.pick(math.random(), Floors.highestOpen())
	Game.broadcastMessage(string.format("In 10 minutes: %s on Floor %d.", kind.name, floor), MESSAGE_EVENT_ADVANCE)
	addEvent(startEvent, SpireEvents.WARNING * 1000, kind, floor)
	return true
end
scheduler:interval(SpireEvents.INTERVAL * 1000)
scheduler:register()

-- Frenzy: +25% loot on that floor's apex monsters
local loot = EventCallback("SpireEventLoot")
function loot.monsterOnDropLoot(monster, corpse)
	local a = SpireEvents.active
	local owner = Player(corpse:getCorpseOwner())
	if not owner or not a then
		return
	end
	local mType = monster:getType()
	local bonus = 0
	if a.kind.id == "frenzy" and monster:getName() == apexOf(a.floor) and os.time() < a.untilTime then
		bonus = bonus + 0.25
	end
	if SpireEvents.factor("loot") > 1 then
		bonus = bonus + 1.0
	end
	if bonus > 0 and mType then
		corpse:addLoot(mType:generateLootRoll({ factor = bonus, gut = false }, {}, owner))
	end
end
loot:register()

-- Weekend XP and skill bonuses
local xp = EventCallback("SpireWeekendXp")
function xp.playerOnGainExperience(player, target, exp, rawExp)
	return exp * SpireEvents.factor("xp")
end
xp:register()

local skills = EventCallback("SpireWeekendSkills")
function skills.playerOnGainSkillTries(player, skill, tries)
	return tries * SpireEvents.factor("skill")
end
skills:register()

-- Login reminder of the weekend bonus
local login = CreatureEvent("SpireEventsLogin")
function login.onLogin(player)
	local w = SpireEvents.currentWeekend()
	if w then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Weekend bonus: " .. w.name .. "!")
	end
	local a = SpireEvents.active
	if a and os.time() < a.untilTime then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("World event running: %s on Floor %d.", a.kind.name, a.floor))
	end
	return true
end
login:register()

-- Weekly Fishing Derby: Saturdays 20:00-21:00 server time. Biggest single catch wins.
function SpireEvents.derbyCatch(player, fishName, kg)
	local d = SpireEvents.derby
	if not d or os.time() >= d.untilTime then
		return
	end
	if not d.best or kg > d.best.kg then
		d.best = { name = player:getName(), kg = kg, fish = fishName }
		Game.broadcastMessage(string.format("Derby: %s leads with a %.2f kg %s!", player:getName(), kg, fishName), MESSAGE_EVENT_ADVANCE)
	end
end

local derby = GlobalEvent("SpireFishingDerby")
function derby.onTime(interval)
	if os.date("*t").wday ~= 7 then
		return true
	end
	SpireEvents.derby = { untilTime = os.time() + 3600 }
	Game.broadcastMessage("The weekly Fishing Derby has begun! Biggest single catch in the next hour wins.", MESSAGE_EVENT_ADVANCE)
	addEvent(function()
		local d = SpireEvents.derby
		SpireEvents.derby = nil
		if d and d.best then
			local p = Player(d.best.name)
			if p then
				p:setBankBalance(p:getBankBalance() + 50000)
				p:kv():scoped("spirebound-titles"):set("Derby Champion", os.time())
			end
			Game.broadcastMessage(string.format("The Fishing Derby is over! %s wins with a %.2f kg %s (50,000 gold and the Derby Champion title).", d.best.name, d.best.kg, d.best.fish), MESSAGE_EVENT_ADVANCE)
		else
			Game.broadcastMessage("The Fishing Derby is over. Nobody caught anything!", MESSAGE_EVENT_ADVANCE)
		end
	end, 3600 * 1000)
	return true
end
derby:time("20:00:00")
derby:register()

-- GM test command: /event <frenzy|incursion|fishing|champion> <floor>
local cmd = TalkAction("/event")
function cmd.onSay(player, words, param)
	local id, floor = param:match("(%a+)%s*(%d*)")
	for _, k in ipairs(SpireEvents.KINDS) do
		if k.id == id then
			startEvent(k, tonumber(floor) or 1)
			return false
		end
	end
	player:sendCancelMessage("Usage: /event frenzy|incursion|fishing|champion <floor>")
	return false
end
cmd:separator(" ")
cmd:groupType("god")
cmd:register()
