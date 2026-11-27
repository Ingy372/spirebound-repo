-- Spire Chronicle in the game (rules: lib/spirebound/chronicle.lua; DESIGN.md 4; roadmap M3).
-- Kills and bosses are counted here; quests, tasks, fish, secrets and Beacon fires call SpireChronicle.add where they
-- happen; level, floor and path are checked every few seconds. !chronicle opens the Journal's Chronicle tab.

local C = SpireChronicle

local function bossKind(name)
	local def = SpireBoss and SpireBoss.defs[name]
	if def then
		return def.kind -- "field" or "floor"
	end
	if SpireTrophies and SpireTrophies.byBoss(name) then
		return "mini"
	end
end
C.bossKind = bossKind

local kill = {} -- N8: counted through SpireKills (one death callback), not the deprecated onKill event
function kill.onKill(player, target)
	if not target or not target:isMonster() or target:getMaster() then
		return true
	end
	C.add(player, "kill", 1)
	local kind = bossKind(target:getName())
	if kind == "field" then
		C.add(player, "fieldboss", 1)
	elseif kind == "floor" then
		C.add(player, "floorboss", 1)
	elseif kind == "mini" then
		C.add(player, "miniboss", 1)
	end
	return true
end
SpireKills.on("SpireChronicleKill", kill.onKill)

-- level, floor and path: whatever any character on the account reached
local function checkReach(p)
	C.reach(p, "level", p:getLevel())
	C.reach(p, "floor", Floors.at(p:getPosition()))
	if p:getVocation():getBaseId() > 0 then
		C.reach(p, "path", 1)
	end
end
C.checkReach = checkReach

local login = CreatureEvent("SpireChronicleLogin")
function login.onLogin(player)
	addEvent(function(pid)
		local p = Player(pid)
		if p then
			checkReach(p)
		end
	end, 2000, player:getId())
	return true
end
login:register()

local tick = GlobalEvent("SpireChronicleTick")
function tick.onThink(interval)
	for _, p in ipairs(Game.getPlayers()) do
		checkReach(p)
	end
	return true
end
tick:interval(5000)
tick:register()

local cmd = TalkAction("!chronicle")
function cmd.onSay(player, words, param)
	local reply = SpireJournal.build(player, "chronicle")
	reply.open = true
	SpireClient.send(player, reply)
	return false
end
cmd:separator(" ")
cmd:groupType("normal")
cmd:register()
