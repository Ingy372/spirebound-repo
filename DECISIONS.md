# Decisions for Jay (yes / no / change a number)

Nothing here is built. Each section ends with what I need from you. Written 2026-11-11.

---

## 1. Shop prices (roadmap 7.3)

**Rules already in DESIGN.md §11:** cosmetics, house items and convenience only; no XP boosts; shop items can be resold for gold; never gambled.

**Currency:** "Spire Coins", sold in packs. My suggestion (about 1 US cent per coin, bigger packs give a small bonus so people don't feel forced into the smallest):

| Pack | Price | Coins |
|---|---|---|
| Small | $5 | 500 |
| Medium | $10 | 1,050 |
| Large | $25 | 2,750 |
| Huge | $50 | 5,750 |

**Price list** (what the closed shop sells today, plus the convenience items DESIGN.md promises):

| Item | Now | Suggested | Why |
|---|---|---|---|
| Candelabrum, red tapestry | 40 / 30 | 40 / 30 | Cheap "first purchase" items. |
| Goblin / minotaur statue kit | 60 | 80 | Statues are display pieces people want in sets. |
| Telescope kit | 80 | 100 | |
| Harp kit | 100 | 150 | |
| Sofa chair kit | 50 | 60 | |
| Piano kit | 150 | 250 | Biggest furniture piece. |
| Outfit (each) | 400 | 600 | Outfits are the main thing people show off, so the main income. |
| Mount | 500 | 800 | Mounts are wanted more than outfits. |
| Name change | n/a | 500 | Rare, one-off. |
| Extra character slot | n/a | 700 | Needed by people who want a Hardcore and a Death Game character. |
| Extra depot space (+500 items) | n/a | 400 | |
| House moving service | n/a | 150 | Houses are limited to 3 portal changes; moving is a convenience. |

Rule of thumb I used: a casual player who spends $10 gets one outfit plus a few decorations; nothing costs more than $10 except big furniture sets.

**Payment setup:** I can't set this up (money and accounts are yours). The usual choice is Stripe Checkout (cards, runs a webhook to give coins) or PayPal. Either needs a business account and a refund/chargeback policy. Do this only right before launch.

**Need from you:** "prices OK", or change any number. Also: are the four pack sizes OK?

---

## 2. Crafting and cooking (roadmap 3.5b): draft design

**Fit with DESIGN.md:** the best gear comes only from bosses and drops; ammo and healing supplies are the gold sink (players can't conjure ammo); fish can be cooked into small regen buffs with no combat stats; the Workshop Bench and Garden were promised as house fixtures.

**Proposal (small on purpose):**
1. **Where:** a *Workshop Bench* and a *Cooking Hearth*, both house fixtures bought from Housewright Orla. Nothing can be crafted outside a house, so houses stay valuable.
2. **Materials:** monsters drop a few new plain materials per floor (hide, iron scrap, resin, crystal shard) and the house Garden grows herbs. Fishing already gives fish. Materials are tradeable on the market.
3. **Cooking:** fish + herb → meals that give small health/mana regeneration for 30 minutes, no damage, no defense, no skill speed. Legendary fish make a one-day cosmetic aura. This uses the 63 fish already in the game.
4. **Workshop products (cosmetic or comfort only):** furniture and tapestries (same items as the shop's house line, but crafted, so non-donors can earn them), dyes, mannequin outfits, and **ammo**. Ammo is crafted at a price that is never cheaper than buying it from the NPC (the generator refuses price loops), so it saves a trip but doesn't remove the gold sink.
5. **Recipes:** found as secrets, boss drops or bought from the Quartermaster. About 40 recipes at launch (10 floors, 4 each). Recipes are account-wide, like cosmetics.
6. **No gear crafting.** No weapon or armor can be crafted or upgraded. This keeps "the best gear comes only from playing and bosses".
7. **Death Game and Hardcore:** same rules for everyone; crafting never risks the character.
8. **Skill:** none (no crafting level), so there is nothing to grind. Cooking and crafting just take a few seconds and the materials.

**Build estimate:** about one working session (recipe table generator, two fixtures, tests that no recipe makes power or beats an NPC price).

**Need from you:** yes/no on the whole idea; and two choices: (a) allow crafting ammo? (I say yes); (b) should recipes be secrets-only? (I say no: secrets, boss drops and Quartermaster).

---

## 3. Hosting (roadmap 10.1)

Spirebound at launch size (a few hundred players, one Canary server, one MariaDB, a small website) needs roughly **2-4 CPU cores, 8 GB RAM, 40+ GB SSD**, and **DDoS protection**, because game servers get attacked. Prices below come from public pages found on 2026-11-11 and move often; **check the live price before buying**.

| Option | Specs | Approx. monthly | Good | Bad |
|---|---|---|---|---|
| **OVHcloud VPS-2/VPS-3** | 4-6 cores, 8-12 GB | about $8.50-$12.50 (Canada page) | Cheapest by far, anti-DDoS included, big RAM | Shared CPU, variable support; confirm the US/Canada site price |
| **Hetzner Cloud (Ashburn, US)** | CCX13: 2 dedicated cores, 8 GB | about $51 after the June 2026 price rise (sources disagree) | Dedicated cores, very reliable | Price jumped sharply, only basic DDoS protection |
| **Dedicated game host or a bigger VPS (e.g. a 4-8 core, 16 GB plan)** | 4-8 cores, 16 GB | about $25-$60 | Room to grow to 1,000 players | Overkill for friend testing |

My recommendation: **start on OVHcloud VPS-3 (about $12/month)** for friend testing and soft launch. Move to something bigger only if lag shows up. Keep daily backups off the server (the backup scripts already make zips). Don't host from your own PC for the public: it exposes your home address and goes down when you sleep.

Sources: [Hetzner price-rise report](https://webhosting.today/2026/06/18/hetzners-price-increases-reached-209-the-30-headline-applied-to-a-different-tier/), [Hetzner 2026 pricing overview](https://www.bitdoze.com/hetzner-cloud-cost-optimized-plans/), [OVHcloud VPS compare](https://www.ovhcloud.com/en-ca/vps/compare/).

**Need from you:** pick one (or say "OVH" and I'll write the setup script when you are ready for task 10.2).

---

## 4. Art list in priority order (for Grok)

Full prompts are in `ART_REQUESTS.md` (copy them from there). Order to make things in, most visible first:

1. **Four vocation outfits** (Vanguard, Ranger, Arcanist, Mystic): every player sees these all the time.
2. **UI set:** floor badge, skill-slot frames, difficulty icons. Cursor markers: they must be **11x11 pixels** (the client's skull size), not 16x16 as ART_REQUESTS.md says; I will fix that line.
3. **Hearthgate NPCs:** Registrar, priest, banker, merchant, Vesper (first thing new players meet).
4. **Floor 1 monsters** (13) and the two Floor 1 bosses (Gate Hound, Axe-Lord and its blade form).
5. **Sword-skill icons** (24).
6. **Underkeep and Old Tusk** monsters, bounty warden, guildwarden, quartermaster, summons.
7. **Shop launch art:** two outfits and one mount.
8. **Azhrakkar** and his sweep effect (needed only at Floor 10, but he is the face of the game, so worth starting early).
9. Floors 2-10 monsters (batches 3-4): do floor by floor as the tower opens.

Style lock to paste before every prompt: *32x32 pixel art sprite, classic Tibia MMORPG style, top-down 3/4 view facing the camera at an angle, transparent background, 1-pixel dark outline, limited 24-color palette, soft top-left lighting, no text, no border.*

**Need from you:** nothing, just make them in that order when you have time.

---

## Roadmap items I could not do overnight (and why)

- **6.4 custom sprite pipeline:** needs writing new entries into the client's appearance file and a new sprite sheet in Tibia's compressed format, then checking it in the client. A real design job, not started. Plan: first decode and re-encode one existing sheet to prove the format, then add one item.
- **6.5b Android build in CI:** I can't test an Android build on this PC. A "drafted but untested" workflow would be misleading, so I left it open.
- **9.2 bot load test:** needs a scripted client that speaks the 15.11 login and game protocol (HTTP login, then encrypted game packets). Not started; the login service I wrote for the client (`tools/login_server.py`) is the first piece.
