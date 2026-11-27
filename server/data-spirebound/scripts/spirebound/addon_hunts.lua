-- Addon hunts (roadmap AD5; adventure design 4.5, Q71). Three outfit-addon quests that were kill counts are now a hunt
-- for a named target: kill 15 of its kind in its ground while on the quest, and it comes out near you (the Journal's
-- step says so). The quest then counts the named target's kill as usual (SpireQuests.countKill, the whole party nearby).
-- Quest rows (hunt = { kind, count, ground }): lib/spirebound/quests.lua. The target stays 10 minutes, then leaves;
-- five more kills of its kind call it back.
SpireAddonHunts = SpireAddonHunts or { out = {} } -- out[player guid] = monster id

local STAYS = 600
local AGAIN = 5 -- kills to call it back after it left

local function kv(player)
	return player:kv():scoped("spirebound-hunts")
end

function SpireAddonHunts.count(player, q)
	return kv(player):get(q.id) or 0
end

-- Pure: does this kill count, and does it bring the target out? Returns counts?, appears?
function SpireAddonHunts.step(have, need, inGround, kindMatches, targetOut)
	if not kindMatches or not inGround or targetOut then
		return false, false
	end
	return true, have + 1 >= need
end

local function spawnFor(player, q)
	local here = player:getPosition()
	local best, bestD = nil, nil
	for _, s in ipairs(SpireRoamers.spots(q.hunt.ground)) do
		local d = math.max(math.abs(s.x - here.x), math.abs(s.y - here.y))
		if s.z == here.z and d >= 4 and (not bestD or d < bestD) then
			best, bestD = s, d
		end
	end
	local pos = best and Position(best.x, best.y, best.z) or here
	local m = Game.createMonster(q.target, pos, true, true)
	if not m then
		return nil
	end
	local guid, cid = player:getGuid(), player:getId()
	SpireAddonHunts.out[guid] = m:getId()
	pos:sendMagicEffect(CONST_ME_TELEPORT)
	local dir = SpireTreasure and SpireTreasure.direction(pos.x - here.x, pos.y - here.y) or "nearby"
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s has come out, %s of you! (%s)", q.target,
		dir == "here" and "right next to you" or ("to the " .. dir), q.name))
	m:setTarget(player)
	local mid = m:getId()
	addEvent(function()
		local c = Creature(mid)
		if c then
			c:getPosition():sendMagicEffect(CONST_ME_POFF)
			c:remove()
			local p = Player(cid)
			if p then
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s has slipped away. Drop %d more %s and it will be back.", q.target, AGAIN, q.hunt.plural))
			end
		end
		if SpireAddonHunts.out[guid] == mid then
			SpireAddonHunts.out[guid] = nil
		end
	end, STAYS * 1000)
	return m
end

function SpireAddonHunts.onKill(player, name)
	for _, q in ipairs(SpireQuests.list) do
		if q.hunt and q.hunt.kind == name and SpireQuests.state(player, q) == 1 then
			local outId = SpireAddonHunts.out[player:getGuid()]
			local targetOut = outId and Creature(outId) ~= nil
			local inGround = SpireRoamers.groundAt(player:getPosition()) == q.hunt.ground
			local have = SpireAddonHunts.count(player, q)
			local counts, appears = SpireAddonHunts.step(have, q.hunt.count, inGround, true, targetOut)
			if counts then
				kv(player):set(q.id, have + 1)
				if appears then
					kv(player):set(q.id, q.hunt.count - AGAIN) -- if it gets away, five more call it back
					spawnFor(player, q)
				elseif (have + 1) % 5 == 0 then
					player:sendTextMessage(MESSAGE_STATUS, string.format("%s: %d of %d %s. %s is getting restless.",
						q.name, have + 1, q.hunt.count, q.hunt.plural, q.target))
				end
			end
		end
	end
end

-- Every kill already reaches SpireQuests.countKill for each member of the party nearby: hook in there at start-up
-- (scripts/spirebound/quests.lua defines it after this file loads). No new kill event: N8 is moving those off the
-- engine's noisy kill event.
function SpireAddonHunts.hook()
	if SpireAddonHunts.hooked or not SpireQuests.countKill then
		return
	end
	SpireAddonHunts.hooked = true
	local plain = SpireQuests.countKill
	SpireQuests.countKill = function(player, name)
		plain(player, name)
		SpireAddonHunts.onKill(player, name)
	end
end

local startup = GlobalEvent("SpireAddonHuntsStartup")
function startup.onStartup()
	SpireAddonHunts.hook()
	return true
end
startup:register()
