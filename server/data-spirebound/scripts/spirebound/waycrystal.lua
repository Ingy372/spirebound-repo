-- Waycrystals in the game (DESIGN.md 3.7). Rules: lib/spirebound/crystals.lua. Right-click a crystal: a menu of its
-- floor's town and the hunting grounds the character has the level for; then stand still for a few seconds and it
-- takes you there, used up on arrival. Never an escape from a fight, a boss room or a party cave.

local pending = {} -- player id -> { itemId, def, choices }
local lastHit = {} -- player id -> os.time() of the last hit given or taken (any creature)
SpireCrystals.lastHit = lastHit
SpireCleanup.add(function(pid)
	pending[pid], lastHit[pid] = nil, nil
end)

local function state(player, def)
	local pos = player:getPosition()
	local inPz = player:getTile() and player:getTile():hasFlag(TILESTATE_PROTECTIONZONE)
	local recent = (lastHit[player:getId()] or 0) > os.time() - SpireCrystalData.FIGHT_LOCK
	local fight = not inPz and (player:isPzLocked() or player:getCondition(CONDITION_INFIGHT, CONDITIONID_DEFAULT) ~= nil or recent)
	return {
		zone = (SpireCalling and SpireCalling.inTrial(player)) and "bossroom" or (SpirePvP and SpirePvP.zoneAt(pos) or "open"), -- (a sealed Path Trial too)
		tutorial = player:getVocation():getId() == 0,
		cave = SpireCrystals.inCave(pos),
		fight = fight,
		floorOpen = Floors.isOpen(def.floor),
	}
end

local function refuse(player, why)
	player:sendCancelMessage(why)
	player:getPosition():sendMagicEffect(CONST_ME_POFF)
end

local crystal = Action()
function crystal.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local def = SpireCrystalData.byItem[item:getId()]
	if not def then
		return false
	end
	local why = SpireCrystals.refusal(state(player, def))
	if why then
		refuse(player, why)
		return true
	end
	local townName = def.floor == 1 and "Hearthgate (the Hearth)" or ("Floor " .. def.floor .. "'s town")
	local choices = SpireCrystals.choices(def.floor, player:getLevel(), townName)
	-- remember where the crystal was used from: a backpack (x = 0xFFFF) or a tile beside the player
	local from = fromPosition.x ~= 0xFFFF and Position(fromPosition.x, fromPosition.y, fromPosition.z) or nil
	pending[player:getId()] = { itemId = item:getId(), def = def, choices = choices, from = from }
	local window = ModalWindow(SpireCrystals.WINDOW, def.name, "Where to? Hold still for " .. SpireCrystalData.CAST_SECONDS
		.. " seconds after you choose. The crystal is used up when you arrive.")
	for i, c in ipairs(choices) do
		window:addChoice(i, c.text)
	end
	window:addButton(1, "Go")
	window:addButton(2, "Cancel")
	window:setDefaultEnterButton(1)
	window:setDefaultEscapeButton(2)
	player:registerEvent("SpireWaycrystalMenu")
	window:sendToPlayer(player)
	return true
end
for itemId in pairs(SpireCrystalData.byItem) do
	crystal:id(itemId)
end
crystal:register()

local function finish(pid, startPos, startHealth, step)
	local player = Player(pid)
	local p = player and pending[pid]
	if not p or not p.go then
		return
	end
	local here = player:getPosition()
	if here.x ~= startPos.x or here.y ~= startPos.y or here.z ~= startPos.z or player:getHealth() < startHealth then
		pending[pid] = nil
		refuse(player, "The crystal's light breaks: you have to hold still.")
		return
	end
	if step < SpireCrystalData.CAST_SECONDS then
		here:sendMagicEffect(CONST_ME_MAGIC_BLUE)
		addEvent(finish, 1000, pid, startPos, startHealth, step + 1)
		return
	end
	pending[pid] = nil
	local why = SpireCrystals.refusal(state(player, p.def))
	if why then
		refuse(player, why)
		return
	end
	local dest = p.go.pos and Position(p.go.pos[1], p.go.pos[2], p.go.pos[3]) or SpireCrystals.townPos(p.def)
	local onTile = p.from and Tile(p.from) and Tile(p.from):getItemById(p.itemId)
	local paid = false
	if onTile then
		paid = onTile:remove(1)
	elseif player:getItemCount(p.itemId) > 0 then
		paid = player:removeItem(p.itemId, 1)
	end
	if not dest or not paid then
		refuse(player, "The crystal is gone.")
		return
	end
	here:sendMagicEffect(CONST_ME_TELEPORT)
	player:teleportTo(dest)
	dest:sendMagicEffect(CONST_ME_TELEPORT)
	logger.info("[Spirebound] {} used a {} to {}", player:getName(), p.def.name, p.go.id)
end

local menu = CreatureEvent("SpireWaycrystalMenu")
function menu.onModalWindow(player, windowId, buttonId, choiceId)
	if windowId ~= SpireCrystals.WINDOW then
		return true
	end
	local p = pending[player:getId()]
	if not p or buttonId ~= 1 or not p.choices[choiceId] then
		pending[player:getId()] = nil
		return true
	end
	p.go = p.choices[choiceId]
	player:sendTextMessage(MESSAGE_STATUS, "The crystal glows. Hold still...")
	finish(player:getId(), player:getPosition(), player:getHealth(), 0)
	return true
end
menu:register()

-- any hit given or taken starts the fight lock (monsters too: a crystal is a time-saver, not an escape)
local hits = CreatureEvent("SpireWaycrystalHits")
function hits.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	if primaryType ~= COMBAT_HEALING and (primaryDamage ~= 0 or secondaryDamage ~= 0) then
		if creature:isPlayer() then
			lastHit[creature:getId()] = os.time()
		end
		local a = attacker and (attacker:getPlayer() or (attacker:getMaster() and attacker:getMaster():getPlayer()))
		if a then
			lastHit[a:getId()] = os.time()
		end
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
hits:register()

local login = CreatureEvent("SpireWaycrystalLogin")
function login.onLogin(player)
	player:registerEvent("SpireWaycrystalHits")
	player:registerEvent("SpireWaycrystalMenu")
	return true
end
login:register()
