-- Death Game made trustworthy (roadmap R5, REVIEW 3.4 and 2.7; DESIGN.md 6.6).
-- A Death Game character is deleted ("retired") only by a death that really was PvE:
--   * the killing blow came from a monster (or the world), not a player;
--   * no outside player (not party, guild or same IP) did real damage (at least 15% of max health) in the last 60 s;
--   * the killing monster was not dragged in: it did not hit another outside player in the last 30 s.
-- A player's killing blow never deletes you, unless it was a friend who did almost nothing (a friend can't "save" you
-- by landing the last hit on a character the monsters were killing).
-- Retirement frees the house, guild leadership, market offers and the character slot, and saves at once.
-- Unfair deaths (a server crash or server lag) are put right by a GM with /restore <name> (policy: RULES below).

SpireDeathGame = SpireDeathGame or { hits = {}, monsterHits = {} }

SpireDeathGame.WINDOW = 60          -- seconds of player damage that are looked at
SpireDeathGame.DRAG_WINDOW = 30     -- a monster that hit another player this recently was dragged in
SpireDeathGame.REAL_DAMAGE = 0.15   -- share of max health that counts as "real" damage
SpireDeathGame.RULES = "Unfair deaths: a Death Game character killed by a server crash or by lag on the server is restored by "
	.. "a gamemaster. Your own internet dropping is not unfair: the tower is cruel. Ask a gamemaster with !report within a day."

-- Note damage a Death Game victim took from a player. attacker = { guid, outside = bool }
function SpireDeathGame.noteHit(victimGuid, attacker, amount, now)
	local list = SpireDeathGame.hits[victimGuid] or {}
	SpireDeathGame.hits[victimGuid] = list
	table.insert(list, { guid = attacker.guid, outside = attacker.outside, amount = amount, time = now })
	while #list > 0 and now - list[1].time > SpireDeathGame.WINDOW do
		table.remove(list, 1)
	end
end

-- Note that a monster hit a player (any player): used for the "dragged in" rule.
function SpireDeathGame.noteMonsterHit(monsterId, playerGuid, now)
	local m = SpireDeathGame.monsterHits[monsterId] or {}
	SpireDeathGame.monsterHits[monsterId] = m
	m[playerGuid] = now
end

local function damageBy(victimGuid, now, filter)
	local total = 0
	for _, h in ipairs(SpireDeathGame.hits[victimGuid] or {}) do
		if now - h.time <= SpireDeathGame.WINDOW and filter(h) then
			total = total + h.amount
		end
	end
	return total
end

-- Pure-ish: the verdict for a death. killer = nil (world), { monsterId = id } or { guid = g, outside = bool }.
-- isOutside(guid) answers whether another player's guid is an "outside" player for this victim.
-- Returns "retire" or "saved", and the reason.
function SpireDeathGame.judge(victimGuid, maxHealth, killer, now, isOutside)
	local real = maxHealth * SpireDeathGame.REAL_DAMAGE
	if killer and killer.guid then
		if killer.outside then
			return "saved", "killed by another player"
		end
		local friendDamage = damageBy(victimGuid, now, function(h)
			return h.guid == killer.guid
		end)
		if friendDamage >= real then
			return "saved", "killed by a friend who really fought you"
		end
	end
	local outside = damageBy(victimGuid, now, function(h)
		return h.outside
	end)
	if outside >= real then
		return "saved", "another player did real damage in the last minute"
	end
	if killer and killer.monsterId then
		for guid, t in pairs(SpireDeathGame.monsterHits[killer.monsterId] or {}) do
			if guid ~= victimGuid and now - t <= SpireDeathGame.DRAG_WINDOW and isOutside(guid) then
				return "saved", "the monster was dragged in by another player"
			end
		end
	end
	return "retire", "a PvE death"
end

function SpireDeathGame.forget(victimGuid)
	SpireDeathGame.hits[victimGuid] = nil
end

-- Free everything a retired character held. Works on the database, so it also works right after death.
function SpireDeathGame.free(guid)
	for _, h in ipairs(Game.getHouses()) do
		if h:getOwnerGuid() == guid then
			h:setHouseOwner(0)
		end
	end
	local g = db.storeQuery("SELECT `id` FROM `guilds` WHERE `ownerid` = " .. guid)
	if g then
		local gid = Result.getNumber(g, "id")
		Result.free(g)
		local nxt = db.storeQuery("SELECT `m`.`player_id` FROM `guild_membership` `m` JOIN `guild_ranks` `r` ON `r`.`id` = `m`.`rank_id` "
			.. "WHERE `m`.`guild_id` = " .. gid .. " AND `m`.`player_id` <> " .. guid .. " ORDER BY `r`.`level` DESC, `m`.`player_id` LIMIT 1")
		if nxt then
			local heir = Result.getNumber(nxt, "player_id")
			Result.free(nxt)
			local top = db.storeQuery("SELECT `id` FROM `guild_ranks` WHERE `guild_id` = " .. gid .. " ORDER BY `level` DESC LIMIT 1")
			if top then
				db.query("UPDATE `guild_membership` SET `rank_id` = " .. Result.getNumber(top, "id") .. " WHERE `player_id` = " .. heir)
				Result.free(top)
			end
			db.query("UPDATE `guilds` SET `ownerid` = " .. heir .. " WHERE `id` = " .. gid)
		else
			db.query("DELETE FROM `guilds` WHERE `id` = " .. gid)
		end
	end
	db.query("DELETE FROM `guild_membership` WHERE `player_id` = " .. guid)
	db.query("DELETE FROM `market_offers` WHERE `player_id` = " .. guid)
	db.query("UPDATE `players` SET `deletion` = " .. os.time() .. " WHERE `id` = " .. guid) -- frees the slot, hides it from the list
end

local function playerKv(guid)
	return kv.scoped("player"):scoped(tostring(guid)):scoped("spirebound")
end

-- GM: bring back a character retired by an unfair death. Returns true, or false and why.
function SpireDeathGame.restore(name)
	local r = db.storeQuery("SELECT `id` FROM `players` WHERE `name` = " .. db.escapeString(name))
	if not r then
		return false, "no character called " .. name
	end
	local guid = Result.getNumber(r, "id")
	Result.free(r)
	local pk = playerKv(guid)
	if pk:get("retired") ~= true then
		return false, name .. " is not retired"
	end
	pk:set("retired", false)
	kv.scoped("spirebound-memorial"):remove(name)
	db.query("UPDATE `players` SET `deletion` = 0 WHERE `id` = " .. guid)
	logger.info("[Spirebound] GM restored Death Game character {}", name)
	return true
end

-- Q14: stepping down costs the extra experience the harder mode's bonus gave.
-- bonusXp = extra experience earned so far through the current mode's bonus. Returns experience to remove.
function SpireDeathGame.stepDownCost(bonusXp, current, new)
	local cur = Difficulty.xpBonus[current] or 0
	if cur <= 0 or not bonusXp or bonusXp <= 0 then
		return 0
	end
	local keep = (Difficulty.xpBonus[new] or 0) / cur
	return math.floor(bonusXp * (1 - keep))
end

-- The Deathbound title: a Death Game character that reaches level 50 alive (account-wide, DESIGN.md 5.4)
SpireDeathGame.DEATHBOUND_LEVEL = 50
function SpireDeathGame.earnsDeathbound(difficulty, level, retired)
	return difficulty == Difficulty.DEATHGAME and level >= SpireDeathGame.DEATHBOUND_LEVEL and not retired
end
