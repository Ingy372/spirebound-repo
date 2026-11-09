local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid) npcHandler:onCreatureAppear(cid) end
function onCreatureDisappear(cid) npcHandler:onCreatureDisappear(cid) end
function onCreatureSay(cid, type, msg) npcHandler:onCreatureSay(cid, type, msg) end
function onThink() npcHandler:onThink() end

npcHandler:setMessage(MESSAGE_GREET, "Be welcome under the tower, |PLAYERNAME|.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Walk safely, |PLAYERNAME|.")
keywordHandler:addKeyword({"job"}, StdModule.say, {npcHandler = npcHandler, text = "I keep the temple of Hearthgate."})
keywordHandler:addKeyword({"name"}, StdModule.say, {npcHandler = npcHandler, text = "I am Sister Ilse."})
keywordHandler:addKeyword({"tower"}, StdModule.say, {npcHandler = npcHandler, text = "Every floor above us is sealed until someone is brave enough to break it open."})

npcHandler:addModule(FocusModule:new())
