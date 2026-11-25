-- Spirebound: in a fight with a player, the built-in helpers only heal (DESIGN.md 12; roadmap M5; Jay 2026-11-25:
-- "the bot should work for pvp strictly for healing. no auto hasting or auto counters to any pvp elements").
-- The server says when a player fight starts and ends (scripts/spirebound/pvp_lock.lua -> modules.game_spirebound).
-- While it lasts, every helper job is paused except healing (HealBot, the friend healer) and eating, and the
-- Spirebound report. Paused means: no auto-haste, no attack spells or runes, no targeting, no ring or amulet swaps,
-- no cures, no Hold Target, and the cavebot stands still (it stays switched on, so its rules still apply).
-- Installed into the client's vBot config by windows/Install-Spirebound.ps1, loaded last.
--
-- Which jobs may keep running: the installer loads spirebound_mark.lua around them, so SpireMarks holds
--   [1] jobs before HealBot, [2] jobs after the friend healer, [3] jobs before eat_food, [4] after it,
--   [5] jobs before spirebound_report (everything from there on is Spirebound's own).
local marks = SpireMarks or {}
local function allowed(i)
  if #marks < 5 then
    return true -- the bookmarks are missing (an old install): pause nothing rather than the wrong things
  end
  return (i > marks[1] and i <= marks[2]) or (i > marks[3] and i <= marks[4]) or i > marks[5]
end

local function locked()
  local sb = modules and modules.game_spirebound
  return sb and sb.pvpLocked and sb.pvpLocked() or false
end

-- wrap every job that must pause: in a player fight it simply does nothing
local paused = 0
for i, m in ipairs(_macros) do
  if not allowed(i) and not m.spireGuarded then
    local original = m.callback
    m.callback = function(macro)
      if locked() then
        return true -- counts as run, so it doesn't retry every frame
      end
      return original(macro)
    end
    m.spireGuarded = true
    paused = paused + 1
  end
end

-- the cavebot also has its own clock: hold it while the fight lasts, so it doesn't walk on the moment it ends
local wasLocked = false
macro(200, function()
  local now = locked()
  if now and CaveBot and CaveBot.isOn and CaveBot.isOn() and CaveBot.delay then
    CaveBot.delay(500)
  end
  if modules and modules.game_spirebound and modules.game_spirebound.botGuard then
    modules.game_spirebound.botGuard.locked = now
  end
  if now ~= wasLocked then
    wasLocked = now
    if now then
      warn("Spirebound: player fight. Helpers only heal until it ends.")
    end
  end
end)

SpireGuard = { paused = paused, allowed = allowed, locked = locked }
-- for the test autopilot (game_autopilot "botguard" step): how many jobs are guarded and whether a fight is on
if modules and modules.game_spirebound then
  modules.game_spirebound.botGuard = { paused = paused, marks = #marks, jobs = #_macros }
end
