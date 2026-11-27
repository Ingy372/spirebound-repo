#!/usr/bin/env python3
"""A very light game client for load tests (roadmap 9.2, N2): logs characters in over the real game protocol (15.11,
the same handshake as OTClient) and keeps them connected. It does not draw or read the game: the server-side brain
(server/data-spirebound/scripts/spirebound/dev_loadbot.lua, test servers only) does the hunting. One process holds
hundreds of connections; tools/loadtest.py drives it.

    python3 tools/loadbot.py HOST PORT NAME:TOKEN [NAME:TOKEN ...]     (log some characters in, stay until Ctrl+C)

The session TOKEN is one whose SHA-256 is in account_sessions (tools/loadtest.py makes them in the test database).
Protocol notes (Canary v3.6.1, src/server/network/protocol/*.cpp):
  * every packet: u16 size in 8-byte blocks, u32 sequence number, then the body (XTEA after login);
  * the server opens with a challenge (timestamp + random byte) that the login packet must echo;
  * the login packet carries an RSA block with our XTEA key, the session token and the character name;
  * incoming packets are never decrypted after the first few (saves CPU): the client answers pings blindly.
"""
from __future__ import annotations

import asyncio
import os
import random
import struct
import sys
import time
import zlib
from pathlib import Path

# Canary's built-in RSA key (src/security/rsa.cpp), used when the server has no key.pem (test copies)
P = 14299623962416399520070177382898895550795403345466153217470516082934737582776038882967213386204600674145392845853859217990626450972452084065728686565928113
Q = 7630979195970404721891201847792002125535401292779123937207447574596692788513647179235335529307251350570728407373705564708871762033017096809910315212884101
N = P * Q
E = 65537
VERSION = 1511
OS_OTCLIENT_LINUX = 10
DELTA = 0x9E3779B9
MASK = 0xFFFFFFFF


def xtea(data: bytes, key, encrypt: bool) -> bytes:
    out = bytearray()
    for i in range(0, len(data), 8):
        v0, v1 = struct.unpack_from("<II", data, i)
        if encrypt:
            s = 0
            for _ in range(32):
                v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + key[s & 3]))) & MASK
                s = (s + DELTA) & MASK
                v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + key[(s >> 11) & 3]))) & MASK
        else:
            s = (DELTA * 32) & MASK
            for _ in range(32):
                v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + key[(s >> 11) & 3]))) & MASK
                s = (s - DELTA) & MASK
                v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + key[s & 3]))) & MASK
        out += struct.pack("<II", v0, v1)
    return bytes(out)


def string(s: str) -> bytes:
    b = s.encode("latin-1")
    return struct.pack("<H", len(b)) + b


def adler32(b: bytes) -> int:
    return zlib.adler32(b) & MASK


