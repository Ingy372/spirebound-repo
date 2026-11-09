# client/

Spirebound's additions to OTClient Redemption (pinned in `server/PINS.env`). The Windows installer copies `client/modules/*` into the downloaded client.

| Module | What it does |
|---|---|
| `modules/game_spirebound` | Floor indicator ("Floor 1 - Hearthgate Plains") at the top of the game screen, Hardcore / Death Game label, the sword-skill bar (up to 6 skills for the weapon in your hand, Shift+1..6 or click, live cooldowns, colour by Opener/Link/Finisher), and SAO-style cursors over players (green clean, orange aggressor, red murderer, dark red serial murderer) |

Server side of the link: `server/data-spirebound/lib/spirebound/client_link.lua` (extended opcode 210, JSON).
Cursor images are placeholders; final art is in `ART_REQUESTS.md` batch 2.
