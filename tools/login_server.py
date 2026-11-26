#!/usr/bin/env python3
"""Tiny local login service for Spirebound (development only).

OTClient 4.2 logs in to clients >= 12.81 over HTTP (not the old port-7171 protocol): it POSTs
{"email","password"} and expects the account's character list back as JSON. Canary does not ship
that web part (the real game uses MyAAC/PHP), so on a dev PC this script plays that role.

It checks the account in the same database the game server uses (password = SHA1, like Canary),
and answers with the characters of that account. The session key it hands out is a fresh random token
(roadmap R4): only its SHA-256 goes into the database (account_sessions), and the game server
(authType = "session") lets the client in with it for 24 hours. The password is never sent back.

It also serves a small sign-up page at /signup so friends can make their own account, the rules at /rules, a page to
make another character at /newchar, account security at /security (two-step login, new password), and the
website itself at / (tools/gen_site.py's pages, rebuilt every 5 minutes
from the game's records by tools/site_snapshot.py into .local/site). Every new account and character name goes
through tools/name_rules.py, and players must agree to the rules.

Usage:  python3 tools/login_server.py [port]        (default 8080)
Settings come from the MYSQL_* environment variables (same as the server build).
"""
import hashlib, hmac, html, json, os, re, secrets, subprocess, sys, threading, time
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_site  # noqa: E402  the website's frame, shared by the sign-up pages
import site_snapshot  # noqa: E402  the website's live pages (Hall of Fame, characters, online...)
import account_security as sec  # noqa: E402  password storage, password rules, two-step codes
import name_rules  # noqa: E402  the name checker (rude words, names from other games, staff titles, our NPCs)
import player_rules  # noqa: E402  the rulebook new players agree to

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
DB = dict(host=os.environ.get("MYSQL_HOST", "127.0.0.1"), user=os.environ.get("MYSQL_USER", "spire"),
          pw=os.environ.get("MYSQL_PASS", "spiretest"), db=os.environ.get("MYSQL_DATABASE", "spirebound"))
# Which network address to listen on. The default serves this PC (the Windows client reaches WSL through it).
# Before anyone outside this PC connects, put this service behind HTTPS (see REVIEW.md 7.1).
# Only this PC by default (REVIEW 7.1). Set SPIRE_LOGIN_BIND only once the friend tunnel (roadmap 9.1) exists.
BIND = os.environ.get("SPIRE_LOGIN_BIND", "127.0.0.1")
SESSION_HOURS = 24
MAX_CHARACTERS = 10        # characters per account (Claude's call; extra characters are welcome, Jay 2026-11-25)
ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / ".local" / "site"           # the live website (has player names: never committed)
PUBLIC_DIR = ROOT / "website" / "public"      # the plain website, used until the first live build
SITE_REFRESH = 300                            # seconds between website rebuilds
PAGE_NAME = re.compile(r"^/((?:img/)?[a-z0-9_-]{1,60}\.(html|css|gif|png))\Z")
TYPES = {"html": "text/html; charset=utf-8", "css": "text/css", "gif": "image/gif", "png": "image/png"}
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


def new_session(acc, now=None):
    """A random session token for the account; only its SHA-256 is stored. Old, expired tokens are cleared."""
    now = int(now or time.time())
    token = secrets.token_urlsafe(32)
    sql(f"DELETE FROM account_sessions WHERE account_id={int(acc)} AND expires < {now}")
    sql(f"INSERT INTO account_sessions (id, account_id, expires) VALUES "
        f"({hexlit(hashlib.sha256(token.encode()).hexdigest())}, {int(acc)}, {now + SESSION_HOURS * 3600})")
    return token


def game_host_for(host_header):
    """The game address to hand a client: the one it reached us on, if that is a Tailscale address (100.64.0.0/10, the
    friend-access network; roadmap 9.1), else this PC. Anything else falls back to GAME_HOST."""
    host = (host_header or "").rsplit(":", 1)[0].strip("[]")
    parts = host.split(".")
    if len(parts) == 4 and all(p.isdigit() and int(p) < 256 for p in parts) and parts[0] == "100" and 64 <= int(parts[1]) <= 127:
        return host
    return GAME_HOST


def check_account(account, password):
    """The account id if the password is right, else None. An old SHA1 password is upgraded to the strong format."""
    if not valid_name(account) or not password or len(password) > 200:
        return None
    rows = sql(f"SELECT id, password FROM accounts WHERE (email={hexlit(account)} OR name={hexlit(account)}) LIMIT 1")
    if not rows:
        sec.hash_password(password)                  # same time either way: no hint whether the account exists
        return None
    ok, upgrade = sec.check_password(rows[0][1], password)
    if not ok:
        return None
    if upgrade:
        sql(f"UPDATE accounts SET password={hexlit(sec.hash_password(password))} WHERE id={int(rows[0][0])}")
    return int(rows[0][0])


