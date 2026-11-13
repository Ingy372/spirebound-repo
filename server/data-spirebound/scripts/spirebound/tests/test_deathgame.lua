-- Roadmap R5: Death Game made trustworthy. Each rule goes through SpireDeathGame.judge, the same code the real
-- onDeath event calls with the real killer; the hit records are written by the same functions the real
-- onHealthChange event uses. Retirement and restore run on the real database and the real houses.

local MAXHP = 1000

local function fresh(guid)
	SpireDeathGame.forget(guid)
end

local function strangers(guid)
	return guid >= 900 -- in these tests, guids 900+ are outside players, below are friends
end

SpireTest.add("death game: a plain monster death retires; a player's killing blow never does", function()
	local v, now = 101, 500000
	fresh(v)
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 1 }, now, strangers)), "retire", "killed by a monster: retired")
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, nil, now, strangers)), "retire", "killed by the world (fire, poison): retired")
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { guid = 901, outside = true }, now, strangers)), "saved", "killed by another player: saved")
end)

SpireTest.add("death game: an outside player's tag only saves you with real damage (15% of health)", function()
	local v, now = 102, 600000
	fresh(v)
	SpireDeathGame.noteHit(v, { guid = 902, outside = true }, 100, now - 10) -- 10%: a tag
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 2 }, now, strangers)), "retire", "a 10% tag does not save")
	SpireDeathGame.noteHit(v, { guid = 902, outside = true }, 60, now - 5) -- now 16%
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 2 }, now, strangers)), "saved", "16% real damage saves")
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 2 }, now + 61, strangers)), "retire", "damage older than 60 s does not")
	fresh(v)
	SpireDeathGame.noteHit(v, { guid = 3, outside = false }, 900, now - 5) -- a party member's damage never saves
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 2 }, now, strangers)), "retire", "friends' damage does not save")
end)

SpireTest.add("death game: a friend can't save you by landing the last hit", function()
	local v, now = 103, 700000
	fresh(v)
	SpireDeathGame.noteHit(v, { guid = 4, outside = false }, 20, now - 1)
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { guid = 4, outside = false }, now, strangers)), "retire", "a friend's 2% last hit: retired")
	SpireDeathGame.noteHit(v, { guid = 4, outside = false }, 300, now - 1)
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { guid = 4, outside = false }, now, strangers)), "saved", "a friend who really fought you: saved")
end)

SpireTest.add("death game: monsters dragged in by another player in the last 30 s don't count as PvE", function()
	local v, now = 104, 800000
	fresh(v)
	SpireDeathGame.noteMonsterHit(77, 905, now - 20) -- the monster chased another (outside) player 20 s ago
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 77 }, now, strangers)), "saved", "dragged in 20 s ago: saved")
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 77 }, now + 15, strangers)), "retire", "35 s ago: a normal hunt, retired")
	SpireDeathGame.noteMonsterHit(78, 5, now - 5) -- a party member pulled it: still PvE
	SpireTest.eq((SpireDeathGame.judge(v, MAXHP, { monsterId = 78 }, now, strangers)), "retire", "pulled by a friend: retired")
end)

local function makePlayer(name)
	db.query("DELETE FROM `players` WHERE `name` = " .. db.escapeString(name))
	db.query("INSERT INTO `players` (`name`, `group_id`, `account_id`, `level`, `vocation`, `health`, `healthmax`, `experience`, "
		.. "`looktype`, `mana`, `manamax`, `town_id`, `conditions`, `cap`, `sex`) SELECT " .. db.escapeString(name)
		.. ", 1, `id`, 30, 4, 500, 500, 368300, 128, 100, 100, 1, '', 400, 1 FROM `accounts` WHERE `name` = 'jay'")
	local r = db.storeQuery("SELECT `id` FROM `players` WHERE `name` = " .. db.escapeString(name))
	local id = Result.getNumber(r, "id")
	Result.free(r)
	return id
end

local function one(q, col)
	local r = db.storeQuery(q)
	if not r then
		return nil
	end
	local v = Result.getNumber(r, col)
	Result.free(r)
	return v
end

