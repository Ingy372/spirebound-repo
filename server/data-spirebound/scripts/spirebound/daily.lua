-- The daily login streak (rules: lib/spirebound/daily.lua). Pays into the bank so a full backpack never loses it.
local login = CreatureEvent("SpireDailyLogin")
function login.onLogin(player)
	if player:getVocation():getBaseId() == 0 then
		return true -- still in the Arrival Yard
	end
	local k = player:kv():scoped("spirebound")
	local today = math.floor(os.time() / 86400)
	local day = SpireDaily.next(k:get("daily_last"), k:get("daily_streak"), today)
	if not day then
		return true
	end
	k:set("daily_last", today)
	k:set("daily_streak", day)
	local r = SpireDaily.reward(day)
	player:setBankBalance(player:getBankBalance() + r.gold)
	if r.potions > 0 then
		player:addItem(266, r.potions)
	end
	local text = string.format("Daily reward, day %d of 7: %d gold to your bank%s. Come back tomorrow for day %d.", day, r.gold,
		r.potions > 0 and (" and " .. r.potions .. " health potions") or "", day % 7 + 1)
	addEvent(function(pid)
		local p = Player(pid)
		if p then
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
		end
	end, 4000, player:getId())
	return true
end
login:register()

-- Every hour one climber online (level 8+, not staff, not last hour's winner) gets a little gold and a shout-out.
local lastLucky
local lucky = GlobalEvent("SpireLuckyClimber")
function lucky.onThink(interval)
	local list = {}
	for _, p in ipairs(Game.getPlayers()) do
		table.insert(list, { name = p:getName(), level = p:getLevel(), staff = p:getGroup():getAccess() })
	end
	local name = SpireDaily.luckyPick(list, lastLucky, math.random())
	local p = name and Player(name)
	if not p then
		return true
	end
	lastLucky = name
	local gold = SpireDaily.luckyGold(p:getLevel())
	p:setBankBalance(p:getBankBalance() + gold)
	p:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
	Game.broadcastMessage(string.format("Lucky climber of the hour: %s! %d gold has been added to their bank.", name, gold), MESSAGE_EVENT_ADVANCE)
	return true
end
lucky:interval(60 * 60 * 1000)
lucky:register()

-- Every 6 hours: a tower bounty on the strongest climber online in PvP range (rules: lib/spirebound/daily.lua)
local topBounty = GlobalEvent("SpireTopBounty")
function topBounty.onThink(interval)
	local list = {}
	for _, p in ipairs(Game.getPlayers()) do
		table.insert(list, { name = p:getName(), level = p:getLevel(), staff = p:getGroup():getAccess() })
	end
	local name = SpireDaily.topBountyPick(list)
	local p = name and Player(name)
	if not p then
		return true
	end
	local total = SpireBounty.add(p:getGuid(), p:getName(), SpireDaily.topBountyGold(p:getLevel()), "the tower")
	Game.broadcastMessage(string.format("The tower marks its strongest climber: %s (level %d). Whoever brings them down claims %d gold.",
		name, p:getLevel(), total), MESSAGE_EVENT_ADVANCE)
	return true
end
topBounty:interval(6 * 60 * 60 * 1000)
topBounty:register()
