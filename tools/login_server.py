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
import hashlib, hmac, json, os, re, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
DB = dict(host=os.environ.get("MYSQL_HOST", "127.0.0.1"), user=os.environ.get("MYSQL_USER", "spire"),
          pw=os.environ.get("MYSQL_PASS", "spiretest"), db=os.environ.get("MYSQL_DATABASE", "spirebound"))
# Which network address to listen on. The default serves this PC (the Windows client reaches WSL through it).
# Before anyone outside this PC connects, put this service behind HTTPS (see REVIEW.md 7.1).
BIND = os.environ.get("SPIRE_LOGIN_BIND", "0.0.0.0")
MAX_BODY = 4096            # bytes: a login request is tiny; anything bigger is refused
MAX_FAILS = 8              # wrong passwords allowed per address ...
FAIL_WINDOW = 5 * 60       # ... within this many seconds, then that address must wait
# Account names / e-mails may only contain these characters (nothing that means something to the database)
NAME_OK = re.compile(r"^[A-Za-z0-9@._+\- ]{1,100}\Z")
GAME_HOST = os.environ.get("SPIRE_GAME_HOST", "127.0.0.1")
GAME_PORT = int(os.environ.get("SPIRE_GAME_PORT", "7172"))
WORLD_NAME = os.environ.get("SPIRE_SERVER_NAME", "Spirebound")  # must equal serverName in config.lua
VOCATIONS = {0: "None", 1: "Arcanist", 2: "Mystic", 3: "Ranger", 4: "Vanguard",
             5: "High Arcanist", 6: "Elder Mystic", 7: "Far Warden", 8: "Blade Warden"}


def sql(query):
    # The password goes in the environment, not on the command line (where other programs could read it)
    out = subprocess.run(["mysql", f"-h{DB['host']}", f"-u{DB['user']}", DB["db"], "-N", "-B", "-e", query],
                         capture_output=True, text=True, timeout=10, env={**os.environ, "MYSQL_PWD": DB["pw"]})
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return [line.split("\t") for line in out.stdout.splitlines() if line]


def valid_name(s):
    """Only plain account names / e-mails are ever put into a database query."""
    return isinstance(s, str) and NAME_OK.match(s) is not None


def hexlit(s):
    """The text as a database hex literal (0x...): no quote or backslash can ever break out of it."""
    return "0x" + s.encode("utf-8").hex()


_fails = {}
_fails_lock = threading.Lock()


def too_many_fails(addr, now=None):
    now = now or time.time()
    with _fails_lock:
        recent = [t for t in _fails.get(addr, []) if now - t < FAIL_WINDOW]
        _fails[addr] = recent
        return len(recent) >= MAX_FAILS


def note_fail(addr, now=None):
    with _fails_lock:
        _fails.setdefault(addr, []).append(now or time.time())


def login(email, password):
    if not valid_name(email) or not password or len(password) > 200:
        return None
    rows = sql(f"SELECT id, password FROM accounts WHERE (email={hexlit(email)} OR name={hexlit(email)}) LIMIT 1")
    if not rows or not hmac.compare_digest(rows[0][1], hashlib.sha1(password.encode()).hexdigest()):
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
        addr = self.client_address[0]
        try:
            size = int(self.headers.get("Content-Length", 0))
            if size < 0 or size > MAX_BODY:
                return self.reply(200, {"errorCode": 2, "errorMessage": "Request too large."})
            data = json.loads(self.rfile.read(size) or b"{}")
            if not isinstance(data, dict) or data.get("type", "login") != "login":
                return self.reply(200, {"errorCode": 1, "errorMessage": "Not supported."})
            if too_many_fails(addr):
                return self.reply(200, {"errorCode": 3, "errorMessage": "Too many wrong passwords. Wait a few minutes and try again."})
            res = login(str(data.get("email", "")), str(data.get("password", "")))
            if res is None:
                note_fail(addr)
                return self.reply(200, {"errorCode": 3, "errorMessage": "Account name or password is not correct."})
            self.reply(200, res)
        except Exception as e:  # keep the service alive whatever happens
            print("login error:", e, flush=True)  # details stay in the server window, not in the reply
            self.reply(200, {"errorCode": 2, "errorMessage": "Login service error. Please try again."})

    def do_GET(self):
        self.reply(200, {"service": "Spirebound local login"})


def selftest():
    """python3 tools/login_server.py --selftest : checks the safety rules without a database."""
    for good in ("jay@localhost", "Test Vanguard", "a.b+c-d_e@x.org"):
        assert valid_name(good), good
    for bad in ("", "x' OR '1'='1", "a;DROP TABLE accounts", "a\\b", 'a"b', "a\nb", "jay\n", "x" * 101, "50%", None, 5):
        assert not valid_name(bad), repr(bad)
    assert hexlit("jay") == "0x6a6179" and "'" not in hexlit("x' OR 1=1 -- ")
    for i in range(MAX_FAILS):
        assert not too_many_fails("t", 1000 + i)
        note_fail("t", 1000 + i)
    assert too_many_fails("t", 1010) and not too_many_fails("other", 1010)
    assert not too_many_fails("t", 1010 + FAIL_WINDOW + 10)
    print("login_server selftest: OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    print(f"Spirebound login service on {BIND}:{PORT}", flush=True)
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
