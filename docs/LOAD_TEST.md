# Load test: how many players Jay's PC can carry (roadmap 9.2)

## In plain English

**Jay's PC carries 150 hunting players on Floor 1 without lag** (measured 2026-11-26). With 100 the server's heartbeat
ran on average 1.3 thousandths of a second late (players feel nothing below about 50) and used a fifth of one processor
core and a quarter of a gigabyte of memory. Going from 100 to 150 players barely changed anything. The target was 100.
What limits a launch evening is therefore room on the map, not the PC (that is roadmap N2: `docs/N2_capacity.md`).

## How it was measured

- **Scripted players, not game windows.** 100 real game clients would need 100 copies of the game on screen, which no
  PC can run. Instead `tools/loadbot.py` is a tiny client that logs characters in over the real game connection (the
  same handshake and encryption as the real client) and keeps them connected. One small program holds 150 of them.
- **They really play.** A test-only script on the server (`scripts/spirebound/dev_loadbot.lua`) makes each one hunt
  its hunting ground like a player: it finds the nearest monster nobody else is fighting, walks to it, hits it as hard as
  a player of that level does (the economy model's damage), pauses 2 seconds after each kill, and walks on to the next
  spot when nothing is in sight. Monsters fight back, the crowd system adds monsters, kills count for tasks and quests,
  and every move is sent to every player who can see it: the same work the server does for real players.
  The script only runs on a test copy started with `SPIRE_LOADTEST=1`, and only for the test accounts
  `loadbotN@localhost` (no real player can have an e-mail like that).
- **Where:** a separate copy of the server in WSL (`/root/sbtest2`, its own ports 7571/7572 and its own test database),
  on Jay's PC, while the live server kept running beside it. Bots spread evenly over Floor 1's twelve walled hunting
  grounds, at each ground's middle level, one of each class in turn.
- **What is measured, every 10 seconds:**
  - *tick lag*: the server keeps a 100 ms heartbeat timer; how late it fires is how far behind the game loop is. Under
    50 ms players feel nothing; past about 100-200 ms walking and attacks start to feel sticky;
  - *CPU*: the game server's share of one processor core (100% = one full core; Canary's game loop is mostly one core);
  - *memory*: what the server process holds.
- **Steps:** 10, 25, 50, 75, 100, 125, then 150 bots, three minutes each, without logging anyone out between steps.
- **Rerun it:** `python3 tools/loadtest.py ramp` on a built test copy (see the top of `tools/loadtest.py`).

## Results

Run of 2026-11-26 12:12-12:35 (`.local/loadtest_ramp.json` on the test copy). "Late" = heartbeats more than 100 ms late in the
three minutes.

| Bots hunting | Online | Tick lag, average | Tick lag, worst | Late beats | Server CPU (one core) | Server memory |
|---|---|---|---|---|---|---|
| 0 (idle) | 0 | 0.1 ms | 1 ms | 0 | 1% | 193 MB |
| 10 | 10 | 0.2 ms | 7 ms | 0 | 5% | 212 MB |
| 25 | 25 | 0.4 ms | 15 ms | 0 | 9% | 221 MB |
| 50 | 50 | 0.5 ms | 44 ms | 0 | 17% | 233 MB |
| 75 | 75 | 1.2 ms | 86 ms | 0 | 20% | 240 MB |
| 100 | 100 | 1.3 ms | 83 ms | 0 | 20% | 247 MB |
| 125 | 125 | 2.0 ms | 67 ms | 0 | 21% | 254 MB |
| 150 | 146 | 2.0 ms | 91 ms | 0 | 21% | 259 MB |

At 150, the last two bots to join (148 and 149) lost their connection while logging in, so the step ran with 146 to
148 bots; the server logged no kicks or errors for them. Every other step had every bot online. The "worst" column is single hiccups of under a tenth of a
second (the server saving, a crowd of monsters appearing); none came near what a player notices.

## Things found along the way

- **Log noise on every kill (worth fixing before launch, not urgent).** Each kill writes 7 to 8 warning lines to the
  server log ("Deprecated use of onKill event") because seven of our scripts count kills the old way. At 100 players
  that is roughly 150,000 lines an hour. On Jay's PC the live server's log is also copied into a file on the Windows
  side (`tools/run_server_wsl.sh` pipes it through `tee` into `.local/server.log`), which is slower than the Linux disk
  this test wrote to. Not measured yet with that copy, because Jay was playtesting on the live server when the test
  ran (`python3 tools/loadtest.py ramp --tee <file on /mnt/c>` measures it). The proper fix is to move those seven
  kill counters to death events (a contained code change, worth its own task).
- **The engine refuses an address that connects more than 5 times within half a second** (an anti-flood rule in the
  engine). Real players never hit it; it only matters for test tools (the bots join 0.6 s apart) and for many players
  behind one internet address reconnecting all at once after a restart. It lifts itself after 3 seconds.
- **The live server's stop scripts stop every server program on the machine** (`pkill -x canary` in
  `tools/stop_server_wsl.sh` and `windows/Stop-Spirebound.bat`), including test copies. The load test now runs its
  server under its own name (`canary-loadtest`) so a live restart can't stop it.
- **Clients must ping every 10 seconds** or the server drops their target, and after 60 seconds out of combat logs them
  out. The real client does this; the bot client now does too.
- **Shardlings' death burst works** (found by the addon test): forty field shardlings killed in one spot killed the
  level 26 test Mystic standing next to them.
