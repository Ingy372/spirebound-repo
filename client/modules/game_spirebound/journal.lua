-- Journal window (roadmap 6.1). Press J. Tabs ask the server (opcode 210, {t="journal", tab=...})
-- and show the text lines it sends back. Server side: lib/spirebound/journal.lua
SpireJournalUi = {}
local win = nil
local TABS = {
  { 'secrets', 'Secrets' }, { 'fishing', 'Fishing' }, { 'quests', 'Quests' },
  { 'task', 'Task' }, { 'top', 'Top' }, { 'memorial', 'Memorial' }, { 'howto', 'How do I' }, { 'commands', 'Commands' },
}
-- Roadmap R19: every chat command a player needs, one click away (the Commands tab sends it for you)
local COMMANDS = {
  { '!hunt', 'Where should I hunt for my level?' }, { '!guide', 'Read the starter letter again' },
  { '!spells', 'Every spell and sword skill of my path' }, { '!rules', 'The rules' },
  { '!taskshop', 'Spend task points' }, { '!top', 'Top climbers' }, { '!memorial', 'The fallen of the Death Game' },
  { '!path', 'Season Path goals' }, { '!trophies', 'My boss trophies' }, { '!openhouse', 'Open my house to visitors (2 hours)' },
  { '!portal', 'Travel through my house portal' }, { '!private', 'Private boss hall (party leader, top of a labyrinth)' },
  { '!lfg', 'Show or hide me as looking for a group' }, { '!language', 'Change language (en, pt, es)' },
  { '!arena join', 'Join the arena event' }, { '!siege join', 'Join the Spire Siege' },
  { '!buyhouse', 'Buy the house whose door I face' }, { '!report', 'Report a player (add: name, what happened)', true },
  { '!summon', 'Summoning Circle in my house (add: boss name)', true }, { '!dice', 'Bet in a Fortune Hall (add: amount high|low)', true },
  { '!fortune', 'Make my house a Fortune Hall (add: license)', true }, { '!mannequin', 'Show my outfit on a house mannequin' },
  { '!pond', 'My house pond' }, { '!warroom', 'My guild war room' }, { '!journal', 'Open this Journal' },
}
local current = 'secrets'
local LABELS = {
  pt = { secrets = 'Segredos', fishing = 'Pesca', quests = 'Missões', task = 'Tarefa', top = 'Top', memorial = 'Memorial', howto = 'Como faço', commands = 'Comandos', close = 'Fechar', journal = 'Diário', loading = 'carregando...' },
  es = { secrets = 'Secretos', fishing = 'Pesca', quests = 'Misiones', task = 'Tarea', top = 'Top', memorial = 'Memorial', howto = 'Cómo hago', commands = 'Comandos', close = 'Cerrar', journal = 'Diario', loading = 'cargando...' },
}
SpireJournalUi.lang = 'en'
local function label(key, english)
  local l = LABELS[SpireJournalUi.lang]
  return (l and l[key]) or english
end

local function showCommands()
  if not win then
    return
  end
  win:setText(label('journal', 'Journal') .. ' - ' .. label('commands', 'Commands'))
  local body = win:getChildById('body')
  body:destroyChildren()
  for _, c in ipairs(COMMANDS) do
    local b = g_ui.createWidget('Button', body)
    b:setText(c[1] .. '   ' .. c[2])
    b:setHeight(20)
    b.onClick = function()
      if c[3] then -- the command needs more words: put it in the chat line to finish
        modules.game_console.setTextEditText(c[1] .. ' ')
      else
        g_game.talk(c[1])
      end
    end
  end
end

local function request(tab)
  current = tab
  if tab == 'commands' then
    showCommands()
    return
  end
  local protocol = g_game.getProtocolGame()
  if protocol then
    protocol:sendExtendedJSONOpcode(210, { t = 'journal', tab = tab })
  end
  if win then
    win:setText(label('journal', 'Journal') .. ' - ' .. label('loading', 'loading...'))
  end
end

function SpireJournalUi.show(data)
  if not win or data.tab ~= current then
    return
  end
  win:setText(label('journal', 'Journal') .. ' - ' .. (data.title or ''))
  local body = win:getChildById('body')
  body:destroyChildren()
  for _, line in ipairs(data.lines or {}) do
    local l = g_ui.createWidget('Label', body)
    l:setTextWrap(true)
    l:setTextAutoResize(true)
    l:setFont('verdana-11px-rounded')
    l:setText(line)
    if line:sub(1, 3) == '[x]' then
      l:setColor('#9fe0a0')
    elseif line:sub(1, 3) ~= '[ ]' and not line:find('^%s') and #(data.lines) > 1 then
      l:setColor('#ffd27f')
    end
  end
end

function SpireJournalUi.hide()
  if win then
    win:destroy()
    win = nil
  end
end

function SpireJournalUi.toggle()
  if win then
    SpireJournalUi.hide()
    return
  end
  if not g_game.isOnline() then
    return
  end
  win = g_ui.loadUI('/modules/game_spirebound/journal', g_ui.getRootWidget())
  local tabs = win:getChildById('tabs')
  for _, t in ipairs(TABS) do
    local b = g_ui.createWidget('SpireTabButton', tabs)
    b:setText(label(t[1], t[2]))
    b.onClick = function() request(t[1]) end
  end
  win:getChildById('closeButton'):setText(label('close', 'Close'))
  win:show()
  win:raise()
  win:focus()
  request(current)
end