class Bot:
    def __init__(self, name, token, host, port, stats, script=None):
        """script: optional list of (seconds to wait, "say" or "npc", text) played after login (NPC talk after "hi"
        goes to the NPCs channel, as the real client does)."""
        self.name, self.token, self.host, self.port, self.stats = name, token, host, port, stats
        self.script = script or []
        self.key = [random.getrandbits(32) for _ in range(4)]
        self.seq = 0
        self.state = "new"
        self.error = ""
        self.writer = None

    def frame(self, body: bytes, checksum: int) -> bytes:
        return struct.pack("<HI", (len(body)) // 8, checksum) + body

    def say(self, text, npc=False):
        self.send(b"\x96" + bytes([12 if npc else 1]) + string(text))   # 1 = say, 12 = to the NPC (NPCs channel)

    def send(self, payload: bytes):
        pad = 8 - (len(payload) % 8) - 1
        body = bytes([pad]) + payload + b"\x33" * pad
        enc = xtea(body, self.key, True)
        self.seq = (self.seq + 1) & 0x7FFFFFFF
        self.writer.write(self.frame(enc, self.seq))

    async def read_packet(self, reader):
        h = await reader.readexactly(2)
        size = struct.unpack("<H", h)[0] * 8 + 4
        return await reader.readexactly(size)

    def decode(self, raw: bytes) -> bytes:
        """Decrypt (and inflate) one server packet; only used for the first few, to see the login result."""
        flag = struct.unpack_from("<I", raw)[0]
        body = xtea(raw[4:], self.key, False)
        pad = body[0]
        data = body[1:len(body) - pad]
        if flag & 0x80000000:
            data = zlib.decompressobj(-15).decompress(data)
        return data

    async def run(self, stay: float):
        try:
            reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), 15)
            raw = await asyncio.wait_for(self.read_packet(reader), 15)
            # challenge: [u32 checksum][u8 pad=1][0x1F][u32 timestamp][u8 random][pad]
            if raw[5] != 0x1F:
                raise RuntimeError("no login challenge (got 0x%02x)" % raw[5])
            ts, rnd = struct.unpack_from("<IB", raw, 6)
            rsa = (b"\x00" + struct.pack("<4I", *self.key) + b"\x00" + string(self.token) + string(self.name)
                   + struct.pack("<IB", ts, rnd))
            rsa += bytes(128 - len(rsa))
            rsa = pow(int.from_bytes(rsa, "big"), E, N).to_bytes(128, "big")
            head = (struct.pack("<HHI", OS_OTCLIENT_LINUX, VERSION, VERSION) + string("15.11.loadbot")
                    + string("loadbot") + b"\x00")
            body = b"\x00\x0a" + head + rsa      # [pad byte][protocol id 0x0A], both skipped by the server
            body += bytes((8 - len(body) % 8) % 8)
            self.writer.write(self.frame(body, adler32(body)))
            await self.writer.drain()
            # the first packets tell us whether the login worked
            for _ in range(4):
                data = self.decode(await asyncio.wait_for(self.read_packet(reader), 20))
                if not data:
                    continue
                op = data[0]
                if op == 0x14:                    # login refused, with a message
                    n = struct.unpack_from("<H", data, 1)[0]
                    raise RuntimeError("refused: " + data[3:3 + n].decode("latin-1", "replace"))
                if op == 0x16:                    # waiting list
                    raise RuntimeError("waiting list")
                if op in (0x0A, 0x17, 0x0F, 0x64, 0x6A, 0x1F):
                    self.state = "online"
                    break
            if self.state != "online":
                self.state = "online"             # no refusal: assume we're in (packets are bundled)
            self.stats["online"] += 1

            async def drain_incoming():           # read and drop everything (never cut a packet in half)
                while True:
                    raw = await self.read_packet(reader)
                    self.stats["bytes"] += len(raw) + 2

            drainer = asyncio.create_task(drain_incoming())
            try:
                for wait, kind, text in self.script:
                    await asyncio.sleep(wait)
                    if drainer.done():
                        drainer.result()
                    if kind == "use":                 # use the item at "x y z itemid stackpos" (as a right click does)
                        x, y, z, iid, stack = (int(v) for v in text.split())
                        self.send(bytes([0x82]) + struct.pack("<HHBHBB", x, y, z, iid, stack, 0))
                    elif kind == "usewith":           # use an item lying at one place on another: "fx fy fz itemid stackpos tx ty tz"
                        fx, fy, fz, iid, fs, tx, ty, tz = (int(v) for v in text.split())
                        self.send(bytes([0x83]) + struct.pack("<HHBHB", fx, fy, fz, iid, fs)
                                  + struct.pack("<HHBHB", tx, ty, tz, 0, 0))
                    elif kind == "unsecure":            # fight modes: offensive, stand, secure mode OFF (may attack
                        self.send(bytes([0xA0, 1, 0, 0, 0]))   # unmarked players), pvp mode dove
                    else:
                        self.say(text, npc=(kind == "npc"))
                    await self.writer.drain()
                end = time.time() + stay
                while time.time() < end:
                    if drainer.done():
                        drainer.result()          # raises the reason the connection closed
                    self.send(b"\x1e")            # ping (Game::playerReceivePing): without one every 10 s the server
                    await self.writer.drain()     # drops your target, and after 60 s out of a fight logs you out
                    await asyncio.sleep(4)
                self.send(b"\x14")                # log out
                await self.writer.drain()
                self.state = "done"
            finally:
                drainer.cancel()
        except (asyncio.IncompleteReadError, ConnectionError) as e:
            self.state, self.error = "dropped", repr(e)
        except Exception as e:                    # noqa: BLE001  a load test reports every failure and carries on
            self.state, self.error = "failed", str(e)
        finally:
            if self.state in ("dropped", "failed"):
                self.stats["failed"] += 1
                self.stats["errors"].append(f"{self.name}: {self.error}")
            if self.writer:
                self.writer.close()


async def swarm(host, port, logins, stay, gap=0.6, stats=None):   # see Ban::acceptConnection: >5 connects 0.5 s apart = blocked
    stats = stats if stats is not None else {"online": 0, "failed": 0, "bytes": 0, "errors": []}
    tasks = []
    for name, token in logins:
        tasks.append(asyncio.create_task(Bot(name, token, host, port, stats).run(stay)))
        await asyncio.sleep(gap)
    await asyncio.gather(*tasks)
    return stats


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    host, port = sys.argv[1], int(sys.argv[2])
    logins = [a.split(":", 1) for a in sys.argv[3:]]
    stats = asyncio.run(swarm(host, port, logins, float(os.environ.get("LOADBOT_STAY", "60"))))
    print(stats)


if __name__ == "__main__":
    main()
