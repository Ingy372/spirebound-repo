// Spirebound patch P1 — named item IDs for every item the engine references directly.
//
// TFS 1.4.2 hard-codes CipSoft item IDs in C++ (const.h enum item_t and a few literals in item.cpp).
// Spirebound builds items.otb from scratch, so every ID the engine needs is declared here and must
// exist as a row in assets/assets.csv with the same id. tools/build_assets.py fails the build if
// any SPIRE_ID_* below is missing from assets.csv (see server/patches/hardcoded_ids.md).
//
// Ranges (full plan in assets/README.md):
//   100–999    grounds and borders
//   1000–1499  walls, doors, stairs, structures
//   1500–1599  fields (fire, poison, energy, magic wall, bramble)
//   2000–2099  engine core items (coins, containers, depot, mail, corpses, splashes)

#ifndef SPIREBOUND_SPIRE_IDS_H
#define SPIREBOUND_SPIRE_IDS_H

#include <cstdint>

// Internal container used for "browse field". Never placed on the map.
constexpr uint16_t SPIRE_ID_BROWSEFIELD = 2099;

// Fields
constexpr uint16_t SPIRE_ID_FIREFIELD_PVP_FULL = 1500;
constexpr uint16_t SPIRE_ID_FIREFIELD_PVP_MEDIUM = 1501;
constexpr uint16_t SPIRE_ID_FIREFIELD_PVP_SMALL = 1502;
constexpr uint16_t SPIRE_ID_FIREFIELD_PERSISTENT_FULL = 1503;
constexpr uint16_t SPIRE_ID_FIREFIELD_PERSISTENT_MEDIUM = 1504;
constexpr uint16_t SPIRE_ID_FIREFIELD_PERSISTENT_SMALL = 1505;
constexpr uint16_t SPIRE_ID_FIREFIELD_NOPVP = 1506;

constexpr uint16_t SPIRE_ID_POISONFIELD_PVP = 1510;
constexpr uint16_t SPIRE_ID_POISONFIELD_PERSISTENT = 1511;
constexpr uint16_t SPIRE_ID_POISONFIELD_NOPVP = 1512;

constexpr uint16_t SPIRE_ID_ENERGYFIELD_PVP = 1515;
constexpr uint16_t SPIRE_ID_ENERGYFIELD_PERSISTENT = 1516;
constexpr uint16_t SPIRE_ID_ENERGYFIELD_NOPVP = 1517;

constexpr uint16_t SPIRE_ID_MAGICWALL = 1520;
constexpr uint16_t SPIRE_ID_MAGICWALL_PERSISTENT = 1521;
constexpr uint16_t SPIRE_ID_MAGICWALL_SAFE = 1522;
constexpr uint16_t SPIRE_ID_MAGICWALL_NOPVP = 1523;

// "Wild growth" in the engine; Spirebound's bramble wall (Ward line, 06).
constexpr uint16_t SPIRE_ID_BRAMBLE = 1525;
constexpr uint16_t SPIRE_ID_BRAMBLE_PERSISTENT = 1526;
constexpr uint16_t SPIRE_ID_BRAMBLE_SAFE = 1527;
constexpr uint16_t SPIRE_ID_BRAMBLE_NOPVP = 1528;

// Currency (07): col, silver col (100), gold col (10,000)
constexpr uint16_t SPIRE_ID_COL = 2001;
constexpr uint16_t SPIRE_ID_SILVER_COL = 2002;
constexpr uint16_t SPIRE_ID_GOLD_COL = 2003;
// No premium currency in the proof (02). Reserved so the engine enum stays valid; never created.
constexpr uint16_t SPIRE_ID_STORE_COIN_UNUSED = 2004;

// Containers
constexpr uint16_t SPIRE_ID_BAG = 2010;
constexpr uint16_t SPIRE_ID_SHOPPING_BAG = 2011;

// Depot, inbox, market
constexpr uint16_t SPIRE_ID_DEPOT = 2020;
constexpr uint16_t SPIRE_ID_LOCKER = 2021;
constexpr uint16_t SPIRE_ID_INBOX = 2022;
constexpr uint16_t SPIRE_ID_MARKET = 2023;
constexpr uint16_t SPIRE_ID_STORE_INBOX = 2024;
constexpr uint16_t SPIRE_ID_DEPOT_BOX_FIRST = 2030; // 17 consecutive ids: 2030–2046

// Mail
constexpr uint16_t SPIRE_ID_PARCEL = 2050;
constexpr uint16_t SPIRE_ID_LETTER = 2051;
constexpr uint16_t SPIRE_ID_LETTER_STAMPED = 2052;
constexpr uint16_t SPIRE_ID_LABEL = 2053;

// Splashes
constexpr uint16_t SPIRE_ID_FULLSPLASH = 2060;
constexpr uint16_t SPIRE_ID_SMALLSPLASH = 2061;

// Read-only document
constexpr uint16_t SPIRE_ID_DOCUMENT_RO = 2070;

// Player corpses
constexpr uint16_t SPIRE_ID_MALE_CORPSE = 2080;
constexpr uint16_t SPIRE_ID_FEMALE_CORPSE = 2081;

// Spirebound has no amulet of loss and no blessings (02 Death). 0 never matches a real item.
constexpr uint16_t SPIRE_ID_NONE = 0;

#endif
