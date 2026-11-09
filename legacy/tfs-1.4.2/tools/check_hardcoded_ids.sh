#!/usr/bin/env bash
# Lists numeric item-id literals in server/src that are not routed through spire_ids.h.
# Exit 1 if any are found. Run after any upstream TFS merge (patch P1).
set -euo pipefail
cd "$(dirname "$0")/../server/src"
hits=$(grep -n -E "(it\.id|getID\(\)|getId\(\)|itemId|clientId) *(==|!=|>=|<=|<|>) *[0-9]{3,5}\b|CreateItem\( *[0-9]{3,5}|new Item\( *[0-9]{3,5}" ./*.cpp ./*.h || true)
if [ -n "$hits" ]; then
  echo "Hardcoded item ids found (route them through spire_ids.h):"
  echo "$hits"
  exit 1
fi
echo "ok: no hardcoded item ids in server/src"
