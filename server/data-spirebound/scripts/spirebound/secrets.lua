-- Secret triggers, rewards and announcements (lib/spirebound/secrets.lua).

local function key(pos)
	return pos.x .. ":" .. pos.y .. ":" .. pos.z
end


local REWARDS = {}
REWARDS.underkeep = function(player, first)
	local entry = WorldPoints.underkeep_entry
	if entry then
		player:teleportTo(entry)
		entry:sendMagicEffect(CONST_ME_TELEPORT)
	elseif first then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The grate is rusted shut, but you hear water and voices far below. (The Underkeep opens in a later update.)")
	end
end
REWARDS.north_crack = function(player, first)
	local exit = WorldPoints.north_crack_exit
	if exit then
		player:teleportTo(exit)
		exit:sendMagicEffect(CONST_ME_POFF)
	end
end
REWARDS.old_tusk = function(player, first)
	-- Old Tusk is one of the hidden mini-bosses now: SpireTrophies.onSecret wakes him (scripts/spirebound/minibosses.lua)
end
REWARDS.sealed_shrine = function(player, first)
	if not first then
		return
	end
	-- the guardians wake for each character who finds it; everyone who fights them gets the shrine's gift (below)
	local ids = {}
	for _ = 1, 2 do
		local m = Game.createMonster("Bandit Captain", player:getPosition(), true, false)
		if m then
			m:registerEvent("SpireShrineGuardianDeath")
			table.insert(ids, m:getId())
		end
	end
	SpireSecrets.shrineFight = SpireSecrets.shrineFight or {}
	for _, id in ipairs(ids) do
		SpireSecrets.shrineFight[id] = ids
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The shrine's guardians wake!")
end

-- What a character keeps from a secret (adventure layer 4.1): given once, each piece only if not had yet, so
-- characters who found a secret before these rewards existed get them at their next login (catchUp below).
function SpireSecrets.giveKeeps(player, secret, quiet)
	local given = player:kv():scoped("spirebound-secret-keeps")
	local function once(key, fn)
		if not given:get(secret.id .. ":" .. key) then
			if fn() ~= false then
				given:set(secret.id .. ":" .. key, os.time())
			end
		end
	end
	if secret.title then
		once("title", function()
			player:kv():scoped("spirebound-titles"):set(secret.title, os.time())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. secret.title .. ".")
		end)
	end
	local r = secret.reward
	if type(r) ~= "table" then
		return
	end
	if r.title then
		once("title_r", function()
			player:kv():scoped("spirebound-titles"):set(r.title, os.time())
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You earned the title " .. r.title .. ".")
		end)
	end
	if r.aura and SpireAuras then
		once("aura", function() SpireAuras.give(player, r.aura) end)
	end
	if r.keepsake and SpireKeepsakes then
		once("keepsake", function() return SpireKeepsakes.give(player, r.keepsake) or SpireKeepsakes.has(player, r.keepsake) end)
	end
	if r.gear and SpireGear.giveSecretGear then
		once("gear", function() return SpireGear.giveSecretGear(player, r.gear) end)
	end
	if not quiet then
		for _, it in ipairs(r.items or {}) do
			SpireGive.reward(player, it[1], it[2]) -- never onto the floor when the backpack is full
		end
		if r.text then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, r.text)
		end
	end
end

local function giveReward(player, secret, first)
	local r = secret.reward
	if type(r) == "string" then
		REWARDS[r](player, first)
	end
	if not first then
		return
	end
	-- the purse, once per account, for every secret (Jay, 2026-11-27)
	if SpireSecrets.goldPaid(player:getAccountId(), secret.id) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Another of your characters already took this secret's gold.")
	else
		SpireSecrets.markGoldPaid(player:getAccountId(), secret.id)
		local gold = SpireSecrets.purse(secret.floor)
		local bag, bank = SpireGive.gold(player, gold) -- the backpack; the bank only if it is full (Q76)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%d gold, %s.", gold, SpireGive.goldWhere(bag, bank)))
	end
	SpireSecrets.giveKeeps(player, secret, false)
end

SpireSecrets.KEEPS_SINCE = 1795791600 -- 2026-11-27 15:00 UTC: the adventure layer's secret rewards went live

-- Characters who found a secret before its keepsake existed get it at login (adventure layer 4.1)
function SpireSecrets.catchUp(player)
	local given = player:kv():scoped("spirebound-secret-keeps")
	for _, secret in ipairs(SpireSecrets.foundList(player)) do
		SpireSecrets.giveKeeps(player, secret, true)
		-- the Sealed Shrine's gift went to its fighters; those who found it before the gift existed get it now
		-- (only for finds before the gift existed: a find since then earns it in the fight, not by walking away)
		local foundAt = player:kv():scoped("spirebound-secrets"):get(secret.id) or 0
		if secret.reward == "sealed_shrine" and foundAt < SpireSecrets.KEEPS_SINCE and not given:get(secret.id .. ":gear") and SpireGear.giveSecretGear
			and SpireGear.giveSecretGear(player, "shrinekeepers_pendant") then
			given:set(secret.id .. ":gear", os.time())
		end
	end
