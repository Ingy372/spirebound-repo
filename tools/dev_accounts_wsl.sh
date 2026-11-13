#!/usr/bin/env bash
# DEV ONLY (roadmap R4): (re)creates the local test account "jay" with its GM character and test characters.
# A normal start (tools/run_server_wsl.sh) no longer does this, so a real server never gets the public test password.
# Used by windows\Make-Test-Accounts.bat and by the first install.
set -euo pipefail
WIN_REPO="${1:-/mnt/c/Users/Muth3/Desktop/spirebound-repo}"
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}" MYSQL_USER="${MYSQL_USER:-spire}" MYSQL_PASS="${MYSQL_PASS:-spiretest}" MYSQL_DATABASE="${MYSQL_DATABASE:-spirebound}"
service mariadb start >/dev/null 2>&1 || true
MYSQL_PWD="$MYSQL_PASS" mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" "$MYSQL_DATABASE" < "$WIN_REPO/server/sql/dev_accounts.sql"
echo "Test account 'jay' is ready (local testing only)."
