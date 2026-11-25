#!/usr/bin/env python3
"""Builds the client package for players on Jay's Tailscale network (friends, a Grok Bot): roadmap 9.1.

Copies the installed client (.local/client) without its debug files (about 700 MB of .pdb/.ilk), points it at this
PC's Tailscale address, and zips it to .local/friend/spirebound-client.zip next to setup.sh, a Linux installer
(Wine) for a Grok Bot's cloud computer. windows\\Share-Client.bat serves that folder on port 8090.
The package is for Jay's own testers only: it contains the Tibia client files, which never go to GitHub.
Run: python tools/make_friend_client.py [tailscale-ip]   (the address is read from Tailscale when left out)
"""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / ".local" / "client"
OUT = ROOT / ".local" / "friend"
SKIP_SUFFIX = (".pdb", ".ilk")
SKIP_NAMES = {"run.json", "autopilot_cmd.json", "autopilot_state.json"}


def tailscale_ip():
    exe = r"C:\Program Files\Tailscale\tailscale.exe"
    try:
        out = subprocess.run([exe, "ip", "-4"], capture_output=True, text=True, timeout=15).stdout.strip().splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out[0].strip() if out and out[0].startswith("100.") else None


SETUP = r"""#!/usr/bin/env bash
# Installs the Spirebound game client on a Linux computer (a Grok Bot's cloud computer) using Wine, and points it at
# Jay's server over Tailscale. Run:  curl -fsSL http://__IP__:8090/setup.sh | bash
set -euo pipefail
SERVER=__IP__
DEST="$HOME/spirebound"
echo "Installing Wine and unzip (needs sudo)..."
if command -v apt-get >/dev/null; then
  sudo dpkg --add-architecture i386 2>/dev/null || true
  sudo apt-get update -y
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y wine wine64 unzip curl || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y wine unzip curl
else
  echo "This script needs a Debian/Ubuntu computer (apt-get)."; exit 1
fi
echo "Downloading the Spirebound client from $SERVER (about 230 MB)..."
mkdir -p "$DEST"
curl -fL "http://$SERVER:8090/spirebound-client.zip" -o "$DEST/client.zip"
rm -rf "$DEST/client"
unzip -q "$DEST/client.zip" -d "$DEST/client"
rm "$DEST/client.zip"
# start in English (skips the language picker)
wineboot -i >/dev/null 2>&1 || true
CFG="$HOME/.wine/drive_c/users/$USER/AppData/Roaming/otcr/otclient"
mkdir -p "$CFG"
[ -f "$CFG/config.otml" ] || echo "locale: en" > "$CFG/config.otml"
cat > "$DEST/play.sh" <<'PLAY'
#!/usr/bin/env bash
cd "$HOME/spirebound/client" && exec wine otclient.exe
PLAY
chmod +x "$DEST/play.sh"
echo
echo "Done. Start the game with:  $DEST/play.sh"
"""


BRIEF = """You are a play tester for Spirebound, a new Open Tibia server (a Tibia-like online RPG) that is not public yet.
The owner (Jay) wants honest feedback from someone playing it for the first time.

SETUP (once, on your computer):
1. Join Jay's private network: install Tailscale and connect with this key:
     curl -fsSL https://tailscale.com/install.sh | sh
     sudo tailscale up --authkey=PASTE-THE-TAILSCALE-KEY-HERE --hostname=grok-tester
2. Install the game client (Wine is used to run it):
     curl -fsSL http://__IP__:8090/setup.sh | bash
3. Start the game:  ~/spirebound/play.sh
   Log in with account: grokbot   password: __PASSWORD__   and pick the character "Grok Tester".

HOW TO PLAY: it plays like Tibia. Click the ground to walk (or use the arrow keys), right-click a monster to attack it,
type "hi" in chat next to an NPC to talk (words in blue are keywords you can click or type), press J for the Journal.
The character is brand new: follow the stone path in the Arrival Yard, do Guide Pell's quest, choose a vocation at the
Registrar, then play Floor 1 like a real new player: hunt, do quests, follow the hints the game gives you.

WHAT TO DO: play for about 1-2 hours. Every 15 minutes or so, write a short note of what you did and what you thought.
When you are done (or stuck for more than 10 minutes), write a playtest report with these sections:
1) What I did. 2) What was fun. 3) What was confusing or unclear. 4) What was boring or slow. 5) Bugs or things that
looked broken (with where they happened). 6) How it compares with other Open Tibia servers you know. 7) The five
changes that would most make you keep playing. Be specific and honest; criticism is the point.
Only play on this account. Don't try to reach anything on Jay's network except the game.
"""


def main(argv):
    ip = argv[0] if argv else tailscale_ip()
    if not ip:
        sys.exit("make_friend_client: no Tailscale address. Open Tailscale and sign in, or pass the address.")
    if not (SRC / "otclient.exe").exists():
        sys.exit("make_friend_client: the client is not installed (.local/client). Run windows\\Install-Client.bat first.")
    OUT.mkdir(parents=True, exist_ok=True)
    stage = OUT / "stage"
    shutil.rmtree(stage, ignore_errors=True)
    shutil.copytree(SRC, stage, ignore=lambda d, names: [n for n in names if n.endswith(SKIP_SUFFIX) or n in SKIP_NAMES])
    init = stage / "init.lua"
    text = init.read_text(encoding="utf-8-sig")
    if '["127.0.0.1"]' not in text:
        sys.exit("make_friend_client: init.lua has no 127.0.0.1 server line to replace")
    init.write_text(text.replace('["127.0.0.1"]', f'["{ip}"]'), encoding="utf-8")
    zpath = OUT / "spirebound-client.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in stage.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(stage))
    shutil.rmtree(stage)
    (OUT / "setup.sh").write_text(SETUP.replace("__IP__", ip), encoding="utf-8", newline="\n")
    pw_file = ROOT / ".local" / "grokbot_password.txt"
    if pw_file.exists():                        # the Grok Bot's brief: kept outside the shared folder (it holds a password)
        brief = ROOT / ".local" / "grok_bot_brief.txt"
        brief.write_text(BRIEF.replace("__IP__", ip).replace("__PASSWORD__", pw_file.read_text().strip()), encoding="utf-8")
        print(f"make_friend_client: the Grok Bot brief is in {brief}")
    print(f"make_friend_client: {zpath} ({zpath.stat().st_size // 2**20} MB) and setup.sh, for server {ip}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
