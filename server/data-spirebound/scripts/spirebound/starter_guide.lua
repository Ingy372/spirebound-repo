-- Starter letter, !guide and !spells (playtest 2026-11-11: "players need a sense of direction" and
-- "I couldn't find the NPC that sells spells"). Spells are never sold: they unlock by level (DESIGN 5.3b).
SpireGuide = {}

local LETTER_ID = 3505 -- "letter" (writeable, so it can carry text)

SpireGuide.TEXT = table.concat({
	"Welcome to Hearthgate, climber.",
	"",
	"THE TOWER. Spirebound rises above these plains: ten floors, each sealed by a guardian. When anyone defeats a floor's guardian, the way up opens for everyone, and their name is carved on the Monument. Nobody climbs alone.",
	"",
	"YOUR FIRST STEPS",
	"1. Hunt rats and wolves in the fields just outside town. Press J at any time for your Journal.",
	"2. Visit Banker Tolliver (your gold) and Quartermaster Bryn (potions). Taskmaster Rhen hands out hunting tasks.",
	"3. Speak to Miller Agna in Millcross: 'Bread for the Road' is your first story quest. Captain Dorrow, at the north gate, has the next.",
	"4. At level 8 you learn your first spells on your own. No one sells spells. Type !spells to see them all.",
	"5. Around level 20, face the Gate Hound at the Pass. Its fall opens the labyrinth beyond.",
	"6. Look off the beaten path. Vesper, the Info Broker, pays well for secrets.",
	"",
	"Type !guide to read this again.",
}, "\n")

function SpireGuide.giveLetter(player)
	local letter = player:addItem(LETTER_ID, 1)
	if letter then
		letter:setAttribute(ITEM_ATTRIBUTE_TEXT, SpireGuide.TEXT)
		letter:setAttribute(ITEM_ATTRIBUTE_DESCRIPTION, "A letter for new climbers. Read it to find your first steps.")
	end
	return letter
end

-- Pure: the lines of the !spells list for a base vocation and level
function SpireGuide.spellLines(baseVocation, level)
	local rows = {}
	for _, row in ipairs(SpireSpells.list) do
		if not row.lostArt and SpireSpells.allowed(row, baseVocation) then
			table.insert(rows, row)
		end
	end
	table.sort(rows, function(a, b)
		if a.level ~= b.level then
			return a.level < b.level
		end
		return a.name < b.name
	end)
	local lines = {}
	for _, row in ipairs(rows) do
		local state = level >= row.level and "learned" or ("level " .. row.level)
		table.insert(lines, string.format("%-18s say \"%s\"   (%s)", row.name, row.words, state))
	end
	return lines
end

local guide = TalkAction("!guide")
function guide.onSay(player, words, param)
	player:showTextDialog(LETTER_ID, SpireGuide.TEXT)
	return false
end
guide:separator(" ")
guide:groupType("normal")
guide:register()

local spells = TalkAction("!spells")
function spells.onSay(player, words, param)
	if SpireTutorial then
		SpireTutorial.mark(player, "spells") -- the Arrival Yard's third gate (R11)
	end
	local base = player:getVocation():getBaseId()
	if base == 0 then
		player:sendTextMessage(MESSAGE_STATUS, "Speak to Registrar Maelis in the temple to choose a path first.")
		return false
	end
	local lines = SpireGuide.spellLines(base, player:getLevel())
	table.insert(lines, 1, "Spells unlock by level. No one sells them: when you reach a level you learn its spells automatically.\n")
	player:showTextDialog(LETTER_ID, table.concat(lines, "\n"))
	return false
end
spells:separator(" ")
spells:groupType("normal")
spells:register()
