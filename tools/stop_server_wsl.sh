#!/usr/bin/env bash
# Saves and stops the Spirebound server in WSL (used by windows\Restart-Server.ps1). Waits up to 30 s for the save.
pkill -INT -x canary || true
for _ in $(seq 1 30); do pgrep -x canary >/dev/null || break; sleep 1; done
pkill -x canary || true
pkill -f run_server_wsl.sh || true
pkill -f login_server.py || true
exit 0
