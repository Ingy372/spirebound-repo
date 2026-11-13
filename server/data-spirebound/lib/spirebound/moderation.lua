-- Moderation basics (roadmap R14, REVIEW section 4): !report, GM mute, a log of every GM action, a chat filter for
-- English, Portuguese and Spanish, the rules in game and a written punishment ladder (docs/RULES.md, the website).

SpireMod = SpireMod or {}

-- Words the public channels refuse (whole words, any case). Add to this list freely; Q23 decides who moderates.
SpireMod.BLOCKED = {
	-- en
	"fuck", "fucking", "fucker", "motherfucker", "cunt", "whore", "retard", "retarded", "faggot",
	-- pt
	"caralho", "porra", "puta", "puto", "viado", "arrombado", "buceta", "fdp",
	-- es
	"puta", "pendejo", "pendeja", "cabron", "cabrón", "gilipollas", "maricon", "maricón", "hijueputa",
}
local BLOCK = {}
for _, w in ipairs(SpireMod.BLOCKED) do
	BLOCK[w] = true
end

-- Pure: does a chat line contain a blocked word? Letters swapped for look-alike digits count too (f4gg0t...).
function SpireMod.blocked(text)
	local t = (text or ""):lower():gsub("[0@]", "o"):gsub("1", "i"):gsub("3", "e"):gsub("4", "a"):gsub("5", "s"):gsub("%$", "s")
	for word in t:gmatch("[%a\128-\255]+") do
		if BLOCK[word] then
			return true, word
		end
	end
	return false
end

-- The punishment ladder (also in docs/RULES.md and on the website). Each step is the usual answer to a repeat.
SpireMod.LADDER = {
	"1. A warning from a gamemaster.",
	"2. A mute: 1 hour, then 24 hours, then 7 days.",
	"3. A ban of the character: 1 day, then 7 days.",
	"4. A ban of the account: 30 days.",
	"5. A permanent ban. Cheating with third-party bots, selling accounts or gold for money, or abusing a bug for gain skips straight to step 3 or 5.",
}
SpireMod.RULES = {
	"Spirebound rules, in short:",
	"- Be decent in public chat: no slurs, no threats, no spam. The chat filter blocks the worst words in English, Portuguese and Spanish.",
	"- Player killing is part of the game where the zones allow it; hunting newcomers again and again is not, and the skull and bounty rules punish it.",
	"- Only the cavebot built into the Spirebound client is allowed. Third-party bots and macros are cheating.",
	"- Bugs: report them with !report, never use them for gain.",
	"- No selling characters, items or gold for real money.",
	"- Report a player: say !report <name>, <what happened>. A gamemaster reads every report.",
	"",
	"What happens to rule breakers:",
}

function SpireMod.rulesText()
	local lines = {}
	for _, l in ipairs(SpireMod.RULES) do
		table.insert(lines, l)
	end
	for _, l in ipairs(SpireMod.LADDER) do
		table.insert(lines, l)
	end
	return table.concat(lines, "\n")
end

-- Every GM action is logged: kept in the database (last 500) and in the server log
function SpireMod.log(gmName, action, target, detail)
	local store = kv.scoped("spirebound-gmlog")
	local list = store:get("entries") or {}
	table.insert(list, { t = os.time(), gm = gmName, action = action, target = target or "", detail = detail or "" })
	while #list > 500 do
		table.remove(list, 1)
	end
	store:set("entries", list)
	logger.info("[Spirebound] GM {} {} {} {}", gmName, action, target or "", detail or "")
end

function SpireMod.recentLog(n)
	local list = kv.scoped("spirebound-gmlog"):get("entries") or {}
	local out = {}
	for i = math.max(1, #list - (n or 20) + 1), #list do
		table.insert(out, list[i])
	end
	return out
end

-- Reports from players: kept until a GM clears them
function SpireMod.addReport(from, about, text)
	local store = kv.scoped("spirebound-reports")
	local list = store:get("open") or {}
	table.insert(list, { t = os.time(), from = from, about = about, text = text })
	store:set("open", list)
	return #list
end

function SpireMod.reports()
	return kv.scoped("spirebound-reports"):get("open") or {}
end

-- Pure: parse "!report <name>, <what happened>"
function SpireMod.parseReport(param)
	local name, what = (param or ""):match("^%s*([^,]+),%s*(.+)$")
	if not name or #what < 5 then
		return nil
	end
	return name:gsub("%s+$", ""), what:sub(1, 300)
end
