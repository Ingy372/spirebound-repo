-- Out-of-date clients get told (Grok session 3, 2026-11-25): the tester played on an old copy of the Spirebound client
-- and reported bugs that were already fixed (keyword braces in speech bubbles, Tibia spells on the action bar, the Store
-- button). The Spirebound client says "hello" with its build number a moment after login; a player whose client is
-- older, or isn't the Spirebound client at all, is asked to update.
local seen = {} -- player guid -> client build

local opcode = CreatureEvent("SpireClientVersionOpcode")
function opcode.onExtendedOpcode(player, op, buffer)
	if op == SpireClient.OPCODE and buffer:find('"t"%s*:%s*"hello"') then
		seen[player:getGuid()] = tonumber(buffer:match('"v"%s*:%s*(%d+)')) or 0
	end
	return true
end
opcode:register()

local login = CreatureEvent("SpireClientVersionLogin")
function login.onLogin(player)
	player:registerEvent("SpireClientVersionOpcode")
	seen[player:getGuid()] = nil
	addEvent(function(pid, guid)
		local p = Player(pid)
		if not p or p:getGroup():getAccess() then
			return
		end
		if (seen[guid] or 0) < SpireClient.CLIENT_VERSION then
			p:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your Spirebound client is out of date, so some fixes are missing. "
				.. "Please download it again (run the setup again) before you play on.")
		end
	end, 10000, player:getId(), player:getGuid())
	return true
end
login:register()

if SpireCleanup then
	SpireCleanup.add(function(pid, guid) seen[guid] = nil end)
end
