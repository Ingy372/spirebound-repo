-- The First Climb, in the game (roadmap FD1; rules and text: lib/spirebound/first_climb.lua).
-- Story objects put down at start-up beside named points (as the builders' stones are), reading records, chapter steps,
-- the townsfolk's lines, the Discoveries "Records" rows and the look line for chapter 4's choice.

local FC = SpireFirstClimb
local STONE, BIN, GRAVE, DESK = 2199, 116, 134, 28481
local AID = { mark = 48101, tally = 48102, bin = 48105, grave = 48106, desk = 48107, watchlog = 48108,
	loose = 48111, record = 48150, wreath = 48151, order = 48202 }
local TALLY = { -- the quartermaster's three supply stones (chapter 2); the third names Millcross
	{ id = "west", near = "loop_starter_west_a", text = "A supply stone, carved with an arrow over three strokes: \"First camp. Forty-one climbers, forty-one packs. Water good. Rats in the grain already.\"" },
	{ id = "east", near = "loop_starter_east_a", text = "A supply stone, carved with an arrow over three strokes: \"Second camp. Rope, two hundred lengths. Lamp oil, eleven casks. Captain Vane says carry less, climb faster.\"" },
	{ id = "south", near = "loop_starter_south_a", text = "A supply stone, carved with an arrow over three strokes: \"Third camp. Bread to come from the mill at Millcross, every tenth day, paid in advance. The miller's girl keeps the book.\"" },
}
local LOOSE = { "song", "margin", "rations" }

local function kv(player)
	return player:kv():scoped("spirebound-fc")
end

local function chapter(id)
	return FC.get(id)
end

local function state(player, q)
	return SpireQuests.state(player, q)
end

local function step(player, q)
	return math.max(0, player:getStorageValue(q.killStorage))
end

local function onStep(player, id, n)
	local q = chapter(id)
	return q and state(player, q) == 1 and step(player, q) == n
end

-- ---------------------------------------------------------------- progress (read by the quest log)
function FC.progress(player, q)
	if q.kind == "oath" then
		return SpireOathroom and SpireOathroom.progress(player) or 0
	end
	local s = step(player, q)
	local sub = 0
	if q.id == "fc2" then
		sub = SpireQuests.collectedCount(player, "fc_tally")
	elseif q.id == "fc3" and s == 2 then
		sub = kv(player):get("fc3_kills") or 0
	elseif q.id == "fc5" then
		sub = SpireQuests.collectedCount(player, "fc_pages")
	end
	return FC.encode(s, sub)
end

-- the next step, or "report" after the last one
function FC.advance(player, id, from)
	local q = chapter(id)
	if not q or state(player, q) ~= 1 or step(player, q) ~= from then
		return false
	end
	local n = from + 1
	if n >= #q.steps then
		player:setStorageValue(q.storage, 2)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, q.name .. ": done! " .. q.report)
	else
		player:setStorageValue(q.killStorage, n)
		SpireQuests.refreshTracker(player, q)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, q.name .. ": " .. FC.stepLine(q, FC.encode(n, 0)))
	end
	player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
	return true
end

