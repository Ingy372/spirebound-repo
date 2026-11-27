-- The Arrival Yard tutorial (roadmap R11, REVIEW 1.2). Four gates on the path; each opens once the new character has
-- done one small thing: beaten a rat, looted it, read the list of skills and spells (sword skills themselves need a
-- vocation, which only the Registrar at the end gives), and drunk a potion. Characters with no vocation can't
-- leave the yard: the Registrar sends them to Hearthgate once they choose a path.

SpireTutorial = { STEPS = { "kill", "loot", "spells", "potion" } }
SpireTutorial.HELP = {
	kill = "Beat a rat first: they are in the cellar of the Old Granary, the timber house just before this gate (take its stairs down). Click a rat in the Battle List (Ctrl+B) or right-click it and choose Attack.",
	loot = "Open a rat's body (right-click it, then drag the cheese into your backpack) before you go on. If the body is gone, beat another rat.",
	spells = "Say !spells to see the skills and spells each path will teach you.",
	potion = "Drink the health potion in your backpack: right-click it, choose 'Use with...', then click yourself.",
}

local function scope(player)
	return player:kv():scoped("spirebound-tutorial")
end

SpireTutorial.CHEESE = 3607 -- every Pen Rat drops one

function SpireTutorial.done(player, step)
	if step == "potion" and scope(player):get(step) ~= true and SpireTutorial.potionDrunk(player) then
		scope(player):set("potion", true)
	end
	if step == "loot" and scope(player):get(step) ~= true and player:getItemCount(SpireTutorial.CHEESE) > 0 then
		scope(player):set("loot", true) -- carrying a rat's cheese counts as looting (autoloot too)
	end
	return scope(player):get(step) == true
end

function SpireTutorial.mark(player, step)
	if player:getVocation():getId() ~= 0 or SpireTutorial.done(player, step) then
		return false
	end
	scope(player):set(step, true)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Well done! The next gate on the path is open.")
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
	return true
end

-- Pure: a gate opens when its step and every step before it are done. Returns open, and the first missing step.
-- done = function(step) -> bool
function SpireTutorial.gateOpen(step, done)
	for _, s in ipairs(SpireTutorial.STEPS) do
		if not done(s) then
			return false, s
		end
		if s == step then
			return true
		end
	end
	return true
end

local function inBox(pos, nw, se)
	return nw ~= nil and se ~= nil and pos.z == nw.z and pos.x >= nw.x and pos.x <= se.x and pos.y >= nw.y and pos.y <= se.y
end

-- the yard, and the Old Granary's rat cellar under it (Jay 2026-11-26)
function SpireTutorial.inYard(pos)
	return inBox(pos, WorldPoints.tutorial_yard_nw, WorldPoints.tutorial_yard_se)
		or inBox(pos, WorldPoints.tutorial_cellar_nw, WorldPoints.tutorial_cellar_se)
end

-- Grok session 2: a tester saw the cheese in the loot message but never got it into the backpack (the body decayed
-- while the client lagged), and the loot gate held them for ten minutes. Now the third try at the loot gate with no
-- cheese hands one over and opens it. The first two tries still teach opening a body.
SpireTutorial.PITY_TRIES = 3
local lootTries = {} -- player id -> tries at the loot gate
function SpireTutorial.pity(player)
	local pid = player:getGuid() -- the same across logins (Grok session 3 relogged and the count started over)
	lootTries[pid] = (lootTries[pid] or 0) + 1
	if lootTries[pid] < SpireTutorial.PITY_TRIES or not SpireTutorial.done(player, "kill") then
		return false
	end
	lootTries[pid] = nil
	SpireGive.item(player, SpireTutorial.CHEESE, 1)
	SpireTutorial.mark(player, "loot")
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "A rat's cheese turns up in the grass at your feet, and you pocket it. Next time, open the body: "
		.. "right-click it and drag what it carried into your backpack.")
	return true
end

