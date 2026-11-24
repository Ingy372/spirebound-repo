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