-- ---------------------------------------------------------------- records
local function giveItem(player, item)
	if player:addItemEx(item, false, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		return true
	end
	local inbox = player.getStoreInbox and player:getStoreInbox()
	if inbox and inbox:addItemEx(item, INDEX_WHEREEVER, FLAG_NOLIMIT) == RETURNVALUE_NOERROR then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Your backpack is full: it went to your store inbox.")
		return true
	end
	item:remove()
	return false
end

function FC.markRecord(player, id)
	local r = FC.record(id)
	if not r or kv(player):get("read_" .. id) then
		return false
	end
	kv(player):set("read_" .. id, os.time())
	if SpireDiscoveries and SpireDiscoveries.mark then
		pcall(SpireDiscoveries.mark, player, "record", id)
	end
	local n = 0
	for _, x in ipairs(FC.RECORDS) do
		if kv(player):get("read_" .. x.id) then
			n = n + 1
		end
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Record read: %s (%d of %d records; see the Discoveries page).", r.name, n, #FC.RECORDS))
	return true
end

function FC.readRecord(player, id, itemId)
	local r = FC.record(id)
	if not r then
		return false
	end
	player:showTextDialog(itemId or r.item, r.text)
	FC.markRecord(player, id)
	return true
end

-- the record as an item to keep (once per character), and read on the spot
function FC.giveRecord(player, id)
	local r = FC.record(id)
	if not r then
		return false
	end
	if not kv(player):get("has_" .. id) then
		local item = Game.createItem(r.item, 1)
		if item then
			item:setAttribute(ITEM_ATTRIBUTE_NAME, r.name)
			item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A record of the First Climb. Use it to read it.")
			item:setActionId(AID.record)
			item:setCustomAttribute("sb_record", id)
			if giveItem(player, item) then
				kv(player):set("has_" .. id, os.time())
			end
		end
	end
	FC.readRecord(player, id)
	return true
end

-- ---------------------------------------------------------------- the chapters' own moments
function FC.onStart(player, q)
	if q.id == "fc3" then
		kv(player):set("fc3_kills", 0)
	elseif q.id == "fc4" then
		local w = Game.createItem(FC.ITEMS.wreath, 1)
		if w then
			w:setAttribute(ITEM_ATTRIBUTE_NAME, "Agna's wheat wreath")
			w:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A wreath of Millcross wheat for Brother Tam's grave. Use it on the grave to lay it there.")
			w:setActionId(AID.wreath)
			giveItem(player, w)
		end
	end
end

function FC.onReport(player, q)
	if q.id == "fc4" then
		local pick = kv(player):get("fc4_choice") or "wreath"
		local c = FC.CHOICES[pick]
		if pick == "pendant" then
			player:removeItem(FC.ITEMS.pendant, 1)
		end
		player:kv():scoped("spirebound-titles"):set(c.title, os.time())
		if SpireKeepsakes and SpireKeepsakes.give then
			SpireKeepsakes.give(player, c.keepsake)
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "New title: " .. c.title .. ".")
		return c.thanks
	elseif q.id == "fc8" then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The First Climb's names are back on the Monument for you to read. Archivist Maren grants your Floor 1 perk: say 'perk' to her.")
		if SpireFinds and SpireFinds.announce then
			pcall(Game.broadcastMessage, player:getName() .. " followed the First Climb to the end of Floor 1: Heir to the First Climb.", MESSAGE_STATUS)
		end
	elseif q.kind == "oath" and SpireOathroom and SpireOathroom.onReport then
		return SpireOathroom.onReport(player, q)
	end
end

-- kills: chapter 3's thornsnaps and chapter 5's pages (the whole party nearby is credited, as for quest kills)
local spawned = {} -- monster id -> owner guid
function FC.onKill(member, target)
	local tid = target:getId()
	if spawned[tid] and spawned[tid] == member:getGuid() and onStep(member, "fc3", 2) then
		local n = (kv(member):get("fc3_kills") or 0) + 1
		kv(member):set("fc3_kills", n)
		if n >= 3 then
			FC.advance(member, "fc3", 2)
		else
			SpireQuests.refreshTracker(member, chapter("fc3"))
			member:sendTextMessage(MESSAGE_STATUS, string.format("Bread for the Climb: %d of 3 thornsnaps.", n))
		end
	end
	if target:getName() == "Bandit Captain" and onStep(member, "fc5", 0) then
		local have = SpireQuests.collected(member, "fc_pages")
		local page = not have.page1 and "page1" or (not have.page2 and "page2") or nil
		if page then
			SpireQuests.find(member, "fc_pages", page)
			FC.giveRecord(member, page)
			if SpireQuests.collectedCount(member, "fc_pages") >= 2 then
				FC.advance(member, "fc5", 0)
			else
				SpireQuests.refreshTracker(member, chapter("fc5"))
				member:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The Pay Chest: 1 of 2 pages. Another Bandit Captain carries the next one.")
			end
		end
	end
end

-- the Axe-Lord (chapter 8): every credited fighter on the chapter gets the last page, first kill or any repeat
function FC.onBossKill(bossName, credit)
	if bossName ~= "Axe-Lord of the Stair" then
		return
	end
	for _, name in ipairs(credit or {}) do
		local p = Player(name)
		if p and onStep(p, "fc8", 0) then
			FC.giveRecord(p, "lastpage")
			FC.advance(p, "fc8", 0)
		end
	end
end

-- the Monument (scripts/spirebound/monument.lua calls this when it is read)
function FC.isHeir(player)
	local q = chapter("fc8")
	return q and state(player, q) == 3
end

function FC.onMonument(player)
	if onStep(player, "fc1", 0) then
		addEvent(function(pid)
			local p = Player(pid)
			if p then
				FC.advance(p, "fc1", 0)
			end
		end, 500, player:getId())
	end
	return FC.monumentHeader(FC.isHeir(player), player:getName())
