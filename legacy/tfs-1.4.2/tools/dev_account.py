#!/usr/bin/env python3
"""Create a test account and character in a STAGING or local database (never production).

Phase 0 uses TFS 1.4.2's stock SHA-1 account hashing; patch P11 (phase 1) replaces it with a
salted modern hash on both the server and the website, and this tool will follow.

Usage:
  python3 tools/dev_account.py --db spirebound --account test --password test --character "Test Adventurer"
(Uses the local `mysql` client and its default credentials, e.g. root via unix socket on a dev box.)
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys


def sql_str(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--account", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--character", required=True)
    ap.add_argument("--sex", type=int, default=1)
    ap.add_argument("--group", type=int, default=1, help="1 player, 3+ gamemaster (staging only)")
    a = ap.parse_args()
    pw = hashlib.sha1(a.password.encode()).hexdigest()
    q = f"""
INSERT INTO accounts (name, password, type, premium_ends_at, email, creation)
  VALUES ({sql_str(a.account)}, '{pw}', 1, 0, '', UNIX_TIMESTAMP())
  ON DUPLICATE KEY UPDATE password = VALUES(password);
SET @acc = (SELECT id FROM accounts WHERE name = {sql_str(a.account)});
INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience,
  lookbody, lookfeet, lookhead, looklegs, looktype, maglevel, mana, manamax, town_id, posx, posy, posz,
  conditions, cap, sex)
  VALUES ({sql_str(a.character)}, {a.group}, @acc, 1, 0, 150, 150, 0,
  88, 88, 78, 58, 1, 0, 100, 100, 1, 0, 0, 0, '', 400, {a.sex})
  ON DUPLICATE KEY UPDATE account_id = @acc;
"""
    r = subprocess.run(["mysql", a.db], input=q, text=True, capture_output=True)
    if r.returncode:
        print(r.stderr); return 1
    print(f"account {a.account!r} with character {a.character!r} ready in {a.db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
