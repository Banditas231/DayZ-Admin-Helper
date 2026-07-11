# DayZ Discord Online Bot

Shows your **DayZ server player count** in your Discord bot's **activity status** (e.g. *Playing 👥 12 / 60*).

Runs on **your Windows PC** or a small **Python host**. Uses Steam **A2S query** — no RCon, no game server mod required.

---

## What you get

| File | Purpose |
|------|---------|
| **`START_BOT_PY.bat`** | Easiest start on Windows (creates venv, installs deps) |
| **`bot.py`** | Main bot code |
| **`OnlineBot_Config.example.json`** | Server IP, query port, status text templates |
| **`.env.example`** | Discord bot token (copy to `.env`) |
| **`requirements.txt`** | Python dependencies |

This bot **only updates the bot's presence** — it does not post messages to channels or manage roles.

---

## Requirements

- **Windows** (for the `.bat` starter) or any OS with Python 3.8+
- **Python 3.8+** with pip
- A **Discord bot application** ([Discord Developer Portal](https://discord.com/developers/applications))
- DayZ server with **Steam query** enabled (query port is usually **game port + 1**)

---

## Quick start (Windows)

1. Download this folder.
2. Copy **`OnlineBot_Config.example.json`** → **`OnlineBot_Config.json`**
3. Edit **`OnlineBot_Config.json`**: set `server.ip` and `server.steamQueryPort`
4. Copy **`.env.example`** → **`.env`** and set:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```
5. Double-click **`START_BOT_PY.bat`**
6. Console should show `Logged in as ...` and `[OK] 👥 x / y` every ~30 seconds

**Stop:** `Ctrl+C` in the console window.

---

## Discord bot setup

1. [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**
2. **Bot** → **Reset Token** → copy token into `.env`
3. Enable **Presence Intent** if required by your Discord app settings
4. **OAuth2 → URL Generator** → scopes: `bot` → invite bot to your server

**Never commit or share your token.** Treat it like a password.

---

## Configuration

Edit **`OnlineBot_Config.json`** (from the example file):

| Field | Description |
|-------|-------------|
| `server.ip` | Your DayZ server public IP |
| `server.steamQueryPort` | A2S query port (often game port + 1) |
| `updater.intervalSeconds` | How often to refresh (default 30) |
| `status.message` | Template for online text (see placeholders below) |
| `status.serverOfflineMessage` | Shown when server does not respond |
| `status.activityType` | `PLAYING`, `WATCHING`, `LISTENING`, etc. |
| `discord.token` | Leave empty if using `.env` |

### Message placeholders

| Placeholder | Value |
|-------------|--------|
| `${online}` | Current players |
| `${max}` | Max slots |
| `${queue}` | Queue count (if used) |
| `${emoji.player}` | From `emojis.player` |
| `${emoji.daytime}` | ☀️ or 🌙 by local time |
| `${status.queueBlock}` | Queue block from `queueBlock` template |

Example default: `"${emoji.player} ${online} / ${max} ${status.queueBlock}"`

---

## Hosting (e.g. game panel / VPS)

Upload:

- `bot.py`
- `requirements.txt`
- `OnlineBot_Config.json`

Start command:

```bash
pip install -r requirements.txt && python bot.py
```

If the host has no environment variables, you may put the token in `OnlineBot_Config.json` → `discord.token` — **not recommended for public repos**.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `DISCORD_TOKEN not found` | Create `.env` with token, or set `discord.token` in config |
| Shows **Server offline** but server is up | Check IP and `steamQueryPort`; ensure query port is open |
| Bot does not appear online | Verify token; check bot is invited to server |
| `pip install` fails on `a2s` | This project uses **`python-a2s`**, not the `a2s` package — the `.bat` removes the wrong one |

---

## How it works

1. Every N seconds, queries DayZ via **Steam A2S** (`python-a2s`)
2. Builds status text from your template
3. Updates Discord **activity** via `discord.py`
4. On timeout/error → shows offline message (no stale fake player count)

---

## Part of DayZ Admin Helper

Shared in [Banditas231/DayZ-Admin-Helper](https://github.com/Banditas231/DayZ-Admin-Helper).

---

## License & prior work

- **[LICENSE](LICENSE)** — MIT for this Python implementation, plus **no selling** this bot as a paid product.
- **[CREDITS.md](CREDITS.md)** — inspired by a **free** community “Online Bot” style project; **original author unknown**. If that is your work, contact us via GitHub and we will credit you or adjust/remove content.

**Free to use and share. Do not sell.**