TWO_FACTOR_TABLE = ("CREATE TABLE IF NOT EXISTS spirebound_twofactor (account_id INT UNSIGNED NOT NULL PRIMARY KEY, "
                    "secret VARCHAR(64) NOT NULL, last_step BIGINT NOT NULL DEFAULT 0, backup TEXT NOT NULL, created BIGINT NOT NULL)")
_table_ready = []


def two_factor(acc):
    """(secret, last used step, [hashed backup codes]) if the account has two-step login on, else None."""
    if not _table_ready:
        sql(TWO_FACTOR_TABLE)
        _table_ready.append(True)
    rows = sql(f"SELECT secret, last_step, backup FROM spirebound_twofactor WHERE account_id={int(acc)}")
    if not rows:
        return None
    return rows[0][0], int(rows[0][1]), [b for b in rows[0][2].split(",") if b]


def check_second_step(acc, code, now=None):
    """True if the account has no two-step login, or the code (or an unused backup code) is right. Uses it up."""
    tf = two_factor(acc)
    if tf is None:
        return True
    secret, last, backups = tf
    step = sec.check_code(secret, code, now=now, last_step=last)
    if step >= 0:
        sql(f"UPDATE spirebound_twofactor SET last_step={step} WHERE account_id={int(acc)}")
        return True
    h = sec.hash_backup(code or "")
    if code and h in backups:
        backups.remove(h)
        sql(f"UPDATE spirebound_twofactor SET backup={hexlit(','.join(backups))} WHERE account_id={int(acc)}")
        return True
    return False


def login(email, password, game_host=None, token=""):
    game_host = game_host or GAME_HOST
    acc = check_account(email, password)
    if acc is None:
        return None
    if two_factor(acc) is not None:
        if not token:
            return {"errorCode": 6, "errorMessage": "Enter the 6-digit code from your authenticator app."}
        if not check_second_step(acc, token):
            return {"errorCode": 6, "errorMessage": "That code is not right. Codes change every 30 seconds.", "wrongCode": True}
    chars = sql("SELECT name, level, vocation, looktype, lookhead, lookbody, looklegs, lookfeet, lookaddons, sex "
                f"FROM players WHERE account_id={int(acc)} AND deletion=0 ORDER BY name")
    return {
        "session": {"sessionkey": new_session(acc), "lastlogintime": 0, "ispremium": True,
                    "premiumuntil": int(time.time()) + 3650 * 86400, "status": "active",
                    "returnernotification": False, "showrewardnews": False, "isreturner": False,
                    "fpstracking": False, "optiontracking": False, "emailcoderequest": False},
        "playdata": {
            "worlds": [{"id": 0, "name": WORLD_NAME, "externaladdress": game_host, "externalport": GAME_PORT,
                        "externaladdressprotected": game_host, "externalportprotected": GAME_PORT,
                        "externaladdressunprotected": game_host, "externalportunprotected": GAME_PORT,
                        "previewstate": 0, "location": "BRA", "anticheatprotection": False, "pvptype": "pvp",
                        "istournamentworld": False, "restrictedstore": False, "currenttournamentphase": 2}],
            "characters": [{"worldid": 0, "name": c[0], "ismale": c[9] == "1", "tutorial": False, "level": int(c[1]),
                            "vocation": VOCATIONS.get(int(c[2]), "None"), "outfitid": int(c[3]), "headcolor": int(c[4]),
                            "torsocolor": int(c[5]), "legscolor": int(c[6]), "detailcolor": int(c[7]),
                            "addonsflags": int(c[8]), "ishidden": False, "ismaincharacter": False,
                            "dailyrewardstate": 0} for c in chars]}}


NAME_RULE = re.compile(r"^[A-Za-z0-9]{3,20}\Z")
EMAIL_RULE = re.compile(r"^[A-Za-z0-9._+\-]{1,60}@[A-Za-z0-9.\-]{1,60}\.[A-Za-z]{2,10}\Z")
_signups = {}


# A character name: 1-3 capitalised words of letters, 3-20 characters in all (e.g. "Mira", "Tom Reed")
CHAR_RULE = re.compile(r"^[A-Z][a-z]+( [A-Z][a-z]+){0,2}\Z")
# A fresh character, the same as the dev account's "Climber": level 1, no vocation yet (picked at the Registrar),
# in Hearthgate (town 1). Outfit 128 = male citizen, 136 = female citizen.
NEW_CHAR = ("INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience, lookbody, "
            "lookfeet, lookhead, looklegs, looktype, mana, manamax, town_id, conditions, cap, sex) VALUES "
            "({name}, 1, {acc}, 1, 0, 150, 150, 0, 68, 76, 78, 58, {look}, 55, 55, 1, '', 400, {sex})")


