#!/usr/bin/env python3
"""Turn a pinned OTClient (mehah) checkout plus a compiled binary into the Spirebound client folder.

Applies Spirebound's changes to the upstream client tree with exact string replacements that fail
loudly if upstream changed (so a silent mis-patch can never ship):
  - app name "Spirebound"; server list = the Spirebound login server only (protocol 1098)
  - disables the upstream "clientAssets" downloader (it fetches CipSoft client files) — never ship it on
  - RSA public key = ours (both constants, so no code path can fall back to a public test key)
  - things loaded from data/things/1098/Spirebound.dat/.spr built by tools/build_assets.py
  - removes the bot module (mods/game_bot) per 03_TECH_STACK and 17_CLIENT_AND_UI
  - copies Spirebound modules from client/modules/spire_* (when present)
Then verifies that data/things holds only our two files.

Usage:
  python3 tools/package_client.py --otclient <checkout> --binary <otclient.exe or otclient> \
      --host <login host> --rsa <decimal public modulus> --out dist/Spirebound
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def patch(path: Path, old: str, new: str, count: int = 1):
    s = path.read_text(encoding="utf-8")
    n = s.count(old)
    if n != count:
        raise SystemExit(f"package_client: expected {count} occurrence(s) in {path} of:\n{old[:200]}\nfound {n}. "
                         "Upstream changed; update tools/package_client.py.")
    path.write_text(s.replace(old, new), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--otclient", required=True)
    ap.add_argument("--binary", required=True, nargs="+", help="executable plus any DLLs next to it")
    ap.add_argument("--host", required=True)
    ap.add_argument("--rsa", required=True, help="decimal RSA public modulus of the server key")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    src, out = Path(a.otclient), Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for d in ("data", "modules", "mods"):
        shutil.copytree(src / d, out / d)
    for f in ("init.lua", "otclientrc.lua", "config.ini", "LICENSE", "cacert.pem"):
        if (src / f).exists():
            shutil.copy(src / f, out / f)
    for b in a.binary:
        shutil.copy(b, out / Path(b).name)

    # --- init.lua: name, services, servers
    init = out / "init.lua"
    patch(init, 'g_app.setName("OTClient - Redemption");', 'g_app.setName("Spirebound");')
    patch(init, 'g_app.setCompactName("otclient");', 'g_app.setCompactName("spirebound");')
    patch(init, 'g_app.setOrganizationName("otcr");', 'g_app.setOrganizationName("spirebound");')
    s = init.read_text(encoding="utf-8")
    start = s.index("    clientAssets = {")
    end = s.index("}, -- ./client_assets") + len("}, -- ./client_assets")
    s = s[:start] + "    clientAssets = { enabled = false }, -- Spirebound: never download third-party client assets" + s[end:]
    start = s.index("    Servers_init = {")
    end = s.index("\nend", start)
    s = s[:start] + (f'    Servers_init = {{\n        ["{a.host}"] = {{\n            port = 7171,\n'
                     f'            protocol = 1098,\n            httpLogin = false\n        }}\n    }}') + s[end:]
    init.write_text(s, encoding="utf-8")

    # --- RSA
    const = out / "modules" / "gamelib" / "const.lua"
    s = const.read_text(encoding="utf-8")
    for name in ("OTSERV_RSA", "CIPSOFT_RSA"):
        i = s.index(f"{name} = ")
        j = s.index("\n\n", i) if "\n\n" in s[i:] else len(s)
        # constant spans concatenated string lines until the first blank line
        s = s[:i] + f"{name} = '{a.rsa}'  -- Spirebound server key (public modulus)" + s[j:]
    const.write_text(s, encoding="utf-8")

    # --- things file name
    patch(out / "modules" / "game_things" / "things.lua", "local filename = nil", "local filename = '1098/Spirebound'")
    things = out / "data" / "things"
    if things.exists():
        shutil.rmtree(things)
    (things / "1098").mkdir(parents=True)
    build = ROOT / "assets" / "build"
    for f in ("Spirebound.dat", "Spirebound.spr"):
        shutil.copy(build / f, things / "1098" / f)

    # --- remove bot module
    bot = out / "mods" / "game_bot"
    if bot.exists():
        shutil.rmtree(bot)

    # --- our modules
    for m in sorted((ROOT / "client" / "modules").glob("spire_*")):
        shutil.copytree(m, out / "modules" / m.name)

    # --- verify
    found = sorted(p.relative_to(things).as_posix() for p in things.rglob("*") if p.is_file())
    if found != ["1098/Spirebound.dat", "1098/Spirebound.spr"]:
        raise SystemExit(f"package_client: data/things must contain only our files, found {found}")
    if (out / "mods" / "game_bot").exists():
        raise SystemExit("package_client: bot module still present")
    (out / "SPIREBOUND.txt").write_text(
        "Spirebound client. Fan-inspired, unofficial, not affiliated with any rights holder. No pay-to-win.\n"
        "Built from OTClient (mehah fork, MIT license); source and pinned commit in the Spirebound repository.\n")
    print(f"package_client: wrote {out} (things: {found})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
