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

-- Pure: does a style view (SpireStyle.view) own this style row? The same checks as casting it (scripts/spirebound/spells.lua).
function SpireGuide.ownsStyle(row, view)
	if not view then
		return false
	end
	if row.path and view.path ~= row.path then
		return false
	end
	if row.final and view.final ~= row.final then
		return false
	end
	return SpireStyle.hasAbilityPure(view, row.style)
end

-- Pure: the lines of the !spells list for a base vocation, level and style view (nil: no style progress).
-- Style abilities come from the style tree, not from levels, so they get their own section (C2, Claude's playtest
-- 2026-11-25: a level-8 Ranger with no path saw six of them marked "learned").
function SpireGuide.spellLines(baseVocation, level, view)
	local rows, styled = {}, {}
	for _, row in ipairs(SpireSpells.list) do
		if not row.lostArt and SpireSpells.allowed(row, baseVocation) then
			table.insert(row.style and styled or rows, row)
		end
	end
	local function lv(row)
		return SpireSpells.levelFor(row, baseVocation)
	end
	table.sort(rows, function(a, b)
		if lv(a) ~= lv(b) then
			return lv(a) < lv(b)
		end
		return a.name < b.name
	end)
	table.sort(styled, function(a, b)
		if a.style ~= b.style then
			return a.style < b.style
		end
		return a.name < b.name
	end)
	local lines = {}
	for _, row in ipairs(rows) do
		local state = level >= lv(row) and "learned" or ("level " .. lv(row))
		table.insert(lines, string.format("%-18s say \"%s\"   (%s)", row.name, row.words, state))
	end
	if #styled > 0 then
		table.insert(lines, "\nStyle abilities: these come from your fighting style, not your level (say !style).")
		for _, row in ipairs(styled) do
			local state
			if SpireGuide.ownsStyle(row, view) then
				state = "yours"
			elseif row.final then
				state = "with the " .. SpireStyle.name(baseVocation, row.final) .. " style"
			elseif row.path then
				state = "with the " .. SpireStyle.name(baseVocation, row.path) .. " path"
			else
				state = "at style Mastery 10"
			end
			table.insert(lines, string.format("%-18s say \"%s\"   (%s)", row.name, row.words, state))
		end
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

-- Pure: before a path is chosen, each path's first spells (the Arrival Yard's gate sends new players here)
SpireGuide.PREVIEW_LEVEL = 10
function SpireGuide.previewLines()
	local lines = { "What each path learns first. Choose your path with Registrar Maelis at the end of the stone path;", "after that, !spells lists everything your path will learn.", "" }
	for _, voc in ipairs({ 4, 3, 1, 2 }) do -- Vanguard, Ranger, Arcanist, Mystic
		local v = Vocation(voc)
		table.insert(lines, (v and v:getName() or ("Path " .. voc)) .. ":")
		local rows = {}
		for _, row in ipairs(SpireSpells.list) do
			if not row.lostArt and not row.style and SpireSpells.allowed(row, voc) and SpireSpells.levelFor(row, voc) <= SpireGuide.PREVIEW_LEVEL then
				table.insert(rows, row)
			end
		end
		table.sort(rows, function(a, b)
			local la, lb = SpireSpells.levelFor(a, voc), SpireSpells.levelFor(b, voc)
			if la ~= lb then return la < lb end
			return a.name < b.name
		end)
		for _, row in ipairs(rows) do
			table.insert(lines, string.format("  %-18s (level %d)", row.name, SpireSpells.levelFor(row, voc)))
		end
		table.insert(lines, "")
	end
	return lines
end

local spells = TalkAction("!spells")
function spells.onSay(player, words, param)
	if SpireTutorial then
		SpireTutorial.mark(player, "spells") -- the Arrival Yard's third gate (R11)
	end
	local base = player:getVocation():getBaseId()
	if base == 0 then -- party playtest 2026-11-26 (hand-off P2-12): the yard gate promises this list before the Registrar
		player:showTextDialog(LETTER_ID, table.concat(SpireGuide.previewLines(), "\n"))
		return false
	end
	local lines = SpireGuide.spellLines(base, player:getLevel(), SpireStyle.get(player))
	table.insert(lines, 1, "Spells unlock by level. No one sells them: when you reach a level you learn its spells automatically.\n")
	player:showTextDialog(LETTER_ID, table.concat(lines, "\n"))
	return false
end
spells:separator(" ")
spells:groupType("normal")
spells:register()
