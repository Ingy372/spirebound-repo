-- Spirebound client UI (roadmap 1.20). Talks to the server over extended opcode 210 (JSON);
-- server side: server/data-spirebound/lib/spirebound/client_link.lua
local OPCODE = 210
local SLOTS = 9
local floorLabel, diffLabel, bar, barTitle = nil, nil, nil, nil
local floorText, zoneText, beaconText = '', '', '' -- beaconText: Floor Beacons (roadmap M1)
local pvpLockText = '' -- M5: shown while helpers only heal
local pvpLockOn = false
local ZONES = {
  town = { 'Safe zone', '#7fff7f' }, guarded = { 'Guarded', '#c8e6ff' }, open = { 'Open PvP', '#ffffff' },
  contested = { 'Contested', '#ffb347' }, deadzone = { 'DEADZONE', '#ff4040' }, bossroom = { 'Boss room: PvP on', '#ff7f7f' },
}

local function updateFloorLabel()
  if floorLabel then
    floorLabel:setText(floorText .. (zoneText ~= '' and ('   [' .. zoneText .. ']') or '') .. beaconText .. pvpLockText)
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
  if barTitle then
    barTitle:setVisible(#skills > 0)
  end
  tickEvent = scheduleEvent(redrawButtons, 100)
end

-- G1: put the path's first spells on action bar 1, buttons 3 and 4 (the stock client fills them with Tibia spell words);
-- button 5 (a third Tibia spell) is cleared. Buttons 1-2 keep the stock potions.
-- Grok session 3: the stock client keeps one bar per class, pre-filled with Tibia spells; when the class changed,
-- that bar came back and hid ours. Now the server sends the list at every login and right after the Registrar, and
-- here a button is only replaced when it is empty or still holds one of the stock Tibia spells: whatever a player
-- put there themselves stays.
local STOCK_WORDS = { ['exura infir'] = true, ['exori infir tera'] = true, ['exevo infir frigo hur'] = true }

local function buttonText(ab, slot)
  local ok, m = pcall(ab.ApiJson.getMapping, 1, slot)
  if not ok or not m then return nil, true end
  local s = m.actionsetting or m
  return s.chatText, (s.chatText == nil and s.useObject == nil and s.passiveId == nil and s.action == nil)
end

local function replaceable(ab, slot, ours)
  local text, empty = buttonText(ab, slot)
  return empty or (text and (STOCK_WORDS[text:lower()] or ours[text:lower()]))
end

local function seedSpellBar(list)
  local ab = modules.game_actionbar
  if not ab or not ab.ApiJson or not ab.actionBars or type(list) ~= 'table' then
    return
  end
  local ours = {}
  for _, words in ipairs(list) do ours[words:lower()] = true end
  local slots = { 3, 4 }
  for i, words in ipairs(list) do
    if slots[i] and replaceable(ab, slots[i], ours) then
      ab.ApiJson.createOrUpdateText(1, slots[i], words, true)
    end
  end
  local text5 = buttonText(ab, 5)
  if ab.ApiJson.removeAction and text5 and STOCK_WORDS[text5:lower()] then
    ab.ApiJson.removeAction(1, 5)
  end
  local bar = ab.actionBars[1]
  if bar and bar.tabBar and ab.updateButton then
    for _, n in ipairs({ 3, 4, 5 }) do
      local b = bar.tabBar:getChildById('1.' .. n)
      if b then
        pcall(ab.updateButton, b)
      end
    end
  end
  if ab.ApiJson.saveData then
    pcall(ab.ApiJson.saveData)
  end
end

local function onMessage(protocol, opcode, data)
  if type(data) ~= 'table' then
    return
  end
  if data.t == 'floor' then
    floorText = (data.n and data.n > 0) and ('Floor ' .. data.n .. ' - ' .. (data.name or '')) or ''
    updateFloorLabel()
  elseif data.t == 'pvplock' then
    -- M5 (DESIGN.md 12): in a fight with a player the built-in helpers only heal (client/modules/game_spirebound/bot/spirebound_pvp_guard.lua)
    pvpLockOn = data.on == true
    pvpLockText = pvpLockOn and '   [Player fight: helpers heal only]' or ''
    updateFloorLabel()
  elseif data.t == 'beacon' then
    -- Floor Beacons: how many of the town's fire bowls burn on this floor (each +5% experience and loot)
    if data.n and data.n > 0 and data.lit and data.lit > 0 then
      beaconText = string.format('   Beacon %d/%d (+%d%%, %d min)', data.lit, data.slots or 4, data.lit * 5, data.mins or 0)
    else
      beaconText = ''
    end
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
  elseif data.t == 'spellbar' then
    seedSpellBar(data.list)
    -- again a moment later: a class change switches the client to that class's bar just after this message
    scheduleEvent(function() seedSpellBar(data.list) end, 1500)
  elseif data.t == 'skills' then
    skills = data.list or {}
  elseif data.t == 'lang' then
    SpireJournalUi.lang = data.lang or 'en'
  elseif data.t == 'journal' then
    SpireJournalUi.show(data)
  elseif data.t == 'tasks' then
    SpireTasksUi.show(data)
  elseif data.t == 'tasksclose' then
    SpireTasksUi.hide()
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
  -- Grok session 2: two sets of attack names looked like a mistake. Name this row as the weapon skills.
  barTitle = g_ui.createWidget('Label', mapPanel)
  barTitle:setId('spireSkillBarTitle')
  barTitle:setFont('verdana-11px-rounded')
  barTitle:setColor('#c8c8c8')
  barTitle:setText('Weapon skills (from the weapon in your hand)')
  barTitle:setTextAutoResize(true)
  barTitle:addAnchor(AnchorBottom, 'spireSkillBar', AnchorTop)
  barTitle:addAnchor(AnchorLeft, 'spireSkillBar', AnchorLeft)
  barTitle:setPhantom(true)
  barTitle:setVisible(false)
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
  if barTitle then barTitle:destroy() barTitle = nil end
  if bar then bar:destroy() bar = nil end
  if floorLabel then floorLabel:destroy() floorLabel = nil end
  if diffLabel then diffLabel:destroy() diffLabel = nil end
  buttons = {}
end

-- G5 (Grok playtest, 2026-11-24): the stock Store button opens an empty shop (ours comes with the website, Phase 7)
local function hideStore()
  local mp = modules.game_mainpanel
  local ui = mp and mp.optionsController and mp.optionsController.ui
  local store = ui and ui.onPanel and ui.onPanel.store
  if store and store:getChildCount() > 0 then
    store:destroyChildren()
    if mp.reloadMainPanelSizes then
      pcall(mp.reloadMainPanelSizes)
    end
  end
end

-- Tell the server which client build this is (Grok session 3 played on a weeks-old copy and reported long-fixed bugs).
-- Raise it together with SpireClient.CLIENT_VERSION (server lib/spirebound/client_link.lua) whenever a client module
-- changes in a way players must have.
local CLIENT_VERSION = 2

local function onGameStart()
  scheduleEvent(function()
    local protocol = g_game.getProtocolGame()
    if protocol then protocol:sendExtendedJSONOpcode(OPCODE, { t = 'hello', v = CLIENT_VERSION }) end
  end, 2000)
  destroyUi()
  createUi()
  skills, cooldownUntil = {}, {}
  removeEvent(tickEvent)
  removeEvent(cursorEvent)
  redrawButtons()
  scheduleEvent(hideStore, 1500)
  -- Q51 (Grok playtest): the bot panel looked unfinished to a new player. Fold it once per install; the player can
  -- open it again, and from then on the bot keeps its own open/closed setting.
  scheduleEvent(function()
    local w = modules.game_bot and modules.game_bot.botWindow
    if not g_settings.getBoolean('spireBotFolded') and w and w.minimize then
      w:minimize()
      g_settings.set('spireBotFolded', true)
      g_settings.save()
    end
  end, 2500)
  -- (polling every creature with g_map.getSpectators crashed the Windows client (heap corruption); cursors now update only when the server sends a skull change)
end

local function onGameEnd()
  pvpLockOn, pvpLockText = false, '' -- a new login starts without a player fight
  SpireJournalUi.hide()
  SpireTasksUi.hide()
  removeEvent(tickEvent)
  removeEvent(cursorEvent)
  destroyUi()
end

-- The built-in bot's Spirebound scripts (M5 and the cavebot report). vBot copies its default config into the player's
-- own folder only the first time, so a player who installed earlier would never get a new script. Every client start
-- refreshes them in each vBot config the player has, and adds them to that config's load order once.
local BOT_SCRIPTS = { 'spirebound_report', 'spirebound_mark', 'spirebound_pvp_guard' }
-- B1 (2026-11-25): this client build hangs for good when a label that wraps its text sits in a hidden bot tab or
-- panel (it has no width, so the wrapping never ends). Switching the bot on froze the client every time. Fix:
-- spirebound_fixes.otui (vBot imports every layout in its vBot folder at start, after its own) redefines vBot's
-- wrapping labels without wrapping, and the cavebot editor's one wrapping label gets a fixed height. Rule for any
-- bot layout we add: no text-wrap on labels in bot tabs.
local EDITOR_OLD = "    text: Double click on action from action list to edit it\n    text-align: center\n    text-auto-resize: true\n    text-wrap: true\n"
local EDITOR_NEW = "    text: Double-click an action to edit it\n    text-align: center\n    height: 14\n"
local function patchEditor(cfg)
  local f = '/bot/' .. cfg .. '/cavebot/editor.otui'
  if not g_resources.fileExists(f) then return end
  local t = g_resources.readFileContents(f):gsub('\r', '')
  local s, e = t:find(EDITOR_OLD, 1, true)
  if s then
    g_resources.writeFileContents(f, t:sub(1, s - 1) .. EDITOR_NEW .. t:sub(e + 1))
  end
end
local function syncBotScripts()
  for _, cfg in ipairs(g_resources.listDirectoryFiles('/bot', false, false) or {}) do
    local loader = '/bot/' .. cfg .. '/_Loader.lua'
    if g_resources.fileExists(loader) and g_resources.directoryExists('/bot/' .. cfg .. '/vBot') then
      for _, name in ipairs(BOT_SCRIPTS) do
        local src = g_resources.readFileContents('/modules/game_spirebound/bot/' .. name .. '.lua')
        local dst = '/bot/' .. cfg .. '/vBot/' .. name .. '.lua'
        if src and src:len() > 0 and (not g_resources.fileExists(dst) or g_resources.readFileContents(dst) ~= src) then
          g_resources.writeFileContents(dst, src)
        end
      end
      local fixes = g_resources.readFileContents('/modules/game_spirebound/bot/spirebound_fixes.otui')
      local fixDst = '/bot/' .. cfg .. '/vBot/spirebound_fixes.otui'
      if fixes and fixes:len() > 0 and (not g_resources.fileExists(fixDst) or g_resources.readFileContents(fixDst) ~= fixes) then
        g_resources.writeFileContents(fixDst, fixes)
      end
      patchEditor(cfg)
      local lt = g_resources.readFileContents(loader)
      -- Q16 / roadmap R15: no automatic attack or spell rotation, no combo helper, no script editor, no pushmax.
      -- The installer removes them from fresh installs; older installs still had them in their own copy.
      if lt then
        local before = lt
        for _, m in ipairs({ '"AttackBot", %-%- last of major modules', '"combo",', '"ingame_editor",', '"pushmax",' }) do
          lt = lt:gsub('\n  ' .. m .. '\r?', '')
        end
        if lt ~= before then
          g_resources.writeFileContents(loader, lt)
        end
      end
      if lt and not lt:find('"spirebound_pvp_guard"', 1, true) then
        if not lt:find('"spirebound_report"', 1, true) then
          lt = lt:gsub('  "cavebot_control_panel"', '  "cavebot_control_panel",\n  "spirebound_report"', 1)
        end
        lt = lt:gsub('  "HealBot",', '  "spirebound_mark",\n  "HealBot",', 1)
        lt = lt:gsub('  "new_healer",', '  "new_healer",\n  "spirebound_mark",', 1)
        lt = lt:gsub('  "eat_food",', '  "spirebound_mark",\n  "eat_food",\n  "spirebound_mark",', 1)
        lt = lt:gsub('  "spirebound_report"', '  "spirebound_mark",\n  "spirebound_report",\n  "spirebound_pvp_guard"', 1)
        g_resources.writeFileContents(loader, lt)
      end
    end
  end
end

function init()
  pcall(syncBotScripts)
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
  g_keyboard.bindKeyDown('J', SpireJournalUi.toggle)
  -- R19: a top-bar button opens the Journal too (its Commands tab sends every chat command with a click)
  pcall(function()
    SpireJournalUi.button = modules.client_topmenu.addRightGameToggleButton('spireJournal', 'Journal (J): quests, secrets, commands',
      '/images/topbuttons/questlog', SpireJournalUi.toggle)
  end)
  connect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd })
  if g_game.isOnline() then
    onGameStart()
  end
end

-- asked by the bot guard (client/modules/game_spirebound/bot/spirebound_pvp_guard.lua): is a player fight on?
function pvpLocked()
  return pvpLockOn
end

function hideJournal()
  SpireJournalUi.hide()
end

function hideTasks()
  SpireTasksUi.hide()
end

function terminate()
  g_keyboard.unbindKeyDown('J')
  if SpireJournalUi.button then
    SpireJournalUi.button:destroy()
    SpireJournalUi.button = nil
  end
  ProtocolGame.unregisterExtendedJSONOpcode(OPCODE)
  if originalOnSkullChange then
    Creature.onSkullChange = originalOnSkullChange
  end
  disconnect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd })
  onGameEnd()
end
