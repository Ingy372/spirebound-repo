-- Floor perks in combat and loot (roadmap R12). Rules: lib/spirebound/perks.lua.

local lastWind = {} -- player id -> time Second Wind last fired
SpireCleanup.add(function(pid) lastWind[pid] = nil end)

local defence = CreatureEvent("SpirePerkDefence")
function defence.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local player = creature:getPlayer()
	if not player then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	local fx = SpirePerks.effects(player)
	if #fx == 0 then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	if primaryType == COMBAT_HEALING then
		if (attacker == nil or attacker == creature) and origin ~= ORIGIN_SPELL then -- a potion (Field Medic)
			primaryDamage = SpirePerks.potionHeal(fx, primaryDamage)
		end
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	primaryDamage = SpirePerks.taken(fx, primaryType, primaryDamage, math.random)
	secondaryDamage = SpirePerks.taken(fx, secondaryType, secondaryDamage, function() return 1 end)
	local after = player:getHealth() - primaryDamage - secondaryDamage
	local heal = SpirePerks.secondWind(fx, after, player:getMaxHealth(), lastWind[player:getId()], os.time())
	if heal > 0 then
		lastWind[player:getId()] = os.time()
		addEvent(function(pid, amount)
			local p = Player(pid)
			if p then
				p:addHealth(amount)
				p:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
				p:sendTextMessage(MESSAGE_STATUS, "Second Wind!")
			end
		end, 1, player:getId(), heal)
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
defence:register()

-- damage players deal (Executioner, Hunter's Eye, Ruinbreaker's Edge): called by the monsters' damage event
function SpirePerks.onDealt(attacker, target, amount)
	local player = attacker and (attacker:getPlayer() or (attacker:getMaster() and attacker:getMaster():getPlayer()))
	if not player or amount <= 0 then
		return amount
	end
	local fx = SpirePerks.effects(player)
	if #fx == 0 then
		return amount
	end
	local mType = target:isMonster() and target:getType()
	local share = target:getHealth() / math.max(1, target:getMaxHealth())
	return SpirePerks.dealt(fx, amount, share, mType and mType:isBoss() or false, math.random)
end

-- loot: Haggler's extra coins, Lucky Find's extra roll
local loot = EventCallback("SpirePerkLoot")
function loot.monsterOnDropLoot(monster, corpse)
	local player = Player(corpse:getCorpseOwner())
	if not player or not corpse:isContainer() then
		return
	end
	local fx = SpirePerks.effects(player)
	local coins = SpirePerks.coinBonus(fx)
	if coins > 0 then
		local gold = 0
		for i = 0, corpse:getSize() - 1 do
			local it = corpse:getItem(i)
			if it and it:getId() == 3031 then gold = gold + it:getCount() end
			if it and it:getId() == 3035 then gold = gold + 100 * it:getCount() end
		end
		local extra = math.floor(gold * coins + math.random())
		if extra > 0 then
			corpse:addItem(3031, math.min(100, extra))
		end
	end
	local roll = SpirePerks.lootRoll(fx)
	local mType = monster:getType()
	if roll > 0 and mType then
		corpse:addLoot(mType:generateLootRoll({ factor = roll, gut = false }, {}, player))
	end
end
loot:register()

local login = CreatureEvent("SpirePerkLogin")
function login.onLogin(player)
	player:registerEvent("SpirePerkDefence")
	return true
end
login:register()
