# DayZ Admin Helper – Steam Ban Checker

Check your DayZ server player list for Steam VAC/Game bans and get ready-to-paste lines for your server `ban.txt`.

## Requirements

- **Python 3** (with `pip`)
- **Steam API key** – get one at [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)

## Setup

1. Open `check_steam_bans.py` and set your key:
   ```python
   STEAM_API_KEY = "YOUR_STEAM_API_KEY"
   ```
2. (Optional) Put `playernames.json` or `players.txt` in this folder, or drag a file onto `run_check.bat` when you run.

## Usage

- **Double-click `run_check.bat`**  
  Uses `playernames.json` if it exists, otherwise `players.txt`.

- **Drag a file onto `run_check.bat`**  
  Uses that file as the player list (.json or .txt).

### Player list format

- **JSON** (e.g. from LBM): `{"version":1,"players":["76561198...","76561198..."]}`  
  Only 17-digit SteamID64 entries in the `players` array are checked.

- **players.txt** (no LBM): one SteamID64 per line (17 digits).  
  Edit `players.txt` and run the .bat, or drag your own .txt file.

## Output

- **banned_players.txt** – Log of all banned players (SteamID, DayZ UID, VAC/Game counts, economy ban).
- **dayz_ban_lines.txt** – Lines you can copy into your DayZ server `ban.txt` (44-character DayZ UID per line).  
  DayZ server `ban.txt` uses this 44-char ID, not SteamID64.

## DayZ server ban.txt

Your server’s `ban.txt` expects the **44-character player UID** (as in .ADM logs), not SteamID64. This tool converts SteamID64 → 44-char UID and writes `dayz_ban_lines.txt` so you can paste directly into `ban.txt`.

## License

Use and share as you like.
