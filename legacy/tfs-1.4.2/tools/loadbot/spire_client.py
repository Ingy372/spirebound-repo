#!/usr/bin/env python3
"""Minimal headless protocol-10.98 client for Spirebound (seed of tools/loadbot, 16_SCALE_OPS).

Phase 0 use: an automated login smoke test against a running server. It logs in through the login
server, reads the character list, enters the game world, and checks that the server sends the
player's own creature (0x17) and a map description (0x64) at the expected position.

Later phases extend this into the load bot (walk, attack nearest, use salve, say).

Usage:
  python3 tools/loadbot/spire_client.py --host 127.0.0.1 --account test --password test \
      --character "Test Adventurer" --key server/key.pem [--expect 5010,5009,7]
Exit code 0 = logged in and received the map; 1 = failure (reason printed).
"""
from __future__ import annotations

import argparse
import os
import socket
import struct
import subprocess
import sys

VERSION = 1098
OS_OTCLIENT_LINUX = 10
DELTA = 0x9E3779B9
M32 = 0xFFFFFFFF


def adler32(data: bytes) -> int:
    a, b = 1, 0
    for ch in data:
        a = (a + ch) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


def xtea_rounds(key):
    rk, s = [], 0
    for _ in range(32):
        rk.append((s + key[s & 3]) & M32)
        s = (s + DELTA) & M32
        rk.append((s + key[(s >> 11) & 3]) & M32)
    return rk


def xtea_encrypt(data: bytes, rk) -> bytes:
    out = bytearray(data)
    for off in range(0, len(out), 8):
        l, r = struct.unpack_from("<II", out, off)
        for i in range(0, 64, 2):
            l = (l + ((((r << 4) ^ (r >> 5)) + r) ^ rk[i])) & M32
            r = (r + ((((l << 4) ^ (l >> 5)) + l) ^ rk[i + 1])) & M32
        struct.pack_into("<II", out, off, l, r)
    return bytes(out)


def xtea_decrypt(data: bytes, rk) -> bytes:
    out = bytearray(data)
    for off in range(0, len(out), 8):
        l, r = struct.unpack_from("<II", out, off)
        for i in range(63, 0, -2):
            r = (r - ((((l << 4) ^ (l >> 5)) + l) ^ rk[i])) & M32
            l = (l - ((((r << 4) ^ (r >> 5)) + r) ^ rk[i - 1])) & M32
        struct.pack_into("<II", out, off, l, r)
    return bytes(out)


def public_modulus(key_path: str) -> int:
    out = subprocess.check_output(["openssl", "rsa", "-in", key_path, "-noout", "-modulus"], stderr=subprocess.DEVNULL)
    return int(out.decode().strip().split("=")[1], 16)


def rsa_block(payload: bytes, n: int) -> bytes:
    assert len(payload) <= 128 and payload[0] == 0
    m = int.from_bytes(payload.ljust(128, b"\0"), "big")
    return pow(m, 65537, n).to_bytes(128, "big")


def pstr(s: str) -> bytes:
    b = s.encode("latin-1")
    return struct.pack("<H", len(b)) + b


class Conn:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=10)
        self.rk = None

    def recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.s.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("connection closed by server")
            buf += chunk
        return buf

    def send_raw(self, body: bytes):
        self.s.sendall(struct.pack("<H", len(body) + 4) + struct.pack("<I", adler32(body)) + body)

    def read_packet(self) -> bytes:
        ln = struct.unpack("<H", self.recv_exact(2))[0]
        data = self.recv_exact(ln)
        body = data[4:]  # skip checksum
        if self.rk is None:
            return body
        plain = xtea_decrypt(body, self.rk)
        inner = struct.unpack_from("<H", plain, 0)[0]
        return plain[2:2 + inner]