def signup(name, email, password, password2, addr, now=None, character="", sex="1", agree=False):
    """Make a new account with its first character (a new account had no way to make one: the client has no
    create-character button). Returns (ok, message)."""
    now = now or time.time()
    recent = [t for t in _signups.get(addr, []) if now - t < 3600]
    if len(recent) >= 3:
        return False, "You have made three accounts in the last hour. Please wait."
    if not NAME_RULE.match(name or ""):
        return False, "The account name must be 3 to 20 letters or digits."
    ok, why = name_rules.check_account(name)
    if not ok:
        return False, why
    if not EMAIL_RULE.match(email or ""):
        return False, "Please give a real e-mail address."
    problem = sec.password_problem(password or "", name, email, character)
    if problem:
        return False, problem
    if password != password2:
        return False, "The two passwords are not the same."
    character = " ".join((character or "").split())
    if not (3 <= len(character) <= 20 and CHAR_RULE.match(character)):
        return False, "The character name must be 3 to 20 letters, each word starting with a capital (e.g. Mira or Tom Reed)."
    ok, why = name_rules.check_character(character)
    if not ok:
        return False, why
    if sex not in ("0", "1"):
        return False, "Please pick male or female."
    if not agree:
        return False, "Please read the rules and tick the box to agree to them."
    if sql(f"SELECT id FROM accounts WHERE name={hexlit(name)} OR email={hexlit(email)} LIMIT 1"):
        return False, "That account name or e-mail is already taken."
    if sql(f"SELECT id FROM players WHERE name={hexlit(character)} LIMIT 1"):
        return False, "That character name is already taken."
    sql("INSERT INTO accounts (name, email, password, type, creation) VALUES "
        f"({hexlit(name)}, {hexlit(email)}, {hexlit(sec.hash_password(password))}, 1, {int(now)})")
    acc = sql(f"SELECT id FROM accounts WHERE name={hexlit(name)} LIMIT 1")
    sql(NEW_CHAR.format(name=hexlit(character), acc=int(acc[0][0]) if acc else 0, look=128 if sex == "1" else 136, sex=int(sex)))
    _signups.setdefault(addr, []).append(now)
    return True, f"Account {name} is ready with your character {character}. Log in with it in the game client."


_newchars = {}


def new_character(account, password, character, sex, addr, agree=False, now=None, code=""):
    """Make another character on an existing account (roadmap 7.1). Returns (ok, message)."""
    now = now or time.time()
    if too_many_fails(addr, now):
        return False, "Too many wrong passwords. Wait a few minutes and try again."
    recent = [t for t in _newchars.get(addr, []) if now - t < 3600]
    if len(recent) >= 5:
        return False, "You have made five characters in the last hour. Please wait."
    acc = check_account(account, password)
    if acc is None:
        note_fail(addr, now)
        return False, "Account name or password is not correct."
    if not check_second_step(acc, code):
        note_fail(addr, now)
        return False, "This account has two-step login: enter the code from your authenticator app (or a backup code)."
    character = " ".join((character or "").split())
    if not (3 <= len(character) <= 20 and CHAR_RULE.match(character)):
        return False, "The character name must be 3 to 20 letters, each word starting with a capital (e.g. Mira or Tom Reed)."
    ok, why = name_rules.check_character(character)
    if not ok:
        return False, why
    if sex not in ("0", "1"):
        return False, "Please pick male or female."
    if not agree:
        return False, "Please read the rules and tick the box to agree to them."
    have = sql(f"SELECT COUNT(*) FROM players WHERE account_id={acc} AND deletion=0")
    if have and int(have[0][0]) >= MAX_CHARACTERS:
        return False, f"An account can hold {MAX_CHARACTERS} characters."
    if sql(f"SELECT id FROM players WHERE name={hexlit(character)} LIMIT 1"):
        return False, "That character name is already taken."
    sql(NEW_CHAR.format(name=hexlit(character), acc=acc, look=128 if sex == "1" else 136, sex=int(sex)))
    _newchars.setdefault(addr, []).append(now)
    return True, f"{character} is ready. Log in with your account in the game client and pick {character} from the list."


NEWCHAR_FORM = """<p>Extra characters are welcome: up to 10 on one account, and they can hunt anywhere.</p>
{msg}<form class="form" method="post" action="/newchar">
<label>Account name or e-mail<input name="account" value="{account}"></label>
<label>Password<input name="password" type="password"></label>
<label>Two-step code (only if you switched two-step login on)<input name="code" autocomplete="one-time-code" inputmode="numeric"></label>
<label>New character's name (e.g. Mira or Tom Reed)<input name="character" value="{character}"></label>
<p><label class="choice"><input name="sex" type="radio" value="1" checked> Male</label>
<label class="choice"><input name="sex" type="radio" value="0"> Female</label></p>
<p><label class="choice"><input name="agree" type="checkbox" value="yes" required> I have read the
<a href="rules.html" target="_blank">rules</a> and agree to them</label></p>
<button class="btn">Make character</button></form>
<p>No account yet? <a href="/signup">Create one</a>.</p>"""


