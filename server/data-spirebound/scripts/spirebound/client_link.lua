-- Keeps the Spirebound client UI (floor indicator, difficulty icon, sword-skill bar) up to date.
local lastFloor, lastFamily, lastZone = {}, {}, {}

local login = CreatureEvent("SpireClientLogin")
function login.onLogin(player)
	addEvent(function(pid)
		local p = Player(pid)
		if p then
			SpireClient.sendAll(p)
			SpireClient.seedSpellBar(p, true) -- every login: the client only swaps out stock Tibia spells (Grok session 3)
			lastFloor[pid] = Floors.at(p:getPosition()) .. "|" .. SpireClient.placeName(p:getPosition())
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
		local pos = p:getPosition()
		local key = Floors.at(pos) .. "|" .. SpireClient.placeName(pos)
		if lastFloor[pid] ~= key then
			lastFloor[pid] = SpireClient.sendFloor(p)
		end
		local zone = SpirePvP.zoneAt(p:getPosition())
		if lastZone[pid] ~= zone then
			lastZone[pid] = zone
			SpireClient.send(p, { t = "zone", tier = zone })
			-- The first time a character walks into an [Open PvP] zone, say what that means (Grok playtest, 2026-11-24:
			-- "if PvP is really open on the newbie floor, new players should be told")
			if zone == "open" and p:kv():scoped("spirebound-notices"):get("open-pvp") ~= true then
				p:kv():scoped("spirebound-notices"):set("open-pvp", true)
				p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("You have left the Guarded land around town. Out here, [Open PvP] means players of level %d and above may fight each other. Below level %d you can't attack anyone and no one can attack you.", SpirePvP.NEWBIE_LEVEL, SpirePvP.NEWBIE_LEVEL))
			end
		end
		local fam, list = SpireClient.skillList(p)
		if lastFamily[pid] ~= fam then
			lastFamily[pid] = fam
			SpireClient.send(p, { t = "skills", family = fam, list = list })
		end
	end
	return true
end
tick:interval(1000)
tick:register()