end

-- ---------------------------------------------------------------- talk (called from SpireQuests.talk for givers)
function FC.talk(npc, handler, player, msg, giver)
	local lower = (msg or ""):lower()
	if not (MsgContains(lower, "climb") or MsgContains(lower, "first climb")) then
		return false
	end
	if giver == "Miller Agna" and onStep(player, "fc3", 0) then
		handler:say("Grandmother's book? She kept it in the old flour store on the mill road, in Thornsnap Hollow north-west of Hearthgate, before the thorns took the place. If it's anywhere, it's still in the flour bin there. Mind the thornsnaps: they love old flour.", npc, player)
		FC.advance(player, "fc3", 0)
		return true
	end
	local line = FC.LORE[giver]
	if line then
		handler:say(line, npc, player)
		return true
	end
	return false
end

-- the townsfolk who answer "rumour" (lib/spirebound/rumours.lua) also answer "climb" with their own line
if SpireRumours and SpireRumours.talk and not FC.rumoursWrapped then
	FC.rumoursWrapped = true
	local orig = SpireRumours.talk
	SpireRumours.talk = function(npc, handler, player, msg, npcName)
		local lower = (msg or ""):lower()
		local line = FC.LORE[npcName or npc:getName()]
		if line and (MsgContains(lower, "climb") or MsgContains(lower, "first climb")) then
			handler:say(line, npc, player)
			return true
		end
		return orig(npc, handler, player, msg, npcName)
	end
end

-- ---------------------------------------------------------------- the look line and the Discoveries rows
SpireFinds = SpireFinds or {}
SpireFinds.LOOK_EXTRAS = SpireFinds.LOOK_EXTRAS or {}
table.insert(SpireFinds.LOOK_EXTRAS, function(target)
	local pick = target:kv():scoped("spirebound-fc"):get("fc4_choice")
	local q = chapter("fc4")
	if pick and q and state(target, q) == 3 and FC.CHOICES[pick] then
		return "Brother Tam: " .. FC.CHOICES[pick].look .. "."
	end
end)

if SpireDiscoveries and SpireDiscoveries.ORDER then
	local present = false
	for _, c in ipairs(SpireDiscoveries.ORDER) do
		present = present or c == "record"
	end
	if not present then
		table.insert(SpireDiscoveries.ORDER, "record")
	end
	SpireDiscoveries.LABEL.record = "Records"
	SpireDiscoveries.sources = SpireDiscoveries.sources or {}
	SpireDiscoveries.sources.record = function(player, id)
		return player:kv():scoped("spirebound-fc"):get("read_" .. id)
	end
	for _, r in ipairs(FC.RECORDS) do
		SpireDiscoveries.register("record", r.id, (r.name:gsub("^%l", string.upper)), 1)
	end
end

if SpireKeepsakes and SpireKeepsakes.add then
	SpireKeepsakes.add({ id = "fc_archive_seal", name = "Seal of the Archive", item = 2834,
		text = "A wax-sealed thank-you from Archivist Maren, for bringing Brother Tam's pendant home." })
	SpireKeepsakes.add({ id = "fc_reed_flower", name = "Pressed Marsh Flower", item = 2981,
		text = "A flower from Brother Tam's grave in Reedmarsh, pressed flat." })
end

-- ---------------------------------------------------------------- objects in the world
FC.placed = FC.placed or {}

local function put(id, pos, aid, desc)
	local item = Game.createItem(id, 1, pos)
	if item then
		item:setActionId(aid)
		if desc then
			item:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, desc)
		end
	end
	return item
end

-- a free tile at the edge of a corridor (a wall on its west side), for the field desk in the 4-wide way to the labyrinth
local function edgeSpot(x1, x2, y1, y2, z)
	for y = y1, y2 do
		for x = x1, x2 do
			local t, w = Tile(Position(x, y, z)), Tile(Position(x - 1, y, z))
			if t and t:getGround() and t:isWalkable(false, false, false, false, true) and #(t:getItems() or {}) == 0
				and not t:getTopCreature() and (not w or not w:getGround() or not w:isWalkable(false, false, false, false, true)) then
				return Position(x, y, z)
			end
		end
	end
end

