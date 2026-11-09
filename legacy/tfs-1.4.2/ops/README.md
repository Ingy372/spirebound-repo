# ops

| File | What |
|---|---|
| config.lua.tpl | server config template (rules from docs 02, 05, 16, 22) |
| render_config.sh | renders `server/config.lua` from the template + `/etc/spirebound/spirebound.env` |
| spirebound.env.example | the keys the env file needs (the real file is never committed) |
| gen_rsa_key.sh | creates the server's own RSA key and prints the public modulus for the client build |

Hosts run in the America/New_York time zone so the 05:00 ET server save is correct.
systemd units, backups and monitoring arrive with staging (phase 2) and production (phase 8).
