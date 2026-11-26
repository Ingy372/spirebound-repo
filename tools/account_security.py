#!/usr/bin/env python3
"""Account safety for the login service (roadmap 10.5, REVIEW 7.4): how passwords are stored, which passwords are
refused, and two-step login with an authenticator app.

Passwords: stored as PBKDF2-SHA256 with a random salt ("pbkdf2$<rounds>$<salt hex>$<hash hex>"), which takes a
computer real time to guess, unlike the old plain SHA1 that Canary's tools write. Old SHA1 passwords still work and
are upgraded the next time their owner logs in (the game server never reads passwords: it only trusts the login
service's session keys, authType = "session").

Two-step login (optional, per account): the standard 6-digit codes from Google Authenticator, Authy, Microsoft
Authenticator and the like (TOTP, RFC 6238). The game client already asks for the code when the login service
answers errorCode 6. Six one-time backup codes are given when it is switched on, for a lost phone.

  python tools/account_security.py --selftest
Standard library only.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import sys
import time

ROUNDS = 200_000
STEP = 30              # seconds per code
DRIFT = 1              # also accept the code just before and just after (phone clocks drift)

# The most common passwords in leaked lists, plus game words: refused at sign-up whatever their length
COMMON = {
    "password", "password1", "password12", "password123", "passw0rd", "12345678", "123456789", "1234567890", "11111111",
    "00000000", "12341234", "87654321", "qwertyui", "qwertyuiop", "qwerty123", "1q2w3e4r", "1q2w3e4r5t", "zaq12wsx",
    "abc12345", "abcd1234", "iloveyou", "sunshine", "princess", "football", "baseball", "superman", "starwars",
    "trustno1", "letmein1", "welcome1", "monkey123", "dragon123", "michael1", "computer", "whatever", "asdfghjk",
    "asdfasdf", "qazwsxedc", "11223344", "aa123456", "123qweasd", "q1w2e3r4", "changeme", "secret123", "master123",
    "tibia123", "tibiatibia", "spirebound", "spirebound1", "spirebound123", "gamemaster", "minecraft", "pokemon1",
    "naruto123", "fortnite", "senha123", "senha1234", "contrasena", "contraseña", "12qwaszx", "admin123", "administrator",
}


# ---------------------------------------------------------------- passwords
def hash_password(password: str, rounds: int = ROUNDS) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"pbkdf2${rounds}${salt.hex()}${digest.hex()}"


def check_password(stored: str, password: str) -> tuple[bool, bool]:
    """(right password, should be upgraded to the strong format)."""
    stored = stored or ""
    if stored.startswith("pbkdf2$"):
        try:
            _, rounds, salt, digest = stored.split("$")
            got = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(rounds))
        except ValueError:
            return False, False
        return hmac.compare_digest(got.hex(), digest), int(rounds) < ROUNDS
    if len(stored) == 40:                                            # the old SHA1 (Canary's tools, dev_accounts.sql)
        return hmac.compare_digest(stored.lower(), hashlib.sha1(password.encode("utf-8")).hexdigest()), True
    return False, False


def password_problem(password: str, *personal: str) -> str | None:
    """Why a new password is refused, or None. Length plus a ban on the commonest ones and on your own names
    (no "must contain a digit" rules: they make passwords worse, not better)."""
    if len(password) < 8 or len(password) > 100:
        return "The password must be 8 to 100 characters."
    low = password.lower()
    if low in COMMON or len(set(low)) <= 2:
        return "That password is one of the first ones people guess. Please pick another."
    for p in personal:
        p = (p or "").lower().split("@")[0].replace(" ", "")
        if len(p) >= 3 and p in low.replace(" ", ""):
            return "The password must not contain your account name, e-mail or character name."
    return None


# ---------------------------------------------------------------- two-step codes (TOTP)
def new_secret() -> str:
    """A fresh authenticator key, in the letters-and-digits form apps let you type in (base32, 32 characters)."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def pretty_secret(secret: str) -> str:
    return " ".join(secret[i:i + 4] for i in range(0, len(secret), 4))


