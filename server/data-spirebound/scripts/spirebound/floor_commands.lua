-- GM command /floor (testing; removed from the production GM group before launch, DESIGN.md 3.2)
--   /floor                    -> status of every floor
--   /floor field N            -> mark floor N's field boss dead (opens the labyrinth)
--   /floor clear N name,name  -> record floor N's first clear and open floor N+1
--   /floor reset N            -> wipe floor N's record
local floorCmd = TalkAction("/floor")

function floorCmd.onSay(player, words, param)
	if not player:getGroup():getAccess() then
		return true
	end
	local args = param:split(" ")
	local action, n = args[1], tonumber(args[2] or "")
	if not action or action == "" then
		local lines = {}
		for i = 1, Floors.LAUNCH_FLOORS do
			local r = Floors.get(i)
			table.insert(lines, string.format("F%d %s: %s, pass %s, boss %s", i, Floors.names[i],
				Floors.isOpen(i) and "open" or "sealed", r.fieldBossDeadAt and "open" or "sealed",
				r.bossDeadAt and ("cleared by " .. table.concat(r.credit or {}, ", ")) or "alive"))
		end
		player:showTextDialog(3217, table.concat(lines, "\n"))
		return false
	end
	if not n then
		player:sendCancelMessage("Usage: /floor [field|clear|reset] N [names]")
		return false
	end
	if action == "field" then
		player:sendTextMessage(MESSAGE_ADMINISTRATOR, Floors.markFieldBoss(n, { player:getName() }) and "Pass opened." or "Pass was already open.")
	elseif action == "clear" then
		local names = args[3] and args[3]:split(",") or { player:getName() }
		if Floors.recordClear(n, names, names[#names], 0) then
			Floors.announceClear(n, names)
		else
			player:sendCancelMessage("Floor " .. n .. " was already cleared.")
		end
	elseif action == "reset" then
		Floors.reset(n)
		player:sendTextMessage(MESSAGE_ADMINISTRATOR, "Floor " .. n .. " reset.")
	end
	logger.info("[Spirebound] /floor {} by {}", param, player:getName())
	return false
end

floorCmd:separator(" ")
floorCmd:groupType("god")
floorCmd:register()
