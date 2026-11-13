-- World floor state (DESIGN.md 3.2). One record per floor for the whole server, stored in Canary's
-- persistent key-value store (database table kv_store), so it survives restarts.

Floors = {
	LAUNCH_FLOORS = 10,
	names = {
		[1] = "Hearthgate Plains", [2] = "Highrest Highlands", [3] = "Rootwell Fogwood", [4] = "Lakehold",
		[5] = "Ringhold", [6] = "Emberreach", [7] = "Glasswater Marsh", [8] = "Frostspire",
		[9] = "The Hollow Bazaar", [10] = "The Cobalt Labyrinth",
	},
	titles = {
		[1] = "Gatebreaker", [2] = "Hornbreaker", [3] = "Rootbreaker", [4] = "Lakebreaker", [5] = "Ringbreaker",
		[6] = "Emberbreaker", [7] = "Marshbreaker", [8] = "Frostbreaker", [9] = "Ledgerbreaker", [10] = "Ruinbreaker",
	},
	MAX_CREDIT = 20,
}

local function store()
	return kv.scoped("spirebound-floors")
end

function Floors.get(n)
	return store():get("floor-" .. n) or {}
end

local function put(n, rec)
	store():set("floor-" .. n, rec)
end

-- Floor 1 is open from launch; floor N+1 opens when floor N's boss dies the first time.
function Floors.isOpen(n)
	if n == 1 then
		return true
	end
	return Floors.get(n - 1).bossDeadAt ~= nil
end

-- Pure: may a character stand on floor n? Nobody (except staff) may be on a floor the tower has not opened yet,
-- however they got there. n = 0 means "not on any floor" (always fine).
function Floors.mayStandOn(n, floorIsOpen, isStaff)
	if isStaff or not n or n <= 1 then
		return true
	end
	return floorIsOpen == true
end

function Floors.highestOpen()
	local n = 1
	while n < Floors.LAUNCH_FLOORS and Floors.isOpen(n + 1) do
		n = n + 1
	end
	return n
end

function Floors.isLabyrinthOpen(n)
	return Floors.get(n).fieldBossDeadAt ~= nil
end

-- Returns true only the first time (the pass opens forever).
function Floors.markFieldBoss(n, names)
	local rec = Floors.get(n)
	if rec.fieldBossDeadAt then
		return false
	end
	rec.fieldBossDeadAt = os.time()
	rec.fieldBossCredit = names or {}
	put(n, rec)
	SpireSave.now("floor " .. n .. " field boss") -- R8: never lose a first kill to a crash
	return true
end

-- Credit ranking (pure): contributions = { {name=..., amount=...}, ... } -> top 20 names by amount.
function Floors.rankCredit(contributions)
	local list = {}
	for _, c in ipairs(contributions) do
		table.insert(list, c)
	end
	table.sort(list, function(a, b)
		if a.amount == b.amount then
			return a.name < b.name
		end
		return a.amount > b.amount
	end)
	local names = {}
	for i = 1, math.min(#list, Floors.MAX_CREDIT) do
		names[i] = list[i].name
	end
	return names
end

-- Enrage timer in seconds (pure): 8 min x 8 / players (players counted up to 8), max 60 min (DESIGN.md 3.2).
function Floors.enrageSeconds(players)
	return math.min(60 * 60, math.floor(8 * 60 * 8 / math.min(math.max(players, 1), 8)))
end

-- Records the first clear. Returns true if this was the first kill (and the next floor just opened).
function Floors.recordClear(n, creditNames, lastHit, durationSeconds)
	local rec = Floors.get(n)
	if rec.bossDeadAt then
		return false
	end
	rec.bossDeadAt = os.time()
	rec.credit = creditNames
	rec.lastHit = lastHit
	rec.duration = durationSeconds
	put(n, rec)
	local nextRec = Floors.get(n + 1)
	nextRec.openedAt = rec.bossDeadAt
	put(n + 1, nextRec)
	SpireSave.now("floor " .. n .. " cleared")
	return true
end

function Floors.announceClear(n, creditNames)
	local who = table.concat(creditNames, ", ")
	Game.broadcastMessage(string.format("Floor %d has been cleared by %s! The way to Floor %d, %s, is open.",
		n, who ~= "" and who or "unknown heroes", n + 1, Floors.names[n + 1] or "the unknown"), MESSAGE_EVENT_ADVANCE)
end

-- GM/testing only
function Floors.reset(n)
	store():remove("floor-" .. n)
end
