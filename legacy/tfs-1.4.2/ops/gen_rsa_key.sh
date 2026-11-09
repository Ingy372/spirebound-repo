#!/usr/bin/env bash
# Generate the server's RSA key (16_SCALE: change the default key; never ship the private key).
# Writes server/key.pem (git-ignored, chmod 600) and prints the public modulus for the client build.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/server/key.pem}"
if [ -e "$OUT" ]; then echo "$OUT exists; refusing to overwrite"; exit 1; fi
openssl genrsa -traditional -out "$OUT" 1024 2>/dev/null || openssl genrsa -out "$OUT" 1024
chmod 600 "$OUT"
echo "private key: $OUT (keep it on the server only)"
echo -n "public modulus (decimal) for the client: "
python3 - "$OUT" <<'PY'
import subprocess, sys
mod = subprocess.check_output(["openssl", "rsa", "-in", sys.argv[1], "-noout", "-modulus"]).decode().strip().split("=")[1]
print(int(mod, 16))
PY
