-- The Calling: how style choices are made (style trees v2, spec 7.1, 8.1, 9.2; Jay approved 2026-11-28).
--   * Only the next choice is ever shown. The first (the path) comes when a character first reaches Floor 2; the second
--     (the final style) at Mastery 20, around level 85.
--   * At each, a sealed letter from the class trainer appears in the backpack (Vanguard: Captain Dorrow; Ranger:
--     Hunter Brannoch; Arcanist: Vesper; Mystic: Fisher Corwin).
--   * The trainer runs the Path Trial (a required quest): about 5 minutes alone in a sealed pit with one option's full
--     power and signature ability, training waves to try it on, no exits and no Waycrystals. Logging out ends it.
--     The choice window opens only once both options have been tried.
--   * The choice window: two cards (name, role, what you gain, what you give up), then a confirm. It is permanent
--     (the class Mastery respec is sold only in the shop, Jay's rule).
-- The trial reuses the Proving's three sealed pits (scripts/spirebound/proving.lua); the two never share a pit.
SpireCalling = SpireCalling or { trials = {} } -- trials: player id -> { key, pit, t, back, wave }
SpireCalling.TRAINERS = { [4] = "Captain Dorrow", [3] = "Hunter Brannoch", [1] = "Vesper", [2] = "Fisher Corwin" }
SpireCalling.TRIAL_SECONDS = 300
SpireCalling.WAVE_EVERY = 45
SpireCalling.WINDOW, SpireCalling.CONFIRM = 7401, 7402
SpireCalling.LETTER = 3505 -- a letter

local function kv(player)
	return player:kv():scoped("spirebound")
end

local function point(name)
	local p = WorldPoints[name]
	return p and Position(p.x, p.y, p.z)
end

function SpireCalling.trainerOf(player)
	return SpireCalling.TRAINERS[player:getVocation():getBaseId()]
end

function SpireCalling.inTrial(player)
	return SpireCalling.trials[player:getId()] ~= nil
end

-- ---------------------------------------------------------------- the summons
-- Pure: the letter's text
function SpireCalling.letterText(trainer, playerName, final)
	if final then
		return string.format("%s,\n\nyour path has served you well. It is time to choose how you will finish it. Come to me: I will put you through the Path Trial for each of the two styles, and then you choose.\n\n%s", playerName, trainer)
	end
	return string.format("%s,\n\nyou have reached the second floor. It is time to choose your path. Come to me in Hearthgate: I will put you through the Path Trial for each of the two paths, about five minutes each, and then you choose.\n\n%s", playerName, trainer)
end

-- The letter in the backpack and a line in the Server Log. final = the second choice. Once per choice.
function SpireCalling.summon(player, final)
	local trainer = SpireCalling.trainerOf(player)
	if not trainer then
		return false
	end
	local flag = final and "calling_letter_2" or "calling_letter_1"
	if kv(player):get(flag) then
		return false
	end
	kv(player):set(flag, os.time())
	local letter = Game.createItem(SpireCalling.LETTER, 1)
	if letter then
		letter:setAttribute(ITEM_ATTRIBUTE_TEXT, SpireCalling.letterText(trainer, player:getName(), final))
		letter:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A sealed letter from " .. trainer .. ".")
		if player:addItemEx(letter, false, INDEX_WHEREEVER, FLAG_NOLIMIT) ~= RETURNVALUE_NOERROR then
			letter:remove()
		end
	end
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("A sealed letter appears in your backpack: %s has summoned you for special training. Visit them and say {calling}.", trainer))
	return true
end

-- Every 5 seconds: anyone who has just reached Floor 2 for the first time is summoned for the path
local arrival = GlobalEvent("SpireCallingArrival")
function arrival.onThink(interval)
	for _, p in ipairs(Game.getPlayers()) do
		if p:getVocation():getBaseId() > 0 and Floors.at(p:getPosition()) >= 2 and SpireStyle.markArrived(p) then
			if not kv(p):get("style_path") then
				SpireCalling.summon(p, false)
			end
		end
	end
	return true
end
arrival:interval(5000)
arrival:register()

-- ---------------------------------------------------------------- the trial
-- The power a trial lends: the style view seen by every combat rule while the trial runs
local realGet = SpireStyle.get
function SpireStyle.get(player)
	local v = realGet(player)
	local t = SpireCalling.trials[player:getId()]
	if not t then
		return v
	end
	local P = SpireGearData.STYLE_POINTS
	if t.final then
		return SpireStyle.view(v.voc, P[30], v.path, t.key, nil, { arrived = true })
	end
	return SpireStyle.view(v.voc, P[20], t.key, nil, nil, { arrived = true })
end

-- Pure: which option keys a view's next choice offers
function SpireCalling.optionsOf(v)
	local out = {}
	for _, o in ipairs(v.options or {}) do
		table.insert(out, o)
	end
	return out
end

