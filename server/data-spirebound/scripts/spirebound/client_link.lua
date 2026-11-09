-- Keeps the Spirebound client UI (floor indicator, difficulty icon, sword-skill bar) up to date.
local lastFloor, lastFamily = {}, {}

local login = CreatureEvent("SpireClientLogin")
function login.onLogin(player)
	addEvent(function(pid)
		local p = Player(pid)
		if p then
			SpireClient.sendAll(p)
			lastFloor[pid] = Floors.at(p:getPosition())
			lastFamily[pid] = SwordSkills.heldFamily(p) or ""
		end
	end, 1000, player:getId())
	return true
end
login:register()

-- Floor changes (walking, portals, stairs) and weapon swaps, checked every 2 seconds
local tick = GlobalEvent("SpireClientTick")
function tick.onThink(interval)
	for _, p in ipairs(Game.getPlayers()) do
		local pid = p:getId()
		local n = Floors.at(p:getPosition())
		if lastFloor[pid] ~= n then
			lastFloor[pid] = n
			SpireClient.send(p, { t = "floor", n = n, name = Floors.names[n] or "" })
		end
		local fam, list = SpireClient.skillList(p)
		if lastFamily[pid] ~= fam then
			lastFamily[pid] = fam
			SpireClient.send(p, { t = "skills", family = fam, list = list })
		end
	end
	return true
end
tick:interval(2000)
tick:register()