def newchar_page(msg="", account="", character=""):
    box = f'<p class="msg">{html.escape(msg)}</p>' if msg else ""
    return gen_site.shell("Make another character", NEWCHAR_FORM.format(
        msg=box, account=html.escape(account), character=html.escape(character)))


_pending = {}                 # setup token -> (account id, account name, secret, expires): two-step login being switched on
SETUP_MINUTES = 10


def security_page(msg="", account="", extra=""):
    box = f'<p class="msg">{html.escape(msg)}</p>' if msg else ""
    a = html.escape(account)
    body = f"""{box}{extra}
<h2>Two-step login</h2>
<p>With two-step login on, logging in needs your password <b>and</b> a 6-digit code from an authenticator app on your
phone (Google Authenticator, Microsoft Authenticator, Authy or any other). Someone who learns your password still
cannot get in. The game client asks for the code after your password.</p>
<form class="form" method="post" action="/security"><input type="hidden" name="do" value="start">
<label>Account name or e-mail<input name="account" value="{a}"></label>
<label>Password<input name="password" type="password"></label>
<button class="btn">Switch two-step login on</button></form>
<h3>Switch it off</h3>
<form class="form" method="post" action="/security"><input type="hidden" name="do" value="off">
<label>Account name or e-mail<input name="account" value="{a}"></label>
<label>Password<input name="password" type="password"></label>
<label>Code from your app, or a backup code<input name="code" autocomplete="one-time-code"></label>
<button class="btn small">Switch two-step login off</button></form>
<h2>Change your password</h2>
<form class="form" method="post" action="/security"><input type="hidden" name="do" value="password">
<label>Account name or e-mail<input name="account" value="{a}"></label>
<label>Current password<input name="password" type="password"></label>
<label>Two-step code (only if it is on)<input name="code" autocomplete="one-time-code" inputmode="numeric"></label>
<label>New password (at least 8 characters; a few unrelated words make a strong one)<input name="new" type="password"></label>
<label>New password again<input name="new2" type="password"></label>
<button class="btn small">Change password</button></form>
<p>Lost your phone? Use one of your backup codes in place of the app's code, then switch two-step login off and on
again. Lost those too? Ask a gamemaster.</p>"""
    return gen_site.shell("Account security", body)


def security_post(form, addr, now=None):
    """The /security forms: switch two-step login on (two stages), off, or change the password. Returns the page."""
    now = now or time.time()
    do, account = form.get("do", ""), form.get("account", "")
    if do == "confirm":
        token = form.get("setup", "")
        pending = _pending.get(token)
        if not pending or pending[3] < now:
            _pending.pop(token, None)
            return security_page("That setup took too long. Please start again.")
        acc, name, secret, _exp = pending
        step = sec.check_code(secret, form.get("code", ""), now=now)
        if step < 0:
            note_fail(addr, now)
            return security_page("That code is not right. Check the key you typed, and that your phone's clock is correct.", name,
                                 setup_box(token, secret, name))
        codes = sec.backup_codes()
        two_factor(acc)                                # makes sure the table exists
        sql(f"DELETE FROM spirebound_twofactor WHERE account_id={acc}")
        sql("INSERT INTO spirebound_twofactor (account_id, secret, last_step, backup, created) VALUES "
            f"({acc}, {hexlit(secret)}, {step}, {hexlit(','.join(sec.hash_backup(c) for c in codes))}, {int(now)})")
        _pending.pop(token, None)
        listed = "".join(f"<li><code>{c}</code></li>" for c in codes)
        return security_page("Two-step login is on. From now on the game asks for your app's code after your password.", name,
                             f'<div class="card"><b>Your backup codes.</b> Each works once, in place of the app\'s code, if you '
                             f'lose your phone. Write them down now: they are not shown again.<ul>{listed}</ul></div>')
    if too_many_fails(addr, now):
        return security_page("Too many wrong tries. Wait a few minutes and try again.", account)
    acc = check_account(account, form.get("password", ""))
    if acc is None:
        note_fail(addr, now)
        return security_page("Account name or password is not correct.", account)
    if do == "start":
        if two_factor(acc) is not None:
            return security_page("Two-step login is already on for this account.", account)
        for t in [t for t, p in _pending.items() if p[3] < now]:
            _pending.pop(t, None)
        token, secret = secrets.token_urlsafe(24), sec.new_secret()
        _pending[token] = (acc, account, secret, now + SETUP_MINUTES * 60)
        return security_page("", account, setup_box(token, secret, account))
    if do == "off":
        if two_factor(acc) is None:
            return security_page("Two-step login is not on for this account.", account)
        if not check_second_step(acc, form.get("code", ""), now=now):
            note_fail(addr, now)
            return security_page("That code is not right.", account)
        sql(f"DELETE FROM spirebound_twofactor WHERE account_id={acc}")
        return security_page("Two-step login is off. Logging in needs only your password now.", account)
    if do == "password":
        if not check_second_step(acc, form.get("code", ""), now=now):
            note_fail(addr, now)
            return security_page("This account has two-step login: enter the code from your app.", account)
        new = form.get("new", "")
        names = [r[0] for r in sql(f"SELECT name FROM players WHERE account_id={acc}")]
        problem = sec.password_problem(new, account, *names)
        if problem:
            return security_page(problem, account)
        if new != form.get("new2", ""):
            return security_page("The two new passwords are not the same.", account)
        sql(f"UPDATE accounts SET password={hexlit(sec.hash_password(new))} WHERE id={acc}")
        sql(f"DELETE FROM account_sessions WHERE account_id={acc}")      # log out everywhere else
        return security_page("Your password is changed. Use the new one next time you log in.", account)
    return security_page()


