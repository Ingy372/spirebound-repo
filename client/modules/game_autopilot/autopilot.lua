-- Spirebound test autopilot. Plays a test route by itself and writes what happened to a log, so Claude can test a
-- hunting ground without clicking through the client one screenshot at a time.
--
-- Does nothing unless tools/autopilot.py has put a run file at modules/game_autopilot/run.json (never committed).
-- The run file: { "account", "password", "character", "exit": true, "steps": [ ... ] }. Steps:
--   { "do": "jump", "to": [x, y, z] }             test-character jump (/pilot, dev account only)
--   { "do": "heal" }                              full health and mana (/pilot heal)
--   { "do": "walk", "to": [x, y, z], "fight": true, "arrive_z": 8, "timeout": 90 }
--                                                 walk there, fighting whatever comes close on the way
--   { "do": "hunt", "seconds": 60, "radius": 7 }  attack the nearest monster in sight, again and again
--   { "do": "wait", "seconds": 5 }
--   { "do": "shot", "name": "yard" }              screenshot
--   { "do": "say", "text": "!hunt" }
--   { "do": "npc", "text": "trade" }              after "hi": talk to the NPC in the NPCs channel
--   { "do": "rune", "id": 3180, "ahead": 2 }        (PvP tests) use a rune on the tile ahead
--   { "do": "use", "at": [x, y, z] }              use the thing on top of a nearby tile (a stone, a lever)
--   { "do": "botguard" }                          (M5) log the player-fight lock and the bot guard's state
--   { "do": "bot", "on": true }                   (M5) switch the built-in bot on (or off) for this character
--   { "do": "react", "text": "quickstep", "seconds": 40 }  (PvP tests) say it whenever you get held
--   { "do": "cast", "text": "inferno core", "target": true, "face": "target", "shots": [0.25, 0.75], "gap": 2.3 }
--                                                 (spell tests) target the nearest monster without chasing it if
--                                                 "target", say the words, take screenshots that many seconds after,
--                                                 move on after "gap" seconds; every server message is logged;
--                                                 "target": "player" targets the nearest other player instead
-- The log (autopilot_log.txt in the client's settings folder) has a line per event, a sample every 2 seconds and a
-- summary per step: monsters in sight, monsters next to you, damage taken, kills, potions.

Autopilot = {}

local RUN = '/game_autopilot/run.json'
local LOG = '/autopilot_log.txt'
local TICK = 250 -- ms
local stepXp
local POTION = 266 -- health potion
local MANA_POTION = 268
local NEAR = 2 -- a monster this close (tiles) gets fought on a walk

local plan, lines, t0
local idx, step, stepT, stepData
local tickEvent, loginEvent
local st, total
local lastPotion, lastSample, lastHp = 0, 0, nil
-- the fight kit (Jay, 2026-11-25: the pilot only swung its weapon, so kill speed and mana use were never measured):
-- what this character can cast, from "/pilot fightkit"; asked at login and after every level change
local kit, kitAsked, lastAttackCast, lastHealCast, lastManaPotion = nil, 0, 0, 0, 0
local ready = {}
local finished = false

local function now()
    return g_clock.millis() / 1000
end

local function flush()
    g_resources.writeFileContents(LOG, table.concat(lines, '\n') .. '\n')
end

local function log(s)
    lines[#lines + 1] = string.format('%7.1f  %s', now() - t0, s)
    flush()
end

local function fmtPos(p)
    return p and string.format('(%d, %d, %d)', p.x, p.y, p.z) or '(?)'
end

local function toPos(t)
    return { x = t[1], y = t[2], z = t[3] }
end

local function dist(a, b)
    return math.max(math.abs(a.x - b.x), math.abs(a.y - b.y))
end

local function newStats()
    return { samples = 0, seenSum = 0, seenMax = 0, nextMax = 0, nextSum = 0, dmg = 0, kills = 0, potions = 0, minHp = 100,
        casts = 0, mana = 0, manaPots = 0 }
end

local function monsters(player)
    local pos = player:getPosition()
    local out = {}
    for _, c in ipairs(g_map.getSpectators(pos, false) or {}) do
        local p = c:getPosition()
        local mine = (c.getMasterId and c:getMasterId() == player:getId())
            or (CreatureTypeSummonOwn and c.getType and c:getType() == CreatureTypeSummonOwn)
        if c:isMonster() and not mine and p and p.z == pos.z and c:getHealthPercent() > 0 then -- (never your own companion)
            out[#out + 1] = { c = c, d = dist(p, pos) }
        end
    end
    table.sort(out, function(a, b) return a.d < b.d end)
    return out
end

-- other players in sight, nearest first (PvP spell tests)
local function players(player)
    local pos = player:getPosition()
    local out = {}
    for _, c in ipairs(g_map.getSpectators(pos, false) or {}) do
        local p = c:getPosition()
        if c:isPlayer() and not c:isLocalPlayer() and p and p.z == pos.z then
            out[#out + 1] = { c = c, d = dist(p, pos) }
        end
    end
    table.sort(out, function(a, b) return a.d < b.d end)
    return out
end

local function summary(s, title)
    local avg = s.samples > 0 and s.seenSum / s.samples or 0
    local avgNext = s.samples > 0 and s.nextSum / s.samples or 0
    return string.format('%s: in sight max %d (avg %.1f), next to you max %d (avg %.1f), damage taken %d, kills %d, potions %d, lowest health %d%%, spells %d, mana spent %d, mana potions %d',
        title, s.seenMax, avg, s.nextMax, avgNext, s.dmg, s.kills, s.potions, s.minHp, s.casts, s.mana, s.manaPots)
end

local function finish(reason)
    if finished then return end
    finished = true
    if step then
        log('== step ' .. idx .. ' ended early (' .. reason .. ')')
        log(summary(st, '   step ' .. idx))
    end
    log(summary(total, 'WHOLE RUN'))
    log('DONE ' .. reason)
    if tickEvent then removeEvent(tickEvent) tickEvent = nil end
    -- a character still in a fight stays in the game after its client closes (and spoils the next test run), so test
    -- characters first jump home to Hearthgate (a safe zone) and log out from there
    local name = g_game.isOnline() and g_game.getCharacterName() or ''
    local home = plan.home ~= false and (name:find('^Pilot ') or name:find('^Spell '))
    if home then g_game.talk('/pilot jump 1225, 1279, 7') end
    scheduleEvent(function() if g_game.isOnline() then g_game.safeLogout() end end, home and 1500 or 0)
    if plan.exit ~= false then
        scheduleEvent(function() g_app.exit() end, home and 4500 or 3000)
    end
end

local function describe(s)
    local d = s['do']
    if s.to then d = d .. ' to ' .. fmtPos(toPos(s.to)) end
    if s.seconds then d = d .. ' for ' .. s.seconds .. 's' end
    if s.name then d = d .. ' "' .. s.name .. '"' end
    if s.text then d = d .. ' "' .. s.text .. '"' end
    return d
end

-- ---------------------------------------------------------------- live mode (tools/grok_tester.py)
-- With "live": true in the run file, the steps are not a fixed route: when the queued steps run out, the client writes
-- autopilot_state.json (and a screenshot) to its settings folder and waits for autopilot_cmd.json from the script,
-- { "seq": n, "steps": [...] } or { "seq": n, "stop": true }. The script decides each move (a Grok play tester).
local CMD, STATE = '/autopilot_cmd.json', '/autopilot_state.json'
local liveSeq, recent = 0, {}
local diedCount, diedLive, foodEaten, reconnecting = 0, false, 0, false

local function remember(s)
    recent[#recent + 1] = s
    if #recent > 40 then table.remove(recent, 1) end
end

local function itemName(it)
    local ok, md = pcall(function() return it:getMarketData() end)
    if ok and md and md.name and md.name ~= '' then return md.name end
    return 'item ' .. it:getId()
end

local function writeState(reason)
    local p = g_game.getLocalPlayer()
    if not p then return end
    local pos = p:getPosition()
    local around = {}
    for _, c in ipairs(g_map.getSpectators(pos, false) or {}) do
        if c ~= p then
            local cp = c:getPosition()
            around[#around + 1] = { name = c:getName(), kind = c:isMonster() and 'monster' or (c:isNpc() and 'npc' or 'player'),
                dx = cp.x - pos.x, dy = cp.y - pos.y, dz = cp.z - pos.z, health = c:getHealthPercent() }
        end
    end
    local bag = {}
    local open = 0
    for _ in pairs(g_game.getContainers()) do open = open + 1 end
    if open == 0 then -- a tester needs to see its potions and loot: open the backpack (shows from the next state on)
        local bp = p:getInventoryItem(InventorySlotBack)
        if bp then g_game.open(bp, nil) end
    end
    for _, c in pairs(g_game.getContainers()) do
        for _, it in ipairs(c:getItems()) do
            bag[#bag + 1] = itemName(it) .. (it:getCount() > 1 and (' x' .. it:getCount()) or '')
        end
    end
    local worn = {}
    for slot = 1, 11 do
        local it = p:getInventoryItem(slot)
        if it then worn[#worn + 1] = itemName(it) end
    end
    local shot = string.format('autopilot_live_%s%d.png', plan.tag and (plan.tag .. '_') or '', liveSeq)
    g_app.doScreenshot(shot)
    local state = { seq = liveSeq, reason = reason, x = pos.x, y = pos.y, z = pos.z,
        health = p:getHealth(), maxHealth = p:getMaxHealth(), mana = p:getMana(), maxMana = p:getMaxMana(),
        level = p:getLevel(), experience = p:getExperience(), vocation = p:getVocation(), soul = p:getSoul(),
        attacking = g_game.isAttacking(), around = around, backpack = bag, worn = worn, messages = recent, screenshot = shot,
        shield = p:getShield(), died = diedCount, food = foodEaten }
    recent = {}
    g_resources.writeFileContents(STATE, json.encode(state))
    log('live: state ' .. liveSeq .. ' written (' .. tostring(reason) .. ')')
end

local function nextStep()
    if step then
        log(string.format('== step %d done in %.0fs', idx, now() - stepT))
        log(summary(st, '   step ' .. idx))
        local lp = g_game.getLocalPlayer()
        if lp and stepXp then -- (playthroughs) experience per step, for experience per hour
            log(string.format('   xp step %d: +%d experience, level %d', idx, lp:getExperience() - stepXp, lp:getLevel()))
        end
    end
    stepXp = g_game.getLocalPlayer() and g_game.getLocalPlayer():getExperience()
    idx = idx + 1
    step = plan.steps[idx]
    if not step and plan.live then
        writeState('ready')
        step = { ['do'] = 'live_wait' }
    end
    if not step then
        return finish('route complete')
    end
    stepT, st, stepData = now(), newStats(), {}
    log('== step ' .. idx .. ': ' .. describe(step) .. (step.note and ('  [' .. step.note .. ']') or ''))
end

-- fight the nearest monster within `radius`; true while busy fighting
local function fight(player, radius)
    if g_game.isAttacking() then
        local t = g_game.getAttackingCreature()
        if t and t:getHealthPercent() > 0 then return true end
    end
    local list = monsters(player)
    if list[1] and list[1].d <= radius then
        -- casters (Arcanist, Mystic) hold their ground and cast from range instead of walking into melee
        local voc = player:getVocation()
        local caster = voc == 1 or voc == 2 or voc == 5 or voc == 6
        g_game.setChaseMode((caster or plan.ranged) and DontChase or ChaseOpponent)
        g_game.attack(list[1].c)
        return true
    end
    return false
end

local handlers = {}
local charlistPending = false

-- G12b: log out to the character list (the client asks the login service again) and write down what the list shows
-- for this character; the run ends there. { "do": "charlist" } (last step)
function handlers.charlist()
    if not stepData.sent then
        stepData.sent = true
        charlistPending = true
        log('charlist: logging out to the character list')
        g_game.safeLogout()
    end
end

local function readCharlist(tries)
    local chars = rootWidget:recursiveGetChildById('charactersWindow')
    local list = chars and chars:isVisible() and chars:getChildById('characters')
    if not list then
        if (tries or 0) < 20 then return scheduleEvent(function() readCharlist((tries or 0) + 1) end, 500) end
        log('charlist: the character list never showed')
        return finish('route complete')
    end
    for _, w in ipairs(list:getChildren()) do
        if w.characterName == plan.character then
            local out = {}
            local function texts(x)
                local t = x.getText and x:getText()
                if t and t ~= '' then out[#out + 1] = t end
                for _, c in ipairs(x:getChildren()) do texts(c) end
            end
            texts(w)
            log('charlist ' .. plan.character .. ': ' .. table.concat(out, ' | '))
        end
    end
    finish('route complete')
end

function handlers.jump(player)
    local to = toPos(step.to)
    if not stepData.sent then
        g_game.talk(string.format('/pilot jump %d, %d, %d', to.x, to.y, to.z))
        stepData.sent = true
    elseif dist(player:getPosition(), to) == 0 and player:getPosition().z == to.z then
        nextStep()
    elseif now() - stepT > 5 then
        log('could not jump (is this a Pilot character on the dev account?)')
        finish('jump failed')
    end
end

-- show a chat tab, e.g. { "do": "console", "tab": "Server Log" } (to screenshot what the game wrote there)
function handlers.console()
    local c = modules.game_console
    local tab = c and c.getTab and c.getTab(step.tab or 'Server Log')
    if tab and c.consoleTabBar then
        c.consoleTabBar:selectTab(tab)
        log('console tab: ' .. tostring(step.tab or 'Server Log'))
    else
        log('console tab not found: ' .. tostring(step.tab))
    end
    nextStep()
end

-- drink a health potion on yourself, as a player does with "Use with..." (the yard's potion gate)
function handlers.drink(player)
    if not stepData.sent then
        g_game.useInventoryItemWith(step.id or POTION, player)
        log('drank item ' .. tostring(step.id or POTION))
        stepData.sent = now()
    elseif now() - stepData.sent > 1 then
        nextStep()
    end
end

function handlers.heal()
    if not stepData.sent then
        g_game.talk('/pilot heal')
        stepData.sent = true
    elseif now() - stepT > 1 then
        nextStep()
    end
end

function handlers.say()
    if not stepData.sent then
        g_game.talk(step.text)
        stepData.sent = true
    elseif now() - stepT > 1.5 then
        nextStep()
    end
end

-- talk to an NPC after "hi": Canary's NPCs only listen to the NPCs channel once a conversation has started
function handlers.npc()
    if not stepData.sent then
        -- NPCs only listen within 3 tiles and some wander: wait (up to 15 s) until the nearest NPC is in earshot
        local me = g_game.getLocalPlayer():getPosition()
        local best
        for _, c in ipairs(g_map.getSpectators(me, false)) do
            if c:isNpc() then
                local p = c:getPosition()
                local d = math.max(math.abs(p.x - me.x), math.abs(p.y - me.y))
                if not best or d < best then best = d end
            end
        end
        if best and best > 3 and now() - stepT < 15 then return end
        if best and best > 3 then log('npc: nearest NPC is ' .. best .. ' tiles away; talking anyway') end
        g_game.talkChannel(MessageModes.NpcTo, 0, step.text)
        stepData.sent = now()
    elseif now() - stepData.sent > 1.5 then
        nextStep()
    end
end

-- use what lies on a map tile (open a chest): { "do": "use", "at": [x, y, z] }
function handlers.use()
    if not stepData.sent then
        local p = toPos(step.at)
        local tile = g_map.getTile(p)
        local thing = tile and tile:getTopUseThing()
        if thing then
            g_game.use(thing)
            log('use: ' .. fmtPos(p))
        else
            log('use: nothing to use at ' .. fmtPos(p))
        end
        stepData.sent = now()
    elseif now() - stepData.sent > 2 then
        nextStep()
    end
end

-- wear an item from the backpack: { "do": "equip", "id": 3350, "slot": "left" } (left right ammo body head legs feet)
function handlers.equip(player)
    if stepData.done then
        if now() - stepT > 1.5 then nextStep() end
        return
    end
    for _, c in pairs(g_game.getContainers()) do
        for _, it in ipairs(c:getItems()) do
            if it:getId() == step.id then
                local slots = { left = InventorySlotLeft, right = InventorySlotRight, ammo = InventorySlotAmmo,
                    body = InventorySlotBody, head = InventorySlotHead, legs = InventorySlotLeg, feet = InventorySlotFeet }
                local slot = slots[step.slot or 'left'] or InventorySlotLeft
                g_game.move(it, { x = 65535, y = slot, z = 0 }, it:getCount())
                log('equip: moved item ' .. step.id .. ' to the ' .. (step.slot or 'left') .. ' hand')
                stepData.done = true
                return
            end
        end
    end
    if not stepData.opened then
        local bp = player:getInventoryItem(InventorySlotBack)
        if bp then g_game.open(bp, nil) end
        stepData.opened = true
    elseif now() - stepT > 4 then
        log('equip: item ' .. step.id .. ' not found')
        nextStep()
    end
end

function handlers.cast(player)
    if not stepData.sent then
        if step.target then
            local list = step.target == 'player' and players(player) or monsters(player)
            if step.target == 'player' then g_game.setSafeFight(false) end -- secure mode off, like a player who means it
            if list[1] then
                g_game.setChaseMode(DontChase)
                if g_game.getAttackingCreature() ~= list[1].c then g_game.attack(list[1].c) end
            else
                log('cast: no monster to target')
            end
        end
        if step.dir then -- face a fixed way first: "north", "east", "south", "west"
            g_game.turn(({ north = North, east = East, south = South, west = West })[step.dir])
        end
        if step.face then -- "target": turn toward the nearest monster (waves, beams); "away": turn away (dashes)
            local list = step.target == 'player' and players(player) or monsters(player)
            if list[1] then
                local a, b = player:getPosition(), list[1].c:getPosition()
                local dx, dy = b.x - a.x, b.y - a.y
                if step.face == 'away' then dx, dy = -dx, -dy end
                local dir
                if math.abs(dx) > math.abs(dy) then dir = dx > 0 and East or West else dir = dy > 0 and South or North end
                g_game.turn(dir)
            end
        end
        stepData.sent, stepData.shot = now(), 1
        g_game.talk(step.text)
        return
    end
    local shots = step.shots or {}
    local due = shots[stepData.shot]
    if due and now() - stepData.sent >= due then
        local name = 'autopilot_' .. (step.name or idx) .. '_' .. stepData.shot .. '.png'
        g_app.doScreenshot(name)
        log('screenshot ' .. name)
        stepData.shot = stepData.shot + 1
    elseif not due and now() - stepData.sent >= (step.gap or 2.2) then
        nextStep()
    end
end

-- (PvP tests) use a rune from the backpack on the tile `ahead` tiles in front of you
function handlers.rune(player)
    if not stepData.sent then
        local pos = player:getPosition()
        local d = player:getDirection()
        local dx = (d == East and 1) or (d == West and -1) or 0
        local dy = (d == South and 1) or (d == North and -1) or 0
        local to = { x = pos.x + dx * (step.ahead or 2), y = pos.y + dy * (step.ahead or 2), z = pos.z }
        local tile = g_map.getTile(to)
        local thing = tile and tile:getTopUseThing()
        if thing then
            g_game.useInventoryItemWith(step.id, thing)
            log('rune ' .. step.id .. ' used at ' .. fmtPos(to))
        else
            log('rune: no tile at ' .. fmtPos(to))
        end
        stepData.sent = now()
    elseif now() - stepData.sent > (step.gap or 2) then
        nextStep()
    end
end

-- (AD5 tests) use an item in an open backpack, as a player double-clicks it: read a treasure map
-- { "do": "useitem", "id": 5706 }
function handlers.useitem(player)
    if not stepData.sent then
        local done = false
        for _, c in pairs(g_game.getContainers()) do
            for _, it in ipairs(c:getItems()) do
                if not done and it:getId() == step.id then
                    g_game.use(it)
                    done = true
                end
            end
        end
        log(done and ('used item ' .. step.id) or ('useitem: no item ' .. step.id .. ' in an open container'))
        stepData.sent = now()
    elseif now() - stepData.sent > (step.gap or 2) then
        nextStep()
    end
end

-- (AD1 tests) look at a creature on screen, as a player shift-clicks it: { "do": "look", "name": "Pilot Bo" }
function handlers.look(player)
    if not stepData.sent then
        local found = nil
        for _, c in ipairs(g_map.getSpectators(player:getPosition(), false) or {}) do
            if not found and c:getName() == step.name then
                found = c
            end
        end
        if found then
            g_game.look(found)
            log('looked at ' .. step.name)
        else
            log('look: no ' .. tostring(step.name) .. ' on screen')
        end
        stepData.sent = now()
    elseif now() - stepData.sent > (step.gap or 2) then
        nextStep()
    end
end

-- use the thing on top of a tile next to you ("at": [x, y, z]): read a stone, pull a lever, open a chest
function handlers.use(player)
    if not stepData.sent then
        if modules.game_textwindow and modules.game_textwindow.destroyWindows then
            modules.game_textwindow.destroyWindows() -- a stone's text from the last use would sit on top
        end
        local to = { x = step.at[1], y = step.at[2], z = step.at[3] }
        local tile = g_map.getTile(to)
        local thing = tile and tile:getTopUseThing()
        if thing then
            g_game.use(thing)
            log('used ' .. thing:getId() .. ' at ' .. fmtPos(to))
        else
            log('use: nothing at ' .. fmtPos(to))
        end
        stepData.sent = now()
    elseif now() - stepData.sent > (step.gap or 2) then
        nextStep()
    end
end

-- (PvP tests) for `seconds`, say `text` the moment you are held (paralysed or rooted): how a player counters a root
function handlers.react(player)
    stepData.last = stepData.last or 0
    if PlayerStates and bit.band(player:getStates(), PlayerStates.Paralyze) > 0 and now() - stepData.last > 2.2 then
        g_game.talk(step.text)
        stepData.last = now()
        log('held: said ' .. step.text)
    end
    if now() - stepT >= (step.seconds or 30) then nextStep() end
end

-- open the spellbook window, log what it lists, screenshot it, close it
function handlers.spellbook()
    local m = modules.game_spelllist
    if not stepData.sent then
        if m and m.toggle then m.toggle() end
        stepData.sent = now()
    elseif now() - stepData.sent > 1.5 and not stepData.shot then
        local list, shown = m and m.spellList, {}
        for _, child in ipairs(list and list:getChildren() or {}) do
            if child:isVisible() then table.insert(shown, child:getId()) end
        end
        log('spellbook: ' .. #shown .. ' shown: ' .. table.concat(shown, ', ', 1, math.min(#shown, 12)))
        g_app.doScreenshot('autopilot_' .. (step.name or 'spellbook') .. '.png')
        stepData.shot = now()
    elseif stepData.shot and now() - stepData.shot > 1 then
        if m and m.toggle then m.toggle() end
        nextStep()
    end
end

-- write down where every monster in view stands, every 2 seconds (S5: does a pack keep together round its leader?)
-- { "do": "watch", "seconds": 30 }
function handlers.watch(player)
    if not stepData.last or now() - stepData.last >= 2 then
        stepData.last = now()
        local pos, parts = player:getPosition(), {}
        for _, m in ipairs(monsters(player)) do
            local p = m.c:getPosition()
            parts[#parts + 1] = string.format('%s (%+d,%+d)', m.c:getName(), p.x - pos.x, p.y - pos.y)
        end
        log('watch: ' .. (#parts > 0 and table.concat(parts, ', ') or 'no monsters in view'))
    end
    if now() - stepT >= (step.seconds or 10) then nextStep() end
end

function handlers.wait()
    if now() - stepT >= (step.seconds or 1) then nextStep() end
end

-- write down what is worn in every slot and what the backpack holds: { "do": "inventory" }
-- (Grok session 3: a new Ranger had no arrows; the check must see the real equipment, not a test kit)
function handlers.inventory(player)
    if not stepData.opened then
        local bp = player:getInventoryItem(InventorySlotBack)
        if bp then g_game.open(bp, nil) end
        stepData.opened = true
        return
    end
    if now() - stepT < 1.5 then return end
    local names = { [InventorySlotHead] = 'head', [InventorySlotNeck] = 'neck', [InventorySlotBack] = 'back',
        [InventorySlotBody] = 'body', [InventorySlotRight] = 'right hand', [InventorySlotLeft] = 'left hand',
        [InventorySlotLeg] = 'legs', [InventorySlotFeet] = 'feet', [InventorySlotFinger] = 'finger', [InventorySlotAmmo] = 'ammo' }
    for slot = InventorySlotHead, InventorySlotAmmo do
        local it = player:getInventoryItem(slot)
        log(string.format('inventory: %s = %s', names[slot] or slot, it and (it:getId() .. ' x' .. it:getCount()) or 'empty'))
    end
    for _, c in pairs(g_game.getContainers()) do
        local ids = {}
        for _, it in ipairs(c:getItems()) do ids[#ids + 1] = it:getId() .. ' x' .. it:getCount() end
        log('inventory: container ' .. (c:getName() or '?') .. ' holds ' .. table.concat(ids, ', '))
    end
    nextStep()
end

-- S4: form a party the way players do (the right-click menu's invite / join / share experience):
--   leader:  { "do": "party", "invite": ["Pilot Ranger", "Pilot Mystic"], "share": true, "seconds": 40 }
--   member:  { "do": "party", "join": "Pilot Vanguard", "seconds": 40 }
-- Retries every 2 seconds until done or out of time; logs who is in the party (the shields over their heads).
local function namedInSight(player, name)
    for _, e in ipairs(players(player)) do
        if e.c:getName() == name then return e.c end
    end
    return nil
end

function handlers.party(player)
    local s = step
    if now() - (stepData.last or 0) < 2 then return end
    stepData.last = now()
    local done = true
    if s.invite then
        for _, name in ipairs(s.invite) do
            local c = namedInSight(player, name)
            local shield = c and c:getShield() or 0
            stepData.joined = stepData.joined or {}
            if c and (shield == ShieldBlue or shield == ShieldBlueSharedExp or shield == ShieldBlueNoSharedExpBlink
                    or shield == ShieldBlueNoSharedExp) then
                stepData.joined[name] = true -- once joined, a member may walk out of sight (S4: they head into the cave)
            end
            if stepData.joined[name] then
                -- already in the party
            elseif not c or (shield ~= ShieldBlue and shield ~= ShieldBlueSharedExp and shield ~= ShieldBlueNoSharedExpBlink
                    and shield ~= ShieldBlueNoSharedExp) then
                done = false
                if c and shield ~= ShieldWhiteBlue then
                    g_game.partyInvite(c:getId())
                    log('party: invited ' .. name)
                end
            end
        end
        if done and s.share and not stepData.shared then
            g_game.partyShareExperience(true)
            stepData.shared = true
            log('party: shared experience switched on')
        end
    end
    if s.join then
        local c = namedInSight(player, s.join)
        local mine = player:getShield()
        if mine ~= ShieldBlue and mine ~= ShieldBlueSharedExp and mine ~= ShieldBlueNoSharedExpBlink and mine ~= ShieldBlueNoSharedExp then
            done = false
            if c and c:getShield() == ShieldWhiteYellow then
                g_game.partyJoin(c:getId())
                log('party: joined ' .. s.join .. "'s party")
            end
        end
    end
    local names = {}
    for _, e in ipairs(players(player)) do names[#names + 1] = e.c:getName() .. '=' .. e.c:getShield() end
    log('party: my shield ' .. player:getShield() .. '; others ' .. table.concat(names, ', '))
    if done or now() - stepT > (s.seconds or 40) then
        log(done and 'party: formed' or 'party: NOT formed in time')
        nextStep()
    end
end

-- M5: switch the built-in bot (vBot) on or off for this character: { "do": "bot", "on": true }
function handlers.bot(player)
    if not stepData.done then
        local settings = g_settings.getNode('bot') or {}
        local index = g_game.getCharacterName() .. '_' .. g_game.getClientVersion()
        settings[index] = { enabled = step.on ~= false, config = step.config or 'vBot_4.8' }
        g_settings.setNode('bot', settings)
        g_settings.save()
        stepData.done = true
        local ok, err = true, nil
        if modules.game_bot and modules.game_bot.refresh then ok, err = pcall(modules.game_bot.refresh) end
        log('bot: ' .. ((step.on ~= false) and 'on' or 'off') .. (ok and '' or (' (bot start error: ' .. tostring(err) .. ')')))
        return
    end
    if now() - stepT >= 3 then nextStep() end
end

-- M5: is a player fight on, is the bot guard installed, and what does it report? { "do": "botguard" }
function handlers.botguard(player)
    local sb = modules.game_spirebound
    log('botguard: player fight = ' .. tostring(sb and sb.pvpLocked and sb.pvpLocked()))
    local lt = g_resources.fileExists('/bot/vBot_4.8/_Loader.lua') and g_resources.readFileContents('/bot/vBot_4.8/_Loader.lua') or ''
    log('botguard: guard in the bot load order = ' .. tostring(lt:find('spirebound_pvp_guard', 1, true) ~= nil)
        .. ', bookmarks = ' .. select(2, lt:gsub('"spirebound_mark"', '')))
    local g = sb and sb.botGuard
    if g then
        log(string.format('botguard: bot running, %d of %d helper jobs guarded, %d bookmarks, fight seen by the bot = %s',
            g.paused or 0, g.jobs or 0, g.marks or 0, tostring(g.locked)))
        log(string.format('botguard: cavebot on = %s, paused job runs held back = %d, bot casts during fights = %d%s',
            tostring(g.cavebotOn), g.held or 0, g.healsInFight or 0, g.lastWords and (' (last: "' .. g.lastWords .. '")') or ''))
        log(string.format('botguard: cavebot route has %d steps, now at "%s"', g.caveSteps or 0, tostring(g.caveAt)))
    else
        log('botguard: the bot is not running (or its guard has not loaded)')
    end
    nextStep()
end

function handlers.live_wait()
    if stepData.polled and now() - stepData.polled < 0.75 then return end
    stepData.polled = now()
    if not g_resources.fileExists(CMD) then return end
    local ok, cmd = pcall(json.decode, g_resources.readFileContents(CMD))
    if not ok or type(cmd) ~= 'table' or (cmd.seq or 0) <= liveSeq then return end
    liveSeq = cmd.seq
    if cmd.stop then return finish('stopped by the tester') end
    log('live: command ' .. liveSeq .. ' with ' .. #(cmd.steps or {}) .. ' steps')
    plan.steps, idx, step = cmd.steps or {}, 0, nil
    nextStep()
end

function handlers.shot()
    local name = 'autopilot_' .. (step.name or idx) .. '.png'
    g_app.doScreenshot(name)
    log('screenshot ' .. name)
    nextStep()
end

function handlers.hunt(player)
    if not fight(player, step.radius or 7) and not stepData.idleSince then
        stepData.idleSince = now()
    elseif g_game.isAttacking() then
        stepData.idleSince = nil
    end
    if now() - stepT >= (step.seconds or 30) then
        if g_game.isAttacking() then g_game.cancelAttack() end
        nextStep()
    end
end

-- (party playtests) stay with the leader and fight what is near the leader:
-- { "do": "assist", "leader": "Pilot Blade", "seconds": 120, "radius": 4, "leash": 5, "ranged": true }
function handlers.assist(player)
    local leader = namedInSight(player, step.leader)
    local me = player:getPosition()
    local radius, leash = step.radius or 4, step.leash or 5
    if leader and leader:getPosition().z == me.z then
        local lp = leader:getPosition()
        local cur = g_game.getAttackingCreature()
        local near = dist(me, lp) <= leash
        if cur and cur:getHealthPercent() > 0 and near and dist(cur:getPosition(), lp) <= radius + 2 then
            -- keep fighting this one
        else
            local best, bd
            for _, m in ipairs(monsters(player)) do
                local d = dist(m.c:getPosition(), lp)
                if d <= radius and (not bd or d < bd) then best, bd = m.c, d end
            end
            if best and near then
                g_game.setChaseMode(step.ranged and DontChase or ChaseOpponent)
                g_game.attack(best)
            else
                if g_game.isAttacking() then g_game.cancelAttack() end
                if dist(me, lp) > 2 and g_game.getFollowingCreature() ~= leader then g_game.follow(leader) end
            end
        end
    else
        if not stepData.lost then
            log('assist: ' .. tostring(step.leader) .. ' is not in sight on this floor')
            stepData.lost = true
        end
        fight(player, radius)
    end
    if now() - stepT >= (step.seconds or 60) then
        pcall(function() g_game.cancelAttackAndFollow() end)
        nextStep()
    end
end

-- (party playtests) pick up items lying next to you into the backpack: { "do": "pickup", "ids": [3359] } (no ids: anything)
function handlers.pickup(player)
    if not stepData.t then
        stepData.t = now()
        local pos = player:getPosition()
        for dx = -1, 1 do
            for dy = -1, 1 do
                local tile = g_map.getTile({ x = pos.x + dx, y = pos.y + dy, z = pos.z })
                local thing = tile and tile:getTopMoveThing()
                if thing and thing:isItem() and (not step.ids or #step.ids == 0 or table.contains(step.ids, thing:getId())) then
                    g_game.move(thing, { x = 65535, y = 64, z = 0 }, math.max(1, thing:getCount()))
                    log('picked up item ' .. thing:getId() .. ' at ' .. fmtPos(tile:getPosition()))
                    remember('picked up item ' .. thing:getId())
                end
            end
        end
        return
    end
    if now() - stepData.t > 1.5 then nextStep() end
end

-- (party playtests) drop junk on the floor under you, as a player does: { "do": "drop", "ids": [3577] }
function handlers.drop(player)
    if not stepData.t then
        stepData.t = now()
        local pos = player:getPosition()
        for _, c in pairs(g_game.getContainers()) do
            for _, it in ipairs(c:getItems()) do
                for _, id in ipairs(step.ids or {}) do
                    if it:getId() == id then
                        g_game.move(it, pos, math.max(1, it:getCount()))
                        log('dropped item ' .. id .. ' x' .. it:getCount())
                    end
                end
            end
        end
        return
    end
    if now() - stepData.t > 1.5 then nextStep() end
end

-- (FD2 tests) use an item from the backpack on a map tile, as a player does with "Use with": a shovel on a truffle spot
-- { "do": "usewith", "id": 3457, "at": [x, y, z] }
function handlers.usewith(player)
    if not stepData.sent then
        local tile = g_map.getTile({ x = step.at[1], y = step.at[2], z = step.at[3] })
        local target = tile and tile:getTopUseThing()
        local done = false
        for _, c in pairs(g_game.getContainers()) do
            for _, it in ipairs(c:getItems()) do
                if not done and target and it:getId() == step.id then
                    g_game.useWith(it, target)
                    done = true
                end
            end
        end
        log(done and ('used item ' .. step.id .. ' on ' .. table.concat(step.at, ',')) or ('usewith: no item or no tile'))
        stepData.sent = now()
    elseif now() - stepData.sent > (step.gap or 2) then
        nextStep()
    end
end

-- (FD4/FD5 tests) drag an item from the backpack onto a map tile, as a player does (food on a fire, coins on the
-- Works Board): { "do": "throw", "id": 3582, "at": [x, y, z], "count": 1 }
function handlers.throw(player)
    if not stepData.t then
        stepData.t = now()
        local to = { x = step.at[1], y = step.at[2], z = step.at[3] }
        for _, c in pairs(g_game.getContainers()) do
            for _, it in ipairs(c:getItems()) do
                if it:getId() == step.id and not stepData.done then
                    stepData.done = true
                    local n = math.min(step.count or it:getCount(), math.max(1, it:getCount()))
                    g_game.move(it, to, n)
                    log('threw item ' .. step.id .. ' x' .. n .. ' to ' .. to.x .. ',' .. to.y .. ',' .. to.z)
                end
            end
        end
        if not stepData.done then log('throw: no item ' .. step.id .. ' in the backpack') end
        return
    end
    if now() - stepData.t > 1.5 then nextStep() end
end

-- (party playtests) buy and sell at an NPC's trade window, as a player does:
-- { "do": "trade", "buy": [["health potion", 50]], "sell": ["rat tail"] }   "sell": ["*"] sells all loot the NPC buys
-- (never potions, food, ammunition or what you wear); walk next to the NPC first
local FOOD = { [3577] = true, [3578] = true, [3582] = true, [3585] = true, [3586] = true, [3587] = true, [3588] = true,
    [3589] = true, [3590] = true, [3591] = true, [3592] = true, [3593] = true, [3595] = true, [3600] = true, [3601] = true,
    [3606] = true, [3607] = true, [3725] = true }
local tradeList
local KEEP = { [266] = true, [268] = true, [236] = true, [237] = true, [3447] = true, [3446] = true, [3448] = true }
local function onOpenTrade(...)
    for _, a in ipairs({ ... }) do
        if type(a) == 'table' then tradeList = a end
    end
end
local function bagCount(id)
    local n = 0
    for _, c in pairs(g_game.getContainers()) do
        for _, it in ipairs(c:getItems()) do
            if it:getId() == id then n = n + math.max(1, it:getCount()) end
        end
    end
    return n
end
function handlers.trade(player)
    if not stepData.t0 then
        stepData.t0, tradeList = now(), nil
        g_game.talk('hi')
        return
    end
    if not stepData.asked and now() - stepData.t0 > 1.5 then
        stepData.asked = true
        g_game.talkChannel(MessageModes.NpcTo, 0, 'trade')
        return
    end
    if not tradeList then
        if now() - stepData.t0 > 8 then
            log('trade: no trade window opened')
            nextStep()
        end
        return
    end
    if stepData.done then
        if now() - stepData.done > 2 then
            pcall(function() g_game.closeNpcTrade() end)
            g_game.talkChannel(MessageModes.NpcTo, 0, 'bye')
            nextStep()
        end
        return
    end
    -- one trade action a second: the server answers "You are exhausted" to a sell and a buy in the same moment
    if not stepData.queue then
        local q = {}
        for _, e in ipairs(step.sell or {}) do
            for _, it in pairs(tradeList) do
                local id = it[1] and it[1]:getId()
                if id and (it[5] or 0) > 0 and ((e == '*' and not KEEP[id] and not FOOD[id]) or it[2]:lower() == e:lower()) then
                    local n = math.min(bagCount(id), 100)
                    if n > 0 then
                        q[#q + 1] = function()
                            g_game.sellItem(it[1], n, true)
                            log(string.format('trade: sold %d %s at %d each', n, it[2], it[5]))
                            remember(string.format('sold %d %s for %d gold', n, it[2], it[5] * n))
                        end
                    end
                end
            end
        end
        for _, b in ipairs(step.buy or {}) do
            local name, found = b[1]:lower(), nil
            for _, it in pairs(tradeList) do
                if it[2]:lower() == name and (it[4] or 0) > 0 then found = it end
            end
            if found then
                local left = b[2]
                while left > 0 do
                    local k = math.min(left, 100)
                    q[#q + 1] = function()
                        g_game.buyItem(found[1], k, step.ignoreCap == true, false)
                        log(string.format('trade: bought %d %s at %d each', k, found[2], found[4]))
                        remember(string.format('bought %d %s for %d gold', k, found[2], k * found[4]))
                    end
                    left = left - k
                end
            else
                local names = {}
                for _, it in pairs(tradeList) do
                    if (it[4] or 0) > 0 then names[#names + 1] = it[2] .. ' ' .. it[4] end
                end
                remember('trade: ' .. name .. ' is not sold here. Sold: ' .. table.concat(names, ', '))
            end
        end
        stepData.queue, stepData.next = q, now() + 0.5
        return
    end
    if now() < stepData.next then return end
    local f = table.remove(stepData.queue, 1)
    if f then
        f()
        stepData.next = now() + 1.2
        return
    end
    stepData.done = now()
end

-- closed doors a walk may open on its own: the Arrival Yard's gates (scripts/spirebound/tutorial.lua, C1). Like a
-- player, the pilot clicks the gate in its way; the server says why if it stays shut.
local OPENABLE = { [1638] = true }
local function openDoorToward(player, to)
    local pos = player:getPosition()
    for dx = -1, 1 do
        for dy = -1, 1 do
            local p = { x = pos.x + dx, y = pos.y + dy, z = pos.z }
            local tile = (dx ~= 0 or dy ~= 0) and g_map.getTile(p)
            local top = tile and tile:getTopUseThing()
            if top and top:isItem() and OPENABLE[top:getId()] and dist(p, to) < dist(pos, to) then
                g_game.use(top)
                log('opened the gate at ' .. fmtPos(p))
                return true
            end
        end
    end
    return false
end

-- no path because a closed gate is in the way (the client never plans through a closed door): the tile in front of
-- the nearest gate that lies towards the goal
local function frontOfGate(player, to)
    local pos = player:getPosition()
    local best, bestD
    for dx = -12, 12 do
        for dy = -12, 12 do
            local p = { x = pos.x + dx, y = pos.y + dy, z = pos.z }
            local tile = g_map.getTile(p)
            local top = tile and tile:getTopUseThing()
            if top and top:isItem() and OPENABLE[top:getId()] and dist(p, to) < dist(pos, to) then
                local d = dist(pos, p)
                if not bestD or d < bestD then
                    local side = pos.x < p.x and -1 or (pos.x > p.x and 1 or 0)
                    best, bestD = { x = p.x + side, y = p.y, z = p.z }, d
                end
            end
        end
    end
    return best
end

function handlers.walk(player)
    local to, pos = toPos(step.to), player:getPosition()
    local arrived = (step.arrive_z and pos.z == step.arrive_z) or (pos.z == to.z and dist(pos, to) == 0)
    if arrived then
        if g_game.isAttacking() and step.fight ~= false and fight(player, NEAR) then return end
        return nextStep()
    end
    if now() - stepT > (step.timeout or 90) then
        log('TIMEOUT walking to ' .. fmtPos(to) .. ', stopped at ' .. fmtPos(pos))
        return nextStep()
    end
    if step.fight ~= false and fight(player, NEAR) then
        stepData.lastMove = now()
        return
    end
    if not stepData.lastPos or dist(stepData.lastPos, pos) > 0 or stepData.lastPos.z ~= pos.z then
        stepData.lastPos, stepData.lastMove = pos, now()
    end
    if not player:isWalking() and now() - (stepData.lastWalk or 0) > 1 then
        stepData.lastWalk = now()
        if now() - (stepData.lastMove or stepT) > 1.5 and now() - (stepData.lastDoor or 0) > 3 then
            -- not getting anywhere: a closed gate may be in the way (the client never plans a path through one)
            if openDoorToward(player, to) then
                stepData.lastDoor = now()
                return
            end
            local front = frontOfGate(player, to)
            if front and dist(front, player:getPosition()) > 0 and player:autoWalk(front) then
                stepData.lastDoor = now()
                return
            end
        end
        local ok = player:autoWalk(to)
        if not ok and not stepData.noPath then
            stepData.noPath = true
            log('no path from ' .. fmtPos(pos) .. ' to ' .. fmtPos(to) .. ' (too far, or blocked)')
        end
    end
    if now() - (stepData.lastMove or stepT) > 10 then
        log('STUCK at ' .. fmtPos(pos) .. ' trying to reach ' .. fmtPos(to))
        return nextStep()
    end
end

-- the best potion of a kind in the bag (strongest first); one the server refused (level or class) is not tried again
local HEALTH_POTIONS, MANA_POTIONS, refusedPotion, lastPotionTried = { 239, 236, 266 }, { 238, 237, 268 }, {}, nil
local function bestPotion(list)
    for _, id in ipairs(list) do
        if not refusedPotion[id] and bagCount(id) > 0 then return id end
    end
    return list[#list]
end

local function sample(player)
    local list = monsters(player)
    local nextTo = 0
    for _, m in ipairs(list) do
        if m.d <= 1 then nextTo = nextTo + 1 end
    end
    local hp = math.floor(100 * player:getHealth() / math.max(1, player:getMaxHealth()))
    for _, s in ipairs({ st, total }) do
        s.samples = s.samples + 1
        s.seenSum, s.nextSum = s.seenSum + #list, s.nextSum + nextTo
        s.seenMax, s.nextMax = math.max(s.seenMax, #list), math.max(s.nextMax, nextTo)
        s.minHp = math.min(s.minHp, hp)
    end
    if now() - lastSample >= 2 then
        lastSample = now()
        log(string.format('   at %s  health %d%%  in sight %d  next to you %d%s', fmtPos(player:getPosition()), hp, #list, nextTo,
            g_game.isAttacking() and '  fighting' or ''))
    end
    if hp < 45 and not plan.noPotions and now() - lastPotion > 2 then -- PvP tests of killing blows turn this off
        lastPotion = now()
        local ok = pcall(function() lastPotionTried = bestPotion(HEALTH_POTIONS); g_game.useInventoryItemWith(lastPotionTried, player) end)
        st.potions, total.potions = st.potions + 1, total.potions + 1
        log('health ' .. hp .. '%: drinking a potion' .. (ok and '' or ' (failed)'))
    end
end

local function isParty(shield)
    return shield == ShieldBlue or shield == ShieldBlueSharedExp or shield == ShieldBlueNoSharedExpBlink
        or shield == ShieldBlueNoSharedExp or shield == ShieldYellow or shield == ShieldYellowSharedExp
        or shield == ShieldYellowNoSharedExpBlink or shield == ShieldYellowNoSharedExp
end

-- eat like a player (food gives health and mana regeneration): one piece every 20 s until "You are full"; with no food
-- in the bag, a character that knows Hearth Ration makes some out of a fight
local lastEat, fullUntil = 0, 0
local function eat(player)
    if plan.noFood or not g_game.isOnline() then return end
    local t = now()
    if t - lastEat < 20 or t < fullUntil then return end
    lastEat = t
    for _, c in pairs(g_game.getContainers()) do
        for _, it in ipairs(c:getItems()) do
            if FOOD[it:getId()] then
                g_game.use(it)
                foodEaten = foodEaten + 1
                log('ate item ' .. it:getId())
                return
            end
        end
    end
    if kit and kit.food and kit.food[1] and not g_game.isAttacking()
            and player:getMana() >= kit.food[1].mana + 40 then
        g_game.talk(kit.food[1].words)
        log('no food: casting ' .. kit.food[1].words)
    end
end

-- "pilot fightkit: attack=words/mana/cd/range,...; heal=words/mana/cd,...; skills=words/cd,..."
local function parseKit(text)
    local function part(name)
        return text:match(name .. '=([^;]*)') or ''
    end
    local k = { attack = {}, heal = {}, skills = {} }
    for e in part('attack'):gmatch('[^,]+') do
        local w, m, cd, r, dir = e:match('^%s*(.-)/(%d+)/(%d+)/(%d+)(/?d?)%s*$')
        if w then table.insert(k.attack, { words = w, mana = tonumber(m), cd = tonumber(cd), range = tonumber(r), dir = dir == '/d' }) end
    end
    for e in part('heal'):gmatch('[^,]+') do
        local w, m, cd = e:match('^%s*(.-)/(%d+)/(%d+)$')
        if w then table.insert(k.heal, { words = w, mana = tonumber(m), cd = tonumber(cd) }) end
    end
    k.ally, k.buff, k.food = {}, {}, {}
    for e in part('ally'):gmatch('[^,]+') do -- heals for party members: kind "target" (say the name) or "party"
        local w, m, cd, kind = e:match('^%s*(.-)/(%d+)/(%d+)/(%a+)$')
        if w then table.insert(k.ally, { words = w, mana = tonumber(m), cd = tonumber(cd), kind = kind }) end
    end
    for e in part('buff'):gmatch('[^,]+') do -- taunts, party buffs, damage reduction (cast in a fight)
        local w, m, cd, kind, dur = e:match('^%s*(.-)/(%d+)/(%d+)/([%a_]+)/(%d+)$')
        if w then table.insert(k.buff, { words = w, mana = tonumber(m), cd = tonumber(cd), kind = kind, dur = tonumber(dur) }) end
    end
    for e in part('food'):gmatch('[^,]+') do -- a spell that makes food (Hearth Ration)
        local w, m, cd = e:match('^%s*(.-)/(%d+)/(%d+)$')
        if w then table.insert(k.food, { words = w, mana = tonumber(m), cd = tonumber(cd) }) end
    end
    for e in part('skills'):gmatch('[^,]+') do
        local w, cd = e:match('^%s*(.-)/(%d+)$')
        if w then table.insert(k.skills, { words = w, mana = 0, cd = tonumber(cd), range = 1 }) end
    end
    return k
end

local function cast(e, kind)
    g_game.talk(e.words)
    ready[e.key or e.words] = now() + math.max(e.cd, (e.dur or 0) - 5) + 0.2
    for _, s in ipairs({ st, total }) do
        s.casts, s.mana = s.casts + 1, s.mana + (e.mana or 0)
    end
    log(kind .. ': ' .. e.words)
end

-- fight like a player: heal when hurt, drink mana when low, and weave attack spells and weapon skills into the fight
local function useKit(player)
    if plan.noSpells or not kit then return end
    local hp = player:getHealth() / math.max(1, player:getMaxHealth())
    local mana, maxMana = player:getMana(), math.max(1, player:getMaxMana())
    local t = now()
    if hp < 0.6 and t - lastHealCast >= 1.1 then
        for _, e in ipairs(kit.heal) do
            if mana >= e.mana and t >= (ready[e.words] or 0) then
                lastHealCast = t
                return cast(e, 'heal spell')
            end
        end
    end
    -- (party play) heal a hurt party member: a group heal when two or more are hurt, else the one lowest on health
    if #(kit.ally or {}) > 0 and t - lastHealCast >= 1.1 then
        local me, hurt = player:getPosition(), {}
        for _, c in ipairs(g_map.getSpectators(me, false) or {}) do
            local cp = c:getPosition()
            if c:isPlayer() and not c:isLocalPlayer() and isParty(c:getShield()) and cp and cp.z == me.z and dist(cp, me) <= 6
                    and c:getHealthPercent() < 65 and c:getHealthPercent() > 0 then
                hurt[#hurt + 1] = c
            end
        end
        table.sort(hurt, function(a, b) return a:getHealthPercent() < b:getHealthPercent() end)
        if hurt[1] then
            for _, e in ipairs(kit.ally) do
                if t >= (ready[e.words] or 0) and mana >= e.mana then
                    if e.kind == 'party' and (#hurt >= 2 or hp < 0.7) then
                        lastHealCast = t
                        return cast(e, 'party heal')
                    elseif e.kind == 'target' then
                        lastHealCast = t
                        return cast({ words = e.words .. ' "' .. hurt[1]:getName() .. '"', key = e.words, mana = e.mana, cd = e.cd },
                            'heal ' .. hurt[1]:getName() .. ' (' .. hurt[1]:getHealthPercent() .. '%)')
                    end
                end
            end
        end
    end
    -- mana potions the way players use them: casters (a big mana pool) top up in a fight; fighters, whose small pool
    -- refills on its own, drink one only when hurt and short of the mana for their healing spell
    local cheapestHeal = kit.heal[1] and kit.heal[1].mana or math.huge
    local wantMana = (maxMana >= 200 and mana / maxMana < 0.3 and g_game.isAttacking())
        or (hp < 0.5 and mana < cheapestHeal and maxMana >= cheapestHeal)
    if wantMana and not plan.noPotions and t - lastManaPotion > 2 and t - lastPotion > 1 then
        lastManaPotion = t
        pcall(function() lastPotionTried = bestPotion(MANA_POTIONS); g_game.useInventoryItemWith(lastPotionTried, player) end)
        st.manaPots, total.manaPots = st.manaPots + 1, total.manaPots + 1
        log('mana ' .. math.floor(100 * mana / maxMana) .. '%: drinking a mana potion')
    end
    -- taunts, party buffs and damage reduction in a fight, keeping enough mana for a heal
    if g_game.isAttacking() and #(kit.buff or {}) > 0 then
        for _, e in ipairs(kit.buff) do
            if t >= (ready[e.words] or 0) and mana >= e.mana + (kit.heal[1] and kit.heal[1].mana or 0) then
                local want = true
                if e.kind == 'taunt' or e.kind == 'dr_self' then -- only when several monsters are close
                    local n = 0
                    for _, m in ipairs(monsters(player)) do
                        if m.d <= 3 then n = n + 1 end
                    end
                    want = n >= 2 or (e.kind == 'dr_self' and hp < 0.5)
                end
                if want then return cast(e, 'buff') end
            end
        end
    end
    if not g_game.isAttacking() or t - lastAttackCast < 2.1 then return end
    local target = g_game.getAttackingCreature()
    if not target or target:getHealthPercent() <= 0 then return end
    -- (2026-11-26, Jay: "is everyone using all the best spells?") choose like a player: an area spell when two or more
    -- monsters are close, else the strongest single-target spell (its mana cost as the measure) or a free weapon
    -- skill; a character with party heals keeps 35% of its mana for them
    local me = player:getPosition()
    local d = dist(me, target:getPosition())
    local close = 0
    for _, m in ipairs(monsters(player)) do
        if m.d <= 2 then close = close + 1 end
    end
    local reserve = (#(kit.ally or {}) > 0) and 0.35 * maxMana or 0
    local best, bestScore
    for _, list in ipairs({ kit.skills, kit.attack }) do
        for _, e in ipairs(list) do
            local short = (e.range or 1) <= 1
            local tp = target:getPosition()
            local aligned = not e.dir or tp.x == me.x or tp.y == me.y -- a beam or wave only hits along its line
            local ok = t >= (ready[e.words] or 0) and mana >= e.mana and d <= math.max(1, e.range) and aligned
                and (e.mana == 0 or mana - e.mana >= reserve)
            if ok then
                local score = e.mana == 0 and 18 or e.mana
                if short and list == kit.attack then -- waves, bursts and strikes: worth it on a crowd
                    score = close >= 2 and (e.mana + 60) or (d <= 1 and e.mana * 0.5 or -1)
                elseif e.dir then -- a beam or wave lined up on the target from range (P0-23)
                    score = e.mana + 10
                end
                if score >= 0 and (not bestScore or score > bestScore) then best, bestScore = e, score end
            end
        end
    end
    if best then
        if (best.range or 1) <= 1 or best.dir then -- face the target, as for a wave
            local a, b = me, target:getPosition()
            local dx, dy = b.x - a.x, b.y - a.y
            g_game.turn(math.abs(dx) > math.abs(dy) and (dx > 0 and East or West) or (dy > 0 and South or North))
        end
        lastAttackCast = t
        return cast(best, 'cast')
    end
end

local function tick()
    tickEvent = scheduleEvent(tick, TICK)
    local player = g_game.getLocalPlayer()
    if not g_game.isOnline() or not player or not step then return end
    -- a character's first login opens the outfit window; it would cover every screenshot
    if modules.game_outfit and modules.game_outfit.destroy then pcall(modules.game_outfit.destroy) end
    sample(player)
    if not plan.noSpells and not kit and now() - kitAsked > 10 then
        kitAsked = now()
        g_game.talk('/pilot fightkit')
    end
    useKit(player)
    eat(player)
    -- (2026-11-26, Jay: "they teleported in, stood there and got slaughtered") whatever the step, a character that
    -- is next to a monster and not fighting fights back, like a player would
    local d = step['do']
    if d ~= 'walk' and d ~= 'hunt' and d ~= 'assist' and d ~= 'cast' and not g_game.isAttacking() and not plan.noDefend then
        local list = monsters(player)
        if list[1] and list[1].d <= 2 then
            g_game.setChaseMode(ChaseOpponent)
            g_game.attack(list[1].c)
            log('defending against ' .. list[1].c:getName())
        end
    end
    local h = handlers[step['do']]
    if not h then
        log('unknown step "' .. tostring(step['do']) .. '"')
        return nextStep()
    end
    h(player)
end

local function onHealthChange(player, health, maxHealth)
    if lastHp and health < lastHp and st then
        st.dmg, total.dmg = st.dmg + (lastHp - health), total.dmg + (lastHp - health)
    end
    lastHp = health
    if health <= 0 and not finished and not diedLive then
        log('DEATH at ' .. fmtPos(player:getPosition()))
        if plan.live then -- (party playtests) a death is part of the game: get up at the temple and carry on
            diedCount, diedLive = diedCount + 1, true
            remember('YOU DIED at ' .. fmtPos(player:getPosition()))
            plan.steps, step = {}, nil
            scheduleEvent(function()
                if modules.game_playerdeath and modules.game_playerdeath.destroyWindows then
                    pcall(modules.game_playerdeath.destroyWindows)
                end
                pcall(function() CharacterList.doLogin() end)
            end, 5000)
        else
            finish('died')
        end
    end
end

local function onText(mode, text)
    if not st then return end
    if plan.live then remember(text) end
    if lastPotionTried and (text:find('can only be') or text:find('only be consumed')) then
        refusedPotion[lastPotionTried] = true
    end
    if text:find('You are full') then
        fullUntil, foodEaten = now() + 240, math.max(0, foodEaten - 1)
    end
    if text:find('^pilot fightkit:') then
        kit = parseKit(text)
        log(string.format('fight kit: %d attack spells, %d heals, %d weapon skills (%s)', #kit.attack, #kit.heal, #kit.skills, text))
        return
    elseif text:find('^pilot: level') or text:find('You advanced') or text:find('[Mm]astery') or text:find('^You are now an?') then
        kit, kitAsked = nil, 0 -- a new level may unlock spells: ask again
    end
    if text:find('^Loot of') then
        st.kills, total.kills = st.kills + 1, total.kills + 1
        log('loot: ' .. text)
    else -- every server message (quests, stones, levers, doors...) so a route's report shows what the game said
        local who = text:match('due to an attack by an? (.-)%.') or text:match('due to an attack by the (.-)%.')
        local p = who and g_game.getLocalPlayer()
        if p then -- P6: how far away the hit came from (a charge or a thrown attack lands from range)
            local best
            for _, c in ipairs(g_map.getSpectators(p:getPosition(), false)) do
                if c:getName():lower() == who:lower() then
                    local d = math.max(math.abs(c:getPosition().x - p:getPosition().x), math.abs(c:getPosition().y - p:getPosition().y))
                    if not best or d < best then best = d end
                end
            end
            if best then text = text .. string.format(' (from %d tiles)', best) end
        end
        log('message: ' .. text)
    end
end

-- P6: conditions a monster puts on the Pilot (the bandit's smoke makes you dizzy, the snapper slows you)
local lastStates = 0
local function onStatesChange(player, states, oldStates)
    if not st or not PlayerStates then return end
    for name, bitv in pairs({ dizzy = PlayerStates.Drunk, slowed = PlayerStates.Paralyze }) do
        if bitv and bit.band(states, bitv) > 0 and bit.band(oldStates or lastStates, bitv) == 0 then
            log('state: you are ' .. name)
        end
    end
    lastStates = states
end

-- P6: an invisible monster leaves the map for players who can't see it: one close by that vanishes alive burrowed
local function onDisappear(creature)
    if not st or not creature:isMonster() or creature:getHealthPercent() <= 0 then return end
    local p = g_game.getLocalPlayer()
    local a, b = p and p:getPosition(), creature:getPosition()
    if a and b and a.z == b.z and math.max(math.abs(a.x - b.x), math.abs(a.y - b.y)) <= 3 then
        log('trick: ' .. creature:getName() .. ' vanished beside you (' .. creature:getHealthPercent() .. '% health)')
    end
end

-- P6: a monster that goes invisible (the mole burrows) gets an empty outfit
local function onOutfitChange(creature, outfit, oldOutfit)
    if not st or not creature:isMonster() then return end
    if outfit and outfit.type == 0 and (not outfit.auxType or outfit.auxType == 0) and oldOutfit and oldOutfit.type ~= 0 then
        log('trick: ' .. creature:getName() .. ' vanished (invisible)')
    end
end

-- what NPCs say back (NPC tests)
local function onTalk(name, level, mode, text)
    if not st then return end
    if plan.live then remember(name .. ': ' .. text) end
    if mode == MessageModes.NpcFrom or mode == MessageModes.NpcFromStartBlock then
        log('npc ' .. name .. ': ' .. text)
    elseif name ~= g_game.getCharacterName() then
        log('talk (' .. tostring(mode) .. ') ' .. name .. ': ' .. text) -- monster tricks announce themselves (P6)
    end
end

local function onGameStart()
    log('in game as ' .. plan.character)
    if diedLive then remember('back in the game after dying') end
    if reconnecting then remember('back in the game after a disconnect') end
    reconnecting = false
    diedLive = false
    lastHp = g_game.getLocalPlayer() and g_game.getLocalPlayer():getHealth()
    scheduleEvent(function()
        idx, step, total = 0, nil, newStats()
        nextStep()
        tickEvent = scheduleEvent(tick, TICK)
    end, 2500)
end

local login -- (defined below; onGameEnd logs back in after a server restart)
local function onGameEnd()
    if diedLive then return end -- (live) the death window logs back in
    if charlistPending and not finished then
        charlistPending = false
        scheduleEvent(readCharlist, 4000)   -- the refreshed list arrives about half a second after the logout
        return
    end
    if not finished and plan.live then -- (live) a server restart: keep trying to log back in
        log('left the game unexpectedly: logging back in')
        remember('disconnected from the server: logging back in')
        reconnecting, plan.steps, step, loginEvent = true, {}, nil, nil
        scheduleEvent(function() login(0) end, 10000)
    elseif not finished then
        log('left the game unexpectedly')
        finish('disconnected')
    end
end

-- log in like a player: fill the login window, then pick the character from the list
local loginShotTaken = false
login = function(tries)
    tries = tries or 0
    if tries > 120 and plan.live and reconnecting then -- the server is still down: try again in a while
        loginEvent = nil
        for _, w in ipairs(rootWidget:getChildren()) do
            pcall(function() if w:getStyleName() == 'MessageBox' or w:getId() == 'errorBox' then w:destroy() end end)
        end
        scheduleEvent(function() login(0) end, 15000)
        return
    end
    if tries > 120 then
        log('could not log in (no login window or character list)')
        return finish('login failed')
    end
    local chars = rootWidget:recursiveGetChildById('charactersWindow')
    if chars and chars:isVisible() then
        local list = chars:getChildById('characters')
        for _, w in ipairs(list and list:getChildren() or {}) do
            if w.characterName == plan.character then
                list:focusChild(w)
                log('picked character ' .. plan.character)
                CharacterList.doLogin()
                if reconnecting then -- (live) the server may still be starting: try again if this login went nowhere
                    scheduleEvent(function()
                        if not g_game.isOnline() and reconnecting then
                            loginEvent = nil
                            for _, w in ipairs(rootWidget:getChildren()) do
                                pcall(function() if w:getStyleName() == 'MessageBox' then w:destroy() end end)
                            end
                            login(0)
                        end
                    end, 20000)
                end
                return
            end
        end
        log('character "' .. plan.character .. '" is not on this account')
        return finish('no such character')
    end
    local eg = rootWidget:recursiveGetChildById('enterGame')
    if eg and eg:isVisible() and plan.loginShot and not loginShotTaken then
        -- "loginShot": true in the run file: a picture of the login window as a player sees it (G5)
        loginShotTaken = true
        scheduleEvent(function()
            g_app.doScreenshot('autopilot_login.png')
            log('screenshot autopilot_login.png (the login window)')
        end, 1500)
        scheduleEvent(function() login(tries + 1) end, 3000)
        return
    end
    if eg and eg:isVisible() and not loginEvent then
        eg:getChildById('accountNameTextEdit'):setText(plan.account)
        eg:getChildById('accountPasswordTextEdit'):setText(plan.password)
        loginEvent = true
        log('logging in')
        EnterGame.doLogin()
    end
    scheduleEvent(function() login(tries + 1) end, 500)
end

function Autopilot.init()
    if not g_resources.fileExists(RUN) then return end
    local ok, p = pcall(json.decode, g_resources.readFileContents(RUN))
    lines, t0 = {}, now()
    if not ok or type(p) ~= 'table' or type(p.steps) ~= 'table' then
        log('bad run file: ' .. tostring(p))
        return
    end
    plan = p
    if p.log then LOG = '/' .. p.log end -- two clients at once (PvP tests) each keep their own log
    if p.tag then -- several live clients at once (claude_play --as): each has its own command and state files
        CMD, STATE = '/autopilot_cmd_' .. p.tag .. '.json', '/autopilot_state_' .. p.tag .. '.json'
    end
    -- with vertical sync on, Windows stalls the client while its window is hidden behind others; a test run must
    -- keep going in the background
    pcall(function() g_window.setVerticalSync(false) end)
    pcall(function() g_app.setMaxFps(30) end)
    log('autopilot run "' .. (plan.name or '?') .. '": ' .. #plan.steps .. ' steps; log folder ' .. g_resources.getWriteDir())
    connect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd, onTextMessage = onText, onTalk = onTalk,
        onOpenNpcTrade = onOpenTrade })
    connect(LocalPlayer, { onHealthChange = onHealthChange, onStatesChange = onStatesChange })
    connect(Creature, { onOutfitChange = onOutfitChange, onDisappear = onDisappear })
    scheduleEvent(function() login(0) end, 2000)
end

function Autopilot.terminate()
    if not plan then return end
    disconnect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd, onTextMessage = onText, onTalk = onTalk,
        onOpenNpcTrade = onOpenTrade })
    disconnect(LocalPlayer, { onHealthChange = onHealthChange, onStatesChange = onStatesChange })
    disconnect(Creature, { onOutfitChange = onOutfitChange, onDisappear = onDisappear })
    if tickEvent then removeEvent(tickEvent) end
end
