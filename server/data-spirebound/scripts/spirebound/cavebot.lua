-- Receives the client's cavebot on/off reports and applies the loot cut. (XP cut: difficulty_events.lua;
-- secrets: secrets.lua; boss rooms: below.)

local function parseOn(buffer)
	if buffer:find('"t"%s*:%s*"bot"') then
		return buffer:find('"on"%s*:%s*true') ~= nil
	end
	return nil
end

local opcode = CreatureEvent("SpireClientOpcode")
function opcode.onExtendedOpcode(player, op, buffer)
	if op ~= SpireClient.OPCODE then
		return true
	end
	local on = parseOn(buffer)
	if on ~= nil then
		local was = SpireCavebot.state[player:getGuid()]
		SpireCavebot.setState(player:getGuid(), on, os.time())
		if (was and was.on) ~= on then
			logger.info("[Spirebound] cavebot {} for {}", on and "ON" or "OFF", player:getName())
			player:sendTextMessage(MESSAGE_STATUS, on and "Cavebot on: you earn 45% experience and half the loot while it runs." or "Cavebot off. Full rewards return in 10 minutes.")
		end
	end
	return true
end
opcode:register()

local login = CreatureEvent("SpireCavebotLogin")
function login.onLogin(player)
	player:registerEvent("SpireClientOpcode")
	return true
end
login:register()

-- Loot cut: each item in the corpse has a 50% chance to vanish (stacks are halved instead)
local loot = EventCallback("SpireCavebotLoot")
function loot.monsterPostDropLoot(monster, corpse)
	local player = Player(corpse:getCorpseOwner())
	if not player or not SpireCavebot.botting(player) then
		return
	end
	for i = corpse:getSize() - 1, 0, -1 do
		local item = corpse:getItem(i)
		if item then
			if item:isStackable() and item:getCount() > 1 then
				item:transform(item:getId(), math.max(1, math.floor(item:getCount() * SpireCavebot.LOOT)))
			elseif math.random() > SpireCavebot.LOOT then
				item:remove()
			end
		end
	end
end
loot:register()

-- R15: kills and positions for the standing-still rule and the suspicion log
local kills = CreatureEvent("SpireBotWatchKill")
function kills.onKill(player, target)
	if target and target:isMonster() and not target:getMaster() then
		local guid = player:getGuid()
		local rec = SpireCavebot.track[guid] or {}
		SpireCavebot.track[guid] = rec
		local now = os.time()
		SpireCavebot.notePos(rec, player:getPosition(), now)
		SpireCavebot.noteKill(rec, now)
		if rec.huntStart and now - rec.huntStart >= SpireCavebot.LONG_HUNT and not rec.flagged then
			rec.flagged = true
			logger.info("[Spirebound] bot watch: {} has hunted for {} hours without a 15-minute break", player:getName(),
				math.floor((now - rec.huntStart) / 3600))
		end
	end
	return true
end
kills:register()

local watchLogin = CreatureEvent("SpireBotWatchLogin")
function watchLogin.onLogin(player)
	player:registerEvent("SpireBotWatchKill")
	return true
end
watchLogin:register()

-- Boss rooms refuse cavebot users
local tick = GlobalEvent("SpireCavebotTick")
function tick.onThink(interval)
	local now = os.time()
	for _, p in ipairs(Game.getPlayers()) do
		local rec = SpireCavebot.track[p:getGuid()]
		if rec then
			local was = SpireCavebot.standingBot(rec, now)
			SpireCavebot.notePos(rec, p:getPosition(), now)
			if not rec.warned and SpireCavebot.standingBot(rec, now) then
				rec.warned = true
				logger.info("[Spirebound] bot watch: {} has hunted for 10 minutes without moving", p:getName())
			elseif was and not SpireCavebot.standingBot(rec, now) then
				rec.warned = nil
			end
		end
		if SpireCavebot.active(p) and SpirePvP.zoneAt(p:getPosition()) == "bossroom" then
			local t = p:getTown()
			p:teleportTo(t:getTemplePosition())
			p:sendCancelMessage("The tower's guardians won't face a cavebot. Switch it off and wait 10 minutes.")
		elseif SpireCavebot.active(p) and SpireCrowd.caveAt(p:getPosition()) then
			-- the party caves are for teams at the keyboard (Q32): back up the stairs
			p:teleportTo(SpireCrowd.caveAt(p:getPosition()).exit)
			p:sendCancelMessage("The caves are for parties at the keyboard. Switch the cavebot off and wait 10 minutes.")
		end
	end
	return true
end
tick:interval(2000)
tick:register()