def setup_uri(secret: str, account: str) -> str:
    """The otpauth:// address an authenticator app understands (for a QR code later)."""
    from urllib.parse import quote
    return f"otpauth://totp/Spirebound:{quote(account)}?secret={secret}&issuer=Spirebound&digits=6&period={STEP}"


def code_at(secret: str, when: float) -> str:
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    msg = struct.pack(">Q", int(when // STEP))
    mac = hmac.new(key, msg, hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    return f"{(struct.unpack('>I', mac[off:off + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def check_code(secret: str, code: str, now: float | None = None, last_step: int = -1) -> int:
    """The time step the code belongs to if it is right (and newer than last_step, so a code works once), else -1."""
    code = "".join(ch for ch in (code or "") if ch.isdigit())
    if len(code) != 6 or not secret:
        return -1
    now = time.time() if now is None else now
    for d in range(-DRIFT, DRIFT + 1):
        step = int(now // STEP) + d
        if step > last_step and hmac.compare_digest(code_at(secret, step * STEP), code):
            return step
    return -1


def backup_codes(n: int = 6) -> list[str]:
    """One-time backup codes for a lost phone, like "k7wq-3mzp" (no look-alike letters)."""
    abc = "abcdefghjkmnpqrstuvwxyz23456789"
    return ["".join(secrets.choice(abc) for _ in range(4)) + "-" + "".join(secrets.choice(abc) for _ in range(4)) for _ in range(n)]


def hash_backup(code: str) -> str:
    return hashlib.sha256(code.strip().lower().replace(" ", "").encode()).hexdigest()


def selftest():
    h = hash_password("correct horse battery")
    assert h.startswith("pbkdf2$") and "correct" not in h
    assert check_password(h, "correct horse battery") == (True, False)
    assert check_password(h, "wrong horse battery")[0] is False
    assert hash_password("same pass 1") != hash_password("same pass 1"), "every password gets its own salt"
    old = hashlib.sha1(b"spirebound").hexdigest()
    assert check_password(old, "spirebound") == (True, True), "old SHA1 passwords still work and get upgraded"
    assert check_password(old, "nope")[0] is False and check_password("", "x") == (False, False)
    assert password_problem("short") and password_problem("password123") and password_problem("aaaaaaaaaa")
    assert password_problem("mira1234567", "Mira") and password_problem("x-tomreed-x", "friend1", "Tom Reed")
    assert password_problem("yellow kite river") is None
    # RFC 6238's own test key and times (SHA1, 8 digits there; the last 6 digits are the same code)
    rfc = base64.b32encode(b"12345678901234567890").decode()
    for t, full in ((59, "94287082"), (1111111109, "07081804"), (1234567890, "89005924"), (2000000000, "69279037")):
        assert code_at(rfc, t) == full[-6:], (t, code_at(rfc, t))
    s = new_secret()
    assert len(s) == 32 and check_code(s, code_at(s, 1000.0), now=1000.0) == 1000 // STEP
    assert check_code(s, code_at(s, 1000.0 - STEP), now=1000.0) >= 0, "a code from 30 s ago still works"
    assert check_code(s, code_at(s, 1000.0 - 3 * STEP), now=1000.0) == -1, "an old code does not"
    step = check_code(s, code_at(s, 1000.0), now=1000.0)
    assert check_code(s, code_at(s, 1000.0), now=1000.0, last_step=step) == -1, "a code works only once"
    assert check_code(s, "12 34 5x", now=1000.0) == -1
    codes = backup_codes()
    assert len(set(codes)) == 6 and hash_backup(codes[0].upper()) == hash_backup(codes[0])
    assert setup_uri(s, "Tom Reed").startswith("otpauth://totp/Spirebound:Tom%20Reed?secret=")
    print("account_security selftest: OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
