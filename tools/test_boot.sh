#!/usr/bin/env bash
# Boot test (ROADMAP: must pass after every task).
# Builds .build/server, makes sure the database exists, starts Canary,
# waits for "server online!", runs in-game tests if any, stops it, and
# fails on any [error] line that is not on the allow-list below.
#
# Usage: tools/test_boot.sh [--offline] [seconds-to-wait, default 90]
# Needs: python3, a running MariaDB/MySQL reachable with MYSQL_* settings
#        (env or server/local.env). On a fresh Linux box run with
#        SPIRE_SETUP_DB=1 as root to create the database and user.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OFFLINE=""
if [[ "${1:-}" == "--offline" ]]; then OFFLINE="--offline"; shift; fi
WAIT="${1:-90}"

[[ -f "$ROOT/server/local.env" ]] && set -a && source "$ROOT/server/local.env" && set +a
: "${MYSQL_HOST:=127.0.0.1}" "${MYSQL_USER:=spire}" "${MYSQL_PASS:=spiretest}" "${MYSQL_DATABASE:=spirebound}"
export MYSQL_HOST MYSQL_USER MYSQL_PASS MYSQL_DATABASE

python3 "$ROOT/tools/check_names.py" | tail -1
python3 "$ROOT/tools/check_names.py" >/dev/null || { echo "FAIL: banned names"; exit 1; }

python3 "$ROOT/tools/gen_site.py" --check || { echo "FAIL: website build"; exit 1; }
python3 "$ROOT/tools/login_server.py" --selftest || { echo "FAIL: login service safety checks"; exit 1; }
# R4: a normal start must never touch the GM test account (only the dev-only step does)
if grep -q "dev_accounts.sql" "$ROOT/tools/run_server_wsl.sh" "$ROOT/windows/Start-Spirebound.ps1"; then
  echo "FAIL: a normal start re-creates the test accounts"; exit 1; fi
grep -q 'authType = "session"' "$ROOT/server/config-overrides.lua" || { echo "FAIL: the game server must take session tokens, not passwords"; exit 1; }
python3 "$ROOT/tools/gen_i18n.py" >/dev/null && git -C "$ROOT" diff --quiet -- server/data-spirebound/lib/spirebound/i18n_pt.lua server/data-spirebound/lib/spirebound/i18n_es.lua 2>/dev/null || true

python3 "$ROOT/tools/build_server.py" $OFFLINE
B="$ROOT/.build/server"

# Cloud/CI convenience: start a local MariaDB if none is answering and we're allowed to
if ! mysqladmin -h"$MYSQL_HOST" ping >/dev/null 2>&1 && [[ "$(id -u)" == "0" ]] && command -v service >/dev/null; then
  service mariadb start >/dev/null 2>&1 || true; sleep 3
fi
if [[ "${SPIRE_SETUP_DB:-0}" == "1" ]]; then
  mysql -uroot -hlocalhost --protocol=socket -e "CREATE DATABASE IF NOT EXISTS \`$MYSQL_DATABASE\`; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASS'; GRANT ALL ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_USER'@'localhost'; FLUSH PRIVILEGES;"
fi
MY=(mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DATABASE")
if ! "${MY[@]}" -N -e "SHOW TABLES LIKE 'server_config'" | grep -q server_config; then
  echo "importing schema"; "${MY[@]}" < "$B/schema.sql"
fi
# Local test accounts (roadmap 1.6); safe to repeat
"${MY[@]}" < "$ROOT/server/sql/dev_accounts.sql"
ACC=$("${MY[@]}" -N -e "SELECT COUNT(*) FROM accounts WHERE name='jay'")
CHARS=$("${MY[@]}" -N -e "SELECT COUNT(*) FROM players p JOIN accounts a ON a.id=p.account_id WHERE a.name='jay' AND p.name IN ('Jay','Climber')")
if [[ "$ACC" != "1" || "$CHARS" != "2" ]]; then echo "FAIL: dev accounts (accounts=$ACC characters=$CHARS)"; exit 1; fi
echo "dev account jay: 1 account, 2 characters"

LOG="$ROOT/.build/boot.log"
cd "$B"
SPIRE_TESTS=1 ./canary > "$LOG" 2>&1 &
PID=$!
ok=0
for _ in $(seq 1 "$WAIT"); do
  if grep -q "server online!" "$LOG"; then ok=1; break; fi
  if ! kill -0 $PID 2>/dev/null; then break; fi
  sleep 1
done
sleep 5   # let startup scripts and in-game tests finish
kill -INT $PID 2>/dev/null || true
for _ in $(seq 1 20); do kill -0 $PID 2>/dev/null || break; sleep 1; done
kill -9 $PID 2>/dev/null || true

# Allowed noise: missing RSA key file on test boxes (a key is generated for real installs),
# running as root in the cloud box, Lua API doc generation (no source tree in release builds).
# Boosted creature/boss (a Tibia daily bonus) need Tibia bestiary data, which Spirebound monsters do not use.
# registerWheelSpellTable: the Wheel of Destiny is off, but the engine still looks for Tibia's spells, which we replaced.
ALLOW='key.pem not found|executed as root|Lua API documentation|loadBoostedCreature|loadBoostedBoss|registerWheelSpellTable'
ERRS=$(grep -E '\[(error|critical)\]' "$LOG" | grep -v -E "$ALLOW" || true)
WARNS=$(grep -E '\[warning\]' "$LOG" | grep -v -E "$ALLOW" || true)
TESTFAIL=$(grep -E '\[SPIRETEST\] FAIL' "$LOG" || true)
TESTPASS=$(grep -c -E '\[SPIRETEST\] PASS' "$LOG" || true)

echo "---- boot test ----"
[[ -n "$WARNS" ]] && { echo "warnings:"; echo "$WARNS" | sort | uniq -c | head -20; }
echo "in-game tests passed: $TESTPASS"
if [[ $ok -ne 1 ]]; then echo "FAIL: server never printed 'server online!' (log: .build/boot.log)"; tail -20 "$LOG"; exit 1; fi
if [[ -n "$ERRS" ]]; then echo "FAIL: errors in boot log:"; echo "$ERRS" | head -20; exit 1; fi
if ! grep -q '\[SPIRETEST\] done' "$LOG"; then echo "FAIL: in-game test runner never finished"; exit 1; fi
if [[ -n "$TESTFAIL" ]]; then echo "FAIL: in-game tests:"; echo "$TESTFAIL"; exit 1; fi
echo "PASS: server online, 0 errors"