def setup_box(token, secret, account):
    return f"""<div class="card"><b>Step 1.</b> In your authenticator app, add an account and choose <i>enter a setup key</i>.
Name it Spirebound and type this key (spaces don't matter):<p style="font-size:1.3rem;letter-spacing:.08em"><code>{sec.pretty_secret(secret)}</code></p>
<b>Step 2.</b> Type the 6-digit code the app now shows, within {SETUP_MINUTES} minutes:
<form class="form" method="post" action="/security"><input type="hidden" name="do" value="confirm">
<input type="hidden" name="setup" value="{html.escape(token)}">
<label>Code from the app<input name="code" autocomplete="one-time-code" inputmode="numeric"></label>
<button class="btn">Switch it on</button></form></div>"""


def refresh_site():
    """Rebuild the live website from the game's records; a failure keeps the last good pages."""
    try:
        site_snapshot.build_site(sql, SITE_DIR, "/signup")
    except Exception as e:  # never take the login service down over the website
        print("website refresh failed:", e, flush=True)


def site_loop():
    while True:
        refresh_site()
        time.sleep(SITE_REFRESH)


def site_file(path):
    """(bytes, content type) for a website page, or None. Only plain page names: no folders, nothing else on disk."""
    path = path.split("?", 1)[0]
    if path == "/":
        path = "/index.html"
    m = PAGE_NAME.match(path)
    if not m:
        return None
    for folder in (SITE_DIR, PUBLIC_DIR):
        f = folder / m.group(1)
        if f.is_file():
            return f.read_bytes(), TYPES[m.group(2)]
    return None


SIGNUP_FORM = """<p>One account holds all your characters. You pick your vocation in the game, at the end of a short
guided start, not here.</p>
{msg}<form class="form" method="post" action="/signup">
<label>Account name (3-20 letters or digits; only you see it)<input name="name" value="{name}"></label>
<label>E-mail<input name="email" type="email" value="{email}"></label>
<label>Password (at least 8 characters)<input name="password" type="password"></label>
<label>Password again<input name="password2" type="password"></label>
<label>Your first character's name (e.g. Mira or Tom Reed)<input name="character" value="{character}"></label>
<p><label class="choice"><input name="sex" type="radio" value="1" checked> Male</label>
<label class="choice"><input name="sex" type="radio" value="0"> Female</label></p>
<p><label class="choice"><input name="agree" type="checkbox" value="yes" required> I have read the
<a href="rules.html" target="_blank">rules</a> and agree to them</label></p>
<button class="btn">Create account</button></form>
<p>Already have an account? <a href="/newchar">Make another character</a>.</p>"""


def rules_page():
    """The rules in the website's frame (the same page as rules.html)."""
    return gen_site.shell("Rules", player_rules.to_html({"pvp": "pvp.html", "modes": "modes.html", "ledger": "exile-ledger.html"}),
                          "rules.html")