function FC.place()
	local P, placed = WorldPoints, {}
	local find = SpireQuestObjects.findSpot
	local function at(key, centre, r, inTown)
		local spot = centre and find(centre, r, 1, inTown)
		if not spot then
			logger.warn("[first climb] no room for {}", key)
		end
		placed[key] = spot
		return spot
	end
	local dorrow = SpireQuests.giverPos("Captain Dorrow")
	local s = at("mark", dorrow, 8, true)
	if s then put(STONE, s, AID.mark, "One of Hearthgate's oldest wall stones, carved with an arrow over three strokes. Use it to look closer.") end
	for i, t in ipairs(TALLY) do
		s = at("tally_" .. t.id, P[t.near], 12)
		if s then put(STONE, s, AID.tally + i - 1, "An old supply stone, carved with an arrow over three strokes. Use it to read it.") end
	end
	s = at("bin", P.loop_thornsnap_hollow_a, 12)
	if s then put(BIN, s, AID.bin, "An old flour bin, split by thorn roots: all that is left of the mill road's flour store.") end
	s = at("grave", P.loop_reed_marsh_a, 12)
	if s then put(GRAVE, s, AID.grave, "A small grave among the reeds. Someone has left fresh reeds on it.") end
	local gate = P.gate_pass_1
	s = gate and edgeSpot(gate.x - 4, gate.x + 4, gate.y - 26, gate.y - 18, gate.z)
	placed.desk = s
	if s then put(DESK, s, AID.desk, "A soldier's field desk, old but sound. Its drawer is locked.") else logger.warn("[first climb] no room for the field desk") end
	local wt = P.apex_watchtower
	s = wt and at("watchlog", Position(wt.x, wt.y - 18, wt.z), 8)
	if s then put(DESK, s, AID.watchlog, "The captain's table of the old watch. A thick log book lies open on it.") end
	for i, id in ipairs(LOOSE) do
		local r = FC.record(id)
		s = at("loose_" .. id, P[r.loose], 10, true)
		if s then put(DESK, s, AID.loose + i - 1, "An old writing desk. Some papers are still in it.") end
	end
	FC.placed = placed
	for k, pos in pairs(placed) do -- (the autopilot routes read these from the server log)
		logger.info("[first climb] {} at {}, {}, {}", k, pos.x, pos.y, pos.z)
	end
end

local startup = GlobalEvent("SpireFirstClimbStartup")
function startup.onStartup()
	FC.place()
	return true
end
startup:register()

-- ---------------------------------------------------------------- using them
local function show(player, item, text)
	player:showTextDialog(item:getId(), text)
end

local mark = Action()
function mark.onUse(player, item)
	if onStep(player, "fc1", 1) then
		show(player, item, "Under the moss on Hearthgate's oldest wall: an arrow over three strokes, cut deep. The First Climb's supply mark. They built this wall.")
		FC.advance(player, "fc1", 1)
	elseif onStep(player, "fc1", 0) then
		show(player, item, "An arrow over three strokes, cut deep into the old stone. You don't know what it means yet: read the Monument's scraped rows first.")
	else
		show(player, item, "An arrow over three strokes, cut deep into the old stone: the First Climb's supply mark.")
	end
	return true
end
mark:aid(AID.mark)
mark:register()

local tally = Action()
function tally.onUse(player, item)
	local t = TALLY[item:getActionId() - AID.tally + 1]
	if not t then
		return false
	end
	show(player, item, t.text)
	local q = chapter("fc2")
	if state(player, q) == 1 and SpireQuests.find(player, "fc_tally", t.id) then
		local n = SpireQuests.collectedCount(player, "fc_tally")
		if n >= 3 then
			FC.giveRecord(player, "tally")
			FC.advance(player, "fc2", 0)
		else
			SpireQuests.refreshTracker(player, q)
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The Quartermaster's Trail: %d of 3 supply stones.", n))
		end
	end
	return true
end
for i = 0, #TALLY - 1 do
	tally:aid(AID.tally + i)
end
tally:register()

local function alive(owner)
	for mid, g in pairs(spawned) do
		if not Monster(mid) then
			spawned[mid] = nil
		elseif g == owner then
			return true
		end
	end
	return false
end

