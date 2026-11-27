-- The Town Works in the game (roadmap FD5). Rules: lib/spirebound/works.lua; pieces: works_pieces.lua (from
-- maps/floor1_features.py). Give by dropping coins on the Works Board; use the board to read it.
local AID_BOARD, AID_HEALER, AID_SUPPLY = 47230, 47231, 47232
local W = SpireDepthData.works

local function boardPos()
	local p = WorldPoints.works_board
	return p and Position(p.x, p.y, p.z)
end

-- read the board
local board = Action()
function board.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	player:showTextDialog(2597, table.concat(SpireWorks.lines(), "\n"))
	return true
end
board:aid(AID_BOARD)
board:register()

-- give: coins dropped on the board
local give = EventCallback("SpireWorksGive")
function give.playerOnItemMoved(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	local b = boardPos()
	if not b or not toPosition or toPosition.x ~= b.x or toPosition.y ~= b.y or toPosition.z ~= b.z or not item then
		return
	end
	local value = SpireWorks.coinValue(item:getId(), item:getCount())
	if not value then
		return
	end
	item:remove()
	local ok, line = SpireWorks.give(player, value)
	if value > ok then
		player:addMoney(value - ok) -- what the board could not take goes back to the backpack
	end
	if ok > 0 then
		b:sendMagicEffect(CONST_ME_GIFT_WRAPS)
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, line)
end
give:register()

-- the Stair Camp's healer's shrine and supply crate (project 3)
local healer = Action()
function healer.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if player:hasCondition(CONDITION_INFIGHT) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The healer's shrine is calm and slow: catch your breath out of the fight first.")
		return true
	end
	player:addHealth(player:getMaxHealth())
	player:addMana(player:getMaxMana())
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You rest a moment at the healer's shrine and feel whole again.")
	return true
end
healer:aid(AID_HEALER)
healer:register()

local supply = Action()
function supply.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	local id, n = W.campPotions[1], W.campPotions[2]
	local price = 50 * n -- the Quartermaster's price, no more
	if not player:removeMoneyBank(price) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The camp's supply crate: %d health potions for %d gold. You cannot pay.", n, price))
		return true
	end
	SpireGive.reward(player, id, n)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You buy %d health potions from the camp's supply crate for %d gold.", n, price))
	return true
end
supply:aid(AID_SUPPLY)
supply:register()

-- after a project's pieces are laid: action ids on the camp's objects, the garden's plaque
function SpireWorks.afterLay(i, s)
	local list = SpireWorksPieces and SpireWorksPieces[i] or {}
	for _, p in ipairs(list) do
		local t = Tile(Position(p.x, p.y, p.z))
		for _, it in ipairs(t and t:getItems() or {}) do
			if it:getId() == 2025 and i == 3 then
				it:setActionId(AID_HEALER)
				it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "The Stair Camp's healer's shrine. Rest here out of a fight.")
			elseif it:getId() == 8772 and i == 3 then
				it:setActionId(AID_SUPPLY)
				it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "The Stair Camp's supply crate: health potions at the Quartermaster's price.")
			end
		end
	end
	if i == 5 then
		local f = s.finished["5"]
		local all, seen = {}, {}
		for _, ff in pairs(s.finished) do
			for _, n in ipairs(ff.names or {}) do
				if not seen[n] then
					seen[n] = true
					table.insert(all, n)
				end
			end
		end
		local b = WorldPoints.monument
		if b and f then
			local pos = Position(b.x + 1, b.y + 1, b.z)
			local sign
			for _, it in ipairs(Tile(pos) and Tile(pos):getItems() or {}) do
				if it:getActionId() == 47233 then
					sign = it
				end
			end
			sign = sign or Game.createItem(2012, 1, pos)
			if sign then
				sign:setActionId(47233)
				sign:setAttribute(ITEM_ATTRIBUTE_TEXT, "The Town Works of this season were built by: " .. table.concat(all, ", ") .. ".")
			end
		end
	end
end

-- the board and the camp's objects never move
local fixed = EventCallback("SpireWorksFixed")
function fixed.playerOnMoveItem(player, item, count, fromPosition, toPosition, fromCylinder, toCylinder)
	local aid = item:getActionId()
	if aid >= AID_BOARD and aid <= 47233 then
		player:sendCancelMessage(RETURNVALUE_NOTMOVABLE)
		return false
	end
	return true
end
fixed:register()

-- banners on the gates after the Axe-Lord's first fall this season
local function banners()
	if SpireWorks.bannersUp or not (Floors and Floors.get(1) and Floors.get(1).bossDeadAt) then
		return
	end
	SpireWorks.bannersUp = true
	SpireWorks.layPieces(SpireWorksPieces and SpireWorksPieces.banners)
end

local tick = GlobalEvent("SpireWorksTick")
function tick.onThink(interval)
	pcall(banners)
	return true
end
tick:interval(60000)
tick:register()

local startup = GlobalEvent("SpireWorksStartup")
function startup.onStartup()
	local b = boardPos()
	local t = b and Tile(b)
	for _, it in ipairs(t and t:getItems() or {}) do
		if it:getId() == 2597 then
			it:setActionId(AID_BOARD)
			it:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "The Works Board. Use it to read what Hearthgate is building; drop coins on it to give.")
		end
	end
	local s = SpireWorks.state()
	logger.info("[Spirebound] Town Works: project {} of {}, {} pieces laid", s.current, #W.projects, SpireWorks.layFinished(s))
	pcall(banners)
	return true
end
startup:register()
