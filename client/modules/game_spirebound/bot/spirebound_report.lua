-- Spirebound: tells the server whether the built-in cavebot is running (DESIGN.md 12).
-- The server applies the cavebot rules (45% XP, half loot, no boss rooms or secrets). Auto-targeting alone is free.
-- Installed into the client's vBot config by windows/Install-Spirebound.ps1. Removing it doesn't help:
-- running the cavebot without reporting it is against the rules.
local lastState = nil
local lastSent = 0

macro(2000, function()
  local on = CaveBot and CaveBot.isOn and CaveBot.isOn() or false
  local now = g_clock.millis()
  if on ~= lastState or now - lastSent > 60000 then
    local protocol = g_game.getProtocolGame()
    if protocol then
      protocol:sendExtendedOpcode(210, '{"t":"bot","on":' .. (on and 'true' or 'false') .. '}')
      lastState = on
      lastSent = now
    end
  end
end)
