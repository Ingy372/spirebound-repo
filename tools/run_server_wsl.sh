#!/usr/bin/env bash
# Runs the Spirebound server inside WSL (Ubuntu) for Jay's PC. Used by windows\Start-Spirebound.bat.
# Copies the repo from Windows into /root/sb, builds the server, makes sure the database and the test
# accounts exist, then runs the server in the foreground (closing the window stops it).
set -euo pipefail
WIN_REPO="${1:-/mnt/c/Users/Muth3/Desktop/spirebound-repo}"
SB=/root/sb
mkdir -p "$SB"
rsync -a --delete --exclude .git --exclude .build --exclude .local --exclude backups --exclude 'server/local.env' "$WIN_REPO/" "$SB/"
cd "$SB"
service mariadb start >/dev/null 2>&1 || true
for _ in $(seq 1 20); do mysqladmin ping >/dev/null 2>&1 && break; sleep 1; done
export SPIRE_SETUP_DB=1
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}" MYSQL_USER="${MYSQL_USER:-spire}" MYSQL_PASS="${MYSQL_PASS:-spiretest}" MYSQL_DATABASE="${MYSQL_DATABASE:-spirebound}"
export MYSQL_HOST MYSQL_USER MYSQL_PASS MYSQL_DATABASE
mysql -uroot -hlocalhost --protocol=socket -e "CREATE DATABASE IF NOT EXISTS \`$MYSQL_DATABASE\`; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASS'; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'127.0.0.1' IDENTIFIED BY '$MYSQL_PASS'; GRANT ALL ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_USER'@'localhost'; GRANT ALL ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_USER'@'127.0.0.1'; FLUSH PRIVILEGES;"
python3 tools/build_server.py --offline || python3 tools/build_server.py
B="$SB/.build/server"
MY=(mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DATABASE")
if ! "${MY[@]}" -N -e "SHOW TABLES LIKE 'server_config'" | grep -q server_config; then "${MY[@]}" < "$B/schema.sql"; fi
"${MY[@]}" < server/sql/dev_accounts.sql
cd "$B"
echo "Starting the Spirebound server..."
exec ./canary
