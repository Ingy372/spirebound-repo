#!/usr/bin/env bash
# Backup / restore of the Spirebound database that lives in WSL. Used by windows\Backup-Spirebound.bat,
# windows\Restore-Spirebound.bat and Start-Spirebound.bat.
#   db_wsl.sh backup  <windows-repo-path-as-seen-from-WSL>
#   db_wsl.sh restore <windows-repo-path-as-seen-from-WSL> [file.zip]
set -euo pipefail
CMD="${1:?backup or restore}"; ROOT="${2:?repo path}"; FILE="${3:-}"
DB="${MYSQL_DATABASE:-spirebound}"
OUT="$ROOT/backups"; mkdir -p "$OUT"
service mariadb start >/dev/null 2>&1 || true
for _ in $(seq 1 20); do mysqladmin ping >/dev/null 2>&1 && break; sleep 1; done
mysql -e "USE \`$DB\`" 2>/dev/null || { echo "There is no Spirebound database yet (start the game once first)."; exit 1; }

backup() {
  local stamp f
  stamp=$(date +%Y-%m-%d_%H-%M-%S)
  f="$OUT/spirebound_$stamp.sql"
  mysqldump --single-transaction --routines "$DB" > "$f"
  [[ $(stat -c %s "$f") -gt 1000 ]] || { rm -f "$f"; echo "The backup did not work."; exit 1; }
  python3 - "$f" <<'PY'
import sys, zipfile, os
f = sys.argv[1]
with zipfile.ZipFile(f + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(f, os.path.basename(f))
os.remove(f)
PY
  echo "Backup saved: $f.zip"
  ls -1t "$OUT"/spirebound_*.sql.zip | tail -n +15 | xargs -r rm -f
}

if [[ "$CMD" == backup ]]; then backup; exit 0; fi

if pgrep -x canary >/dev/null; then echo "The server is still running. Run Stop Spirebound first."; exit 1; fi
if [[ -z "$FILE" ]]; then FILE=$(ls -1t "$OUT"/spirebound_*.sql.zip 2>/dev/null | head -n 1 || true); fi
[[ -n "$FILE" && -f "$FILE" ]] || { echo "There are no backups to restore."; exit 1; }
backup   # safety copy of the current state first
TMP=$(mktemp -d)
python3 - "$FILE" "$TMP" <<'PY'
import sys, zipfile
zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])
PY
mysql "$DB" < "$TMP"/*.sql
rm -rf "$TMP"
echo "Restored from $FILE"