SpireTest.add("death game: retirement frees house, guild leadership, market offers and the slot; a GM can restore", function()
	local a, b = makePlayer("Retire Tester"), makePlayer("Retire Heir")
	db.query("INSERT INTO `guilds` (`name`, `ownerid`, `creationdata`) VALUES ('Retire Test Guild', " .. a .. ", " .. os.time() .. ")")
	local gid = one("SELECT `id` FROM `guilds` WHERE `name` = 'Retire Test Guild'", "id")
	local lead = one("SELECT `id` FROM `guild_ranks` WHERE `guild_id` = " .. gid .. " AND `level` = 3", "id")
	local member = one("SELECT `id` FROM `guild_ranks` WHERE `guild_id` = " .. gid .. " AND `level` = 1", "id")
	db.query("INSERT INTO `guild_membership` (`player_id`, `guild_id`, `rank_id`) VALUES (" .. a .. ", " .. gid .. ", " .. lead .. "), (" .. b .. ", " .. gid .. ", " .. member .. ")")
	db.query("INSERT INTO `market_offers` (`player_id`, `sale`, `itemtype`, `amount`, `created`, `price`) VALUES (" .. a .. ", 1, 3031, 1, " .. os.time() .. ", 10)")
	local house = Game.getHouses()[1]
	local oldOwner = house:getOwnerGuid()
	house:setHouseOwner(a)
	kv.scoped("player"):scoped(tostring(a)):scoped("spirebound"):set("retired", true)

	SpireDeathGame.free(a)
	SpireTest.eq(house:getOwnerGuid(), 0, "the house is free again")
	SpireTest.eq(one("SELECT `ownerid` FROM `guilds` WHERE `id` = " .. gid, "ownerid"), b, "the guild passes to the next member")
	SpireTest.eq(one("SELECT `rank_id` FROM `guild_membership` WHERE `player_id` = " .. b, "rank_id"), lead, "the heir becomes leader")
	SpireTest.eq(one("SELECT COUNT(*) AS `n` FROM `guild_membership` WHERE `player_id` = " .. a, "n"), 0, "the retired character left the guild")
	SpireTest.eq(one("SELECT COUNT(*) AS `n` FROM `market_offers` WHERE `player_id` = " .. a, "n"), 0, "its market offers are gone")
	SpireTest.eq((one("SELECT `deletion` FROM `players` WHERE `id` = " .. a, "deletion") or 0) > 0, true, "its character slot is freed")

	local ok = SpireDeathGame.restore("Retire Tester")
	SpireTest.eq(ok, true, "a GM can restore it")
	SpireTest.eq(kv.scoped("player"):scoped(tostring(a)):scoped("spirebound"):get("retired"), false, "no longer retired")
	SpireTest.eq(one("SELECT `deletion` FROM `players` WHERE `id` = " .. a, "deletion"), 0, "back on the character list")
	SpireTest.eq((SpireDeathGame.restore("Retire Heir")), false, "a character that never died can't be 'restored'")

	house:setHouseOwner(oldOwner)
	db.query("DELETE FROM `guilds` WHERE `id` = " .. gid)
	db.query("DELETE FROM `players` WHERE `id` IN (" .. a .. ", " .. b .. ")")
	kv.scoped("player"):scoped(tostring(a)):scoped("spirebound"):remove("retired")
end)

SpireTest.add("death game: stepping down costs the bonus; Deathbound needs level 50 alive", function()
	SpireTest.eq(SpireDeathGame.stepDownCost(1000, Difficulty.DEATHGAME, Difficulty.NORMAL), 1000, "Death Game to Normal: all the bonus")
	SpireTest.eq(SpireDeathGame.stepDownCost(1000, Difficulty.DEATHGAME, Difficulty.HARDCORE), 500, "Death Game to Hardcore: half")
	SpireTest.eq(SpireDeathGame.stepDownCost(0, Difficulty.DEATHGAME, Difficulty.NORMAL), 0, "no bonus earned: free")
	SpireTest.eq(SpireDeathGame.earnsDeathbound(Difficulty.DEATHGAME, 49, false), false, "level 49: not yet")
	SpireTest.eq(SpireDeathGame.earnsDeathbound(Difficulty.DEATHGAME, 50, false), true, "level 50 alive: Deathbound")
	SpireTest.eq(SpireDeathGame.earnsDeathbound(Difficulty.DEATHGAME, 80, true), false, "retired: no")
	SpireTest.eq(SpireDeathGame.earnsDeathbound(Difficulty.NORMAL, 80, false), false, "not on the Death Game: no")
	SpireTest.eq(SpireDeathGame.RULES:find("crash") ~= nil, true, "the unfair-death policy is written down")
end)
