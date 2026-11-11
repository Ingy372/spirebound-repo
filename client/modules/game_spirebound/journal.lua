-- Journal window (roadmap 6.1). Press J. Tabs ask the server (opcode 210, {t="journal", tab=...})
-- and show the text lines it sends back. Server side: lib/spirebound/journal.lua
SpireJournalUi = {}
local win = nil
local TABS = {
  { 'secrets', 'Secrets' }, { 'fishing', 'Fishing' }, { 'quests', 'Quests' },
  { 'task', 'Task' }, { 'top', 'Top' }, { 'memorial', 'Memorial' },
}
local current = 'secrets'

local function request(tab)
  current = tab
  local protocol = g_game.getProtocolGame()
  if protocol then
    protocol:sendExtendedJSONOpcode(210, { t = 'journal', tab = tab })
  end
  if win then
    win:setText('Journal - loading...')
  end
end

function SpireJournalUi.show(data)
  if not win or data.tab ~= current then
    return
  end
  win:setText('Journal - ' .. (data.title or ''))
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
    b:setText(t[2])
    b.onClick = function() request(t[1]) end
  end
  win:show()
  win:raise()
  win:focus()
  request(current)
end
