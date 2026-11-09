-- Wires the PvP rules (lib/spirebound/pvp.lua) into the game. Roadmap 2.1 - 2.4.

local recentAttacks = {} -- victimGuid -> { [attackerGuid] = time }
local lastSafe = {} -- playerId -> last position outside restricted zones
local graceUntil = {} -- playerId -> time (after login / respawn, guards leave you alone briefly)

local function guildId(p)
	local g = p:getGuild()
	return g and g:getId() or 0
end

local function sanctuaryActive(victim, attackerGuild)
	if attackerGuild == 0 then
		return false
	end
	local s = SpirePvP.scope(victim):get("sanctuary") or {}
	return (s[tostring(attackerGuild)] or 0) > os.time()
end

-- Who may attack whom
local target = EventCallback("SpirePvPTarget")
function target.creatureOnTargetCombat(creature, victim)
	local a = creature and (creature:getPlayer() or (creature:getMaster() and creature:getMaster():getPlayer()))
	local v = victim and victim:getPlayer()
	if not a or not v or a == v then
		return RETURNVALUE_NOERROR
	end
	local zone = SpirePvP.zoneAt(v:getPosition())
	local ra = recentAttacks[a:getGuid()] or {}
	local ok, reason = SpirePvP.canAttack(
		{ level = a:getLevel(), skull = a:getSkull(), sanctuaryVsTheirGuild = sanctuaryActive(a, guildId(v)) },
		{ level = v:getLevel(), skull = v:getSkull(), attackedMeRecently = (ra[v:getGuid()] or 0) > os.time() - 60,
			sanctuaryVsMyGuild = sanctuaryActive(v, guildId(a)) },
		zone)
	if not ok then
		if creature:isPlayer() then
			creature:sendCancelMessage(reason)
		end
		return RETURNVALUE_YOUMAYNOTATTACKTHISPLAYER
	end
	return RETURNVALUE_NOERROR
end
target:register()

-- Remember who hit whom (for "fight back" and the outnumbered shield)
local hits = CreatureEvent("SpirePvPHits")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local v = creature:getPlayer()
	local a = attacker and (attacker:getPlayer() or (attacker:getMaster() and attacker:getMaster():getPlayer()))
	if v and a and a ~= v and primaryType ~= COMBAT_HEALING then
		local now = os.time()
		local list = recentAttacks[v:getGuid()] or {}
		list[a:getGuid()] = now
		recentAttacks[v:getGuid()] = list
		local n = 0
		for _, t in pairs(list) do
			if now - t <= SpirePvP.OUTNUMBER_WINDOW then
				n = n + 1
			end
		end
		local pct = SpirePvP.outnumberedReduction(n)
		if pct > 0 then
			primaryDamage = math.floor(primaryDamage * (1 - pct / 100))
			secondaryDamage = math.floor(secondaryDamage * (1 - pct / 100))
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
hits:register()

