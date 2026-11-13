-- Task window (Jay, 2026-11-13): every floor's taskmaster opens the same menu, listing that floor's monsters.
-- The server sends {t="tasks", master, floor, points, active, list={...}} when you greet a taskmaster;
-- the buttons send {t="task", a="take"|"report"|"cancel", id} back. Server side: lib/spirebound/tasks.lua
SpireTasksUi = {}
local win = nil

local function send(action, id)
  local protocol = g_game.getProtocolGame()
  if protocol then
    protocol:sendExtendedJSONOpcode(210, { t = 'task', a = action, id = id })
  end
end

local function waitText(seconds)
  local h = math.floor(seconds / 3600)
  local m = math.floor((seconds % 3600) / 60)
  if h > 0 then
    return string.format('in %dh %dm', h, m)
  end
  return string.format('in %dm', math.max(1, m))
end

local function plural(n, word)
  return n .. ' ' .. word .. (n == 1 and '' or 's')
end

function SpireTasksUi.hide()
  if win then
    win:destroy()
    win = nil
  end
end

function SpireTasksUi.show(data)
  if not g_game.isOnline() then
    return
  end
  if not win then
    win = g_ui.loadUI('/modules/game_spirebound/tasks', g_ui.getRootWidget())
    win:getChildById('activeBox'):getChildById('report').onClick = function() send('report') end
    win:getChildById('activeBox'):getChildById('cancel').onClick = function() send('cancel') end
  end
  win:setText(string.format('%s - Floor %d hunting tasks', data.master or 'Taskmaster', data.floor or 0))
  win:getChildById('points'):setText(string.format('Task points: %d        Pick a task:', data.points or 0))

  local box = win:getChildById('activeBox')
  local a = data.active
  local hasActive = type(a) == 'table'
  local bar = box:getChildById('activeBar')
  if hasActive then
    local done = (a.kills or 0) >= (a.count or 1)
    box:getChildById('activeText'):setText(string.format('Current task: %s (Floor %d)  -  %d of %d  -  reward %d gold, %s',
      a.monster, a.floor or 0, a.kills or 0, a.count or 0, a.gold or 0, plural(a.points or 0, 'point')))
    bar:setPercent(math.floor(100 * (a.kills or 0) / math.max(1, a.count or 1)))
    bar:setText(done and 'Done! Press Report.' or string.format('%d / %d', a.kills or 0, a.count or 0))
    bar:setVisible(true)
    box:getChildById('report'):setEnabled(done)
    box:getChildById('cancel'):setEnabled(true)
  else
    box:getChildById('activeText'):setText('No task yet. Pick one below.')
    bar:setVisible(false)
    box:getChildById('report'):setEnabled(false)
    box:getChildById('cancel'):setEnabled(false)
  end

  local list = win:getChildById('list')
  list:destroyChildren()
  for _, row in ipairs(data.list or {}) do
    local w = g_ui.createWidget('SpireTaskRow', list)
    local look = row.look or {}
    if (look[1] or 0) > 0 then
      w:getChildById('look'):setOutfit({ type = look[1], head = look[2] or 0, body = look[3] or 0, legs = look[4] or 0, feet = look[5] or 0 })
    end
    w:getChildById('name'):setText(row.monster)
    w:getChildById('info'):setText(string.format('Hunt %d   -   %d gold   -   %s', row.count, row.gold, plural(row.points, 'task point')))
    local b = w:getChildById('take')
    if row.status == 'active' then
      b:setText('Your task')
      b:setEnabled(false)
      w:setBorderColor('#4a6a4a')
    elseif row.status == 'wait' then
      b:setText(waitText(row.wait or 0))
      b:setEnabled(false)
      b:setTooltip('You did this one recently. It comes back after 20 hours.')
    else
      b:setText('Take task')
      b:setEnabled(not hasActive)
      if hasActive then
        b:setTooltip('Finish or cancel your current task first.')
      end
      b.onClick = function() send('take', row.id) end
    end
  end
  win:show()
  win:raise()
  win:focus()
end
