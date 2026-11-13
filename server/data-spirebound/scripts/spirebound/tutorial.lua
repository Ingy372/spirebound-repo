-- The Arrival Yard tutorial (roadmap R11, REVIEW 1.2). Four gates on the path; each opens once the new character has
-- done one small thing: beaten a rat, looted it, read the list of skills and spells (sword skills themselves need a
-- vocation, which only the Registrar at the end gives), and drunk a potion. Characters with no vocation can't
-- leave the yard: the Registrar sends them to Hearthgate once they choose a path.

SpireTutorial = { STEPS = { "kill", "loot", "spells", "potion" } }
SpireTutorial.HELP = {
	kill = "Beat a rat in the pen first: click it in the Battle List (Ctrl+B) or right-click it and choose Attack.",
	loot = "Open a rat's body (right-click it) and take the cheese it carried before you go on.",
	spells = "Say !spells to see the sword skills and spells your path will teach you.",
	potion = "Drink the health potion in your backpack (right-click it, or drag it onto yourself).",
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

function SpireTutorial.inYard(pos)
	local nw, se = WorldPoints.tutorial_yard_nw, WorldPoints.tutorial_yard_se
	return nw ~= nil and pos.z == nw.z and pos.x >= nw.x and pos.x <= se.x and pos.y >= nw.y and pos.y <= se.y
end

-- the gates: stepping onto a closed door sends you back a tile with a hint
local gate = MoveEvent()
function gate.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player or player:getGroup():getAccess() then
		return true
	end
	for _, step in ipairs(SpireTutorial.STEPS) do
		for i = 1, 2 do
			local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
			if p and p == position then
				local open, missing = SpireTutorial.gateOpen(step, function(s)
					return SpireTutorial.done(player, s)
				end)
				if not open and fromPosition.x < position.x then
					player:teleportTo(fromPosition, true)
					position:sendMagicEffect(CONST_ME_ENERGYHIT)
					player:sendCancelMessage(SpireTutorial.HELP[missing])
					return true
				end
			end
		end
	end
	return true
end
for _, step in ipairs(SpireTutorial.STEPS) do
	for i = 1, 2 do
		local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
		if p then
			gate:position(p)
		end
	end
end
gate:type("stepin")
gate:register()

-- step 1: beat a rat
local kill = CreatureEvent("SpireTutorialKill")
function kill.onKill(player, target)
	if target and target:isMonster() and target:getName() == "Pen Rat" then
		SpireTutorial.mark(player, "kill")
	end
	return true
end
kill:register()

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
	player:registerEvent("SpireTutorialKill")
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

-- something to see at each gate (Jay, 2026-11-13: "a door, a gate, a wall of fire or energy, anything will do"):
-- a shimmering wall of energy across each gap. It never hurts; the gate check above is what stops you.
local shimmer = GlobalEvent("SpireTutorialShimmer")
function shimmer.onThink(interval)
	for _, step in ipairs(SpireTutorial.STEPS) do
		for i = 1, 2 do
			local p = WorldPoints["tutorial_gate_" .. step .. "_" .. i]
			if p and #Game.getSpectators(p, false, true, 9, 9, 7, 7) > 0 then
				p:sendMagicEffect(CONST_ME_ENERGYAREA)
			end
		end
	end
	return true
end
shimmer:interval(1200)
shimmer:register()
