-- The test autopilot (tools/autopilot.py, client module game_autopilot): lets Claude's test characters jump to the
-- start of a test route and heal between runs, so a run tests the place, not the walk there.
-- Only works on the local test account whose e-mail is autopilot@localhost (server/sql/dev_accounts.sql). The sign-up
-- page refuses any e-mail without a real domain, so no player can ever have that account; for everyone else the words
-- are ordinary chat.
--   /pilot jump x, y, z    go there
--   /pilot heal            full health and mana
--   /pilot level n         (gear tests) set your level
--   /pilot gearreset       (gear tests) forget the barracks weapon, style and trophies; drop Spirebound gear
--   /pilot spawn name, n, hp   (spell tests) top up to n monsters of that name around you, each with hp health
--   /pilot clear           remove every monster within 9 tiles
--   /pilot give id, n      items into the backpack
--   /pilot hp n            set your health (PvP tests)
--   /pilot pardon          clear skulls and unjust kills from test fights
--   /pilot arena join|go|stop   a Wild PvP arena event with just the test characters
--   /pilot wall id, n      a wall item (vine 2130, barrier 2128) n tiles ahead of you
--   /pilot unsummon        send your summons away
--   /pilot logout          leave the game at once (even right after a fight)
--   /pilot final p f       (style tests) path p and final style f chosen and finished
--   /pilot path key        (style tests) that path chosen and finished (its ability ready)
--   /pilot mastery n       (style tests) Mastery n of the first stage, no path, no stance
--   /pilot stairkey [off]  (boss tests) the Axe-Lord's hall opens without the Stair Key's three pieces
--   /pilot newbie          (tutorial tests) become a brand-new character again: no path, no mode, the Proving not done,
--                          a practice club in hand, at the Registrar
--   /pilot trace on|off    log what every spell you cast did (server log, [SPELLTRACE]); refills you after each
--                          cast and lets you cast Lost Arts, so a test can try every spell
local pilot = TalkAction("/pilot")