def signup_page(msg="", name="", email="", character=""):
    box = f'<p class="msg">{html.escape(msg)}</p>' if msg else ""
    return gen_site.shell("Create your account", SIGNUP_FORM.format(
        msg=box, name=html.escape(name), email=html.escape(email), character=html.escape(character)))


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

    def page(self, text, ctype="text/html; charset=utf-8"):
        body = text if isinstance(text, bytes) else text.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        addr = self.client_address[0]
        if self.path.split("?", 1)[0] in ("/newchar", "/newchar/"):
            try:
                size = int(self.headers.get("Content-Length", 0))
                if size < 0 or size > MAX_BODY:
                    return self.page(newchar_page("That request was too large."))
                form = {k: v[0] for k, v in parse_qs(self.rfile.read(size).decode("utf-8", "replace")).items()}
                ok, msg = new_character(form.get("account", ""), form.get("password", ""), form.get("character", ""),
                                        form.get("sex", "1"), addr, agree=form.get("agree") == "yes", code=form.get("code", ""))
                return self.page(newchar_page(msg, form.get("account", ""), "" if ok else form.get("character", "")))
            except Exception as e:
                print("newchar error:", e, flush=True)
                return self.page(newchar_page("Something went wrong. Please try again."))
        if self.path.split("?", 1)[0] in ("/security", "/security/"):
            try:
                size = int(self.headers.get("Content-Length", 0))
                if size < 0 or size > MAX_BODY:
                    return self.page(security_page("That request was too large."))
                form = {k: v[0] for k, v in parse_qs(self.rfile.read(size).decode("utf-8", "replace")).items()}
                return self.page(security_post(form, addr))
            except Exception as e:
                print("security error:", e, flush=True)
                return self.page(security_page("Something went wrong. Please try again."))
        if self.path.split("?", 1)[0] in ("/signup", "/signup/"):
            try:
                size = int(self.headers.get("Content-Length", 0))
                if size < 0 or size > MAX_BODY:
                    return self.page(signup_page("That request was too large."))
                form = {k: v[0] for k, v in parse_qs(self.rfile.read(size).decode("utf-8", "replace")).items()}
                ok, msg = signup(form.get("name", ""), form.get("email", ""), form.get("password", ""), form.get("password2", ""), addr,
                                 character=form.get("character", ""), sex=form.get("sex", "1"), agree=form.get("agree") == "yes")
                keep = (lambda k: "" if ok else form.get(k, ""))
                return self.page(signup_page(msg, keep("name"), keep("email"), keep("character")))
            except Exception as e:
                print("signup error:", e, flush=True)
                return self.page(signup_page("Something went wrong. Please try again."))
        try:
            size = int(self.headers.get("Content-Length", 0))
            if size < 0 or size > MAX_BODY:
                return self.reply(200, {"errorCode": 2, "errorMessage": "Request too large."})
            data = json.loads(self.rfile.read(size) or b"{}")
            if not isinstance(data, dict) or data.get("type", "login") != "login":
                return self.reply(200, {"errorCode": 1, "errorMessage": "Not supported."})
            if too_many_fails(addr):
                return self.reply(200, {"errorCode": 3, "errorMessage": "Too many wrong passwords. Wait a few minutes and try again."})
            token = str(data.get("token") or data.get("authenticatorToken") or "")
            res = login(str(data.get("email", "")), str(data.get("password", "")), game_host_for(self.headers.get("Host")), token)
            if res is None:
                note_fail(addr)
                return self.reply(200, {"errorCode": 3, "errorMessage": "Account name or password is not correct."})
            if res.pop("wrongCode", False):
                note_fail(addr)
            self.reply(200, res)
        except Exception as e:  # keep the service alive whatever happens
            print("login error:", e, flush=True)  # details stay in the server window, not in the reply
            self.reply(200, {"errorCode": 2, "errorMessage": "Login service error. Please try again."})

    def do_GET(self):
        if self.path.split("?", 1)[0] in ("/signup", "/signup/"):
            return self.page(signup_page())
        if self.path.split("?", 1)[0] in ("/rules", "/rules/"):
            return self.page(rules_page())
        if self.path.split("?", 1)[0] in ("/newchar", "/newchar/"):
            return self.page(newchar_page())
        if self.path.split("?", 1)[0] in ("/security", "/security/"):
            return self.page(security_page())
        found = site_file(self.path)
        if found:
            return self.page(*found)
        self.reply(200, {"service": "Spirebound local login"})


