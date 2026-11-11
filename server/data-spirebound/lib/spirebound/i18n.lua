-- Languages (roadmap 6.3). English is the source text. Players pick a language with !language en|pt|es.
-- Every text sent with player:sendTextMessage is looked up in the player's language table
-- (lib/spirebound/i18n_pt.lua, i18n_es.lua): exact sentences first, then patterns with captures.
-- Anything with no translation is sent in English, so a missing line never breaks the game.
SpireI18n = {
	LANGS = { en = "English", pt = "Português (Brasil)", es = "Español" },
	dict = {}, -- lang -> { exact = {...}, rules = { {pattern, replacement}, ... } }
	cache = {}, -- guid -> lang (only non-English entries are stored)
}

function SpireI18n.register(lang, exact, rules)
	SpireI18n.dict[lang] = { exact = exact or {}, rules = rules or {} }
end

-- Pure: translate one text for a language. Returns the text unchanged if nothing matches.
function SpireI18n.translate(lang, text)
	local d = SpireI18n.dict[lang]
	if not d or type(text) ~= "string" then
		return text
	end
	local hit = d.exact[text]
	if hit then
		return hit
	end
	for _, rule in ipairs(d.rules) do
		local out, n = text:gsub(rule[1], rule[2])
		if n > 0 then
			return out
		end
	end
	return text
end

function SpireI18n.langOf(player)
	return SpireI18n.cache[player:getGuid()] or "en"
end

function SpireI18n.setLang(player, lang)
	if not SpireI18n.LANGS[lang] then
		return false
	end
	player:kv():scoped("spirebound-lang"):set("lang", lang)
	SpireI18n.cache[player:getGuid()] = lang ~= "en" and lang or nil
	return true
end

function SpireI18n.load(player)
	local lang = player:kv():scoped("spirebound-lang"):get("lang")
	SpireI18n.cache[player:getGuid()] = (lang and lang ~= "en" and SpireI18n.LANGS[lang]) and lang or nil
end

-- Translate a text for a player
function SpireI18n.t(player, text)
	local lang = SpireI18n.langOf(player)
	if lang == "en" then
		return text
	end
	return SpireI18n.translate(lang, text)
end

-- Wrap the message senders once. If translation ever throws, the English text goes out instead.
if not SpireI18n.hooked then
	SpireI18n.hooked = true
	local origSend = Player.sendTextMessage
	function Player:sendTextMessage(messageType, text, ...)
		local ok, out = pcall(SpireI18n.t, self, text)
		return origSend(self, messageType, ok and out or text, ...)
	end
	local origDialog = Player.showTextDialog
	function Player:showTextDialog(itemId, text, ...)
		-- dialogs are many lines: translate line by line
		local ok, out = pcall(function()
			if SpireI18n.langOf(self) == "en" or type(text) ~= "string" then
				return text
			end
			local lines = {}
			for line in (text .. "
"):gmatch("(.-)
") do
				table.insert(lines, SpireI18n.t(self, line))
			end
			return table.concat(lines, "
")
		end)
		return origDialog(self, itemId, ok and out or text, ...)
	end
end

dofile(DATA_DIRECTORY .. "/lib/spirebound/i18n_pt.lua")
dofile(DATA_DIRECTORY .. "/lib/spirebound/i18n_es.lua")
