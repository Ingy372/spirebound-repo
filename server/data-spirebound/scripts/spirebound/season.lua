-- /season: season tools for the owner (god only).
--   /season              -> current season number and what an end of season does
--   /season remix [n]    -> preview what season n (default: next) changes
--   /season end <number> -> archive everyone and wipe for the next season. Type the CURRENT season number to confirm.
--                           Nobody may be online except you. Restart the server afterwards.
local cmd = TalkAction("/season")
function cmd.onSay(player, words, param)
	local current = SpireSeason.current()
	local action, num = param:match("(%a+)%s*(%d*)")
	if action == "remix" then
		local n = tonumber(num) or current + 1
		local plan = SpireRemix.bossPlan(SpireFloorBosses, n)
		local lines = { string.format("Season %d remix preview (applies automatically when that season starts):", n), "" }
		for f = 2, 10 do
			local b, p = SpireFloorBosses[f], plan[f]
			if b and p then
				table.insert(lines, string.format("Floor %d: %s -> %s, %s -> %s", f, b.field, p.fieldPattern, b.boss, p.bossPattern))
			end
		end
		local moved = 0
		for id, p in pairs(SpireRemix.secretPlan(SpireSecrets.list, n)) do
			local s = SpireSecrets.get(id)
			if s and s.tier ~= p.tier then
				moved = moved + 1
			end
		end
		table.insert(lines, "")
		table.insert(lines, moved .. " secrets change reward size. Locations and hints stay.")
		player:showTextDialog(2821, table.concat(lines, "\n"))
		return false
	end
	if action ~= "end" then
		player:showTextDialog(2821, string.format("Season %d.\n\nSay '/season end %d' to end it: every character is archived to the Hall of Seasons, account-wide titles carry over, then characters, houses, guilds, the market and world progress are wiped. Accounts are kept. Restart the server afterwards.", current, current))
		return false
	end
	if tonumber(num) ~= current then
		player:sendCancelMessage("To confirm, type the current season number: /season end " .. current)
		return false
	end
	if #Game.getPlayers() > 1 then
		player:sendCancelMessage("Everyone else must be logged out first.")
		return false
	end
	local q = db.storeQuery("SELECT `id`, `account_id`, `name`, `level`, `vocation` FROM `players` WHERE `group_id` < 4")
	local count = 0
	if q then
		repeat
			SpireSeason.archivePlayer(Result.getNumber(q, "id"), Result.getNumber(q, "account_id"), Result.getString(q, "name"),
				Result.getNumber(q, "level"), Result.getNumber(q, "vocation"), current)
			count = count + 1
		until not Result.next(q)
		Result.free(q)
	end
	kv.scoped("spirebound-season"):set("number", current + 1)
	for _, sql in ipairs(SpireSeason.wipeStatements()) do
		db.query(sql)
	end
	logger.info("[Spirebound] season {} ended by {}: {} characters archived", current, player:getName(), count)
	player:showTextDialog(2821, string.format("Season %d is over. %d characters archived to the Hall of Seasons. Season %d begins after a server restart.", current, count, current + 1))
	return false
end
cmd:separator(" ")
cmd:groupType("god")
cmd:register()

local login = CreatureEvent("SpireSeasonLogin")
function login.onLogin(player)
	SpireSeason.applyLegacy(player)
	return true
end
login:register()
