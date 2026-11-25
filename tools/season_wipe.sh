#!/usr/bin/env bash
# Season reset, offline (roadmap 8.3). The wipe runs only while the server is stopped, so nothing the server still holds
# in memory can be saved back over it.
#
#   tools/season_wipe.sh rehearse <repo>   load the newest backup into a scratch database, wipe it there, print what
#                                          changed (Jay's real database is not touched)
#   tools/season_wipe.sh wipe <repo>       back up, then wipe the real database (the server must be stopped)
#
# What is wiped: server/data-spirebound/season_wipe.sql. /season end (in game) archives every character first.
set -euo pipefail
CMD="${1:?rehearse or wipe}"; ROOT="${2:?repo path}"
DB="${MYSQL_DATABASE:-spirebound}"
SQL="$ROOT/server/data-spirebound/season_wipe.sql"
service mariadb start >/dev/null 2>&1 || true
for _ in $(seq 1 20); do mysqladmin ping >/dev/null 2>&1 && break; sleep 1; done

counts() {
  mysql -N "$1" -e "SELECT 'characters', COUNT(*) FROM players WHERE group_id < 4
    UNION ALL SELECT 'staff characters', COUNT(*) FROM players WHERE group_id >= 4
    UNION ALL SELECT 'accounts', COUNT(*) FROM accounts
    UNION ALL SELECT 'owned houses', COUNT(*) FROM houses WHERE owner > 0
    UNION ALL SELECT 'saved house tiles', COUNT(*) FROM tile_store
    UNION ALL SELECT 'guilds', COUNT(*) FROM guilds
    UNION ALL SELECT 'market offers', COUNT(*) FROM market_offers
    UNION ALL SELECT 'character data (kv)', COUNT(*) FROM kv_store WHERE key_name LIKE 'player.%'
    UNION ALL SELECT 'account rewards (kv)', COUNT(*) FROM kv_store WHERE key_name LIKE 'account.%'
    UNION ALL SELECT 'Hall of Seasons (kv)', COUNT(*) FROM kv_store WHERE key_name LIKE 'hall-of-seasons%'"
}

if [[ "$CMD" == rehearse ]]; then
  FILE=$(ls -1t "$ROOT"/backups/spirebound_*.sql.zip 2>/dev/null | head -n 1 || true)
  [[ -n "$FILE" ]] || { echo "No backup to rehearse on (backups/ is empty)."; exit 1; }
  R=spirebound_rehearsal
  mysql -e "DROP DATABASE IF EXISTS \`$R\`; CREATE DATABASE \`$R\`"
  mysql -e "GRANT ALL PRIVILEGES ON \`$R\`.* TO 'spire'@'localhost'"   # the dump's triggers run as the game's user
  TMP=$(mktemp -d)
  python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$FILE" "$TMP"
  mysql "$R" < "$TMP"/*.sql
  rm -rf "$TMP"
  echo "Rehearsal on a copy of $(basename "$FILE")"
  echo "--- before ---"; counts "$R"
  mysql "$R" < "$SQL"
  echo "--- after ---"; counts "$R"
  mysql -e "DROP DATABASE \`$R\`"
  echo "Rehearsal done. Characters, houses, guilds and the market should be empty; accounts, staff, account rewards and the Hall of Seasons kept."
  exit 0
fi

if [[ "$CMD" == wipe ]]; then
  if pgrep -x canary >/dev/null; then echo "The server is still running. Stop it first."; exit 1; fi
  bash "$ROOT/tools/db_wsl.sh" backup "$ROOT"
  echo "--- before ---"; counts "$DB"
  mysql "$DB" < "$SQL"
  echo "--- after ---"; counts "$DB"
  echo "Season wiped. Start the server: the new season begins."
  exit 0
fi
echo "usage: season_wipe.sh rehearse|wipe <repo>"; exit 1
