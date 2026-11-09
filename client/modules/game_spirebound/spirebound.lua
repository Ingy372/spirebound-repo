-- Spirebound client UI (roadmap 1.20). Talks to the server over extended opcode 210 (JSON);
-- server side: server/data-spirebound/lib/spirebound/client_link.lua
local OPCODE = 210
local SLOTS = 9
local floorLabel, diffLabel, bar = nil, nil, nil
local floorText, zoneText = '', ''
local ZONES = {
  town = { 'Safe zone', '#7fff7f' }, guarded = { 'Guarded', '#c8e6ff' }, open = { 'Open PvP', '#ffffff' },
  contested = { 'Contested', '#ffb347' }, deadzone = { 'DEADZONE', '#ff4040' }, bossroom = { 'Boss room: PvP on', '#ff7f7f' },
}

local function updateFloorLabel()
  if floorLabel then
    floorLabel:setText(floorText .. (zoneText ~= '' and ('   [' .. zoneText .. ']') or ''))
  end
end
local buttons = {}
local skills = {}
local cooldownUntil = {} -- skill name -> g_clock.millis() when ready
local tickEvent, cursorEvent = nil, nil
local IMG = '/modules/game_spirebound/images/'

-- SAO-style cursors mapped onto Tibia skulls (DESIGN.md 6.1)
local function cursorFor(creature, skull)
  if not creature:isPlayer() then
    return nil
  end
  if skull == SkullRed then
    return IMG .. 'cursor_red'
  elseif skull == SkullBlack then
    return IMG .. 'cursor_black'
  elseif skull == SkullWhite or skull == SkullYellow or skull == SkullOrange then
    return IMG .. 'cursor_orange'
  end
  return IMG .. 'cursor_green'
end

local originalOnSkullChange = nil

local function refreshCursors()
  local player = g_game.getLocalPlayer()
  if player then
    for _, c in ipairs(g_map.getSpectators(player:getPosition(), false)) do
      if c:isPlayer() then
        local path = cursorFor(c, c:getSkull())
        if path then
          c:setSkullTexture(path)
        end
      end
    end
  end
  cursorEvent = scheduleEvent(refreshCursors, 1000)
end

local function cast(index)
  local s = skills[index]
  if not s or not g_game.isOnline() then
    return
  end
  g_game.talk(s.words)
end

local function redrawButtons()
  local now = g_clock.millis()
  for i = 1, SLOTS do
    local b = buttons[i]
    local s = skills[i]
    if b then
      if s then
        local left = (cooldownUntil[s.name] or 0) - now
        if left > 0 then
          b:setText(string.format('%s\n%.1fs', s.name, left / 1000))
          b:setOn(false)
          b:setColor('#888888')
        else
          b:setText(s.name .. '\n[Shift+' .. i .. ']')
          b:setOn(true)
          b:setColor(s.tag == 'finisher' and '#ffd27f' or (s.tag == 'link' and '#9fe0ff' or '#ffffff'))
        end
        b:setVisible(true)
      else
        b:setVisible(false)
      end
    end
  end
  tickEvent = scheduleEvent(redrawButtons, 100)
end

local function onMessage(protocol, opcode, data)
  if type(data) ~= 'table' then
    return
  end
  if data.t == 'floor' then
    floorText = (data.n and data.n > 0) and ('Floor ' .. data.n .. ' - ' .. (data.name or '')) or ''
    updateFloorLabel()
  elseif data.t == 'zone' then
    local z = ZONES[data.tier]
    zoneText = z and z[1] or ''
    updateFloorLabel()
  elseif data.t == 'difficulty' then
    if diffLabel then
      local text = ''
      if data.mode == 2 then
        text = 'Hardcore'
        diffLabel:setColor('#ff9a3c')
      elseif data.mode == 3 then
        text = 'Death Game'
        diffLabel:setColor('#ff4040')
      end
      diffLabel:setText(text)
    end
  elseif data.t == 'skills' then
    skills = data.list or {}
  elseif data.t == 'cast' then
    cooldownUntil[data.name] = g_clock.millis() + (data.cd or 0)
  end
end

local function createUi()
  local mapPanel = modules.game_interface.getMapPanel()
  floorLabel = g_ui.createWidget('Label', mapPanel)
  floorLabel:setId('spireFloor')
  floorLabel:setFont('verdana-11px-rounded')
  floorLabel:setColor('#7fffd4')
  floorLabel:setTextAutoResize(true)
  floorLabel:addAnchor(AnchorTop, 'parent', AnchorTop)
  floorLabel:addAnchor(AnchorHorizontalCenter, 'parent', AnchorHorizontalCenter)
  floorLabel:setMarginTop(6)
  floorLabel:setPhantom(true)

  diffLabel = g_ui.createWidget('Label', mapPanel)
  diffLabel:setId('spireDifficulty')
  diffLabel:setTextAutoResize(true)
  diffLabel:addAnchor(AnchorTop, 'spireFloor', AnchorBottom)
  diffLabel:addAnchor(AnchorHorizontalCenter, 'parent', AnchorHorizontalCenter)
  diffLabel:setMarginTop(2)
  diffLabel:setPhantom(true)

  bar = g_ui.createWidget('UIWidget', mapPanel)
  bar:setId('spireSkillBar')
  bar:setSize({ width = SLOTS * 92, height = 40 })
  bar:addAnchor(AnchorBottom, 'parent', AnchorBottom)
  bar:addAnchor(AnchorHorizontalCenter, 'parent', AnchorHorizontalCenter)
  bar:setMarginBottom(8)
  for i = 1, SLOTS do
    local b = g_ui.createWidget('Button', bar)
    b:setId('spireSkill' .. i)
    b:setSize({ width = 88, height = 36 })
    b:addAnchor(AnchorTop, 'parent', AnchorTop)
    b:addAnchor(AnchorLeft, 'parent', AnchorLeft)
    b:setMarginLeft((i - 1) * 92)
    b:setFont('verdana-11px-rounded')
    b.onClick = function() cast(i) end
    b:setVisible(false)
    buttons[i] = b
    g_keyboard.bindKeyDown('Shift+' .. i, function() cast(i) end)
  end
end

local function destroyUi()
  for i = 1, SLOTS do
    g_keyboard.unbindKeyDown('Shift+' .. i)
  end
  if bar then bar:destroy() bar = nil end
  if floorLabel then floorLabel:destroy() floorLabel = nil end
  if diffLabel then diffLabel:destroy() diffLabel = nil end
  buttons = {}
end

local function onGameStart()
  destroyUi()
  createUi()
  skills, cooldownUntil = {}, {}
  removeEvent(tickEvent)
  removeEvent(cursorEvent)
  redrawButtons()
  refreshCursors()
end

local function onGameEnd()
  removeEvent(tickEvent)
  removeEvent(cursorEvent)
  destroyUi()
end

function init()
  ProtocolGame.registerExtendedJSONOpcode(OPCODE, onMessage)
  originalOnSkullChange = Creature.onSkullChange
  Creature.onSkullChange = function(self, skullId)
    local path = cursorFor(self, skullId)
    if path then
      self:setSkullTexture(path)
    elseif originalOnSkullChange then
      originalOnSkullChange(self, skullId)
    end
  end
  connect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd })
  if g_game.isOnline() then
    onGameStart()
  end
end

function terminate()
  ProtocolGame.unregisterExtendedJSONOpcode(OPCODE)
  if originalOnSkullChange then
    Creature.onSkullChange = originalOnSkullChange
  end
  disconnect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd })
  onGameEnd()
end
