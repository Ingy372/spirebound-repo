#!/usr/bin/env python3
"""Tiny local login service for Spirebound (development only).

OTClient 4.2 logs in to clients >= 12.81 over HTTP (not the old port-7171 protocol): it POSTs
{"email","password"} and expects the account's character list back as JSON. Canary does not ship
that web part (the real game uses MyAAC/PHP), so on a dev PC this script plays that role.

It checks the account in the same database the game server uses (password = SHA1, like Canary),
and answers with the characters of that account. The session key it hands out ("email\npassword")
is what Canary's game server expects when the client then connects to the game port.

Usage:  python3 tools/login_server.py [port]        (default 8080)
Settings come from the MYSQL_* environment variables (same as the server build).
"""
import hashlib, json, os, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DB = dict(host=os.environ.get("MYSQL_HOST", "127.0.0.1"), user=os.environ.get("MYSQL_USER", "spire"),
          pw=os.environ.get("MYSQL_PASS", "spiretest"), db=os.environ.get("MYSQL_DATABASE", "spirebound"))
GAME_HOST = os.environ.get("SPIRE_GAME_HOST", "127.0.0.1")
GAME_PORT = int(os.environ.get("SPIRE_GAME_PORT", "7172"))
WORLD_NAME = os.environ.get("SPIRE_SERVER_NAME", "Spirebound")  # must equal serverName in config.lua
VOCATIONS = {0: "None", 1: "Arcanist", 2: "Mystic", 3: "Ranger", 4: "Vanguard",
             5: "High Arcanist", 6: "Elder Mystic", 7: "Far Warden", 8: "Blade Warden"}


def sql(query):
    out = subprocess.run(["mysql", f"-h{DB['host']}", f"-u{DB['user']}", f"-p{DB['pw']}", DB["db"], "-N", "-B", "-e", query],
                         capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return [line.split("\t") for line in out.stdout.splitlines() if line]


def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\'")


def login(email, password):
    rows = sql(f"SELECT id, password FROM accounts WHERE (email='{esc(email)}' OR name='{esc(email)}') LIMIT 1")
    if not rows or rows[0][1] != hashlib.sha1(password.encode()).hexdigest():
        return None
    acc = rows[0][0]
    chars = sql("SELECT name, level, vocation, looktype, lookhead, lookbody, looklegs, lookfeet, lookaddons, sex "
                f"FROM players WHERE account_id={int(acc)} AND deletion=0 ORDER BY name")
    return {
        "session": {"sessionkey": f"{email}\n{password}", "lastlogintime": 0, "ispremium": True,
                    "premiumuntil": int(time.time()) + 3650 * 86400, "status": "active",
                    "returnernotification": False, "showrewardnews": False, "isreturner": False,
                    "fpstracking": False, "optiontracking": False, "emailcoderequest": False},
        "playdata": {
            "worlds": [{"id": 0, "name": WORLD_NAME, "externaladdress": GAME_HOST, "externalport": GAME_PORT,
                        "externaladdressprotected": GAME_HOST, "externalportprotected": GAME_PORT,
                        "externaladdressunprotected": GAME_HOST, "externalportunprotected": GAME_PORT,
                        "previewstate": 0, "location": "BRA", "anticheatprotection": False, "pvptype": "pvp",
                        "istournamentworld": False, "restrictedstore": False, "currenttournamentphase": 2}],
            "characters": [{"worldid": 0, "name": c[0], "ismale": c[9] == "1", "tutorial": False, "level": int(c[1]),
                            "vocation": VOCATIONS.get(int(c[2]), "None"), "outfitid": int(c[3]), "headcolor": int(c[4]),
                            "torsocolor": int(c[5]), "legscolor": int(c[6]), "detailcolor": int(c[7]),
                            "addonsflags": int(c[8]), "ishidden": False, "ismaincharacter": False,
                            "dailyrewardstate": 0} for c in chars]}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def reply(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if data.get("type", "login") != "login":
                return self.reply(200, {"errorCode": 1, "errorMessage": "Not supported."})
            res = login(str(data.get("email", "")), str(data.get("password", "")))
            if res is None:
                return self.reply(200, {"errorCode": 3, "errorMessage": "Account name or password is not correct."})
            self.reply(200, res)
        except Exception as e:  # keep the service alive whatever happens
            print("login error:", e, flush=True)
            self.reply(200, {"errorCode": 2, "errorMessage": "Login service error: " + str(e)})

    def do_GET(self):
        self.reply(200, {"service": "Spirebound local login"})


if __name__ == "__main__":
    print(f"Spirebound login service on port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
