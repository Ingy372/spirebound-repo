-- Fixes from Claude's party playtest, 2026-11-26 (docs/playtests/2026-11-26-HANDOFF-floor1-fixes.md).
local HERE = WorldPoints.temple_hearthgate

-- A stand-in player for gear hand-outs: a real backpack, a real "hand" and a real stand-in Store Inbox on the ground.
-- full = the backpack refuses everything (no free slot), like a real player's would.
local function gearPlayer(full)
	local p = { bp = Game.createItem(2854, 1, HERE), hand = Game.createItem(2854, 1, HERE), inbox = Game.createItem(2854, 1, HERE), msgs = {} }
	if full then -- really full: every slot taken
		for _ = 1, p.bp:getCapacity() do
			p.bp:addItem(3264, 1)
		end
	end
	function p:isPlayer() return true end
	function p:getStoreInbox() return self.inbox end
	function p:sendTextMessage(_, m) table.insert(self.msgs, m) end
	function p:getSlotItem(slot)
		if slot == CONST_SLOT_BACKPACK then return self.bp end
		if slot == CONST_SLOT_LEFT then return self.hand:getItem(0) end
	end
	function p:addItemEx(item, drop, slot, flags)
		SpireTest.eq(drop, false, "never allowed to drop on the floor")
		if slot == CONST_SLOT_LEFT then
			return self.hand:getSize() == 0 and self.hand:addItemEx(item) or RETURNVALUE_NOTENOUGHROOM
		end
		if full then return RETURNVALUE_NOTENOUGHROOM end
		return self.bp:addItemEx(item)
	end
	function p:clear()
		self.bp:remove(); self.hand:remove(); self.inbox:remove()
	end
	return p
end

SpireTest.add("party fixes P1-1: quest gear goes in the backpack, never the floor", function()
	local p = gearPlayer(false)
	local item, where = SpireGear.make(p, "f1_vanguard_sword")
	SpireTest.eq(item ~= nil and item:getName(), "Hearthguard Sword", "made")
	SpireTest.eq(where, "bag", "in the backpack")
	SpireTest.eq(p.bp:getSize(), 1, "one item in the backpack")
	p:clear()
end)

SpireTest.add("party fixes P1-1: a full backpack sends quest gear to the Store Inbox, and says so", function()
	local p = gearPlayer(true)
	local item, where = SpireGear.make(p, "f1_vanguard_sword")
	SpireTest.eq(item ~= nil, true, "still made")
	SpireTest.eq(where, "inbox", "went to the Store Inbox")
	SpireTest.eq(p.inbox:getSize(), 1, "it is in the inbox")
	SpireTest.eq((p.msgs[1] or ""):find("Store Inbox", 1, true) ~= nil, true, "the player is told: " .. tostring(p.msgs[1]))
	SpireTest.eq(SpireGear.defOf(p.inbox:getItem(0)).id, "f1_vanguard_sword", "it keeps its Spirebound identity")
	p:clear()
end)

SpireTest.add("party fixes P1-5: Dorrow's weapon goes straight into the hand, the old one to the backpack", function()
	local p = gearPlayer(false)
	p.hand:addItem(3270, 1) -- the starter club
	local item, where = SpireGear.equip(p, "f1_vanguard_sword")
	SpireTest.eq(where, "hand", "equipped")
	SpireTest.eq(p:getSlotItem(CONST_SLOT_LEFT):getName(), "Hearthguard Sword", "the new weapon is in hand")
	SpireTest.eq(p.bp:getSize(), 1, "the old weapon moved to the backpack")
	SpireTest.eq(p.bp:getItem(0):getId(), 3270, "and it is the club")
	SpireTest.eq(SpireGear.whereLine("hand"):find("in your hand", 1, true) ~= nil, true, "Dorrow says where it went")
	p:clear()
end)

SpireTest.add("party fixes P1-5: no room for the old weapon: the new one goes to the backpack or inbox instead", function()
	local p = gearPlayer(true)
	p.hand:addItem(3270, 1)
	local item, where = SpireGear.equip(p, "f1_vanguard_sword")
	SpireTest.eq(item ~= nil, true, "still given")
	SpireTest.eq(where, "inbox", "full backpack: Store Inbox")
	SpireTest.eq(p:getSlotItem(CONST_SLOT_LEFT):getId(), 3270, "the old weapon stays in hand")
	SpireTest.eq(SpireGear.whereLine("bag"):find("drag it into your weapon hand", 1, true) ~= nil, true, "bag line explains")
	p:clear()
end)

-- A stand-in party member: storage values, a position, an id
local function member(id, dx)
	local p = { id = id, pos = Position(HERE.x + dx, HERE.y, HERE.z), st = {}, msgs = {} }
	function p:getId() return self.id end
	function p:getPosition() return self.pos end
	function p:getStorageValue(k) return self.st[k] or -1 end
	function p:setStorageValue(k, v) self.st[k] = v end
	function p:sendTextMessage(_, m) table.insert(self.msgs, m) end
	function p:getParty() return self.party end
	return p
