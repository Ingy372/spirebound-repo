#!/usr/bin/env python3
"""Assemble a runnable Spirebound server in .build/server/ (Linux) from:

  1. the pinned Canary release binary (server/PINS.env),
  2. Canary's core data/ folder, config.lua.dist and schema.sql at the pinned tag,
  3. our datapack server/data-spirebound/,
  4. our core overrides server/core-overrides/ (copied over data/),
  5. config.lua = config.lua.dist + server/config-overrides.lua.

Third-party files (Canary binary, core data with appearances.dat) are
downloaded into .cache/ and never committed (.cache/ and .build/ are git-ignored).

Usage: python3 tools/build_server.py [--offline]
Database settings: env MYSQL_HOST/USER/PASS/DATABASE, or server/local.env.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
BUILD = ROOT / ".build" / "server"


def read_env(path: Path) -> dict[str, str]:
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


PINS = read_env(ROOT / "server" / "PINS.env")
TAG = PINS["CANARY_TAG"]


def fetch(url: str, dest: Path, offline: bool) -> Path:
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    if offline:
        sys.exit(f"missing {dest} and --offline given")
    print(f"downloading {url}")
    CACHE.mkdir(exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    urllib.request.urlretrieve(url, tmp)
    tmp.rename(dest)
    return dest


def core_data_tgz(offline: bool) -> Path:
    """Canary's data/, config.lua.dist, schema.sql at the pinned tag (sparse clone)."""
    dest = CACHE / f"canary-{TAG.lstrip('v')}-data.tgz"
    if dest.exists():
        return dest
    if offline:
        sys.exit(f"missing {dest} and --offline given")
    work = CACHE / "canary-src"
    if work.exists():
        shutil.rmtree(work)
    git = ["git", "-c", "advice.detachedHead=false"]
    subprocess.check_call(git + ["clone", "-q", "--depth", "1", "--branch", TAG, "--filter=blob:none",
                                 "--sparse", PINS["CANARY_GIT"], str(work)])
    subprocess.check_call(["git", "-C", str(work), "sparse-checkout", "set", "--no-cone",
                           "/data/", "/data-canary/", "/config.lua.dist", "/schema.sql", "/LICENSE"])
    with tarfile.open(dest, "w:gz") as t:
        for name in ("LICENSE", "config.lua.dist", "schema.sql", "data", "data-canary"):
            t.add(work / name, arcname=name)
    shutil.rmtree(work)
    return dest


def apply_overrides(dist: str, overrides_path: Path, values: dict[str, str]) -> str:
    out = dist
    for raw in overrides_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("--") or "=" not in line:
            continue
        key, val = (s.strip() for s in line.split("=", 1))
        for k, v in values.items():
            val = val.replace(f"@{k}@", v)
        if key.startswith("+"):  # a setting that does not exist in config.lua.dist: append it
            out += f"\n{key[1:]} = {val}\n"
            continue
        pat = re.compile(rf"^{re.escape(key)}\s*=.*$", re.M)
        if not pat.search(out):
            sys.exit(f"config override '{key}' is not a setting in Canary's config.lua.dist")
        out = pat.sub(lambda _m: f"{key} = {val}", out, count=1)
    return out


def main(argv: list[str]) -> None:
    offline = "--offline" in argv
    CACHE.mkdir(exist_ok=True)
    zip_path = fetch(PINS["CANARY_LINUX_ZIP"], CACHE / f"canary-{TAG.lstrip('v')}-linux.zip", offline)
    tgz = core_data_tgz(offline)

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(BUILD)
    (BUILD / "canary").chmod(0o755)
    with tarfile.open(tgz) as t:
        t.extractall(BUILD, filter="data") if sys.version_info >= (3, 12) else t.extractall(BUILD)

    # our datapack + core overrides
    shutil.copytree(ROOT / "server" / "data-spirebound", BUILD / "data-spirebound")
    ov = ROOT / "server" / "core-overrides"
    for f in ov.rglob("*"):
        if f.is_file():
            dst = BUILD / "data" / f.relative_to(ov)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)

    # map: ours if compiled, else Canary's small test map as a temporary stand-in
    world = BUILD / "data-spirebound" / "world"
    ours = ROOT / ".build" / "maps" / "spirebound.otbm"
    if ours.exists():
        shutil.copy2(ours, world / "spirebound.otbm")
        for f in (ROOT / ".build" / "maps").glob("spirebound-*.xml"):
            shutil.copy2(f, world / f.name)
        print("map: Spirebound compiled map")
    else:
        shutil.copy2(BUILD / "data-canary" / "world" / "canary.otbm", world / "spirebound.otbm")
        # that map names its side files canary-*.xml; give it our (empty) ones under those names
        for k in ("monster", "npc", "house", "zones"):
            shutil.copy2(world / f"spirebound-{k}.xml", world / f"canary-{k}.xml")
        print("map: TEMPORARY stand-in (Canary test map) until roadmap task 1.8")
    shutil.rmtree(BUILD / "data-canary")

    env = read_env(ROOT / "server" / "local.env")
    values = {k: os.environ.get(k, env.get(k, d)) for k, d in
              (("MYSQL_HOST", "127.0.0.1"), ("MYSQL_USER", "spire"), ("MYSQL_PASS", ""), ("MYSQL_DATABASE", "spirebound"))}
    cfg = apply_overrides((BUILD / "config.lua.dist").read_text(), ROOT / "server" / "config-overrides.lua", values)
    (BUILD / "config.lua").write_text(cfg)
    print(f"built {BUILD}")


if __name__ == "__main__":
    main(sys.argv[1:])