local WAVES = { -- what the training waves are made of (the pit's monsters are only there to try the power on)
	{ "Ruin Sentinel", 2 }, { "Stonehorn Ram", 2 }, { "Road Bandit", 3 }, { "Ruin Archer", 2 }, { "Bandit Captain", 1 }, { "Meadow Wolf", 4 },
}

local function wave(i, n)
	local w = WAVES[(n - 1) % #WAVES + 1]
	local at = point("proving_pit_" .. i .. "_boss")
	for _ = 1, w[2] do
		local m = at and Game.createMonster(w[1], at, true, false)
		if m then
			local t = SpireCalling.trialsByPit and SpireCalling.trialsByPit[i]
			if t then
				table.insert(t.monsters, m:getId())
			end
		end
	end
end

local function finish(pid, done)
	local t = SpireCalling.trials[pid]
	if not t then
		return
	end
	SpireCalling.trials[pid] = nil
	SpireCalling.trialsByPit[t.pit] = nil
	SpireProving.pits[t.pit] = nil
	for _, id in ipairs(t.monsters) do
		local m = Creature(id)
		if m then
			m:remove()
		end
	end
	local p = Player(pid)
	if p then
		p:unregisterEvent("SpireCallingGuard")
		if done then
			SpireStyle.markTrial(p, t.key)
		end
		if SpireStyle.applySpeed then
			SpireStyle.applySpeed(p)
		end
		if SpireStyle.applyBody then
			SpireStyle.applyBody(p)
		end
		p:addHealth(p:getMaxHealth())
		p:addMana(p:getMaxMana())
		if t.back then
			p:teleportTo(t.back)
			t.back:sendMagicEffect(CONST_ME_TELEPORT)
		end
		local name = SpireStyle.name(p:getVocation():getBaseId(), t.key)
		p:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("The %s trial is over. Say {calling} to %s for the next step.", name, SpireCalling.trainerOf(p) or "your trainer"))
	end
end
SpireCalling.finish = finish
SpireCalling.trialsByPit = SpireCalling.trialsByPit or {}

-- Start the trial of option `key`. Returns ok, message.
function SpireCalling.startTrial(player, key)
	local v = realGet(player)
	if not v.choiceReady then
		return false, "Your trial comes when your next choice does: I will send for you."
	end
	local option
	for _, o in ipairs(v.options or {}) do
		if o.key == key then
			option = o
		end
	end
	if not option then
		return false, "That is not one of your choices."
	end
	if SpireCalling.trials[player:getId()] then
		return false, "You are in a trial already."
	end
	local i = SpireProving.freePit(SpireProving.pits, SpireProving.PITS)
	if not i then
		return false, "The trial yards are all in use. Come back in a few minutes."
	end
	local t = { key = key, final = v.path ~= nil, pit = i, t = os.time(), back = player:getPosition(), waves = 0, monsters = {} }
	SpireProving.pits[i] = { pid = player:getId(), trial = key, t = os.time() } -- the Proving's own tick leaves it alone
	SpireCalling.trials[player:getId()] = t
	SpireCalling.trialsByPit[i] = t
	player:registerEvent("SpireCallingGuard")
	if SpireProving.light then
		SpireProving.light(player)
	end
	if SpireStyle.applySpeed then
		SpireStyle.applySpeed(player)
	end
	if SpireStyle.applyBody then
		SpireStyle.applyBody(player)
	end
	player:addHealth(player:getMaxHealth())
	player:addMana(player:getMaxMana())
	local to = point("proving_pit_" .. i .. "_player")
	player:teleportTo(to)
	to:sendMagicEffect(CONST_ME_TELEPORT)
	return true, string.format("The %s trial: for five minutes you hold its full power and its signature ability (%s). The yard is sealed: logging out ends the trial.",
		option.name, option.gain)
end

-- Every 2 seconds: waves, the time limit, and trials whose climber logged out
local tick = GlobalEvent("SpireCallingTick")
function tick.onThink(interval)
	local now = os.time()
	for pid, t in pairs(SpireCalling.trials) do
		local p = Player(pid)
		if not p then
			finish(pid, false)
		elseif now - t.t >= SpireCalling.TRIAL_SECONDS then
			finish(pid, true)
		elseif now - t.t >= t.waves * SpireCalling.WAVE_EVERY then
			t.waves = t.waves + 1
			wave(t.pit, t.waves)
		end
	end
	return true
end
tick:interval(2000)
tick:register()

-- Nobody dies in a trial: at the last point of health it ends (and counts as tried)
local guard = CreatureEvent("SpireCallingGuard")
function guard.onHealthChange(creature, attacker, primaryDamage, primaryType, secondaryDamage, secondaryType, origin)
	local player = creature:getPlayer()
	if not player or primaryType == COMBAT_HEALING or not SpireCalling.trials[player:getId()] then
		return primaryDamage, primaryType, secondaryDamage, secondaryType
	end
	if math.abs(primaryDamage) + math.abs(secondaryDamage) >= player:getHealth() then
		local pid = player:getId()
		addEvent(function()
			finish(pid, true)
		end, 0)
		return 0, primaryType, 0, secondaryType
	end
	return primaryDamage, primaryType, secondaryDamage, secondaryType
end
guard:register()

-- A climber who logged out inside a trial pit starts the next session at their trainer's town
local login = CreatureEvent("SpireCallingLogin")
function login.onLogin(player)
	if SpireProving.pitAt(player:getPosition()) and not SpireCalling.trials[player:getId()] and SpireProving.done(player) then
		local temple = player:getTown() and player:getTown():getTemplePosition()
		if temple then
			player:teleportTo(temple)
		end
	end
	player:registerEvent("SpireCallingWindow")
	return true
end
login:register()

-- ---------------------------------------------------------------- the choice window
local choosing = {} -- player id -> { options, picked }
SpireCleanup.add(function(pid) choosing[pid] = nil end)

function SpireCalling.openWindow(player)
	local v = realGet(player)
	local opts = SpireCalling.optionsOf(v)
	if #opts == 0 then
		return false
	end
	choosing[player:getId()] = { options = opts }
	local lines = {}
	for i, o in ipairs(opts) do
		table.insert(lines, string.format("%d. %s, %s.\n   Gain: %s.\n   Give up: %s.", i, o.name, o.role, o.gain, o.cost))
	end
	local w = ModalWindow(SpireCalling.WINDOW, v.path and "Choose your style" or "Choose your path", table.concat(lines, "\n\n"))
	for i, o in ipairs(opts) do
		w:addChoice(i, o.name .. " (" .. o.role .. ")")
	end
	w:addButton(1, "Choose")
	w:addButton(2, "Not yet")
	w:setDefaultEnterButton(1)
	w:setDefaultEscapeButton(2)
	w:sendToPlayer(player)
	return true
end

local window = CreatureEvent("SpireCallingWindow")
function window.onModalWindow(player, windowId, buttonId, choiceId)
	local c = choosing[player:getId()]
	if windowId == SpireCalling.WINDOW then
		if not c or buttonId ~= 1 or not c.options[choiceId] then
			choosing[player:getId()] = nil
			return true
		end
		c.picked = c.options[choiceId]
		local w = ModalWindow(SpireCalling.CONFIRM, "This is permanent", string.format("Choose %s for good? Only a Mastery Respec Scroll from the shop can undo it.", c.picked.name))
		w:addButton(1, "Yes, " .. c.picked.name)
		w:addButton(2, "Go back")
		w:setDefaultEnterButton(2)
		w:setDefaultEscapeButton(2)
		w:sendToPlayer(player)
	elseif windowId == SpireCalling.CONFIRM then
		choosing[player:getId()] = nil
		if not c or not c.picked then
			return true
		end
		if buttonId ~= 1 then
			SpireCalling.openWindow(player)
			return true
		end
		local ok, msg = SpireStyle.choose(player, c.picked.key)
		player:sendTextMessage(ok and MESSAGE_EVENT_ADVANCE or MESSAGE_STATUS, msg)
		if ok then
			player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
			if SpireStyle.applySpeed then
				SpireStyle.applySpeed(player)
			end
			if SpireStyle.applyBody then
				SpireStyle.applyBody(player)
			end
		end
	end
	return true
end
window:register()

-- ---------------------------------------------------------------- the trainer's talk
-- Called from the four trainers' talk (lib/spirebound/quests.lua SpireQuests.talk, npc/hearthgate_vesper.lua).
local IS_TRAINER = {}
for _, n in pairs(SpireCalling.TRAINERS) do
	IS_TRAINER[n] = true
end
function SpireCalling.talk(npc, handler, player, msg, npcName)
	if not IS_TRAINER[npcName] or not player.getVocation or npcName ~= SpireCalling.trainerOf(player) then
		return false
	end
	local lower = msg:lower()
	if not (MsgContains(lower, "calling") or MsgContains(lower, "trial") or MsgContains(lower, "choose") or MsgContains(lower, "style")) then
		return false
	end
	local say = function(text) handler:say(text, npc, player) end
	local v = realGet(player)
	if not v.choiceReady then
		if v.final then
			say("Your style is complete. There is nothing left for me to teach you, only to watch.")
		elseif v.path then
			say(string.format("Keep at it. When your %s reaches Mastery 10, I will send for you again.", SpireStyle.name(v.voc, v.path)))
		else
			say("Not yet. When you reach the second floor of the tower, I will send for you, and you will choose your path.")
		end
		return true
	end
	local opts = SpireCalling.optionsOf(v)
	for _, o in ipairs(opts) do
		if MsgContains(lower, o.name:lower()) or MsgContains(lower, o.key) then
			if v.trials[o.key] then
				say(string.format("You have tried %s already.", o.name))
				return true
			end
			local ok, text = SpireCalling.startTrial(player, o.key)
			say(text)
			return true
		end
	end
	local missing = {}
	for _, o in ipairs(opts) do
		if not v.trials[o.key] then
			table.insert(missing, "{" .. o.name:lower() .. "}")
		end
	end
	if #missing > 0 then
		say(string.format("Your choice: %s (%s) or %s (%s). Before you choose, you take the Path Trial for each, about five minutes alone with its power. Say %s to begin.",
			opts[1].name, opts[1].role, opts[2].name, opts[2].role, table.concat(missing, " or ")))
		return true
	end
	say("You have tried both. Choose with care: the window is open.")
	SpireCalling.openWindow(player)
	return true
end
