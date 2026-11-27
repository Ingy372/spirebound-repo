-- Rumours (adventure layer 4.7, roadmap AD7). Innkeepers and townsfolk answer "rumour": one per character every
-- 20 hours. A rumour points at something this character has not found yet, in its level band first, and names the
-- ground, never the spot. The row on the Discoveries page then reads "??? (rumoured: <ground>)".
-- Jay, 2026-11-27: rumours never point at secrets or hidden beasts (riddles only). They cover ground chests, builders'
-- stones, elites and rare roamers. A message bottle from the water holds one secret's riddle instead.
SpireRumours = SpireRumours or {}
SpireRumours.COOLDOWN = 20 * 3600
SpireRumours.CATEGORIES = { chest = true, stone = true, elite = true, roamer = true }
SpireRumours.TALKERS = { ["Innkeeper Roan"] = true, ["Innkeeper Bess"] = true } -- plus every townsperson (SpireTownsfolk)

-- Floor 1's elites and where they lead their packs (FLOOR1_REVIEW F1-11; quest text in lib/spirebound/quests.lua)
SpireRumours.ELITE_GROUND = { ["Old Bristleback"] = "boar_meadow", ["Moonhowl"] = "wolf_copse", ["Mossback Snapper"] = "reed_marsh",
	["Blackthorn"] = "thornsnap_hollow", ["Prism Shardling"] = "shard_fields", ["Granite Warden"] = "old_quarry" }

-- How each kind is told (%s = the ground). Several per kind, picked by the row, so two players hear different words.
SpireRumours.LINES = {
	chest = {
		"A trapper swears there's a chest in %s that nobody has thought to open.",
		"They say the old hunters hid a strongbox somewhere in %s. Deep in, where it's quiet.",
		"My cousin found a chest in %s once. Wouldn't say where. You might have better luck.",
	},
	stone = {
		"An old mason told me the builders left a carved stone in %s. Words on it, if you can read them.",
		"There's writing on a stone out in %s, older than the town. Scholars would pay to know what it says.",
	},
	elite = {
		"Hunters whisper that something bigger than the rest leads the beasts of %s.",
		"A ranger came back from %s pale as milk. Said the pack had a leader the size of a cart.",
		"Don't go into %s thinking you've seen all it has. Something there is older, and it glows.",
	},
	roamer = {
		"Folk say a strange beast wanders %s now and then, and never for long. Worth a fortune, if you catch it.",
		"Every so often something rare turns up in %s. By the time the word reaches town, it's gone.",
	},
}

-- Pure: may this character hear a new rumour? last = time of the last one
function SpireRumours.ready(last, now)
	return not last or now - last >= SpireRumours.COOLDOWN
end

