-- Player-fight lock for the built-in helpers (DESIGN.md 12; roadmap M5; Jay 2026-11-25: "the bot should work for pvp
-- strictly for healing"). From the moment a player hits you or you hit a player, for LOCK seconds after the last such
-- hit, the server tells your client {t="pvplock", on=true, secs}; the client's bot guard (client/modules/game_spirebound/bot/
-- spirebound_pvp_guard.lua) then pauses every helper except healing and eating, and the cavebot stands still.
-- {t="pvplock", on=false} when it ends. The engine's own fight rules (skulls, logout) are not touched.
SpirePvPLock = { LOCK = 60 }

local last = {} -- player (creature) id -> os.time() of the last hit between players
local sentOn = {} -- player id -> true while the client was told the lock is on

-- Pure: is the lock on, given the last player hit?
function SpirePvPLock.active(lastHit, now)
	return lastHit ~= nil and now - lastHit < SpirePvPLock.LOCK
end

function SpirePvPLock.isLocked(player)
	return SpirePvPLock.active(last[player:getId()], os.time())
end

local function mark(player, now)
	local g = player:getId()
	last[g] = now
	if not sentOn[g] then
		sentOn[g] = true
		SpireClient.send(player, { t = "pvplock", on = true, secs = SpirePvPLock.LOCK })
	end
end
SpirePvPLock.mark = mark

local function ownerPlayer(creature)
	if not creature then
		return nil
	end
	local p = creature:getPlayer()
	if p then
		return p
	end
	local master = creature:getMaster()
	return master and master:getPlayer() or nil
end

local hits = CreatureEvent("SpirePvPLockHit")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local victim = creature:getPlayer()
	local a = ownerPlayer(attacker)
	if victim and a and a ~= victim and primaryType ~= COMBAT_HEALING then
		local now = os.time()
		mark(victim, now)
		mark(a, now)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
hits:register()

local login = CreatureEvent("SpirePvPLockLogin")
function login.onLogin(player)
	player:registerEvent("SpirePvPLockHit")
	return true
end
login:register()

local tick = GlobalEvent("SpirePvPLockTick")
function tick.onThink(interval)
	local now = os.time()
	for g in pairs(sentOn) do
		if not SpirePvPLock.active(last[g], now) then
			sentOn[g] = nil
			local p = Player(g)
			if p then
				SpireClient.send(p, { t = "pvplock", on = false })
			end
		end
	end
	return true
end
tick:interval(1000)
tick:register()

if SpireCleanup then
	SpireCleanup.add(function(pid, guid)
		last[pid] = nil
		sentOn[pid] = nil
	end)
end
