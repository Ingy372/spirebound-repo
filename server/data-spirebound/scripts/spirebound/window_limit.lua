-- Up to 3 game windows per computer (QA16; Q53, Claude's call, 2026-11-27; DESIGN.md 12). The engine only limits
-- characters per account (2), so a 4th character logging in from the same address is sent away with a message.
-- Staff never count, and neither do the test characters ("Pilot ..." on the autopilot accounts), so Claude's party
-- tests on Jay's PC keep working.
SpireWindows = SpireWindows or { MAX = 3 }

-- Pure: may a character join when `others` (characters already online from the same address, already filtered) exist?
function SpireWindows.allowed(others)
	return others < SpireWindows.MAX
end

function SpireWindows.exempt(player)
	return player:getGroup():getAccess() or player:getName():sub(1, 6) == "Pilot "
end

function SpireWindows.othersFrom(player)
	local ip, n = player:getIp(), 0
	if not ip or ip == 0 then
		return 0
	end
	for _, p in ipairs(Game.getPlayers()) do
		if p ~= player and p:getIp() == ip and not SpireWindows.exempt(p) then
			n = n + 1
		end
	end
	return n
end

local login = CreatureEvent("SpireWindowLimit")
function login.onLogin(player)
	if SpireWindows.exempt(player) or SpireWindows.allowed(SpireWindows.othersFrom(player)) then
		return true
	end
	local text = string.format("Only %d game windows per computer can be in the tower at once. Log out another character first.", SpireWindows.MAX)
	logger.info("[Spirebound] window limit: {} refused ({} already online from the same computer)", player:getName(), SpireWindows.othersFrom(player))
	player:popupFYI(text)
	local pid = player:getId()
	addEvent(function()
		local p = Player(pid)
		if p then
			p:remove()
		end
	end, 1500)
	return true
end
login:register()
