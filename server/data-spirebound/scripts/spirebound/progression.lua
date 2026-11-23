-- Gear progression in the game: kills feed familiarity and style; style passives on damage taken, healing and speed.
-- Rules: lib/spirebound/progress.lua, lib/spirebound/style.lua. Damage dealt is applied in spells.lua's damage event.

local counted = {} -- monster id -> true once its kill was shared (onKill can fire for the last hitter and the top damage dealer)

local kill = CreatureEvent("SpireProgressKill")
function kill.onKill(player, target)
	if not target or not target:isMonster() then
		return true
	end
	local tid = target:getId()
	if counted[tid] then
		return true
	end
	counted[tid] = true
	addEvent(function(id) counted[id] = nil end, 5000, tid)
	local raw = target:getType():experience()
	local members = SpireProgress.sharers(player, target:getPosition())
	local share = SpireProgress.killShare(raw, #members)
	for _, m in ipairs(members) do
		SpireProgress.credit(m, target, share)
	end
	return true
end
kill:register()

local applied = {} -- player id -> speed added by the style
SpireCleanup.add(function(pid) applied[pid] = nil end)

function SpireStyle.applySpeed(player)
	local want = math.floor(SpireStyle.speedBonus(SpireStyle.get(player)))
	local have = applied[player:getId()] or 0
	if want ~= have then
		player:changeSpeed(want - have)
		applied[player:getId()] = want
	end
end

local guard = CreatureEvent("SpireStyleGuard")
function guard.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local player = creature:getPlayer()
	if not player then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	if primaryType == COMBAT_HEALING then
		local healer = SpireProgress.owner(attacker)
		if healer then
			primaryDamage = math.floor(primaryDamage * SpireStyle.healFactor(SpireStyle.get(healer)) + 0.5)
		end
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local f = SpireStyle.takenFactor(SpireStyle.get(player))
	if f < 1 then
		primaryDamage = math.floor(primaryDamage * f + 0.5)
		secondaryDamage = math.floor(secondaryDamage * f + 0.5)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
guard:register()

local login = CreatureEvent("SpireProgressLogin")
function login.onLogin(player)
	player:registerEvent("SpireProgressKill")
	player:registerEvent("SpireStyleGuard")
	SpireStyle.applySpeed(player)
	return true
end
login:register()