-- Unjust kills, skulls, guard marks, Sanctuary
local death = CreatureEvent("SpirePvPDeath")
function death.onDeath(player, corpse, killer, mostDamageKiller, unjustified, mostDamageUnjustified)
	graceUntil[player:getId()] = os.time() + 30
	local k = killer and (killer:getPlayer() or (killer:getMaster() and killer:getMaster():getPlayer()))
	if not k or k == player then
		return true
	end
	local now = os.time()
	local zone = SpirePvP.zoneAt(player:getPosition())
	-- Bounty on the victim?
	local bounty = SpireBounty.get(player:getGuid())
	if (bounty.total or 0) > 0 then
		local ok, why = SpireBounty.validClaimer(Difficulty.playerInfo(player), Difficulty.playerInfo(k))
		if ok then
			k:setBankBalance(k:getBankBalance() + bounty.total)
			SpireBounty.clear(player:getGuid())
			Game.broadcastMessage(string.format("%s collected the %d gold bounty on %s!", k:getName(), bounty.total, player:getName()), MESSAGE_EVENT_ADVANCE)
		else
			k:sendTextMessage(MESSAGE_EVENT_ADVANCE, "No bounty for you on " .. player:getName() .. " (" .. why .. ").")
		end
	end
	-- Sanctuary against a guild that keeps killing you (outside wars)
	local kg = guildId(k)
	if kg ~= 0 and unjustified then
		local s = SpirePvP.scope(player)
		local gk = s:get("guildKills") or {}
		local list = gk[tostring(kg)] or {}
		table.insert(list, now)
		gk[tostring(kg)] = list
		s:set("guildKills", gk)
		if SpirePvP.sanctuaryDue(list, now) then
			local sanct = s:get("sanctuary") or {}
			sanct[tostring(kg)] = now + SpirePvP.SANCTUARY_TIME
			s:set("sanctuary", sanct)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Sanctuary: " .. k:getGuild():getName() .. " can't attack you for 30 minutes.")
			logger.info("[Spirebound] Sanctuary for {} against guild {}", player:getName(), k:getGuild():getName())
		end
	end
	if not unjustified then
		return true
	end
	local w = SpirePvP.unjustWeight(k:getLevel(), player:getLevel(), zone, Difficulty.get(player) == Difficulty.DEATHGAME)
	if w <= 0 then
		return true
	end
	local ks = SpirePvP.scope(k)
	local frags = ks:get("frags") or {}
	for _ = 1, w do
		table.insert(frags, { t = now, w = 1 })
	end
	-- keep only the last 30 days
	local kept = {}
	for _, f in ipairs(frags) do
		if now - f.t <= 30 * 86400 then
			table.insert(kept, f)
		end
	end
	ks:set("frags", kept)
	if zone == "guarded" then
		ks:set("guardMarkUntil", now + SpirePvP.GUARD_MARK)
		k:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You murdered someone near town. The guards will hunt you for 30 minutes.")
	end
	local skull = SpirePvP.skullFor(kept, now)
	if skull == SKULL_BLACK then
		k:setSkull(SKULL_BLACK)
		k:setSkullTime(now + SpirePvP.BLACK_DAYS * 86400)
		Game.broadcastMessage(k:getName() .. " now carries a black mark for serial murder.", MESSAGE_EVENT_ADVANCE)
	elseif skull == SKULL_RED and k:getSkull() ~= SKULL_BLACK then
		k:setSkull(SKULL_RED)
		k:setSkullTime(now + SpirePvP.RED_DAYS * 86400)
		k:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You are now a murderer (red). Towns, shops and boss rooms are closed to you, and death will cost you everything you carry.")
	end
	if skull and SpireBounty then
		SpireBounty.onMurderer(k)
	end
	return true
end
death:register()

-- Murderers and guard-marked killers are thrown out of towns and boss rooms; under-50s are kept out of Contested/Deadzone
local tick = GlobalEvent("SpirePvPTick")
function tick.onThink(interval)
	local now = os.time()
	for _, p in ipairs(Game.getPlayers()) do
		local pid = p:getId()
		local pos = p:getPosition()
		local zone = SpirePvP.zoneAt(pos)
		local murderer = SpirePvP.isMurderer(p)
		local marked = (SpirePvP.scope(p):get("guardMarkUntil") or 0) > now
		local graced = (graceUntil[pid] or 0) > now
		local out = nil
		if zone == "town" and (murderer or marked) and not graced and not p:getGroup():getAccess() then
			out = "The town guards drive you out!"
			p:addHealth(-math.floor(p:getMaxHealth() * 0.25))
		elseif zone == "bossroom" and murderer then
			out = "Murderers may not challenge the tower's guardians."
		elseif (zone == "contested" or zone == "deadzone") and p:getLevel() < SpirePvP.NEWBIE_LEVEL and not p:getGroup():getAccess() then
			out = "This ground is too dangerous below level " .. SpirePvP.NEWBIE_LEVEL .. "."
		end
		if out and lastSafe[pid] then
			p:teleportTo(lastSafe[pid])
			p:getPosition():sendMagicEffect(CONST_ME_POFF)
			p:sendCancelMessage(out)
		elseif not out and zone ~= "town" and zone ~= "bossroom" and zone ~= "contested" and zone ~= "deadzone" then
			lastSafe[pid] = pos
		elseif not out and zone == "town" and not murderer and not marked then
			lastSafe[pid] = pos
		end
	end
	return true
end
tick:interval(1000)
tick:register()

-- Black skulls can't join parties; murderers can't trade with NPCs (checked in the NPC files)
local party = EventCallback("SpirePvPParty")
function party.partyOnJoin(p, player)
	if player:getSkull() == SKULL_BLACK then
		player:sendCancelMessage("Nobody will party with a black-marked murderer.")
		return false
	end
	return true
end
party:register()

local login = CreatureEvent("SpirePvPLogin")
function login.onLogin(player)
	player:registerEvent("SpirePvPHits")
	player:registerEvent("SpirePvPDeath")
	graceUntil[player:getId()] = os.time() + 30
	return true
end
login:register()