-- Pure: pick one candidate. cands = { { row, lo, hi, ground } }; level = the character's level; roll in [0,1).
-- Ones in the level band come first; otherwise the closest band.
function SpireRumours.pick(cands, level, roll)
	if #cands == 0 then
		return nil
	end
	local inBand = {}
	for _, c in ipairs(cands) do
		if level >= c.lo and level <= c.hi then
			table.insert(inBand, c)
		end
	end
	local pool = inBand
	if #pool == 0 then
		local best
		for _, c in ipairs(cands) do
			local d = level < c.lo and c.lo - level or level - c.hi
			if not best or d < best then
				best = d
			end
		end
		pool = {}
		for _, c in ipairs(cands) do
			local d = level < c.lo and c.lo - level or level - c.hi
			if d == best then
				table.insert(pool, c)
			end
		end
	end
	return pool[math.floor(roll * #pool) + 1]
end

-- Pure: the words
function SpireRumours.line(category, groundTitle, seed)
	local list = SpireRumours.LINES[category] or SpireRumours.LINES.chest
	local where = SpireFinds and SpireFinds.theGround(groundTitle) or groundTitle
	return string.format(list[(seed % #list) + 1], where)
end

local function groundById(id)
	for _, g in ipairs(SpireWilds.grounds) do
		if g.id == id then
			return g
		end
	end
end

-- Everything on Floor 1 this character could hear about: { row, lo, hi, ground (title) }
function SpireRumours.candidates(player)
	local out = {}
	for _, r in ipairs(SpireDiscoveries.floorRows(1)) do
		if SpireRumours.CATEGORIES[r.category] and not SpireDiscoveries.foundAt(player, r.category, r.id)
			and not SpireDiscoveries.rumoured(player, r.category, r.id) then
			local gid
			if r.category == "chest" or r.category == "stone" then
				gid = r.id
			elseif r.category == "elite" then
				gid = SpireRumours.ELITE_GROUND[r.id]
			end
			if gid then
				local g = groundById(gid)
				if g then
					table.insert(out, { row = r, lo = g.lo, hi = g.hi, ground = g.title })
				end
			elseif r.category == "roamer" and SpireRoamers and SpireRoamers.get then
				local ro = SpireRoamers.get(r.id)
				local g = ro and ro.grounds and groundById(ro.grounds[math.random(#ro.grounds)])
				if g then
					table.insert(out, { row = r, lo = ro.lo, hi = ro.hi, ground = g.title })
				end
			end
		end
	end
	return out
end

local function last(player)
	return player:kv():scoped("spirebound"):get("rumour_at")
end

-- Give this character a rumour now (nil + reason when none). force skips the 20-hour wait (tests).
function SpireRumours.tell(player, force)
	local now = os.time()
	if not force and not SpireRumours.ready(last(player), now) then
		local h = math.ceil((SpireRumours.COOLDOWN - (now - last(player))) / 3600)
		return nil, string.format("That's all I've heard. Come back tomorrow, I'll have news (in about %d hour%s).", h, h == 1 and "" or "s")
	end
	local c = SpireRumours.pick(SpireRumours.candidates(player), player:getLevel(), math.random())
	if not c then
		return nil, "Rumours? You've seen more of these plains than I have. Tell me one!"
	end
	SpireDiscoveries.setRumour(player, c.row.category, c.row.id, (c.ground:gsub("^The ", "")))
	player:kv():scoped("spirebound"):set("rumour_at", now)
	return SpireRumours.line(c.row.category, c.ground, #c.row.id + now % 7) .. " (Your Journal's Discoveries page remembers it.)", c
end

local function isTalker(name)
	if SpireRumours.TALKERS[name] then
		return true
	end
	for _, f in ipairs(SpireTownsfolk or {}) do
		if f.name == name then
			return true
		end
	end
	return false
end

-- NPC talk hook: true when handled. Called by every generated NPC (through SpireGear.talk) and the townsfolk.
function SpireRumours.talk(npc, handler, player, msg, npcName)
	local lower = (msg or ""):lower()
	if not (lower:find("rumour", 1, true) or lower:find("rumor", 1, true) or lower:find("gossip", 1, true)) then
		return false
	end
	if not isTalker(npcName or npc:getName()) then
		return false
	end
	local text, why = SpireRumours.tell(player)
	handler:say(text or why, npc, player)
	return true
end

-- ---------------------------------------------------------------- the message bottle (fishing)
-- Pure: which secret's riddle a bottle holds: one this character has not found and does not hold yet; nil if none
function SpireRumours.bottlePick(secrets, found, held, roll)
	local pool = {}
	for _, s in ipairs(secrets) do
		if s.floor == 1 and s.hint and not found(s.id) and not held(s.id) then
			table.insert(pool, s)
		end
	end
	if #pool == 0 then
		return nil
	end
	return pool[math.floor(roll * #pool) + 1]
end

function SpireRumours.openBottle(player)
	local s = SpireRumours.bottlePick(SpireSecrets.list, function(id) return SpireSecrets.hasFound(player, id) end,
		function(id) return SpireSecrets.holdsRiddle(player, id) end, math.random())
	if not s then
		return "The note inside is blank, washed clean by the river."
	end
	SpireSecrets.heldRiddles(player):set(s.id, os.time())
	return "A note in a shaky hand: \"" .. s.hint .. "\" (Your Journal keeps the riddle.)"
end
