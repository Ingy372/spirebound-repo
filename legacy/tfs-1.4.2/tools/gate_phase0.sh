#!/usr/bin/env bash
# Phase 0 automated gate checks (docs/04_BUILD_PHASES.md). Runs locally on an Ubuntu 24.04 box with
# MariaDB running, and in CI (.github/workflows/server.yml).
#
#   1. design tables regenerate with no diff       (tools/gen_tables.py)
#   2. no banned names in shipped content          (tools/check_names.py)
#   3. no hardcoded CipSoft item ids in C++ (P1)   (tools/check_hardcoded_ids.sh)
#   4. asset build + round-trip test                (tools/build_assets.py)
#   5. map compile + validation                     (tools/compile_map.py)
#   6. server boots with zero warnings/errors       (server/build/tfs)
#   7. a scripted client logs in and lands at the temple (tools/loadbot/spire_client.py)
#
# Usage: tools/gate_phase0.sh <path to env file>   (see ops/spirebound.env.example; DB must exist)
# Needs: server built in server/build (cmake), mysql client with access to the DB, python3 + pillow.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${1:?usage: tools/gate_phase0.sh <env file>}"
cd "$ROOT"
pass=0; fail=0
report() { if [ "$1" = 0 ]; then echo "PASS  $2"; pass=$((pass+1)); else echo "FAIL  $2"; fail=$((fail+1)); fi; }

python3 tools/gen_tables.py >/dev/null && git diff --quiet -- data/; report $? "1 design tables regenerate with no diff"
python3 tools/check_names.py >/tmp/spire-names.log; report $? "2 check_names: $(tail -1 /tmp/spire-names.log)"
tools/check_hardcoded_ids.sh >/dev/null; report $? "3 no hardcoded item ids in server/src (P1)"
python3 tools/build_assets.py --install >/tmp/spire-assets.log; report $? "4 build_assets round-trip: $(tail -1 /tmp/spire-assets.log)"
python3 tools/compile_map.py --install >/tmp/spire-map.log; report $? "5 compile_map: $(tail -1 /tmp/spire-map.log)"

set -a; . "$ENV_FILE"; set +a
ops/render_config.sh "$ENV_FILE" >/dev/null
[ -f server/key.pem ] || ops/gen_rsa_key.sh >/dev/null
DB="${SPIRE_DB_NAME}"
if [ "$(mysql -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB' AND table_name='players'")" = "0" ]; then
  mysql "$DB" < server/schema.sql
fi
python3 tools/dev_account.py --db "$DB" --account gatetest --password gatetest --character "Gate Tester" >/dev/null

( cd server && ./build/tfs > /tmp/spire-boot.log 2>&1 & echo $! > /tmp/spire-tfs.pid )
for _ in $(seq 1 60); do grep -q "Server Online" /tmp/spire-boot.log && break; sleep 1; done
grep -q "Server Online" /tmp/spire-boot.log
online=$?
warn=$(grep -E -i "warning|error" /tmp/spire-boot.log | grep -v "executed as root user" || true)
[ $online = 0 ] && [ -z "$warn" ]; report $? "6 server boot: online=$([ $online = 0 ] && echo yes || echo no), warnings/errors=$(printf '%s' "$warn" | grep -c . || true)"
[ -n "$warn" ] && echo "$warn" | head -20

temple=$(python3 - <<'PY'
import csv
meta = {r["key"]: r["value"] for r in csv.DictReader(open("maps/src/test_town/meta.csv"))}
for r in csv.DictReader(open("maps/src/test_town/points.csv")):
    if r["type"] == "town":
        print(f'{int(meta["origin_x"]) + int(r["x"])},{int(meta["origin_y"]) + int(r["y"])},{r["z"]}')
        break
PY
)
out=$(python3 tools/loadbot/spire_client.py --host 127.0.0.1 --account gatetest --password gatetest \
      --character "Gate Tester" --key server/key.pem --expect "$temple")
report $? "7 scripted login: $out"

kill "$(cat /tmp/spire-tfs.pid)" 2>/dev/null; sleep 3
echo "phase 0 automated gate: $pass passed, $fail failed"
[ $fail = 0 ]
