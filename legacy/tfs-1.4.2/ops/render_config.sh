#!/usr/bin/env bash
# Render server/config.lua from ops/config.lua.tpl and an env file (default /etc/spirebound/spirebound.env).
# The env file holds secrets and host values; it is never committed. Example keys: ops/spirebound.env.example
set -euo pipefail
ENV_FILE="${1:-/etc/spirebound/spirebound.env}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
set -a; . "$ENV_FILE"; set +a
envsubst '${SPIRE_PUBLIC_IP} ${SPIRE_DB_HOST} ${SPIRE_DB_USER} ${SPIRE_DB_PASS} ${SPIRE_DB_NAME} ${SPIRE_WEBSITE_URL}' \
  < "$ROOT/ops/config.lua.tpl" > "$ROOT/server/config.lua"
chmod 600 "$ROOT/server/config.lua"
echo "wrote server/config.lua"
