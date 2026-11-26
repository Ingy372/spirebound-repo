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
--   /pilot give id, n      items into the backpack (says if they did not fit)
--   /pilot emptybag        (M1 tests) empty the backpack
--   /pilot pvphit          (M5 tests) start the player-fight lock, as if a player had hit you
--   /pilot hp n            set your health (PvP tests)
--   /pilot beacon n        (M1 tests) put out every fire of floor n's Beacon
--   /pilot pardon          clear skulls and unjust kills from test fights
--   /pilot arena join|go|stop   a Wild PvP arena event with just the test characters
--   /pilot arena solo|open|unban   (M4 tests) you and an absent dummy; sign-ups only; lift a deserter ban
--   /pilot wall id, n      a wall item (vine 2130, barrier 2128) n tiles ahead of you
--   /pilot unsummon        send your summons away
--   /pilot logout          leave the game at once (even right after a fight)
--   /pilot final p f       (style tests) path p and final style f chosen and finished
--   /pilot path key        (style tests) that path chosen and finished (its ability ready)
--   /pilot quest id state  (quest tests) set a quest's state; taking a delivery also gives its item
--   /pilot kit             (HB) the test kit: a Ranger wears a quiver of arrows in its shield hand
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
	if not email or not email:match("^autopilot%d*@localhost$") then -- autopilot2/3: the party Pilots (S4)
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
		if need >= player:getExperience() then
			player:addExperience(need - player:getExperience(), false)
		else -- (ability tests raise a tester to 280 and put it back afterwards)
			player:removeExperience(player:getExperience() - need, false)
		end
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
	elseif cmd == "fightkit" then -- what this character can really cast now, for the autopilot to fight like a player
		-- "pilot fightkit: attack=words/mana/cd/range,...; heal=words/mana/cd,...; skills=words/cd,..."
		-- (Jay, 2026-11-25: the autopilot only swung its weapon, so kill speed and mana use were never measured)
		local base, lvl = player:getVocation():getBaseId(), player:getLevel()
		local atk, heal, skills = {}, {}, {}
		for _, row in ipairs(SpireSpells.list) do
			if not row.lostArt and not row.style and not row.path and not row.final and SpireSpells.allowed(row, base)
					and SpireSpells.levelFor(row, base) <= lvl and (row.mana or 0) <= player:getMaxMana() then
				if row.kind == "attack_target" or row.kind == "attack_area" or row.kind == "strike" then
					table.insert(atk, string.format("%s/%d/%d/%d", row.words, row.mana or 0, row.cd or 2,
						row.kind == "attack_target" and (row.range or 4) or 1))
				elseif row.kind == "heal_self" or row.kind == "heal" or row.kind == "heal_burst" then
					table.insert(heal, string.format("%s/%d/%d", row.words, row.mana or 0, row.cd or 1))
				end
			end
		end
		local fam = SwordSkills.heldFamily(player)
		for _, s in ipairs(SwordSkills.list) do
			if fam and s.family == fam and (s.level or 1) <= lvl and (not s.twinFang or SwordSkills.hasTwinFang(player)) then
				table.insert(skills, string.format("%s/%d", s.words, math.floor((s.cd or 4000) / 1000)))
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot fightkit: attack=" .. table.concat(atk, ",") .. "; heal="
			.. table.concat(heal, ",") .. "; skills=" .. table.concat(skills, ","))
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
	elseif cmd == "kit" then -- (HB) the test kit: a Ranger wears a quiver with 100 arrows in the shield hand
		if player:getVocation():getBaseId() == 3 then
			local worn = player:getSlotItem(CONST_SLOT_RIGHT)
			if worn and worn:getId() ~= SpireQuiver.ID then
				worn:moveTo(player:getSlotItem(CONST_SLOT_BACKPACK) or player:getPosition())
				worn = nil
			end
			if not worn then
				SpireQuiver.give(player, 100)
			elseif worn:isContainer() and worn:getItemCountById(3447) < 50 then
				worn:addItem(3447, 100)
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: kit")
	elseif cmd == "quest" then -- (quest tests) "/pilot quest id state": set a quest's state (-1 new, 1 taken, 2 ready, 3 done);
		-- taking a delivery quest also hands over its item
		local id, st = rest:match("^(%S+)%s+(%-?%d+)")
		local q = id and SpireQuests.get(id)
		if q then
			player:setStorageValue(q.storage, tonumber(st))
			if tonumber(st) == 1 and q.kind == "deliver" and player:getItemCount(q.item) == 0 then
				player:addItem(q.item, 1)
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: quest " .. tostring(id) .. " " .. tostring(st))
	elseif cmd == "gear" then -- (boss tests) "/pilot gear n": wear the class's Floor 1 weapon and armour at tier n, familiarity full
		local t = tonumber(rest:match("%d+")) or 3
		local voc = player:getVocation():getBaseId()
		local worn = {}
		local family = ({ [4] = "sword", [3] = "bow" })[voc] -- the weapon the fight kit's skills need
		for _, spec in ipairs({ { src = "main", slot = CONST_SLOT_LEFT }, { src = "quest", slot = voc == 3 and CONST_SLOT_LEGS or CONST_SLOT_ARMOR } }) do
			local d = spec.src == "main" and family and SpireGear.mainFor(voc, 1, family) or SpireGear.find(voc, 1, spec.src)
			if d then
				local old = player:getSlotItem(spec.slot)
				if old then
					old:remove()
				end
				local item = player:addItem(d.base, 1, false, 1, spec.slot)
				if item then
					item:setCustomAttribute("sb_gear", d.id)
					SpireGear.setState(item, { tier = t, famPoints = 10 ^ 6, awakened = false })
					table.insert(worn, d.name)
				end
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: gear tier " .. t .. ": " .. table.concat(worn, ", "))
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
		local before = player:getItemCount(tonumber(id))
		player:addItem(tonumber(id), tonumber(n))
		local got = player:getItemCount(tonumber(id)) - before
		player:sendTextMessage(MESSAGE_STATUS, got > 0 and ("pilot: given " .. got) or "pilot: no room, it fell on the floor")
	elseif cmd == "pvphit" then -- (M5 tests) start the player-fight lock as if another player had hit you
		SpirePvPLock.mark(player, os.time())
		player:sendTextMessage(MESSAGE_STATUS, "pilot: player fight for " .. SpirePvPLock.LOCK .. " seconds")
	elseif cmd == "emptybag" then -- (M1 tests) the test character's backpack, emptied (loot from earlier runs fills it)
		local bag = player:getSlotItem(CONST_SLOT_BACKPACK)
		local n = 0
		if bag and bag:isContainer() then
			for i = bag:getSize() - 1, 0, -1 do
				local it = bag:getItem(i)
				if it then
					it:remove()
					n = n + 1
				end
			end
		end
		player:sendTextMessage(MESSAGE_STATUS, "pilot: emptied " .. n)
	elseif cmd == "beacon" then -- (M1 tests) "/pilot beacon n": put out every fire of floor n's Beacon
		local n = tonumber(rest:match("(%d+)")) or 1
		SpireBeacons.put(n, { slots = {} })
		SpireBeacons.syncBowls(n, os.time())
		player:sendTextMessage(MESSAGE_STATUS, "pilot: beacon " .. n .. " dark")
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
		elseif what == "solo" and not SpireArena.current then
			-- (M4 tests) the real event loop with one test character and an absent dummy: stand still and watch the
			-- pressure rise, the idle move at 60 seconds and the deserter at 2 minutes
			local st = SpireArena.new("lms", os.time())
			SpireArena.current = st
			SpireArena.join(st, player:getGuid(), player:getName(), math.max(player:getLevel(), SpireArena.MIN_LEVEL))
			SpireArena.join(st, -1, "Arena Dummy", SpireArena.MIN_LEVEL)
			st.players[-1].dummy = true
			local keep = SpireArena.MIN_PLAYERS
			SpireArena.MIN_PLAYERS = 2
			SpireArena.begin()
			SpireArena.MIN_PLAYERS = keep
			player:sendTextMessage(MESSAGE_STATUS, "pilot: arena solo " .. tostring(SpireArena.current and SpireArena.current.phase))
		elseif what == "open" and not SpireArena.current then -- (M4 tests) sign-ups open, no broadcast, no timer
			SpireArena.current = SpireArena.new("lms", os.time())
			player:sendTextMessage(MESSAGE_STATUS, "pilot: arena open")
		elseif what == "unban" then -- (M4 tests) lift a deserter ban
			player:kv():scoped("spirebound-arena"):remove("banUntil")
			player:sendTextMessage(MESSAGE_STATUS, "pilot: arena unbanned")
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
