-- Floor perks (DESIGN.md 8.3; roadmap R12: every perk really works). One perk per floor, chosen at the Registrar
-- after the floor's story quests. Stat perks are conditions; combat perks change damage in the events of
-- scripts/spirebound/perks.lua, through the pure functions here (tested one by one).

SpirePerks = SpirePerks or {}

-- key -> what it does
SpirePerks.EFFECTS = {
	thick_skin = { maxhp = 105 }, light_step = { speed = 10 },
	field_medic = { potion = 0.15 }, deep_reserves = { maxmana = 110 },
	fog_sense = { dodge = 0.05 }, hunters_eye = { crit = 0.03 },
	iron_will = { protect = { [COMBAT_PHYSICALDAMAGE] = 0.08 } }, second_wind_perk = { secondwind = 0.15 },
	executioner = { execute = 0.10 }, bulwark = { reduce = 0.05 },
	ember_skin = { protect = { [COMBAT_FIREDAMAGE] = 0.10 } }, forgehand = { skills = 105 },
	marsh_walker = { speed = 15 }, toxin_ward = { protect = { [COMBAT_EARTHDAMAGE] = 0.10 } },
	frost_blood = { protect = { [COMBAT_ICEDAMAGE] = 0.10 } }, winter_vigor = { maxhp = 105 },
	haggler = { coins = 0.08 }, lucky_find = { lootroll = 0.03 },
	cobalt_heart = { maxhp = 105, maxmana = 105 }, ruinbreaker = { bossdmg = 0.05 },
}
SpirePerks.SECOND_WIND_COOLDOWN = 300

function SpirePerks.get(player, floor)
	return player:kv():scoped("spirebound-perks"):get("floor" .. floor)
end

function SpirePerks.choose(player, floor, key)
	player:kv():scoped("spirebound-perks"):set("floor" .. floor, key)
	SpirePerks.apply(player)
end

-- every effect the player's chosen perks give, as one list
function SpirePerks.effects(player)
	local out = {}
	for floor = 1, 10 do
		local key = SpirePerks.get(player, floor)
		if key and SpirePerks.EFFECTS[key] then
			table.insert(out, SpirePerks.EFFECTS[key])
		end
	end
	return out
end

local SUBID = 4500
function SpirePerks.apply(player)
	for i = 0, 9 do
		player:removeCondition(CONDITION_ATTRIBUTES, CONDITIONID_DEFAULT, SUBID + i)
		player:removeCondition(CONDITION_HASTE, CONDITIONID_DEFAULT, SUBID + 20 + i)
	end
	local maxhp, maxmana, speed, skills = 100, 100, 0, 100
	for _, e in ipairs(SpirePerks.effects(player)) do
		if e.maxhp then maxhp = maxhp + (e.maxhp - 100) end
		if e.maxmana then maxmana = maxmana + (e.maxmana - 100) end
		if e.speed then speed = speed + e.speed end
		if e.skills then skills = skills + (e.skills - 100) end
	end
	if maxhp > 100 or maxmana > 100 or skills > 100 then
		local c = Condition(CONDITION_ATTRIBUTES)
		c:setParameter(CONDITION_PARAM_SUBID, SUBID)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		if maxhp > 100 then c:setParameter(CONDITION_PARAM_STAT_MAXHITPOINTSPERCENT, maxhp) end
		if maxmana > 100 then c:setParameter(CONDITION_PARAM_STAT_MAXMANAPOINTSPERCENT, maxmana) end
		if skills > 100 then
			c:setParameter(CONDITION_PARAM_SKILL_MELEEPERCENT, skills)
			c:setParameter(CONDITION_PARAM_SKILL_DISTANCEPERCENT, skills)
		end
		player:addCondition(c)
	end
	if speed > 0 then
		local c = Condition(CONDITION_HASTE)
		c:setParameter(CONDITION_PARAM_SUBID, SUBID + 20)
		c:setParameter(CONDITION_PARAM_TICKS, -1)
		c:setParameter(CONDITION_PARAM_SPEED, speed)
		player:addCondition(c)
	end
end

-- Pure: damage a player takes, after perks. roll() returns 0..1 (math.random in the game).
function SpirePerks.taken(effects, dmgType, amount, roll)
	for _, e in ipairs(effects) do
		if e.dodge and roll() < e.dodge then
			return 0
		end
	end
	local f = 1
	for _, e in ipairs(effects) do
		if e.reduce then f = f - e.reduce end
		if e.protect and e.protect[dmgType] then f = f - e.protect[dmgType] end
	end
	return math.floor(amount * math.max(0, f))
end

-- Pure: damage a player deals, after perks
function SpirePerks.dealt(effects, amount, targetHealthShare, targetIsBoss, roll)
	local f = 1
	for _, e in ipairs(effects) do
		if e.execute and targetHealthShare < 0.30 then f = f + e.execute end
		if e.bossdmg and targetIsBoss then f = f + e.bossdmg end
		if e.crit and roll() < e.crit then f = f + 0.5 end
	end
	return math.floor(amount * f)
end

-- Pure: a potion's healing after Field Medic
function SpirePerks.potionHeal(effects, amount)
	local f = 1
	for _, e in ipairs(effects) do
		if e.potion then f = f + e.potion end
	end
	return math.floor(amount * f + 0.5)
end

-- Pure: Second Wind fires when health drops below 25%, at most every 5 minutes. Returns heal amount (0 = no).
function SpirePerks.secondWind(effects, healthAfter, maxHealth, lastAt, now)
	for _, e in ipairs(effects) do
		if e.secondwind and healthAfter > 0 and healthAfter < maxHealth * 0.25
			and (not lastAt or now - lastAt >= SpirePerks.SECOND_WIND_COOLDOWN) then
			return math.floor(maxHealth * e.secondwind)
		end
	end
	return 0
end

-- Pure: extra coins (Haggler) and the extra loot roll (Lucky Find)
function SpirePerks.coinBonus(effects)
	local b = 0
	for _, e in ipairs(effects) do
		if e.coins then b = b + e.coins end
	end
	return b
end

function SpirePerks.lootRoll(effects)
	local b = 0
	for _, e in ipairs(effects) do
		if e.lootroll then b = b + e.lootroll end
	end
	return b
end