end

SpireTest.add("party fixes P1-3: a kill counts for every party member nearby, once each", function()
	local tank, healer, far = member(910001, 0), member(910002, 3), member(910003, 60)
	local party = { getMembers = function() return { healer, far } end, getLeader = function() return tank end }
	tank.party, healer.party, far.party = party, party, party
	local target = { getId = function() return 990001 end, getPosition = function() return HERE end }
	local q = SpireQuests.get("q1_iron1")
	for _, p in ipairs({ tank, healer, far }) do
		p:setStorageValue(q.storage, 1)
		p:setStorageValue(q.killStorage, 0)
	end
	-- onKill fires for the top damage dealer and for the last hitter: each member must count once
	for _, killer in ipairs({ tank, healer }) do
		for _, m in ipairs(SpireProgress.killCredit("quest-test", killer, target)) do
			SpireQuests.countKill(m, q.target)
		end
	end
	SpireTest.eq(tank:getStorageValue(q.killStorage), 1, "the tank counts it")
	SpireTest.eq(healer:getStorageValue(q.killStorage), 1, "the healer counts it too (once)")
	SpireTest.eq(far:getStorageValue(q.killStorage), 0, "a member 60 tiles away does not")
	local solo = member(910004, 1)
	SpireTest.eq(#SpireProgress.killCredit("quest-test", solo, { getId = function() return 990002 end, getPosition = function() return HERE end }), 1, "no party: the killer alone")
end)

SpireTest.add("party fixes P1-2: no shop passes the 'ignore capacity' tick on", function()
	local p = io.popen("ls data-spirebound/npc/*.lua 2>/dev/null")
	local bad, n = {}, 0
	for path in p:lines() do
		local f = io.open(path, "r")
		local text = f and f:read("*a") or ""
		if f then f:close() end
		if text:find("sellItem", 1, true) then
			n = n + 1
			if not text:find("0, false, inBackpacks", 1, true) or text:find("0, ignore, inBackpacks", 1, true) then
				table.insert(bad, path:match("[^/]+$"))
			end
		end
	end
	p:close()
	SpireTest.eq(n >= 60, true, "found the shops (" .. n .. ")")
	SpireTest.eq(table.concat(bad, ", "), "", "shops that still pass the tick on")
end)

SpireTest.add("party fixes P2-6/P2-7: inns buy meat, coins go to the bank", function()
	SpireTest.eq(configKeys.AUTOBANK ~= nil, true, "this engine knows autoBank")
	SpireTest.eq(configManager.getBoolean(configKeys.AUTOBANK), true, "looted coins go to the bank")
	local f = io.open("data-spirebound/npc/hearthgate_innkeeper.lua", "r")
	local text = f:read("*a")
	f:close()
	SpireTest.eq(text:find('itemName = "meat", clientId = 3577, buy = 5, sell = 2', 1, true) ~= nil, true, "Roan buys meat")
end)

-- A stand-in player for the autoloot default: real KV storage under a test name
local function kvPlayer(tag)
	local p = { feats = {} }
	function p:kv() return { scoped = function(_, name) return kv.scoped("spiretest-" .. tag .. "-" .. name) end } end
	function p:getFeature(f) return self.feats[f] end
	function p:setFeature(f, v) self.feats[f] = v end
	return p
end

SpireTest.add("party fixes P1-4: autoloot is on for a new character, once, and !autoloot off sticks", function()
	local tag = "autoloot" .. os.time()
	local p = kvPlayer(tag)
	SpireTest.eq(SpireQuests.autolootDefault(p), true, "first login switches it on")
	SpireTest.eq(p:getFeature(Features.AutoLoot), 1, "autoloot on")
	p:setFeature(Features.AutoLoot, 0) -- the player says !autoloot off
	SpireTest.eq(SpireQuests.autolootDefault(p), false, "a later login leaves it alone")
	SpireTest.eq(p:getFeature(Features.AutoLoot), 0, "still off")
	kv.scoped("spiretest-" .. tag .. "-spirebound"):remove("autoloot-default")
end)

SpireTest.add("party fixes P2-12: !spells before a path shows each path's first spells", function()
	local text = table.concat(SpireGuide.previewLines(), "\n")
	for _, voc in ipairs({ 1, 2, 3, 4 }) do
		SpireTest.eq(text:find(Vocation(voc):getName() .. ":", 1, true) ~= nil, true, "lists " .. Vocation(voc):getName())
	end
	SpireTest.eq(select(2, text:gsub("%(level %d+%)", "")) >= 4, true, "lists spells: " .. text)
end)
