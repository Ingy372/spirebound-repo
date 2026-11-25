-- Floor Beacons (DESIGN.md 3.6, roadmap M1; Jay 2026-11-25: "r1 do it"). Each open floor's town has a Beacon of four
-- fire bowls. A player hands in a Beacon Ember to light one bowl for an hour; every lit bowl gives everyone hunting on
-- that floor +5% experience and +5% loot, and with all four lit the floor's apex spawn refills faster.
-- One guild may hold at most two bowls on a floor at a time. State lives in Canary's kv store, so a restart keeps it.
-- Wiring (experience, loot, Ember drops, the bowls, the apex refill, the HUD): scripts/spirebound/beacons.lua.
SpireBeacons = {
	SLOTS = 4,
	DURATION = 3600, -- seconds a lit bowl burns
	XP_PER_SLOT = 0.05,
	LOOT_PER_SLOT = 0.05, -- an extra loot roll of this size per lit bowl
	GUILD_CAP = 2,
	EMBER = 9636, -- renamed "Beacon Ember" by tools/gen_gear.py (data/item_renames.json)
	UNLIT = 30964, -- empty fire bowl
	LIT = 30965, -- fire bowl
	-- the fourth bowl: extra apex monsters at the heart of the floor's apex spawn, back soon after they die
	APEX_EXTRA = 3,
	APEX_RETURN = 90, -- seconds
	-- where Embers come from (Claude's call, Jay can veto): sure drops from field bosses and hidden mini-bosses,
	-- a chance from elites and apex monsters
	FIELD_BOSS_EMBERS = 2,
	MINIBOSS_EMBERS = 1,
	ELITE_CHANCE = 0.08,
	APEX_CHANCE = 0.015,
	FLOOR1 = { field = "Gate Hound", elites = { "Grey Alpha", "Bandit Captain" }, apex = "Stonehorn Ram" },
	APEX = { [1] = "Stonehorn Ram", [2] = "Mesa Wyrmling", [3] = "Grove Hydraling", [4] = "Siege Beast",
		[5] = "Undying Champion", [6] = "Pyre Wyrm", [7] = "Shard Hydra", [8] = "Hoarfrost Wyrm",
		[9] = "Treasure Devourer", [10] = "Lapis Wyrm" },
}

local function store()
	return kv.scoped("spirebound-beacons")
end

-- rec = { slots = { [i] = { untilTime, by, guild } } }
function SpireBeacons.get(floor)
	local rec = store():get("floor-" .. floor) or {}
	rec.slots = rec.slots or {}
	return rec
end

function SpireBeacons.put(floor, rec)
	store():set("floor-" .. floor, rec)
end

-- Pure: is slot i burning at time now?
function SpireBeacons.isLit(rec, i, now)
	local s = rec.slots[i]
	return s ~= nil and (s.untilTime or 0) > now
end

-- Pure: how many bowls burn at time now
function SpireBeacons.litCount(rec, now)
	local n = 0
	for i = 1, SpireBeacons.SLOTS do
		if SpireBeacons.isLit(rec, i, now) then
			n = n + 1
		end
	end
	return n
end

-- Pure: how many burning bowls belong to this guild (guild 0 = no guild, never capped)
function SpireBeacons.guildCount(rec, guild, now)
	if not guild or guild == 0 then
		return 0
	end
	local n = 0
	for i = 1, SpireBeacons.SLOTS do
		if SpireBeacons.isLit(rec, i, now) and rec.slots[i].guild == guild then
			n = n + 1
		end
	end
	return n
end

-- Pure: may this player light bowl i? Returns true, or false and the reason to show.
function SpireBeacons.canLight(rec, i, guild, now)
	if i < 1 or i > SpireBeacons.SLOTS then
		return false, "That is not part of the Beacon."
	end
	if SpireBeacons.isLit(rec, i, now) then
		local mins = math.ceil((rec.slots[i].untilTime - now) / 60)
		return false, string.format("This fire burns for %d more minute%s. Light another bowl.", mins, mins == 1 and "" or "s")
	end
	if SpireBeacons.guildCount(rec, guild, now) >= SpireBeacons.GUILD_CAP then
		return false, string.format("Your guild already keeps %d of this Beacon's fires. Let other climbers light the rest.", SpireBeacons.GUILD_CAP)
	end
	return true
end

-- Lights bowl i of a floor's Beacon (no Ember check: the caller takes the Ember). Returns ok, reason-or-record.
function SpireBeacons.light(floor, i, name, guild, now)
	now = now or os.time()
	local rec = SpireBeacons.get(floor)
	local ok, why = SpireBeacons.canLight(rec, i, guild, now)
	if not ok then
		return false, why
	end
	rec.slots[i] = { untilTime = now + SpireBeacons.DURATION, by = name, guild = guild or 0 }
	SpireBeacons.put(floor, rec)
	return true, rec
end

-- Experience multiplier for kills on this floor
function SpireBeacons.xpFactor(floor, now)
	if not floor or floor < 1 then
		return 1
	end
	return 1 + SpireBeacons.XP_PER_SLOT * SpireBeacons.litCount(SpireBeacons.get(floor), now or os.time())
end

-- Size of the extra loot roll for kills on this floor (0 = none)
function SpireBeacons.lootBonus(floor, now)
	if not floor or floor < 1 then
		return 0
	end
	return SpireBeacons.LOOT_PER_SLOT * SpireBeacons.litCount(SpireBeacons.get(floor), now or os.time())
end

function SpireBeacons.apexFast(floor, now)
	return SpireBeacons.litCount(SpireBeacons.get(floor), now or os.time()) >= SpireBeacons.SLOTS
end

-- Seconds until the next bowl goes out (nil when none burn)
function SpireBeacons.nextOut(rec, now)
	local best
	for i = 1, SpireBeacons.SLOTS do
		if SpireBeacons.isLit(rec, i, now) then
			local left = rec.slots[i].untilTime - now
			if not best or left < best then
				best = left
			end
		end
	end
	return best
end

-- Pure: one line for the HUD and !beacon
function SpireBeacons.statusLine(floor, rec, now)
	local lit = SpireBeacons.litCount(rec, now)
	if lit == 0 then
		return string.format("Floor %d Beacon: dark. Bring a Beacon Ember to a fire bowl in town.", floor)
	end
	local names = {}
	for i = 1, SpireBeacons.SLOTS do
		if SpireBeacons.isLit(rec, i, now) then
			table.insert(names, rec.slots[i].by)
		end
	end
	return string.format("Floor %d Beacon: %d of %d fires lit (+%d%% experience and loot%s), lit by %s. Next fire goes out in %d min.",
		floor, lit, SpireBeacons.SLOTS, math.floor(lit * SpireBeacons.XP_PER_SLOT * 100 + 0.5),
		lit >= SpireBeacons.SLOTS and ", apex spawn refilling fast" or "", table.concat(names, ", "),
		math.ceil(SpireBeacons.nextOut(rec, now) / 60))
end

-- How many Embers does this monster drop? roll() returns 0..1. floorBosses = SpireFloorBosses (floors 2-10).
function SpireBeacons.embersFor(name, roll, floorBosses)
	local f1 = SpireBeacons.FLOOR1
	if name == f1.field then
		return SpireBeacons.FIELD_BOSS_EMBERS
	end
	if SpireTrophies and SpireTrophies.byBoss and SpireTrophies.byBoss(name) then
		return SpireBeacons.MINIBOSS_EMBERS
	end
	local isElite = false
	for _, e in ipairs(f1.elites) do
		if e == name then
			isElite = true
		end
	end
	for _, b in pairs(floorBosses or {}) do
		if b.field == name then
			return SpireBeacons.FIELD_BOSS_EMBERS
		end
		if b.elite == name then
			isElite = true
		end
	end
	if isElite then
		return roll() < SpireBeacons.ELITE_CHANCE and 1 or 0
	end
	for _, a in pairs(SpireBeacons.APEX) do
		if a == name then
			return roll() < SpireBeacons.APEX_CHANCE and 1 or 0
		end
	end
	return 0
end

-- Which floor and bowl does a map position belong to? (points beacon_<floor>_<slot>, written by tools/mapgen.py)
function SpireBeacons.slotAt(pos)
	for floor = 1, 10 do
		for i = 1, SpireBeacons.SLOTS do
			local p = WorldPoints["beacon_" .. floor .. "_" .. i]
			if p and p.x == pos.x and p.y == pos.y and p.z == pos.z then
				return floor, i
			end
		end
	end
end
