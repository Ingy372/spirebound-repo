-- Wires the PvP rules (lib/spirebound/pvp.lua) into the game. Roadmap 2.1 - 2.4.

local recentAttacks = {} -- victimGuid -> { [attackerGuid] = time }
local lastSafe = {} -- playerId -> last position outside restricted zones
local graceUntil = {} -- playerId -> time (after login / respawn, guards leave you alone briefly)
SpireCleanup.add(function(pid, guid)
	lastSafe[pid], graceUntil[pid] = nil, nil
	recentAttacks[guid] = nil
	SpirePvP.damage[guid] = nil
	SpirePvP.aidUntil[guid] = nil
end)

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
	if zone == "arena" then
		-- equal-footing events: only opponents in the running event (no level rules)
		if SpireArena.current and SpireArena.canHit(SpireArena.current, a:getGuid(), v:getGuid()) then
			return RETURNVALUE_NOERROR
		end
		return RETURNVALUE_YOUMAYNOTATTACKTHISPLAYER
	end
	if zone == "siege" then
		if SpireSiege.current and SpireSiege.canHit(SpireSiege.current, a:getGuid(), v:getGuid()) then
			return RETURNVALUE_NOERROR
		end
		return RETURNVALUE_YOUMAYNOTATTACKTHISPLAYER
	end
	local ra = recentAttacks[a:getGuid()] or {}
	local ok, reason = SpirePvP.canAttack(
		{ level = a:getLevel(), skull = a:getSkull(), sanctuaryVsTheirGuild = sanctuaryActive(a, guildId(v)) },
		{ level = v:getLevel(), skull = v:getSkull(), attackedMeRecently = (ra[v:getGuid()] or 0) > os.time() - 60,
			sanctuaryVsMyGuild = sanctuaryActive(v, guildId(a)), aidedSkull = SpirePvP.aiding(v:getGuid(), os.time()) },
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
	if v and a and a ~= v and primaryType == COMBAT_HEALING and SpirePvP.isSkulled(v:getSkull()) and not SpirePvP.isSkulled(a:getSkull()) then
		SpirePvP.noteAid(a:getGuid(), os.time()) -- healing a skulled player costs your own protection for 5 minutes
		a:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You are helping a marked player: for 5 minutes, anyone may attack you.")
	end
	if v and a and a ~= v and primaryType ~= COMBAT_HEALING and SpirePvP.zoneAt(v:getPosition()) ~= "arena" and SpirePvP.zoneAt(v:getPosition()) ~= "siege" then
		local now = os.time()
		local list = recentAttacks[v:getGuid()] or {}
		list[a:getGuid()] = now
		recentAttacks[v:getGuid()] = list
		SpirePvP.noteDamage(v:getGuid(), a:getGuid(), math.max(0, primaryDamage) + math.max(0, secondaryDamage), now)
		local vinfo = Difficulty.playerInfo(v)
		local n = SpirePvP.outnumberedCount(v:getGuid(), v:getMaxHealth(), now, function(g)
			local other = Player(g)
			return other ~= nil and Difficulty.countsAsOutsidePlayer(vinfo, Difficulty.playerInfo(other))
		end)
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
	if SpirePvP.isMurderer(player) then
		SpirePvP.scope(player):set("outlawRespawn", true) -- murderers wake in the Outlaw Camp, not in town
	end
	local parts = SpirePvP.participants(player:getGuid(), k:getGuid(), player:getMaxHealth(), now)
	SpirePvP.damage[player:getGuid()] = nil
	local target = Difficulty.playerInfo(player)
	target.partiedRecently = SpirePvP.partnersOf(player:getGuid(), now)
	-- Bounty on the victim: shared by everyone in the kill who may claim it, by damage
	local bounty = SpireBounty.get(player:getGuid())
	if (bounty.total or 0) > 0 then
		local shares = SpirePvP.bountyShares(bounty.total, parts, function(g)
			local p = Player(g)
			return p ~= nil and (SpireBounty.validClaimer(target, Difficulty.playerInfo(p)))
		end)
		local paid = false
		for g, amount in pairs(shares) do
			local p = Player(g)
			if p and amount > 0 then
				p:setBankBalance(p:getBankBalance() + amount)
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Your share of the bounty on %s: %d gold (to your bank).", player:getName(), amount))
				paid = true
			end
		end
		if paid then
			SpireBounty.clear(player:getGuid())
			Game.broadcastMessage(string.format("The %d gold bounty on %s has been collected!", bounty.total, player:getName()), MESSAGE_EVENT_ADVANCE)
		else
			local _, why = SpireBounty.validClaimer(target, Difficulty.playerInfo(k))
			k:sendTextMessage(MESSAGE_EVENT_ADVANCE, "No bounty for you on " .. player:getName() .. " (" .. (why or "not allowed") .. ").")
		end
	end
	-- Unjust kills: everyone who took part, not only the killing blow
	local victimClean = not SpirePvP.isSkulled(player:getSkull()) and not SpirePvP.aiding(player:getGuid(), now)
	local guildsHit = {}
	for _, part in ipairs(parts) do
		local p = Player(part.guid)
		if p then
			local victimAttackedThem = ((recentAttacks[p:getGuid()] or {})[player:getGuid()] or 0) > now - 60
			local atWar = guildId(p) ~= 0 and guildId(player) ~= 0 and SpireWar.active(guildId(p), guildId(player))
			local unjust = (p == k and unjustified) or (p ~= k and victimClean and not victimAttackedThem and not atWar)
			if unjust then
				SpirePvP.creditUnjust(p, player, zone, now)
				if guildId(p) ~= 0 then
					guildsHit[guildId(p)] = p:getGuild():getName()
				end
			end
		end
	end
	-- Sanctuary against a guild that keeps killing you (outside wars): every guild that took part counts
	for kg, gname in pairs(guildsHit) do
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
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Sanctuary: " .. gname .. " can't attack you for 30 minutes.")
			logger.info("[Spirebound] Sanctuary for {} against guild {}", player:getName(), gname)
		end
	end
	return true
end

-- One unjust kill for player k: frags, guard mark, skull
function SpirePvP.creditUnjust(k, player, zone, now)
	local w = SpirePvP.unjustWeight(k:getLevel(), player:getLevel(), zone, Difficulty.get(player) == Difficulty.DEATHGAME)
	if w <= 0 then
		return
	end
	local ks = SpirePvP.scope(k)
	local frags = ks:get("frags") or {}
	for _ = 1, w do
		table.insert(frags, { t = now, w = 1 })
	end
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
		k:setSkullTime(SpirePvP.skullSeconds(SKULL_BLACK)) -- seconds remaining, not a calendar time
		Game.broadcastMessage(k:getName() .. " now carries a black mark for serial murder.", MESSAGE_EVENT_ADVANCE)
	elseif skull == SKULL_RED and k:getSkull() ~= SKULL_BLACK then
		k:setSkull(SKULL_RED)
		k:setSkullTime(SpirePvP.skullSeconds(SKULL_RED))
		k:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You are now a murderer (red). Towns, shops and boss rooms are closed to you, and death will cost you everything you carry.")
	end
	if skull and SpireBounty then
		SpireBounty.onMurderer(k)
	end
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
	-- remember party partners for 24 hours: they can't collect bounties on each other (R7)
	local guids = { player:getGuid() }
	if p:getLeader() then
		table.insert(guids, p:getLeader():getGuid())
	end
	for _, m in ipairs(p:getMembers()) do
		table.insert(guids, m:getGuid())
	end
	SpirePvP.notePartners(guids, os.time())
	return true
end
party:register()

local login = CreatureEvent("SpirePvPLogin")
function login.onLogin(player)
	player:registerEvent("SpirePvPHits")
	player:registerEvent("SpirePvPDeath")
	graceUntil[player:getId()] = os.time() + 30
	local s = SpirePvP.scope(player)
	if s:get("outlawRespawn") then -- a murderer who died wakes in the Outlaw Camp, outside every town
		s:remove("outlawRespawn")
		if WorldPoints.outlaw_camp then
			player:teleportTo(WorldPoints.outlaw_camp)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Murderers are not welcome in the temple. You wake in the Outlaw Camp.")
		end
	end
	return true
end
login:register()