def login(host, account, password, character, key_path, expect=None, login_port=7171, game_port=7172):
    n = public_modulus(key_path)
    key = list(struct.unpack("<4I", os.urandom(16)))
    rk = xtea_rounds(key)

    # ---- login server
    c = Conn(host, login_port)
    head = struct.pack("<HH", OS_OTCLIENT_LINUX, VERSION) + struct.pack("<IIIIB", VERSION, 0, 0, 0, 0)
    b1 = rsa_block(b"\0" + struct.pack("<4I", *key) + pstr(account) + pstr(password), n)
    b2 = rsa_block(b"\0" + pstr("") + b"\0", n)
    c.send_raw(bytes([0x01]) + head + b1 + b2)
    c.rk = rk
    p = c.read_packet()
    i, session, chars, world_ip, world_port = 0, None, [], None, None
    while i < len(p):
        op = p[i]; i += 1
        if op == 0x0B:  # error
            ln = struct.unpack_from("<H", p, i)[0]; return False, "login error: " + p[i + 2:i + 2 + ln].decode("latin-1")
        if op == 0x14:  # motd
            ln = struct.unpack_from("<H", p, i)[0]; i += 2 + ln
        elif op == 0x28:  # session key
            ln = struct.unpack_from("<H", p, i)[0]; session = p[i + 2:i + 2 + ln].decode("latin-1"); i += 2 + ln
        elif op == 0x64:  # character list
            nworlds = p[i]; i += 1
            for _ in range(nworlds):
                i += 1
                ln = struct.unpack_from("<H", p, i)[0]; i += 2 + ln
                ln = struct.unpack_from("<H", p, i)[0]; world_ip = p[i + 2:i + 2 + ln].decode(); i += 2 + ln
                world_port = struct.unpack_from("<H", p, i)[0]; i += 2
                i += 1
            nchars = p[i]; i += 1
            for _ in range(nchars):
                i += 1
                ln = struct.unpack_from("<H", p, i)[0]; chars.append(p[i + 2:i + 2 + ln].decode("latin-1")); i += 2 + ln
            break
        else:
            return False, f"unexpected login opcode 0x{op:02x}"
    c.s.close()
    if character not in chars:
        return False, f"character {character!r} not in list {chars}"

    # ---- game server
    g = Conn(host, game_port)
    ch = g.read_packet()
    if ch[2] != 0x1F:
        return False, f"expected challenge 0x1F, got {ch[:8].hex()}"
    ts, rnd = struct.unpack_from("<IB", ch, 3)
    head = struct.pack("<HH", OS_OTCLIENT_LINUX, VERSION) + struct.pack("<IBH", VERSION, 0, 0)
    blk = b"\0" + struct.pack("<4I", *key) + b"\0" + pstr(session) + pstr(character) + struct.pack("<IB", ts, rnd)
    g.send_raw(bytes([0x0A]) + head + rsa_block(blk, n))  # 0x0A: game protocol id
    g.rk = rk
    got_self = got_map = False
    pos = None
    for _ in range(20):
        try:
            p = g.read_packet()
        except (socket.timeout, ConnectionError) as e:
            if got_self and got_map:
                break
            return False, f"game connection: {e}"
        j = 0
        while j < len(p):  # walk the opcodes we know; stop at the first one we do not
            op = p[j]
            if op == 0x14:
                ln = struct.unpack_from("<H", p, j + 1)[0]
                return False, "game error: " + p[j + 3:j + 3 + ln].decode("latin-1")
            if op == 0x32:  # extended opcode notice: u8 opcode, u16 length, payload
                ln = struct.unpack_from("<H", p, j + 2)[0]; j += 4 + ln
            elif op == 0x17:  # self appear: id u32, beat u16, 3 doubles (5 bytes each), 3 flags, u16, u16
                got_self = True; j += 1 + 4 + 2 + 15 + 3 + 2 + 2
            elif op in (0x0A, 0x0F):  # pending state, enter world
                j += 1
            elif op == 0x64:  # map description starts with the player's position
                got_map = True; pos = struct.unpack_from("<HHB", p, j + 1); break
            elif op == 0x1D:  # ping: not answered; the smoke test disconnects before the server's ping timeout
                break
            else:
                break
        if got_self and got_map:
            break
    g.s.close()
    if not (got_self and got_map):
        return False, f"login incomplete (self={got_self}, map={got_map})"
    if expect and tuple(pos) != tuple(expect):
        return False, f"entered game at {pos}, expected {expect}"
    return True, f"logged in as {character!r} at {pos} via {world_ip}:{world_port}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--account", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--character", required=True)
    ap.add_argument("--key", required=True, help="server key.pem (public modulus is read from it)")
    ap.add_argument("--expect", help="x,y,z")
    a = ap.parse_args()
    exp = tuple(int(v) for v in a.expect.split(",")) if a.expect else None
    ok, msg = login(a.host, a.account, a.password, a.character, a.key, exp)
    print(("PASS: " if ok else "FAIL: ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
