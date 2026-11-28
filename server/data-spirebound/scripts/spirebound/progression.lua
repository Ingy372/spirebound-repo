-- Gear progression in the game: kills feed familiarity and style; style passives on damage taken, healing and speed.
-- Rules: lib/spirebound/progress.lua, lib/spirebound/style.lua. Damage dealt is applied in spells.lua's damage event.

local counted = {} -- monster id -> true once its kill was shared (onKill can fire for the last hitter and the top damage dealer)

local kill = {} -- N8: counted through SpireKills (one death callback), not the deprecated onKill event
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
SpireKills.on("SpireProgressKill", kill.onKill)

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
			primaryDamage = math.floor(primaryDamage * SpireStyle.healFactor(SpireStyle.get(healer)) * SpireGear.perkHealFactor(SpireGear.perkOf(healer)) + 0.5)
		end
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	-- Pathfinder (ST1): party members near a Pathfinder sometimes dodge a monster's attack completely
	if attacker and attacker:isMonster() and primaryDamage < 0 then
		local dodge = SpireStyle.partyDodgeAround(player)
		if dodge > 0 and math.random() < dodge then
			player:getPosition():sendMagicEffect(CONST_ME_BLOCKHIT)
			return 0, primaryType, 0, secondaryType
		end
	end
	local f = SpireStyle.takenFactor(SpireStyle.get(player), { shield = SpireProgress.holdsShield(player) })
	if f ~= 1 then -- (damage arrives negative: round the size, keep the sign; Bloodedge's minus makes f above 1)
		primaryDamage = (primaryDamage < 0 and -1 or 1) * math.floor(math.abs(primaryDamage) * f + 0.5)
		secondaryDamage = (secondaryDamage < 0 and -1 or 1) * math.floor(math.abs(secondaryDamage) * f + 0.5)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
guard:register()

-- The best dodge chance a Pathfinder in this player's party (within 7 tiles, the player too) gives
SpireStyle.PATHFINDER_RANGE = 7
function SpireStyle.partyDodgeAround(player)
	local party = player:getParty()
	local members = { player }
	if party then
		members = party:getMembers()
		table.insert(members, party:getLeader())
	end
	local best = 0
	for _, m in ipairs(members) do
		if m:getPosition():getDistance(player:getPosition()) <= SpireStyle.PATHFINDER_RANGE then
			best = math.max(best, SpireStyle.partyDodge(SpireStyle.get(m)))
		end
	end
	return best
end

-- Ironwall's extra health (ST1): a lasting condition, refreshed with the speed
local BODY_SUBID = 4611
function SpireStyle.applyBody(player)
	local bonus = SpireStyle.maxHealthBonus(SpireStyle.get(player))
	player:removeCondition(CONDITION_ATTRIBUTES, CONDITIONID_DEFAULT, BODY_SUBID)
	if bonus > 0 then
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, BODY_SUBID)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		c:setParameter(CONDITION_PARAM_STAT_MAXHITPOINTSPERCENT, 100 + math.floor(bonus * 100 + 0.5))
		player:addCondition(c)
	end
end

local login = CreatureEvent("SpireProgressLogin")
function login.onLogin(player)
	player:registerEvent("SpireStyleGuard")
	SpireStyle.migrate(player)
	SpireStyle.applySpeed(player)
	SpireStyle.applyBody(player)
	return true
end
login:register()