def selftest_security():
    """Two-step login and password changes against a small pretend database (no real database needed)."""
    import re as _re
    global sql
    real = sql
    unhex = lambda s: bytes.fromhex(s[2:]).decode() if s.startswith("0x") else s  # noqa: E731
    db = {"pw": hashlib.sha1(b"old pass word").hexdigest(), "tf": None, "sessions": 1}

    def fake(q):
        if q.startswith("SELECT id, password FROM accounts"):
            return [["7", db["pw"]]] if "0x" + "tomr".encode().hex() in q else []
        m = _re.match(r"UPDATE accounts SET password=(0x[0-9a-f]+) WHERE id=7", q)
        if m:
            db["pw"] = unhex(m.group(1)); return []
        if q.startswith("CREATE TABLE"):
            return []
        if q.startswith("SELECT secret"):
            return [list(map(str, db["tf"]))] if db["tf"] else []
        m = _re.match(r"INSERT INTO spirebound_twofactor .* VALUES \(7, (0x[0-9a-f]+), (\d+), (0x[0-9a-f]*), \d+\)", q)
        if m:
            db["tf"] = [unhex(m.group(1)), int(m.group(2)), unhex(m.group(3)) if len(m.group(3)) > 2 else ""]; return []
        if q.startswith("DELETE FROM spirebound_twofactor"):
            db["tf"] = None; return []
        m = _re.match(r"UPDATE spirebound_twofactor SET last_step=(\d+)", q)
        if m:
            db["tf"][1] = int(m.group(1)); return []
        m = _re.match(r"UPDATE spirebound_twofactor SET backup=(0x[0-9a-f]*)", q)
        if m:
            db["tf"][2] = unhex(m.group(1)) if len(m.group(1)) > 2 else ""; return []
        if q.startswith("SELECT name FROM players"):
            return [["Tom Reed"]]
        if q.startswith("DELETE FROM account_sessions"):
            db["sessions"] = 0; return []
        return []
    sql = fake
    _fails.clear()
    _pending.clear()
    try:
        # an old SHA1 password works once and is upgraded on the spot
        assert check_account("tomr", "old pass word") == 7 and db["pw"].startswith("pbkdf2$"), "old passwords are upgraded"
        assert check_account("tomr", "old pass word") == 7 and check_account("tomr", "wrong") is None
        assert check_account("nobody", "old pass word") is None
        # switch two-step login on: password, then a code from the app
        page = security_post({"do": "start", "account": "tomr", "password": "old pass word"}, "a", now=1000.0)
        token, secret = next(iter(_pending.items()))[0], next(iter(_pending.values()))[2]
        assert sec.pretty_secret(secret) in page and db["tf"] is None, "the key is shown, nothing is on yet"
        page = security_post({"do": "confirm", "setup": token, "code": "000000"}, "a", now=1001.0)
        assert db["tf"] is None and "not right" in page
        page = security_post({"do": "confirm", "setup": token, "code": sec.code_at(secret, 1002.0)}, "a", now=1002.0)
        assert db["tf"] and "backup codes" in page, "two-step login is on, backup codes shown once"
        assert check_second_step(7, sec.code_at(secret, 1002.0 + 30), now=1002.0 + 30), "the next code works right after switching on"
        assert not check_second_step(7, sec.code_at(secret, 1002.0), now=1003.0), "the switch-on code itself does not"
        backups = _re.findall(r"<code>([a-z0-9]{4}-[a-z0-9]{4})</code>", page)
        assert len(backups) == 6 and backups[0] not in db["tf"][2], "only the backup codes' hashes are stored"
        # the game login now needs the code (errorCode 6 makes the client ask for it)
        r = login("tomr", "old pass word")
        assert r == {"errorCode": 6, "errorMessage": "Enter the 6-digit code from your authenticator app."}
        r = login("tomr", "old pass word", token="123456")
        assert r["errorCode"] == 6 and r.get("wrongCode")
        good = sec.code_at(secret, time.time())
        r = login("tomr", "old pass word", token=good)
        assert "session" in r, "the right code lets the player in"
        r = login("tomr", "old pass word", token=good)
        assert r.get("errorCode") == 6, "the same code does not work twice"
        r = login("tomr", "old pass word", token=backups[0])
        assert "session" in r, "a backup code works"
        assert login("tomr", "old pass word", token=backups[0]).get("errorCode") == 6, "a backup code works only once"
        assert login("tomr", "wrong", token=sec.code_at(secret, time.time() + 30)) is None
        # another character needs the code too
        ok, msg = new_character("tomr", "old pass word", "Ash Varrow", "1", "b", agree=True)
        assert not ok and "two-step" in msg
        # change the password: rules, the code, sessions cleared
        page = security_post({"do": "password", "account": "tomr", "password": "old pass word", "code": backups[1],
                              "new": "password123", "new2": "password123"}, "c", now=time.time())
        assert "first ones people guess" in page
        page = security_post({"do": "password", "account": "tomr", "password": "old pass word", "code": backups[2],
                              "new": "yellow kite river", "new2": "yellow kite river"}, "c", now=time.time())
        assert "changed" in page and db["sessions"] == 0 and check_account("tomr", "yellow kite river") == 7
        # switch it off with a backup code
        page = security_post({"do": "off", "account": "tomr", "password": "yellow kite river", "code": backups[3]}, "d", now=time.time())
        assert db["tf"] is None and "off" in page
        assert "session" in login("tomr", "yellow kite river"), "only the password again"
        assert "<script>" not in security_page("<script>x</script>")
    finally:
        sql = real
        _fails.clear()
        _pending.clear()


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
    # R4: the session key is a random token, never the password, and only its hash reaches the database
    global sql
    real, seen = sql, []

    def fake(q):
        seen.append(q)
        if q.startswith("SELECT id, password FROM accounts"):
            return [["7", hashlib.sha1(b"correct horse").hexdigest()]]
        return []
    sql = fake
    try:
        a = login("jay", "correct horse")
        b = login("jay", "correct horse")
        key = a["session"]["sessionkey"]
        assert key != "correct horse" and "correct horse" not in key and "jay" not in key, "session key must not be the password"
        assert key != b["session"]["sessionkey"], "every login gets a new token"
        assert len(key) >= 40
        stored = [q for q in seen if q.startswith("INSERT INTO account_sessions")]
        assert stored and key not in stored[0] and key.encode().hex() not in stored[0], "only the token's hash is stored"
        assert hashlib.sha256(key.encode()).hexdigest().encode().hex() in stored[0]
        assert login("jay", "wrong") is None
        assert not signup("ab", "a@b.cd", "longenough", "longenough", "x")[0]
        assert not signup("friend1", "a@b.cd", "short", "short", "x")[0]
        assert not signup("friend1", "a@b.cd", "longenough", "different", "x")[0]
        assert not signup("friend1", "a@b.cd", "longenough", "longenough", "y", agree=True, character="")[0], "a character name is needed"
        assert not signup("friend1", "a@b.cd", "longenough", "longenough", "y", agree=True, character="x'; DROP")[0]
        assert not signup("friend1", "a@b.cd", "longenough", "longenough", "y", agree=True, character="Mira", sex="2")[0]
        assert not signup("friend1", "a@b.cd", "longenough", "longenough", "y", character="Tom Reed")[0], "the rules must be agreed"
        seen.clear()
        for rude in ("Kirito", "Fucker", "Gm Mira", "Vesper", "Xwhorex"):
            assert not signup("friend1", "a@b.cd", "longenough", "longenough", "y", agree=True, character=rude)[0], rude
        assert not signup("admin", "a@b.cd", "longenough", "longenough", "y", agree=True, character="Tom Reed")[0], "staff account name"
        assert not any(q.startswith("INSERT") for q in seen), "a refused name never reaches the database"
        seen.clear()
        assert signup("friend1", "a@b.cd", "longenough", "longenough", "y", agree=True, character="Tom  Reed", sex="0")[0]
        made = [q for q in seen if q.startswith("INSERT INTO players")]
        assert made and hexlit("Tom Reed") in made[0] and ", 136, " in made[0], "the first character is made with the account"
        assert "<script>" not in signup_page("<script>x</script>")
        assert 'name="agree"' in signup_page() and "What is not allowed" in rules_page()
        # another character on an existing account: right password, name checks, the rules, the per-account limit
        _fails.clear()
        assert not new_character("jay", "wrong", "Ash Varrow", "1", "z", agree=True)[0]
        assert not new_character("jay", "correct horse", "Kirito", "1", "z", agree=True)[0], "the name checker runs"
        assert not new_character("jay", "correct horse", "Ash Varrow", "1", "z")[0], "the rules must be agreed"
        seen.clear()
        assert new_character("jay", "correct horse", "Ash Varrow", "0", "z", agree=True)[0]
        made = [q for q in seen if q.startswith("INSERT INTO players")]
        assert made and hexlit("Ash Varrow") in made[0] and "7, 1, 0" in made[0], "made on the right account"
        assert "<script>" not in newchar_page("<script>x</script>")
        for bad in ("/../config.lua", "/x/../../etc/passwd", "/.local/site/index.html", "/index.html/..", "/A.HTML", "/a.py"):
            assert site_file(bad) is None, bad
        assert site_file("/") and site_file("/rules.html")[1].startswith("text/html") and site_file("/style.css")[1] == "text/css"
        assert site_file("/img/walk_wolf.png")[1] == "image/png" and site_file("/img/../style.css") is None
        assert 'href="style.css"' in signup_page() and "Create your account" in signup_page(), "sign-up wears the website's look"
    finally:
        sql = real
    assert BIND == "127.0.0.1" or os.environ.get("SPIRE_LOGIN_BIND"), "listens on this PC only by default"
    assert game_host_for("100.101.102.103:8080") == "100.101.102.103", "a Tailscale client gets the Tailscale address"
    assert game_host_for("127.0.0.1:8080") == GAME_HOST and game_host_for("evil.example.com") == GAME_HOST, "anything else: this PC"
    assert game_host_for("100.200.1.1:8080") == GAME_HOST, "only Tailscale's 100.64.0.0/10"
    selftest_security()
    print("login_server selftest: OK (with two-step login)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    print(f"Spirebound login service on {BIND}:{PORT} (website at /, sign-up at /signup)", flush=True)
    threading.Thread(target=site_loop, daemon=True).start()
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