function pilot.onSay(player, words, param)
	local q = db.storeQuery("SELECT `email` FROM `accounts` WHERE `id` = " .. player:getAccountId())
	local email = q and Result.getString(q, "email")
	if q then
		Result.free(q)
	end
	if email ~= "autopilot@localhost" then
		return false -- not a dev account: the words go out as ordinary chat, as if the command did not exist
	end
	local cmd, rest = param:match("^%s*(%a+)%s*(.*)$")
	if cmd == "jump" then
		local x, y, z = rest:match("(%d+)%D+(%d+)%D+(%d+)")
		local to = x and Position(tonumber(x), tonumber(y), tonumber(z))
		if not to or not Tile(to) then
			player:sendCancelMessage("pilot: no such place")
			return true
		end
		player:teleportTo(to)
		player:sendTextMessage(MESSAGE_STATUS, "pilot: jumped")
	elseif cmd == "level" then -- (gear tests) set the test character's level
		local n = tonumber(rest:match("(%d+)"))
		if not n then
			player:sendCancelMessage("pilot: level n")
			return true
		end
		local l = n - 1
		local need = math.floor((50 * l * l * l - 150 * l * l + 400 * l) / 3) -- Tibia: experience for level n
		player:addExperience(math.max(0, need - player:getExperience()), false)
		player:sendTextMessage(MESSAGE_STATUS, "pilot: level " .. player:getLevel())
	elseif cmd == "gearreset" then -- (gear tests) forget the barracks' weapon, style and trophies; drop Spirebound gear
		local k = player:kv():scoped("spirebound")
		for _, key in ipairs({ "gear_main_1", "style_points", "style_path", "style_final", "style_respec_at", "style_stance" }) do
			k:remove(key)
		end
		for _, t in ipairs(SpireTrophies.LIST) do
			k:remove("trophy_" .. t.id)
		end
		for _, it in ipairs(SpireGear.carried(player)) do
			if SpireGear.defOf(it) then
				it:remove()
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: gear reset")
	elseif cmd == "heal" then
		player:addHealth(player:getMaxHealth())
		player:addMana(player:getMaxMana())
		player:sendTextMessage(MESSAGE_STATUS, "pilot: healed")
	elseif cmd == "spawn" then
		local name, n, hp = rest:match("^([^,]+),%s*(%d+),%s*(%d+)")
		n, hp = tonumber(n), tonumber(hp)
		if not name then
			player:sendCancelMessage("pilot: spawn name, count, health")
			return true
		end
		local here = player:getPosition()
		local have = {}
		for _, c in ipairs(Game.getSpectators(here, false, false, 5, 5, 5, 5)) do
			if c:isMonster() and c:getName():lower() == name:lower() then
				table.insert(have, c)
			end
		end
		for _, c in ipairs(have) do
			c:setMaxHealth(hp)
			c:addHealth(hp)
		end
		local made, tries = #have, 0
		while made < n and tries < 60 do
			tries = tries + 1
			local a = math.random() * 2 * math.pi
			local d = 2 + math.random(0, 2)
			local pos = Position(here.x + math.floor(math.cos(a) * d + 0.5), here.y + math.floor(math.sin(a) * d + 0.5), here.z)
			local m = Tile(pos) and Game.createMonster(name, pos, false, false)
			if m then
				m:setMaxHealth(hp)
				m:addHealth(hp)
				made = made + 1
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: " .. made .. " " .. name)
	elseif cmd == "mastery" then -- (style tests, P11) set the style tree to Mastery n of stage 1 (no path chosen)
		local n = math.max(1, math.min(10, tonumber(rest) or 1))
		local k = player:kv():scoped("spirebound")
		k:set("style_points", SpireGearData.STYLE_POINTS[n])
		k:remove("style_path")
		k:remove("style_final")
		k:remove("style_stance")
		player:sendTextMessage(MESSAGE_STATUS, "pilot: mastery " .. n)
	elseif cmd == "path" then -- (style tests, P1b) choose a path and finish it: Mastery 10 of stage 2, its ability learned
		local key = rest:gsub("%s", "")
		local k = player:kv():scoped("spirebound")
		k:set("style_points", SpireGearData.STYLE_POINTS[20])
		k:set("style_path", key)
		k:remove("style_final")
		player:sendTextMessage(MESSAGE_STATUS, "pilot: path " .. key)
	elseif cmd == "final" then -- (style tests, P1c) "/pilot final path final": both choices made, the style finished
		local path, final = rest:match("^(%S+)%s+(%S+)")
		local k = player:kv():scoped("spirebound")
		k:set("style_points", SpireGearData.STYLE_POINTS[30])
		k:set("style_path", path)
		k:set("style_final", final)
		player:sendTextMessage(MESSAGE_STATUS, "pilot: final " .. tostring(final))
	elseif cmd == "stairkey" then -- (boss tests) open the Axe-Lord's hall without the three pieces; "/pilot stairkey off" undoes it
		local k = player:kv():scoped("spirebound")
		if rest:find("off") then
			k:remove("stair_key_pilot")
		else
			k:set("stair_key_pilot", os.time())
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: stairkey " .. (k:get("stair_key_pilot") and "on" or "off"))
	elseif cmd == "newbie" then -- (tutorial tests, G2) start over as a character that has just reached the Registrar
		player:setVocation(Vocation(0))
		player:kv():scoped("spirebound"):remove("difficulty")
		player:kv():scoped("spirebound-proving"):remove("done")
		player:kv():scoped("spirebound-notices"):remove("spellbar")
		player:setStorageValue(50121, -1) -- Pell's First Blood can be taken again (G3 test)
		player:setStorageValue(50122, -1)
		player:kv():scoped("quest-tracker"):remove("known-quests") -- the tracker adds Pell's quest again as if new
		player:kv():scoped("quest-tracker"):remove("tracked-missions")
		for _, slot in ipairs({ CONST_SLOT_LEFT, CONST_SLOT_RIGHT }) do
			local it = player:getSlotItem(slot)
			if it then
				it:remove()
			end
		end
		player:addItem(3270, 1, true, 1, CONST_SLOT_LEFT)
		if Town(50) then
			player:setTown(Town(50))
		end
		local r = WorldPoints.tutorial_registrar
		if r then
			player:teleportTo(Position(r.x - 2, r.y, r.z))
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: newbie")
	elseif cmd == "clear" then
		local n = 0
		for _, c in ipairs(Game.getSpectators(player:getPosition(), false, false, 9, 9, 9, 9)) do
			if c:isMonster() then
				c:remove()
				n = n + 1
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: cleared " .. n)
	elseif cmd == "give" then
		local id, n = rest:match("(%d+)%D+(%d+)")
		player:addItem(tonumber(id), tonumber(n))
		player:sendTextMessage(MESSAGE_STATUS, "pilot: given")
	elseif cmd == "hp" then
		-- (PvP tests) set your health, to test what saves you from a killing blow
		local n = tonumber(rest:match("(%d+)")) or player:getMaxHealth()
		player:addHealth(n - player:getHealth())
		player:sendTextMessage(MESSAGE_STATUS, "pilot: health " .. player:getHealth())
	elseif cmd == "pardon" then
		-- (PvP tests) forget skulls and unjust kills from the test fights
		player:setSkull(SKULL_NONE)
		player:setSkullTime(0)
		SpirePvP.scope(player):remove("frags")
		player:sendTextMessage(MESSAGE_STATUS, "pilot: pardoned")
	elseif cmd == "arena" then
		-- (PvP tests) a Wild PvP arena event with just the test characters: "join", then "go" from the last one in
		local what = rest:match("(%a+)")
		if what == "join" then
			if not SpireArena.current then
				SpireArena.current = SpireArena.new("wild", os.time())
			end
			local ok, why = SpireArena.join(SpireArena.current, player:getGuid(), player:getName(), player:getLevel())
			player:sendTextMessage(MESSAGE_STATUS, "pilot: arena " .. (ok and "joined" or tostring(why)))
		elseif what == "go" and SpireArena.current then
			local keep = SpireArena.MIN_PLAYERS
			SpireArena.MIN_PLAYERS = 2
			SpireArena.begin()
			SpireArena.MIN_PLAYERS = keep
			player:sendTextMessage(MESSAGE_STATUS, "pilot: arena " .. tostring(SpireArena.current and SpireArena.current.phase))
		elseif what == "stop" and SpireArena.current then
			if SpireArena.current.phase == "running" then
				SpireArena.finish(SpireArena.current, {})
			else
				SpireArena.current = nil
			end
			player:sendTextMessage(MESSAGE_STATUS, "pilot: arena stopped")
		end
	elseif cmd == "wall" then
		-- (PvP spell tests) put a wall item (vine 2130, barrier 2128) this many tiles ahead of you
		local id, n = rest:match("(%d+)%D+(%d+)")
		local pos = player:getPosition()
		for _ = 1, tonumber(n) do
			pos:getNextPosition(player:getDirection())
		end
		local it = Game.createItem(tonumber(id), 1, pos)
		if it then
			it:decay()
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: wall " .. (it and "placed" or "failed"))
	elseif cmd == "unsummon" then
		for _, m in ipairs(player:getSummons()) do
			m:remove()
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: summons gone")
	elseif cmd == "logout" then
		-- end of a test: leave at once, summons and all, so the next tester on this account can log in
		for _, m in ipairs(player:getSummons()) do
			m:remove()
		end
		SpireSpells.TRACE[player:getId()] = nil
		player:remove()
		return true
	elseif cmd == "trace" then
		SpireSpells.TRACE[player:getId()] = rest:find("on") and true or nil
		player:sendTextMessage(MESSAGE_STATUS, "pilot: trace " .. (SpireSpells.TRACE[player:getId()] and "on" or "off"))
	else
		player:sendCancelMessage("pilot: jump x, y, z | heal | spawn name, n, hp | clear | give id, n | trace on|off")
	end
	return true -- handled: the client showed "/pilot ..." as normal chat when this returned false
end

pilot:separator(" ")
pilot:groupType("normal")
pilot:register()
