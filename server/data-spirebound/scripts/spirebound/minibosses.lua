-- Hidden mini-bosses in the game (gear progression spec 4.8). Rules: lib/spirebound/trophies.lua.
-- scripts/spirebound/secrets.lua calls SpireTrophies.onSecret when someone steps on a secret's trigger tile.

local alive = {}    -- trophy id -> monster id while the boss is up
local restUntil = {} -- trophy id -> os.time() when it may wake again

function SpireTrophies.onSecret(player, secret, first)
	for _, t in ipairs(SpireTrophies.LIST) do
		if t.secret == secret.id then
			if alive[t.id] and Creature(alive[t.id]) then
				return
			end
			if os.time() < (restUntil[t.id] or 0) then
				if first then
					player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Fresh tracks. Something big was here not long ago, and it will be back.")
				end
				return
			end
			local pos = (t.spawn and WorldPoints[t.spawn]) or player:getPosition()
			local m = Game.createMonster(t.boss, pos, true, true)
			if m then
				alive[t.id] = m:getId()
				m:say(t.boss:upper() .. " WAKES!", TALKTYPE_MONSTER_YELL)
			end
			return
		end
	end
end

local death = CreatureEvent("SpireMiniBossDeath")
function death.onDeath(creature, corpse, killer, mostDamageKiller, unjustified, mostDamageUnjustified)
	local t = SpireTrophies.byBoss(creature:getName())
	if not t then
		return true
	end
	alive[t.id] = nil
	restUntil[t.id] = os.time() + SpireTrophies.respawnDelay(math.random)
	local credit = {}
	for cid in pairs(creature:getDamageMap()) do
		local p = Player(cid)
		if p then
			SpireTrophies.grant(p, t.id)
			table.insert(credit, p)
		end
	end
	-- adventure layer 4.2/4.3: the first kill of the season is heard server-wide, never where; later kills are silent
	if SpireFinds and SpireFinds.first("beast", t.id, credit, t.boss) then
		SpireFinds.announce("beast", {}, nil, Floors.at(creature:getPosition()) > 0 and Floors.at(creature:getPosition()) or 1)
	end
	return true
end
death:register()

local login = CreatureEvent("SpireTrophyLogin")
function login.onLogin(player)
	SpireTrophies.apply(player)
	return true
end
login:register()
