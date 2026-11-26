#!/usr/bin/env python3
"""Builds the client package for players on Jay's Tailscale network (friends, a Grok Bot): roadmap 9.1.

Copies the installed client (.local/client) without its debug files (about 700 MB of .pdb/.ilk), points it at this
PC's Tailscale address, and zips it to .local/friend/spirebound-client.zip, next to:
  setup.ps1   the Windows installer for friends: one line in PowerShell downloads it, installs it in their user folder,
              adds a desktop shortcut and starts the game (running it again updates the client);
  setup.sh    a Linux installer (Wine) for a Grok Bot's cloud computer;
  index.html  a download page with the steps, at http://<address>:8090/.
It also writes .local/friend_invite.txt: a message Jay can send a friend (Tailscale, the install line, sign-up).
windows\\Share-Client.bat serves the folder on port 8090.
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


# The Windows installer. Friends run:  irm http://__IP__:8090/setup.ps1 | iex
# (SPIRE_DEST / SPIRE_NOLAUNCH / SPIRE_SERVER_URL change where it installs, whether it starts the game and where it
# downloads from: for testing.)
WIN_SETUP = r"""# Spirebound game client installer for Windows (friends on Jay's Tailscale network).
# Run in PowerShell:  irm http://__IP__:8090/setup.ps1 | iex
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'          # much faster downloads in Windows PowerShell
$src  = if ($env:SPIRE_SERVER_URL) { $env:SPIRE_SERVER_URL } else { 'http://__IP__:8090' }
$dest = if ($env:SPIRE_DEST) { $env:SPIRE_DEST } else { Join-Path $env:LOCALAPPDATA 'Spirebound' }
Write-Host ''
Write-Host '  SPIREBOUND - installing the game client' -ForegroundColor Yellow
Write-Host "  Downloading from Jay's server (about 230 MB, a few minutes)..."
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$zip = Join-Path $dest 'client.zip'
try {
    Invoke-WebRequest -UseBasicParsing -Uri "$src/spirebound-client.zip" -OutFile $zip
} catch {
    Write-Host "  Could not reach Jay's server. Is Tailscale connected (its icon by the clock), and is Jay sharing the client right now?" -ForegroundColor Red
    return
}
Write-Host '  Unpacking...'
$client = Join-Path $dest 'client'
if (Test-Path $client) { Remove-Item -Recurse -Force $client }
Expand-Archive -Path $zip -DestinationPath $client -Force
Remove-Item $zip
Get-ChildItem -Recurse $client | Unblock-File
# start in English the first time (skips the language picker); your own settings are kept on updates
$cfgDir = Join-Path $env:APPDATA 'otcr\otclient'
$cfg = Join-Path $cfgDir 'config.otml'
if (-not (Test-Path $cfg)) { New-Item -ItemType Directory -Force -Path $cfgDir | Out-Null; Set-Content -Encoding ASCII -Path $cfg -Value 'locale: en' }
$exe = Join-Path $client 'otclient.exe'
if (-not $env:SPIRE_DEST) {
    $lnk = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Spirebound.lnk'
    $sh = New-Object -ComObject WScript.Shell
    $s = $sh.CreateShortcut($lnk); $s.TargetPath = $exe; $s.WorkingDirectory = $client; $s.Description = 'Spirebound'; $s.Save()
    Write-Host '  Added a Spirebound shortcut to your desktop.'
}
Write-Host ''
Write-Host '  Done! Log in with the account you made on the Spirebound website.' -ForegroundColor Green
Write-Host '  If Windows says it protected your PC, click "More info", then "Run anyway".'
if (-not $env:SPIRE_NOLAUNCH) { Start-Process -FilePath $exe -WorkingDirectory $client }
"""

INDEX = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Get Spirebound</title><style>body{margin:0;background:#0b0907;color:#e9e2d0;font:16px/1.6 "Segoe UI",Tahoma,sans-serif}
.w{max-width:760px;margin:0 auto;padding:24px 16px}h1{font-family:Georgia,serif;color:#ffdf8f;letter-spacing:.1em;font-size:2.2rem;margin:.2em 0}
h2{font-family:Georgia,serif;color:#e9c36a;border-bottom:1px solid #5c4625;padding-bottom:4px}a{color:#e9c36a}
code{display:block;background:#000;border:1px solid #5c4625;border-radius:4px;padding:10px 12px;color:#ffdf8f;font-size:1rem;overflow-x:auto;white-space:nowrap}
.box{background:#1d1813;border:1px solid #5c4625;border-radius:6px;padding:4px 18px 14px;margin:16px 0}li{margin:6px 0}</style></head>
<body><div class="w"><h1>SPIREBOUND</h1><p>Welcome, climber. Three steps and you are in the tower.</p>
<div class="box"><h2>1. Make your account</h2><p>On the website: <a href="http://__IP__:8080/signup">http://__IP__:8080/signup</a>.
Read the rules, pick an account name, a password and your first character's name.</p></div>
<div class="box"><h2>2. Install the game (Windows)</h2><ol><li>Press the Windows key, type <b>PowerShell</b> and open it.</li>
<li>Paste this line and press Enter:<code>irm http://__IP__:8090/setup.ps1 | iex</code></li>
<li>Wait a few minutes. It installs the game, puts a <b>Spirebound</b> shortcut on your desktop and starts it.</li></ol>
<p>Rather do it by hand? Download <a href="spirebound-client.zip">spirebound-client.zip</a>, unzip it anywhere and run <b>otclient.exe</b>.
If Windows says it protected your PC, click <i>More info</i>, then <i>Run anyway</i>.</p></div>
<div class="box"><h2>3. Play</h2><p>Log in with your account name (or e-mail) and password, pick your character, and follow the
stone path in the Arrival Yard. The website has <a href="http://__IP__:8080/how-to-play.html">how to play</a>, the
<a href="http://__IP__:8080/rules.html">rules</a> and the <a href="http://__IP__:8080/hall-of-fame.html">Hall of Fame</a>.</p></div>
<p style="color:#a99f88;font-size:.9rem">On Linux? <code>curl -fsSL http://__IP__:8090/setup.sh | bash</code></p></div></body></html>
"""

