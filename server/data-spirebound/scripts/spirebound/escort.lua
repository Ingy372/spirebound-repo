-- P9b The Last of the Patrol (FLOOR1_REVIEW.md: an escort): Patrolman Teodric waits in the Smugglers' Cellar under the
-- Bandit Road. Said "follow" to, he becomes the player's companion (the monster "Patrolman Teodric", a summon) and walks
-- with them; he keeps up on stairs and ladders (this script brings him along), and Captain Dorrow pays out when the
-- player reports with him close by. If he falls, the player goes back for him: the patrolman in the cellar is still there
-- (each climber frees their own copy of him).
SpireEscort = SpireEscort or { walking = {} }
local NAME = "Patrolman Teodric"
local QUEST = "q1_2b"
local NEAR_DORROW = 6

local function companion(player)
	for _, s in ipairs(player:getSummons()) do
		if s:getName() == NAME then
			return s
		end
	end
end

function SpireEscort.start(player, npc)
	local q = SpireQuests.get(QUEST)
	if SpireQuests.state(player, q) ~= 1 then
		return "Who are you? I only go with someone Captain Dorrow sent. Ask him for a {quest}."
	end
	if companion(player) then
		return "I'm right behind you."
	end
	if #player:getSummons() >= 1 then
		return "You've already someone with you. Send them off first, then come back for me."
	end
	local m = Game.createMonster(NAME, player:getPosition(), true, false)
	if not m then
		return "There's no room to stand. Step into the open."
	end
	m:setMaster(player)
	m:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	SpireEscort.walking[player:getId()] = true
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Patrolman Teodric follows you. Keep him alive and bring him to Captain Dorrow at Hearthgate's north gate.")
	return "Thank you. Lead on; I'll stay close."
end

-- the player is reporting to Dorrow with Teodric close by
function SpireEscort.arrived(player, npc)
	local m = companion(player)
	return m ~= nil and m:getPosition().z == npc:getPosition().z and m:getPosition():getDistance(npc:getPosition()) <= NEAR_DORROW
end

function SpireEscort.finish(player)
	local m = companion(player)
	if m then
		m:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
		m:remove()
	end
	SpireEscort.walking[player:getId()] = nil
end

-- keep a walker's patrolman with them (stairs, ladders and long runs)
local function bringAlong(player, m)
	local p, mp = player:getPosition(), m:getPosition()
	if mp.z == p.z and mp:getDistance(p) <= 7 then
		return
	end
	for _, d in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 }, { 1, 1 }, { -1, -1 }, { 1, -1 }, { -1, 1 } }) do
		local to = Position(p.x + d[1], p.y + d[2], p.z)
		local t = Tile(to)
		if t and t:getGround() and not t:hasProperty(CONST_PROP_BLOCKSOLID) and not t:getTopCreature() then
			m:teleportTo(to)
			return
		end
	end
	m:teleportTo(p)
end

local think = GlobalEvent("SpireEscortThink")
function think.onThink(interval)
	for pid in pairs(SpireEscort.walking) do
		local player = Player(pid)
		if not player then
			SpireEscort.walking[pid] = nil
		else
			local m = companion(player)
			if m then
				bringAlong(player, m)
			else
				SpireEscort.walking[pid] = nil
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Patrolman Teodric has fallen. Go back to the Smugglers' Cellar: he is still hiding there.")
			end
		end
	end
	return true
end
think:interval(2000)
think:register()

-- start-up: put the patrolman in the Smugglers' Cellar, beside the bandits who hold him (the first open spot by one of
-- the cellar's crowd spots)
local startup = GlobalEvent("SpireEscortStartup")
function startup.onStartup()
	local spot
	for _, k in ipairs({ "crowd_bandit_road_d_4", "crowd_bandit_road_d_5", "crowd_bandit_road_d_6" }) do
		local c = WorldPoints[k]
		spot = spot or (c and SpireQuestObjects and SpireQuestObjects.findSpot(c, 8))
	end
	if spot then
		Game.createNpc(NAME, spot, false, true)
		logger.info("[quest objects] teodric at {}, {}, {}", spot.x, spot.y, spot.z)
	else
		logger.warn("[quest objects] no room for Patrolman Teodric")
	end
	return true
end
startup:register()