end

local catchUp = CreatureEvent("SpireSecretKeepsLogin")
function catchUp.onLogin(player)
	local pid = player:getId()
	addEvent(function()
		local p = Player(pid)
		if p then
			SpireSecrets.catchUp(p)
		end
	end, 1500)
	return true
end
catchUp:register()

-- The Sealed Shrine's gift: when the last guardian of a fight falls, everyone who hurt either of them gets it
local guardianDeath = CreatureEvent("SpireShrineGuardianDeath")
function guardianDeath.onDeath(creature)
	local fight = SpireSecrets.shrineFight and SpireSecrets.shrineFight[creature:getId()]
	if not fight then
		return true
	end
	local credit = SpireSecrets.shrineCredit or {}
	SpireSecrets.shrineCredit = credit
	credit[fight] = credit[fight] or {}
	for cid in pairs(creature:getDamageMap()) do
		if Player(cid) then
			credit[fight][cid] = true
		end
	end
	SpireSecrets.shrineFight[creature:getId()] = nil
	for _, id in ipairs(fight) do
		if SpireSecrets.shrineFight[id] and Creature(id) then
			return true -- the other guardian still stands
		end
	end
	for cid in pairs(credit[fight]) do
		local p = Player(cid)
		if p and SpireGear.giveSecretGear then
			local given = p:kv():scoped("spirebound-secret-keeps")
			if not given:get("s7:gear") and SpireGear.giveSecretGear(p, "shrinekeepers_pendant") then
				given:set("s7:gear", os.time())
			end
		end
	end
	credit[fight] = nil
	return true
end
guardianDeath:register()

local function trigger(player, secret)
	if secret.night and not SpireSecrets.isNight(SpireSecrets.gameHour()) then
		return
	end
	local first = not SpireSecrets.hasFound(player, secret.id)
	if first then
		local count = SpireSecrets.record(player, secret)
		SpirePath.progress(player, "secret", 1)
		SpireChronicle.add(player, "secret", 1)
		if secret.id == "s1" then -- the way into the Underkeep (scripts/spirebound/underkeep.lua)
			SpireChronicle.add(player, "underkeep", 1)
		end
		local by = SpireSecrets.publicBy(secret.id)
		local msg = "You discovered a secret: " .. secret.name .. "!"
		if by then
			msg = msg .. " (Everyone knows it already: " .. by .. " sold it.)"
		else
			msg = msg .. " Vesper, the information broker in Hearthgate, would pay " .. SpireSecrets.payout(secret) .. " gold for it. Or keep it to yourself."
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, msg)
		player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_BLUE)
		logger.info("[Spirebound] {} discovered {} ({} found)", player:getName(), secret.id, count)
		-- adventure layer 4.2/4.3: the season's first find is heard server-wide (the floor only, never where); later
		-- finds are silent so a kept secret stays kept
		if SpireFinds and SpireFinds.first("secret", secret.id, { player }, SpireFinds.secretLabel(secret)) then
			SpireFinds.announce("secret", {}, nil, secret.floor)
		end
		if SpireDiscoveries then
			SpireDiscoveries.checkMilestones(player, secret.floor)
		end
	end
	giveReward(player, secret, first)
	if SpireTrophies and SpireTrophies.onSecret then
		SpireTrophies.onSecret(player, secret, first)
	end
end

local startup = GlobalEvent("SpireSecretsStartup")
function startup.onStartup()
	SpireRemix.applySecrets(SpireSecrets.list, SpireSeason.current()) -- season remix (roadmap 8.2)
	for _, s in ipairs(SpireSecrets.list) do
		local pos = WorldPoints[s.point or ("secret_" .. s.id)]
		if pos then
			SpireSecrets.byPos[key(pos)] = s
		elseif s.floor == 1 then
			logger.warn("[Spirebound] secret {} has no trigger point on the map", s.id)
		end
	end
	return true
end
startup:register()

-- R17: a secret triggers the moment you step on its tile (it used to be a twice-a-second check, which a fast walker or
-- a cavebot could step over)
SpireSecrets.onStep = function(player, pos)
	local s = SpireSecrets.byPos[key(pos)]
	if s and not (SpireCavebot and SpireCavebot.blocksRewards(player)) then
		trigger(player, s)
		return true
	end
	return false
end
local step = MoveEvent()
function step.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if player then
		SpireSecrets.onStep(player, position)
	end
	return true
end
local registered = 0
for name, pos in pairs(WorldPoints) do
	if name:find("^secret_") or name:find("^f%d+_secret_") then
		step:position(pos)
		registered = registered + 1
	end
end
step:type("stepin")
step:register()
SpireSecrets.stepTiles = registered
