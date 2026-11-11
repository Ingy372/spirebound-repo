#!/usr/bin/env bash
# Runs the Spirebound game server and the local login service inside WSL (Ubuntu) for Jay's PC.
# Used by windows\Start-Spirebound.bat. Copies the repo from Windows into /root/sb, builds the server,
# makes sure the database and the test accounts exist, then runs in the foreground
# (closing the window or Stop-Spirebound stops everything).
set -euo pipefail
WIN_REPO="${1:-/mnt/c/Users/Muth3/Desktop/spirebound-repo}"
SB=/root/sb
mkdir -p "$SB"
rsync -a --delete --exclude .git --exclude .build --exclude .cache --exclude .local --exclude backups --exclude screenshots --exclude 'server/local.env' "$WIN_REPO/" "$SB/"
cd "$SB"
# files written on Windows may have CRLF line endings; the Linux tools need LF
find tools -name '*.sh' -o -name '*.py' | xargs sed -i 's/\r$//'
# WSL's clock drifts while Windows sleeps; copy Windows' time (best effort)
NOW=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()" 2>/dev/null | tr -d '\r' || true)
[[ "$NOW" =~ ^[0-9]+$ ]] && date -u -s "@$NOW" >/dev/null 2>&1 || true
service mariadb start >/dev/null 2>&1 || true
for _ in $(seq 1 20); do mysqladmin ping >/dev/null 2>&1 && break; sleep 1; done
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}" MYSQL_USER="${MYSQL_USER:-spire}" MYSQL_PASS="${MYSQL_PASS:-spiretest}" MYSQL_DATABASE="${MYSQL_DATABASE:-spirebound}"
export MYSQL_HOST MYSQL_USER MYSQL_PASS MYSQL_DATABASE
mysql -uroot -hlocalhost --protocol=socket -e "CREATE DATABASE IF NOT EXISTS \`$MYSQL_DATABASE\`; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASS'; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'127.0.0.1' IDENTIFIED BY '$MYSQL_PASS'; GRANT ALL ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_USER'@'localhost'; GRANT ALL ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_USER'@'127.0.0.1'; FLUSH PRIVILEGES;"
python3 tools/build_server.py --offline || python3 tools/build_server.py
B="$SB/.build/server"
MY=(mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DATABASE")
if ! "${MY[@]}" -N -e "SHOW TABLES LIKE 'server_config'" | grep -q server_config; then "${MY[@]}" < "$B/schema.sql"; fi
"${MY[@]}" < server/sql/dev_accounts.sql
pkill -f login_server.py 2>/dev/null || true
python3 tools/login_server.py 8080 &
LOGIN_PID=$!
trap 'kill $LOGIN_PID 2>/dev/null || true' EXIT
cd "$B"
echo "Starting the Spirebound server (wait for 'Spirebound server online!')..."
mkdir -p "$WIN_REPO/.local"
./canary 2>&1 | tee "$WIN_REPO/.local/server.log"