local bin = Action()
function bin.onUse(player, item)
	local pos = item:getPosition()
	if onStep(player, "fc3", 1) or (onStep(player, "fc3", 2) and not alive(player:getGuid())) then
		local want = 3 - (kv(player):get("fc3_kills") or 0)
		for i = 1, want do
			local m = Game.createMonster("Thornsnap", Position(pos.x + (i - 2), pos.y + 1, pos.z), true, true)
			if m then
				spawned[m:getId()] = player:getGuid()
			end
		end
		pos:sendMagicEffect(CONST_ME_POFF)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Thorn roots burst out of the flour bin, and thornsnaps with them!")
		if onStep(player, "fc3", 1) then
			FC.advance(player, "fc3", 1)
		end
	elseif onStep(player, "fc3", 2) then
		player:sendTextMessage(MESSAGE_STATUS, "Deal with the thornsnaps first.")
	elseif onStep(player, "fc3", 3) then
		FC.giveRecord(player, "ledger")
		FC.advance(player, "fc3", 3)
	else
		player:sendTextMessage(MESSAGE_INFO_DESCR, "An old flour bin, split by thorn roots. Nothing in it now but mouse droppings.")
	end
	return true
end
bin:aid(AID.bin)
bin:register()

local grave = Action()
function grave.onUse(player, item)
	if onStep(player, "fc4", 0) then
		show(player, item, "A small stone among the reeds: TAM. HE CAME BACK. A pendant hangs on the stone, and a scrap of prayer is tucked beneath it.")
		FC.giveRecord(player, "prayer")
		FC.advance(player, "fc4", 0)
	elseif onStep(player, "fc4", 1) then
		local p = Game.createItem(FC.ITEMS.pendant, 1)
		if p then
			p:setAttribute(ITEM_ATTRIBUTE_NAME, "Brother Tam's pendant")
			p:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A healer's pendant, worn smooth. Archivist Maren wants it for the archive.")
			giveItem(player, p)
		end
		kv(player):set("fc4_choice", "pendant")
		player:removeItem(FC.ITEMS.wreath, 1)
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You take Brother Tam's pendant for the archive.")
		FC.advance(player, "fc4", 1)
	else
		show(player, item, "A small stone among the reeds: TAM. HE CAME BACK.")
	end
	return true
end
grave:aid(AID.grave)
grave:register()

local wreath = Action()
function wreath.onUse(player, item, fromPosition, target, toPosition)
	if not target or not target.getActionId or target:getActionId() ~= AID.grave then
		player:sendTextMessage(MESSAGE_STATUS, "Use the wreath on Brother Tam's grave in Reedmarsh.")
		return true
	end
	if not onStep(player, "fc4", 1) then
		player:sendTextMessage(MESSAGE_STATUS, "Read the grave first.")
		return true
	end
	item:remove(1)
	kv(player):set("fc4_choice", "wreath")
	toPosition:sendMagicEffect(CONST_ME_MAGIC_GREEN)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You lay Agna's wreath on the grave and leave the pendant where it hangs.")
	FC.advance(player, "fc4", 1)
	return true
end
wreath:aid(AID.wreath)
wreath:register()

local order = Action()
function order.onUse(player, item)
	if onStep(player, "fc6", 0) then
		FC.giveRecord(player, "order")
		FC.advance(player, "fc6", 0)
	else
		FC.readRecord(player, "order", item:getId())
	end
	return true
end
order:aid(AID.order)
order:register()

local watchlog = Action()
function watchlog.onUse(player, item)
	if onStep(player, "fc6", 1) then
		FC.giveRecord(player, "watchlog")
		FC.advance(player, "fc6", 1)
	else
		FC.readRecord(player, "watchlog", 2821)
	end
	return true
end
watchlog:aid(AID.watchlog)
watchlog:register()

local desk = Action()
function desk.onUse(player, item)
	if not SpireStairKey.has(player) then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The drawer is locked. Its keyhole is the shape of the Stair Key (see the Stair Key quest in your log).")
		return true
	end
	if onStep(player, "fc7", 0) then
		FC.giveRecord(player, "letter")
		FC.advance(player, "fc7", 0)
	else
		FC.readRecord(player, "letter", 2818)
	end
	return true
end
desk:aid(AID.desk)
desk:register()

local loose = Action()
function loose.onUse(player, item)
	local id = LOOSE[item:getActionId() - AID.loose + 1]
	if not id then
		return false
	end
	FC.giveRecord(player, id)
	return true
end
for i = 0, #LOOSE - 1 do
	loose:aid(AID.loose + i)
end
loose:register()

local record = Action()
function record.onUse(player, item)
	local id = item:getCustomAttribute("sb_record")
	if not id then
		return false
	end
	FC.readRecord(player, id, item:getId())
	return true
end
record:aid(AID.record)
record:register()

