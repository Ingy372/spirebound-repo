-- Cosmetics you keep (adventure layer 4.1): auras and house keepsakes. No new art: an aura is a small magic effect that
-- plays on the character every few seconds, seen by everyone; a keepsake is a placeholder item renamed (each has a
-- Grok icon request in ART_REQUESTS.md).
--   SpireAuras.give(player, id)       (the seam) the character owns it from now on; the first one is switched on
--   !aura <name|off>                  (scripts/spirebound/finds.lua) choose which one shows
--   SpireKeepsakes.give(player, id)   a house keepsake into the backpack, once per character
SpireAuras = SpireAuras or {}

-- effects: played in turn, one every `every` seconds. Effect constants that this engine lacks fall back to a number.
SpireAuras.LIST = {
	{ id = "fireflies", name = "Fireflies", every = 3, effects = { CONST_ME_YELLOWENERGY or 49 } },
	{ id = "dyers_drift", name = "Dyer's Drift", every = 4, effects = { CONST_ME_PURPLEENERGY or 48, CONST_ME_GREENSMOKE or 46, CONST_ME_YELLOWENERGY or 49, CONST_ME_ENERGYHIT or 12 } },
	{ id = "trailblazers_wake", name = "Trailblazer's Wake", every = 3, effects = { CONST_ME_HITBYFIRE or 16 } },
	{ id = "cartographers_compass", name = "Cartographer's Compass", every = 4, effects = { CONST_ME_YELLOW_RINGS or 33 } },
}

function SpireAuras.get(id)
	for _, a in ipairs(SpireAuras.LIST) do
		if a.id == id then
			return a
		end
	end
end

-- Pure: find an aura by what a player typed ("fireflies", "Dyer's Drift", "dyers drift", "trail")
function SpireAuras.match(text)
	local want = (text or ""):lower():gsub("[^%a]", "")
	if want == "" then
		return nil
	end
	for _, a in ipairs(SpireAuras.LIST) do
		local name = a.name:lower():gsub("[^%a]", "")
		local id = a.id:gsub("[^%a]", "")
		if name == want or id == want or name:sub(1, #want) == want then
			return a
		end
	end
end

local function store(player)
	return player:kv():scoped("spirebound-auras")
end

function SpireAuras.owned(player)
	local out = {}
	for _, a in ipairs(SpireAuras.LIST) do
		if store(player):get(a.id) then
			table.insert(out, a)
		end
	end
	return out
end

function SpireAuras.has(player, id)
	return store(player):get(id) ~= nil
end

SpireAuras.cache = SpireAuras.cache or {} -- player id -> aura row or false (read every second by the aura loop)
SpireCleanup.add(function(pid) SpireAuras.cache[pid] = nil end)

function SpireAuras.active(player)
	local pid = player:getId()
	local c = SpireAuras.cache[pid]
	if c == nil then
		local id = player:kv():scoped("spirebound"):get("aura_on")
		c = id and id ~= "" and SpireAuras.has(player, id) and SpireAuras.get(id) or false
		SpireAuras.cache[pid] = c
	end
	return c or nil
end

function SpireAuras.setActive(player, id)
	player:kv():scoped("spirebound"):set("aura_on", id or "")
	SpireAuras.cache[player:getId()] = nil
end

-- The seam. Returns true when it is new to this character.
function SpireAuras.give(player, id)
	local a = SpireAuras.get(id)
	if not a or SpireAuras.has(player, id) then
		return false
	end
	store(player):set(id, os.time())
	if not SpireAuras.active(player) then
		SpireAuras.setActive(player, id)
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Aura: %s! Everyone can see it on you. Say !aura to switch auras or turn yours off.", a.name))
	player:getPosition():sendMagicEffect(a.effects[1])
	return true
end

function SpireAuras.take(player, id) -- tests
	store(player):remove(id)
	if player:kv():scoped("spirebound"):get("aura_on") == id then
		SpireAuras.setActive(player, nil)
	end
end

-- ---------------------------------------------------------------- house keepsakes
SpireKeepsakes = SpireKeepsakes or {}
-- item = the placeholder picture until Grok's icon arrives (ART_REQUESTS.md, adventure layer)
SpireKeepsakes.LIST = {
	{ id = "inn_tankard", name = "Inn Tankard", item = 2880, text = "A keepsake of the Inn Smith's back room. Its owner is a regular." },
	{ id = "brass_spyglass", name = "Brass Spyglass", item = 23512, text = "A keepsake from the Gate Balcony. On a clear day you can see the Pass." },
	{ id = "plains_map", name = "Plains Map", item = 2823, text = "A keepsake: half of Floor 1, drawn by its owner's own hand." },
}

function SpireKeepsakes.get(id)
	for _, k in ipairs(SpireKeepsakes.LIST) do
		if k.id == id then
			return k
		end
	end
end

-- other scripts (Session B's treasure keepsakes and roamers) add their own rows
function SpireKeepsakes.add(row)
	if not SpireKeepsakes.get(row.id) then
		table.insert(SpireKeepsakes.LIST, row)
	end
end

local function kstore(player)
	return player:kv():scoped("spirebound-keepsakes")
end

function SpireKeepsakes.has(player, id)
	return kstore(player):get(id) ~= nil
end

function SpireKeepsakes.owned(player)
	local out = {}
	for _, k in ipairs(SpireKeepsakes.LIST) do
		if SpireKeepsakes.has(player, k.id) then
			table.insert(out, k)
		end
	end
	return out
end

-- Make the item itself (into a player or a container); nil if it would not fit
function SpireKeepsakes.makeItem(k)
	local item = Game.createItem(k.item, 1)
	if not item then
		return nil
	end
	item:setAttribute(ITEM_ATTRIBUTE_NAME, k.name)
	item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, k.text .. " (A keepsake for your house.)")
	item:setCustomAttribute("sb_keepsake", k.id)
	return item
end

-- Once per character (repeat = true hands another one over anyway, for keepsakes that drop more than once)
function SpireKeepsakes.give(player, id, repeatable)
	local k = SpireKeepsakes.get(id)
	if not k or (SpireKeepsakes.has(player, id) and not repeatable) then
		return false
	end
	local item = SpireKeepsakes.makeItem(k)
	if not item then
		return false
	end
	if player:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) ~= RETURNVALUE_NOERROR then
		local inbox = player.getStoreInbox and player:getStoreInbox()
		if not (inbox and inbox:addItemEx(item, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR) then
			item:remove()
			return false
		end
	end
	kstore(player):set(id, os.time())
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Keepsake: %s! Set it out in your house for visitors to see.", k.name))
	return true
end

function SpireKeepsakes.forget(player, id) -- tests
	kstore(player):remove(id)
end
