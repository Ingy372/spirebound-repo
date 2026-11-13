-- Secret triggers, rewards and announcements (lib/spirebound/secrets.lua).

local function key(pos)
	return pos.x .. ":" .. pos.y .. ":" .. pos.z
end

local lastTusk = 0

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
	if os.time() - lastTusk < 30 * 60 then
		if first then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Fresh tracks in the mud. Old Tusk was here recently.")
		end
		return
	end
	lastTusk = os.time()
	local m = Game.createMonster("Old Tusk", WorldPoints.old_tusk_spawn, false, true)
	if m then
		m:say("HRRROOONK!", TALKTYPE_MONSTER_YELL)
	end
end
REWARDS.sealed_shrine = function(player, first)
	if not first then
		return
	end
	for _ = 1, 2 do
		Game.createMonster("Bandit Captain", player:getPosition(), true, false)
	end
	player:addMoney(1000)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The shrine's chest holds 1,000 gold, and its guardians wake!")
end

local function giveReward(player, secret, first)
	local r = secret.reward
	if type(r) == "string" then
		REWARDS[r](player, first)
		return
	end
	if not first or type(r) ~= "table" then
		return
	end
	if r.gold then
		if SpireSecrets.goldPaid(player:getAccountId(), secret.id) then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Another of your characters already took this secret's gold.")
		else
			SpireSecrets.markGoldPaid(player:getAccountId(), secret.id)
			player:addMoney(r.gold)
		end
	end
	for _, it in ipairs(r.items or {}) do
		player:addItem(it[1], it[2])
	end
	if r.text then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, r.text)
	end
end

local function trigger(player, secret)
	if secret.night and not SpireSecrets.isNight(SpireSecrets.gameHour()) then
		return
	end
	local first = not SpireSecrets.hasFound(player, secret.id)
	if first then
		local count = SpireSecrets.record(player, secret)
		SpirePath.progress(player, "secret", 1)
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
	end
	giveReward(player, secret, first)
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