-- The gates (Claude's playtest 2026-11-25, C1; Jay: "use a gate of expertise"): a closed timber door on each gate tile,
-- placed at start-up. Like Canary's level doors, nobody can walk onto a closed door; clicking it opens it and moves you
-- through only when the step is done, and it closes behind you. (The old open gap pushed walkers back with a teleport;
-- the engine rate-limits teleports, so after ~20 s of bumping a walker slipped through, and every bump repeated the
-- hint.)
SpireTutorial.GATE_AID = 47200
SpireTutorial.DOOR_CLOSED, SpireTutorial.DOOR_OPEN = 1638, 1639 -- the timber fence's own door (an ordinary door to the engine)
SpireTutorial.HINT_GAP = 8 -- seconds between two hints to the same player

local function gateStep(pos)
	for _, step in ipairs(SpireTutorial.STEPS) do
		for i = 1, 2 do
			local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
			if p and p == pos then
				return step
			end
		end
	end
end

local function check(player, step)
	return SpireTutorial.gateOpen(step, function(s)
		return SpireTutorial.done(player, s)
	end)
end

local lastHint = {} -- player guid -> when a gate last explained itself
local function hint(player, text)
	local pid = player:getGuid()
	if (lastHint[pid] or 0) + SpireTutorial.HINT_GAP <= os.time() then
		lastHint[pid] = os.time()
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
		return true
	end
	return false
end

local gateStartup = GlobalEvent("SpireTutorialGates")
function gateStartup.onStartup()
	for _, step in ipairs(SpireTutorial.STEPS) do
		for i = 1, 2 do
			local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
			local tile = p and Tile(p)
			if tile then
				local door = tile:getItemById(SpireTutorial.DOOR_CLOSED) or tile:getItemById(SpireTutorial.DOOR_OPEN)
					or Game.createItem(SpireTutorial.DOOR_CLOSED, 1, p)
				if door then
					if door:getId() ~= SpireTutorial.DOOR_CLOSED then
						door:transform(SpireTutorial.DOOR_CLOSED)
					end
					door:setActionId(SpireTutorial.GATE_AID)
					door:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A yard gate. Click it to pass: it opens once you have done what the sign beside it says.")
				end
			end
		end
	end
	return true
end
gateStartup:register()

local gateUse = Action()
function gateUse.onUse(player, item, fromPosition, target, toPosition)
	local pos = item:getPosition()
	local step = gateStep(pos)
	if not step then
		return false
	end
	local ppos = player:getPosition()
	local goingBack = ppos.x > pos.x
	if not goingBack and not player:getGroup():getAccess() then
		local open, missing = check(player, step)
		if not open and missing == "loot" and SpireTutorial.pity(player) then
			open = check(player, step) -- a free cheese after a few tries: the gate never locks anyone in (Grok session 2)
		end
		if not open then
			pos:sendMagicEffect(CONST_ME_ENERGYHIT)
			player:sendCancelMessage(SpireTutorial.HELP[missing])
			-- in the Server Log too: the bottom-of-screen line alone was missed (Grok session 3, SB3-08)
			hint(player, "This gate is closed. " .. SpireTutorial.HELP[missing])
			return true
		end
	end
	if Tile(pos):getCreatureCount() > 0 then
		player:sendCancelMessage("Someone is standing in the gate. Wait a moment.")
		return true
	end
	if item:getId() == SpireTutorial.DOOR_CLOSED then
		item:transform(SpireTutorial.DOOR_OPEN)
		pos:sendSingleSoundEffect(SOUND_EFFECT_TYPE_ACTION_OPEN_DOOR)
	end
	player:teleportTo(pos, true)
	return true
end
gateUse:aid(SpireTutorial.GATE_AID)
gateUse:register()

-- an open gate (someone just went through) still turns back anyone who hasn't done the step
local gateIn = MoveEvent()
gateIn:type("stepin")
function gateIn.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player or player:getGroup():getAccess() or fromPosition.x >= position.x then
		return true
	end
	local step = gateStep(position)
	if not step then
		return true
	end
	local open, missing = check(player, step)
	if not open then
		player:teleportTo(fromPosition, true)
		hint(player, "This gate is closed. " .. SpireTutorial.HELP[missing])
	end
	return true
end
gateIn:aid(SpireTutorial.GATE_AID)
gateIn:register()

-- ... and closes behind whoever walked through
local gateOut = MoveEvent()
gateOut:type("stepout")
function gateOut.onStepOut(creature, item, position, fromPosition)
	if item:getId() == SpireTutorial.DOOR_OPEN and Tile(position):getCreatureCount() == 0 then
		item:transform(SpireTutorial.DOOR_CLOSED)
	end
	return true
end
gateOut:aid(SpireTutorial.GATE_AID)
gateOut:register()

-- the tile in front of each gate says once what to do: click the gate, or do the step first
local gateFront = MoveEvent()
gateFront:type("stepin")
function gateFront.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player or player:getVocation():getId() ~= 0 or fromPosition.x > position.x then
		return true
	end
	local step = gateStep(Position(position.x + 1, position.y, position.z))
	if not step then
		return true
	end
	local open, missing = check(player, step)
	if open then
		hint(player, "A gate: click it to open it and walk through.")
	else
		hint(player, "This gate is closed. " .. SpireTutorial.HELP[missing])
	end
	return true
end
for _, step in ipairs(SpireTutorial.STEPS) do
	for i = 1, 2 do
		local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
		if p then
			gateFront:position(Position(p.x - 1, p.y, p.z))
		end
	end
end
gateFront:register()

-- step 1: beat a rat
local kill = {} -- N8: counted through SpireKills (one death callback), not the deprecated onKill event
function kill.onKill(player, target)
	if target and target:isMonster() and target:getName() == "Pen Rat" then
		local second = SpireTutorial.done(player, "kill") -- this is at least the second rat
		SpireTutorial.mark(player, "kill")
		-- Grok session 3: an Arcanist killed rats over the fence, never found a body, and the loot gate held it for
		-- good. From the second rat on, a character who still hasn't looted gets the cheese straight into the
		-- backpack: the first kill still teaches opening a body, but nobody can be stuck here.
		if second and player:getVocation():getId() == 0 and not SpireTutorial.done(player, "loot") then
			SpireGive.item(player, SpireTutorial.CHEESE, 1)
			SpireTutorial.mark(player, "loot")
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You take the rat's cheese and put it in your backpack. (Next time, open a body yourself: right-click it and drag out what it carried.)")
		end
	end
	return true
end
SpireKills.on("SpireTutorialKill", kill.onKill)

-- step 2: take something out of a body
local loot = EventCallback("SpireTutorialLoot")
function loot.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	if fromCylinder and fromCylinder:isItem() and ItemType(fromCylinder:getId()):isCorpse() then
		SpireTutorial.mark(player, "loot")
	end
	return true
end
loot:register()

-- step 4: drink a potion. Counted by the potion really leaving your backpack (playtest 2026-11-13: counting any heal
-- let ordinary health regeneration open the gate).
local POTION = 266
function SpireTutorial.potionDrunk(player)
	local base = scope(player):get("potionBase")
	return base ~= nil and player:getItemCount(POTION) < base
end

local login = CreatureEvent("SpireTutorialLogin")
function login.onLogin(player)
	if player:getVocation():getId() == 0 and not scope(player):get("potionBase") then
		scope(player):remove("potion") -- the old check could count regeneration as the potion: check it again
		if player:getItemCount(POTION) == 0 then
			player:addItem(POTION, 1) -- a health potion for the last gate
		end
		scope(player):set("potionGiven", true)
		scope(player):set("potionBase", player:getItemCount(POTION))
	end
	return true
end
login:register()

-- nobody without a vocation walks out of the yard (the town gates stay shut until the Registrar has seen you)
local guard = GlobalEvent("SpireTutorialGuard")
function guard.onThink(interval)
	for _, p in ipairs(Game.getPlayers()) do
		if p:getVocation():getId() == 0 and not p:getGroup():getAccess() and not SpireTutorial.inYard(p:getPosition())
			and WorldPoints.tutorial_spawn then
			p:teleportTo(WorldPoints.tutorial_spawn)
			p:sendCancelMessage("Choose your path with the Registrar first. Follow the stone path east.")
		end
	end
	return true
end
guard:interval(5000)
guard:register()
