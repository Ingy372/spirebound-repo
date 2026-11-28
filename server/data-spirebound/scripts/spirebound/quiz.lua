-- J9 (Jay's direction list): ten-minute mini events between the big world events. The Tower Quiz: halfway between two
-- world events (every 3 hours, first one 90 minutes after start-up) the tower asks a question about the game; the
-- first climber to say !answer and the right word wins gold in the bank.
SpireQuiz = SpireQuiz or { open = nil, used = {} }
SpireQuiz.MINUTES = 3
SpireQuiz.QUESTIONS = {
	{ q = "Who buys word of secrets in Hearthgate?", a = { "vesper" } },
	{ q = "What guards the Pass on Floor 1?", a = { "gate hound", "the gate hound", "hound" } },
	{ q = "Who gives a new climber's very first quest?", a = { "pell", "guide pell" } },
	{ q = "Which difficulty ends a character for good at its first monster death?", a = { "death game", "deathgame" } },
	{ q = "Which town with a mill lies west of Hearthgate?", a = { "millcross" } },
	{ q = "What rare drop upgrades a weapon at the smith?", a = { "hearth shard", "hearth shards", "shard", "shards" } },
	{ q = "How many floors does the tower have?", a = { "10", "ten" } },
	{ q = "Which Ranger path slows and traps its prey?", a = { "trapper" } },
	{ q = "Who sells arrows and quivers in Hearthgate?", a = { "tamsin", "fletcher tamsin" } },
	{ q = "Who waits at the top of Floor 1's labyrinth?", a = { "axe-lord", "axe lord", "the axe-lord", "axe-lord of the stair" } },
	{ q = "Which path heals with the power of growing things?", a = { "mystic", "lifebinder" } },
	{ q = "What do you say to ask the tower where to hunt?", a = { "!hunt", "hunt" } },
}

-- Pure: does `said` answer question `row`? (case, spaces and a leading "the" don't matter)
function SpireQuiz.correct(row, said)
	local s = (said or ""):lower():gsub("^%s+", ""):gsub("%s+$", ""):gsub("%s+", " ")
	for _, a in ipairs(row.a) do
		if s == a or s == "the " .. a then
			return true
		end
	end
	return false
end

-- Pure: the prize for a climber of this level
function SpireQuiz.prize(level)
	return math.min(2000, 50 * math.max(1, level))
end

-- Pure: pick a question not asked lately (used = set of indexes asked; it resets once every question was asked)
function SpireQuiz.pick(used, roll)
	local pool = {}
	for i = 1, #SpireQuiz.QUESTIONS do
		if not used[i] then
			table.insert(pool, i)
		end
	end
	if #pool == 0 then
		for k in pairs(used) do
			used[k] = nil
		end
		return SpireQuiz.pick(used, roll)
	end
	return pool[math.floor(roll * #pool) + 1]
end

function SpireQuiz.ask()
	if #Game.getPlayers() == 0 then
		return
	end
	local i = SpireQuiz.pick(SpireQuiz.used, math.random())
	SpireQuiz.used[i] = true
	SpireQuiz.open = { index = i, untilTime = os.time() + SpireQuiz.MINUTES * 60 }
	Game.broadcastMessage("Tower Quiz! " .. SpireQuiz.QUESTIONS[i].q .. " The first to say !answer and the answer wins gold.", MESSAGE_EVENT_ADVANCE)
	addEvent(function()
		if SpireQuiz.open and SpireQuiz.open.index == i then
			SpireQuiz.open = nil
			Game.broadcastMessage("Tower Quiz: nobody got it. The answer was: " .. SpireQuiz.QUESTIONS[i].a[1] .. ".", MESSAGE_EVENT_ADVANCE)
		end
	end, SpireQuiz.MINUTES * 60 * 1000)
end

local function loop()
	SpireQuiz.ask()
	addEvent(loop, SpireEvents.INTERVAL * 1000)
end

local startup = GlobalEvent("SpireQuizStartup")
function startup.onStartup()
	addEvent(loop, SpireEvents.INTERVAL / 2 * 1000) -- halfway between world events
	return true
end
startup:register()

local answer = TalkAction("!answer")
function answer.onSay(player, words, param)
	local open = SpireQuiz.open
	if not open or os.time() > open.untilTime then
		player:sendTextMessage(MESSAGE_STATUS, "There is no Tower Quiz right now. One comes every few hours.")
		return false
	end
	local row = SpireQuiz.QUESTIONS[open.index]
	if not SpireQuiz.correct(row, param) then
		player:sendTextMessage(MESSAGE_STATUS, "Not quite. Try again!")
		return false
	end
	SpireQuiz.open = nil
	local gold = SpireQuiz.prize(player:getLevel())
	SpireGive.gold(player, gold) -- Q76: coins go in the backpack
	player:getPosition():sendMagicEffect(CONST_ME_FIREWORK_YELLOW)
	Game.broadcastMessage(string.format("Tower Quiz: %s answered first (%s)! %d gold for them.", player:getName(), row.a[1], gold), MESSAGE_EVENT_ADVANCE)
	return false
end
answer:separator(" ")
answer:groupType("normal")
answer:register()
