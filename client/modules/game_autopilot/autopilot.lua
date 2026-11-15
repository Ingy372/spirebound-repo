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
-- The log (autopilot_log.txt in the client's settings folder) has a line per event, a sample every 2 seconds and a
-- summary per step: monsters in sight, monsters next to you, damage taken, kills, potions.

Autopilot = {}

local RUN = '/game_autopilot/run.json'
local LOG = '/autopilot_log.txt'
local TICK = 250 -- ms
local POTION = 266 -- health potion
local NEAR = 2 -- a monster this close (tiles) gets fought on a walk

local plan, lines, t0
local idx, step, stepT, stepData
local tickEvent, loginEvent
local st, total
local lastPotion, lastSample, lastHp = 0, 0, nil
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
    return { samples = 0, seenSum = 0, seenMax = 0, nextMax = 0, nextSum = 0, dmg = 0, kills = 0, potions = 0, minHp = 100 }
end

local function monsters(player)
    local pos = player:getPosition()
    local out = {}
    for _, c in ipairs(g_map.getSpectators(pos, false) or {}) do
        local p = c:getPosition()
        if c:isMonster() and p and p.z == pos.z and c:getHealthPercent() > 0 then
            out[#out + 1] = { c = c, d = dist(p, pos) }
        end
    end
    table.sort(out, function(a, b) return a.d < b.d end)
    return out
end

local function summary(s, title)
    local avg = s.samples > 0 and s.seenSum / s.samples or 0
    local avgNext = s.samples > 0 and s.nextSum / s.samples or 0
    return string.format('%s: in sight max %d (avg %.1f), next to you max %d (avg %.1f), damage taken %d, kills %d, potions %d, lowest health %d%%',
        title, s.seenMax, avg, s.nextMax, avgNext, s.dmg, s.kills, s.potions, s.minHp)
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
    if g_game.isOnline() then g_game.safeLogout() end
    if plan.exit ~= false then
        scheduleEvent(function() g_app.exit() end, 3000)
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

local function nextStep()
    if step then
        log(string.format('== step %d done in %.0fs', idx, now() - stepT))
        log(summary(st, '   step ' .. idx))
    end
    idx = idx + 1
    step = plan.steps[idx]
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
        g_game.setChaseMode(ChaseOpponent)
        g_game.attack(list[1].c)
        return true
    end
    return false
end

local handlers = {}

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

function handlers.wait()
    if now() - stepT >= (step.seconds or 1) then nextStep() end
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
        if not player:autoWalk(to) and not stepData.noPath then
            stepData.noPath = true
            log('no path from ' .. fmtPos(pos) .. ' to ' .. fmtPos(to) .. ' (too far, or blocked)')
        end
    end
    if now() - (stepData.lastMove or stepT) > 10 then
        log('STUCK at ' .. fmtPos(pos) .. ' trying to reach ' .. fmtPos(to))
        return nextStep()
    end
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
    if hp < 45 and now() - lastPotion > 2 then
        lastPotion = now()
        local ok = pcall(function() g_game.useInventoryItemWith(POTION, player) end)
        st.potions, total.potions = st.potions + 1, total.potions + 1
        log('health ' .. hp .. '%: drinking a potion' .. (ok and '' or ' (failed)'))
    end
end

local function tick()
    tickEvent = scheduleEvent(tick, TICK)
    local player = g_game.getLocalPlayer()
    if not g_game.isOnline() or not player or not step then return end
    -- a character's first login opens the outfit window; it would cover every screenshot
    if modules.game_outfit and modules.game_outfit.destroy then pcall(modules.game_outfit.destroy) end
    sample(player)
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
    if health <= 0 and not finished then
        log('DEATH at ' .. fmtPos(player:getPosition()))
        finish('died')
    end
end

local function onText(mode, text)
    if not st then return end
    if text:find('^Loot of') then
        st.kills, total.kills = st.kills + 1, total.kills + 1
    elseif text:find('^pilot:') or text:find('[Yy]ou are dead') or text:find('[Ll]evel') then
        log('message: ' .. text)
    end
end

local function onGameStart()
    log('in game as ' .. plan.character)
    lastHp = g_game.getLocalPlayer() and g_game.getLocalPlayer():getHealth()
    scheduleEvent(function()
        idx, step, total = 0, nil, newStats()
        nextStep()
        tickEvent = scheduleEvent(tick, TICK)
    end, 2500)
end

local function onGameEnd()
    if not finished then
        log('left the game unexpectedly')
        finish('disconnected')
    end
end

-- log in like a player: fill the login window, then pick the character from the list
local function login(tries)
    tries = tries or 0
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
                return
            end
        end
        log('character "' .. plan.character .. '" is not on this account')
        return finish('no such character')
    end
    local eg = rootWidget:recursiveGetChildById('enterGame')
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
    -- with vertical sync on, Windows stalls the client while its window is hidden behind others; a test run must
    -- keep going in the background
    pcall(function() g_window.setVerticalSync(false) end)
    pcall(function() g_app.setMaxFps(30) end)
    log('autopilot run "' .. (plan.name or '?') .. '": ' .. #plan.steps .. ' steps; log folder ' .. g_resources.getWriteDir())
    connect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd, onTextMessage = onText })
    connect(LocalPlayer, { onHealthChange = onHealthChange })
    scheduleEvent(function() login(0) end, 2000)
end

function Autopilot.terminate()
    if not plan then return end
    disconnect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd, onTextMessage = onText })
    disconnect(LocalPlayer, { onHealthChange = onHealthChange })
    if tickEvent then removeEvent(tickEvent) end
end