INVITE = """Hey! Want to try Spirebound, my Open Tibia server? It isn't public yet, so you join through a private network.

1. Install Tailscale (free): https://tailscale.com/download - and sign in (Google, Microsoft or GitHub is fine).
2. Open this link to get access to my server (it only shows you my game, nothing else of mine):
   PASTE-THE-SHARE-LINK-HERE
3. Make your account: http://__IP__:8080/signup
4. Install the game: open PowerShell (Windows key, type PowerShell) and paste this line:
   irm http://__IP__:8090/setup.ps1 | iex
   It puts a Spirebound shortcut on your desktop. (Everything with pictures: http://__IP__:8090/)
5. Log in, follow the stone path, and tell me what you think!
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


def selftest():
    """The installers and pages are plain ASCII (a BOM or curly quote breaks "irm | iex") and carry the address."""
    for name, text in (("setup.ps1", WIN_SETUP), ("index.html", INDEX), ("setup.sh", SETUP), ("invite", INVITE)):
        text.encode("ascii")
        assert "__IP__" in text, name
    assert "irm http://__IP__:8090/setup.ps1 | iex" in INDEX and "irm http://__IP__:8090/setup.ps1 | iex" in INVITE
    assert "8080/signup" in INDEX and "8080/signup" in INVITE, "friends are sent to the sign-up page"
    assert "Unblock-File" in WIN_SETUP and "Expand-Archive" in WIN_SETUP
    print("make_friend_client selftest: OK")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
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
    # plain ASCII, no BOM: "irm ... | iex" turns a BOM into stray characters on the first line
    (OUT / "setup.ps1").write_text(WIN_SETUP.replace("__IP__", ip), encoding="ascii", newline="\r\n")
    (OUT / "index.html").write_text(INDEX.replace("__IP__", ip), encoding="utf-8")
    invite = ROOT / ".local" / "friend_invite.txt"     # kept outside the shared folder: Jay sends it himself
    invite.write_text(INVITE.replace("__IP__", ip), encoding="utf-8")
    print(f"make_friend_client: a message to send a friend is in {invite} (add your Tailscale share link)")
    pw_file = ROOT / ".local" / "grokbot_password.txt"
    if pw_file.exists():                        # the Grok Bot's brief: kept outside the shared folder (it holds a password)
        brief = ROOT / ".local" / "grok_bot_brief.txt"
        brief.write_text(BRIEF.replace("__IP__", ip).replace("__PASSWORD__", pw_file.read_text().strip()), encoding="utf-8")
        print(f"make_friend_client: the Grok Bot brief is in {brief}")
    print(f"make_friend_client: {zpath} ({zpath.stat().st_size // 2**20} MB) and setup.sh, for server {ip}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
