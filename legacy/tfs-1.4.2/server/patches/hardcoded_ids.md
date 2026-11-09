# Hardcoded item IDs in TFS 1.4.2 (patch P1)

How this list was made: `grep` of `src/` at upstream commit 31d6e85 for the `item_t` enum in `const.h`
and for numeric item-id literals (`it.id == N`, `getID() == N`, `CreateItem(N)`, ranges). Re-run the
check with `tools/check_hardcoded_ids.sh` after any upstream merge.

## Routed through `src/spire_ids.h` (enum `item_t` in `const.h`)

| Engine name | Upstream (CipSoft) id | Spirebound id | Spirebound item |
|---|---|---|---|
| ITEM_BROWSEFIELD | 460 | 2099 | internal browse-field container |
| ITEM_FIREFIELD_PVP_FULL / MEDIUM / SMALL | 1487 / 1488 / 1489 | 1500 / 1501 / 1502 | fire field |
| ITEM_FIREFIELD_PERSISTENT_FULL / MEDIUM / SMALL | 1492 / 1493 / 1494 | 1503 / 1504 / 1505 | fire field (map-placed) |
| ITEM_FIREFIELD_NOPVP | 1500 | 1506 | fire field (non-PvP) |
| ITEM_POISONFIELD_PVP / PERSISTENT / NOPVP | 1490 / 1496 / 1503 | 1510 / 1511 / 1512 | poison field |
| ITEM_ENERGYFIELD_PVP / PERSISTENT / NOPVP | 1491 / 1495 / 1504 | 1515 / 1516 / 1517 | energy field |
| ITEM_MAGICWALL / PERSISTENT / SAFE / NOPVP | 1497 / 1498 / 11098 / 20669 | 1520–1523 | barrier wall |
| ITEM_WILDGROWTH / PERSISTENT / SAFE / NOPVP | 1499 / 2721 / 11099 / 20670 | 1525–1528 | bramble wall (Ward) |
| ITEM_BAG | 1987 | 2010 | bag |
| ITEM_SHOPPING_BAG | 23782 | 2011 | shopping bag |
| ITEM_GOLD_COIN | 2148 | 2001 | col |
| ITEM_PLATINUM_COIN | 2152 | 2002 | silver col (100) |
| ITEM_CRYSTAL_COIN | 2160 | 2003 | gold col (10,000) |
| ITEM_STORE_COIN | 24774 | 2004 | reserved, never created (no premium currency) |
| ITEM_DEPOT | 2594 | 2020 | depot chest |
| ITEM_LOCKER1 | 2589 | 2021 | depot locker |
| ITEM_INBOX | 14404 | 2022 | inbox |
| ITEM_MARKET | 14405 | 2023 | market |
| ITEM_STORE_INBOX | 26052 | 2024 | store inbox (phase 10 Wardrobe grants) |
| ITEM_DEPOT_BOX_I … XVII | 25453–25469 | 2030–2046 | depot boxes |
| ITEM_PARCEL / LETTER / LETTER_STAMPED / LABEL | 2595 / 2597 / 2598 / 2599 | 2050 / 2051 / 2052 / 2053 | mail |
| ITEM_FULLSPLASH / SMALLSPLASH | 2016 / 2019 | 2060 / 2061 | splashes |
| ITEM_DOCUMENT_RO | 1968 | 2070 | read-only document |
| ITEM_MALE_CORPSE / FEMALE_CORPSE | 3058 / 3065 | 2080 / 2081 | player corpses |
| ITEM_AMULETOFLOSS | 2173 | 0 (none) | no amulet of loss (02 Death) |

## Removed (CipSoft item special cases with no Spirebound equivalent)

| File | Upstream code | Action |
|---|---|---|
| item.cpp `Item::CreateItem` | ids 2202–2206, 2210–2212, 2215–2216 (magic rings), 2640 (soft boots), 6301 (death ring), 18528 (prismatic ring) transform on create | removed |
| item.cpp `getDescription` (×3) | ids 7369–7371 (trophy books) distance-read exception | removed |

## Not item IDs (left alone)

`iologindata.cpp` `pid < 100` (inventory slot / container pid), `items.cpp` `id < 100` and `spriteId >= 100` (reserved range), `runningId = 100`.

## Lua side

Upstream `data/global.lua` lists CipSoft door, key and rope-spot ids. Spirebound's `server/data/global.lua`
is generated from `assets/assets.csv` instead (doors, keys and rope spots are flagged there).
