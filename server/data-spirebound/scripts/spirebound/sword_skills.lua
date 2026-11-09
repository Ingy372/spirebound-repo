-- Turns every entry in SwordSkills.list (lib/spirebound/sword_skills.lua) into a castable spell.
-- The client's sword-skill bar (task 1.20) casts them by their words; players can also type the words.

local AREAS = {
	front3 = { { 1, 1, 1 }, { 0, 3, 0 } },
	line3 = { { 1 }, { 1 }, { 1 }, { 3 } },
	line4 = { { 1 }, { 1 }, { 1 }, { 1 }, { 3 } },
	around1 = { { 1, 1, 1 }, { 1, 2, 1 }, { 1, 1, 1 } },
	around2 = { { 0, 1, 1, 1, 0 }, { 1, 1, 1, 1, 1 }, { 1, 1, 2, 1, 1 }, { 1, 1, 1, 1, 1 }, { 0, 1, 1, 1, 0 } },
	targetaround1 = { { 1, 1, 1 }, { 1, 3, 1 }, { 1, 1, 1 } },
}
local DIRECTIONAL = { front3 = true, line3 = true, line4 = true }
local VOCATIONS = {
	sword = { "vanguard;true", "blade warden;true" }, axe = { "vanguard;true", "blade warden;true" }, club = { "vanguard;true", "blade warden;true" },
	bow = { "ranger;true", "far warden;true" }, crossbow = { "ranger;true", "far warden;true" }, spear = { "ranger;true", "far warden;true" },
	wand = { "arcanist;true", "high arcanist;true" },
	rod = { "mystic;true", "elder mystic;true" },
}

local comboState = {} -- playerId -> combo state
local activeMultiplier = {} -- playerId -> multiplier for the cast in progress

local function makeFormula(skillDef)
	local fam = SwordSkills.families[skillDef.family]
	local name = "SpireSkillFormula_" .. skillDef.key
	if fam.kind == "melee" then
		_G[name] = function(player, skill, attack, factor)
			local mult = skillDef.coef * (activeMultiplier[player:getId()] or 1)
			local max = (player:getLevel() / 5) + (skill * attack * 0.06 + attack) * mult
			return -max * 0.75, -max
		end
		return CALLBACK_PARAM_SKILLVALUE, name
	end
	_G[name] = function(player, level, magicLevel)
		local mult = skillDef.coef * (activeMultiplier[player:getId()] or 1)
		local base = (level / 5) + magicLevel * 4 + 15
		return -base * 0.8 * mult, -base * 1.2 * mult
	end
	return CALLBACK_PARAM_LEVELMAGICVALUE, name
end

for i, def in ipairs(SwordSkills.list) do
	local combat = Combat()
	combat:setParameter(COMBAT_PARAM_TYPE, def.element)
	combat:setParameter(COMBAT_PARAM_EFFECT, def.effect)
	if def.distance then
		combat:setParameter(COMBAT_PARAM_DISTANCEEFFECT, def.distance)
	end
	if def.family ~= "wand" and def.family ~= "rod" then
		combat:setParameter(COMBAT_PARAM_BLOCKARMOR, true)
	end
	if def.area ~= "target" then
		combat:setArea(createCombatArea(AREAS[def.area]))
	end
	if def.slow then
		local condition = Condition(CONDITION_PARALYZE)
		condition:setParameter(CONDITION_PARAM_TICKS, 3000)
		condition:setFormula(-0.4, 0, -0.4, 0)
		combat:addCondition(condition)
	end
	local cbType, cbName = makeFormula(def)
	combat:setCallback(cbType, cbName)

	local spell = Spell("instant")
	function spell.onCastSpell(creature, var)
		local player = creature:getPlayer()
		if not player then
			return false
		end
		if def.twinFang and not SwordSkills.hasTwinFang(player) then
			player:sendCancelMessage(def.name .. " belongs to the Twin Fang. Only its holders know it.")
			return false
		end
		local held = SwordSkills.heldFamily(player)
		if held ~= def.family then
			player:sendCancelMessage(def.name .. " needs a " .. def.family .. " in hand.")
			player:getPosition():sendMagicEffect(CONST_ME_POFF)
			return false
		end
		local pid = player:getId()
		local newState, mult = SwordSkills.comboStep(comboState[pid], def.tag, os.time())
		comboState[pid] = newState
		activeMultiplier[pid] = mult
		local ok = combat:execute(creature, var)
		activeMultiplier[pid] = nil
		if ok and SpireClient then
			SpireClient.send(player, { t = "cast", name = def.name, cd = def.cd, combo = mult > 1 })
		end
		if mult > 1 then
			local kvs = player:kv():scoped("spirebound-twinfang")
			kvs:set("combos", (kvs:get("combos") or 0) + 1)
			SpirePath.progress(player, "combo", 1)
			player:say("COMBO!", TALKTYPE_MONSTER_SAY)
			player:getPosition():sendMagicEffect(CONST_ME_CRITICAL_DAMAGE)
		end
		if def.partyHeal and ok then
			local party = player:getParty()
			local members = party and party:getMembers() or {}
			if party then
				table.insert(members, party:getLeader())
			else
				members = { player }
			end
			for _, m in ipairs(members) do
				if m:getPosition():getDistance(player:getPosition()) <= 5 then
					m:addHealth(math.floor(m:getMaxHealth() * def.partyHeal))
					m:getPosition():sendMagicEffect(CONST_ME_MAGIC_GREEN)
				end
			end
		end
		return ok
	end
	spell:name(def.name)
	spell:words(def.words)
	spell:group("attack", "special")
	spell:id(240 + i) -- spell ids 241+ are unused by Canary's default spells
	spell:cooldown(def.cd)
	spell:groupCooldown(SwordSkills.SHARED_COOLDOWN, SwordSkills.SHARED_COOLDOWN)
	spell:level(def.level or 1)
	spell:mana(0)
	spell:isPremium(false)
	spell:isAggressive(true)
	if def.area == "target" or def.area == "targetaround1" then
		spell:needTarget(true)
		local melee = def.family == "sword" or def.family == "axe" or def.family == "club"
		spell:range(melee and 1 or 6)
	elseif DIRECTIONAL[def.area] then
		spell:needDirection(true)
	end
	spell:blockWalls(true)
	spell:vocation(unpack(VOCATIONS[def.family]))
	spell:register()
end
