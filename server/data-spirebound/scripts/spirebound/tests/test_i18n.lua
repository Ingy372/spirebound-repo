-- Roadmap 6.3: Portuguese and Spanish
SpireTest.add("i18n: exact sentences and patterns translate, unknown text stays English", function()
	SpireTest.eq(SpireI18n.translate("pt", "You left the sign-up list."), "Você saiu da lista de inscrição.", "pt exact")
	SpireTest.eq(SpireI18n.translate("es", "You left the sign-up list."), "Saliste de la lista de inscripción.", "es exact")
	SpireTest.eq(SpireI18n.translate("pt", "You fished up a white pearl."), "Você pescou a white pearl.", "pt pattern")
	SpireTest.eq(SpireI18n.translate("es", "You caught a Silver Carp (2.50 kg)!"), "¡Has pescado Silver Carp (2.50 kg)!", "es pattern with two captures")
	SpireTest.eq(SpireI18n.translate("pt", "Task: 30 of 50 Meadow Wolfs."), "Tarefa: 30 de 50 Meadow Wolf.", "task progress")
	SpireTest.eq(SpireI18n.translate("pt", "Something nobody translated."), "Something nobody translated.", "unknown stays English")
	SpireTest.eq(SpireI18n.translate("xx", "It is empty."), "It is empty.", "unknown language stays English")
end)

SpireTest.add("i18n: pt and es cover exactly the same sentences and every pattern is valid", function()
	local pt, es = SpireI18n.dict.pt, SpireI18n.dict.es
	for k in pairs(pt.exact) do
		if not es.exact[k] then error("missing Spanish: " .. k) end
	end
	for k in pairs(es.exact) do
		if not pt.exact[k] then error("missing Portuguese: " .. k) end
	end
	SpireTest.eq(#pt.rules, #es.rules, "same number of patterns")
	for i, r in ipairs(pt.rules) do
		SpireTest.eq(r[1], es.rules[i][1], "same pattern " .. i)
		local ok, err = pcall(string.gsub, "x", r[1], r[2])
		if not ok then error("bad pt rule " .. i .. ": " .. tostring(err)) end
		ok, err = pcall(string.gsub, "x", es.rules[i][1], es.rules[i][2])
		if not ok then error("bad es rule " .. i .. ": " .. tostring(err)) end
	end
end)

SpireTest.add("i18n: journal text has a translation for the tab titles and secret rows", function()
	SpireTest.eq(SpireI18n.translate("es", "Fishing log"), "Registro de pesca", "tab title")
	local row = SpireJournal.secretLine(SpireSecrets.list[1], true)
	SpireTest.eq(SpireI18n.translate("pt", row):find("encontrado", 1, true) ~= nil, true, "found row")
	local hidden = SpireJournal.secretLine(SpireSecrets.list[6], false)
	SpireTest.eq(SpireI18n.translate("pt", hidden):sub(1, 14), "[ ] Andar 1 - ", "hidden row")
end)
