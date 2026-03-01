import requests
import sys
import os
import json
import hashlib
import base64
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

# ==== ENTER YOUR STEAM API KEY ====
# Get one at: https://steamcommunity.com/dev/apikey
STEAM_API_KEY = "YOUR_STEAM_API_KEY"
# ====================================

BANNED_LOG = "banned_players.txt"
DAYZ_BAN_LINES = "dayz_ban_lines.txt"

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def steamid_to_dayz_uid(steamid_str):
    """Convert SteamID64 to DayZ ban.txt 44-character UID (as in .ADM logs)."""
    s = str(steamid_str).strip()
    raw = hashlib.sha256(s.encode("utf-8")).digest()
    b64 = base64.b64encode(raw).decode("ascii")
    return b64.replace("+", "-").replace("/", "_")

def check_steam_bans(steamid):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamids": steamid
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(Fore.RED + f"Network / API error: {e}")
        return None
    except ValueError:
        print(Fore.RED + "Invalid response (not JSON).")
        return None

    players = data.get("players", [])
    if not players:
        print(Fore.RED + f"Invalid SteamID or bad API key: {steamid}")
        return None

    player = players[0]
    vac_bans = player.get("NumberOfVACBans", 0)
    game_bans = player.get("NumberOfGameBans", 0)
    days_since_last_ban = player.get("DaysSinceLastBan", 0)
    economy_ban = player.get("EconomyBan", "none")
    has_bans = vac_bans > 0 or game_bans > 0 or economy_ban != "none"

    print("\n========== STEAM BAN CHECK ==========")
    print(f"SteamID: {steamid}")
    print("--------------------------------------")
    print(f"VAC Bans: {vac_bans}")
    print(f"Game Bans: {game_bans}")
    print(f"Days Since Last Ban: {days_since_last_ban}")
    print(f"Economy Ban: {economy_ban}")
    print("--------------------------------------")

    if has_bans:
        print(Fore.RED + "THIS ACCOUNT HAS BANS!")
    else:
        print(Fore.GREEN + "Clean account")

    if has_bans:
        return {
            "steamid": steamid,
            "dayz_uid": steamid_to_dayz_uid(steamid),
            "vac_bans": vac_bans,
            "game_bans": game_bans,
            "days_since_last_ban": days_since_last_ban,
            "economy_ban": economy_ban,
        }
    return None


if __name__ == "__main__":
    script_dir = get_script_dir()
    os.chdir(script_dir)

    if len(sys.argv) >= 2 and sys.argv[1].strip():
        file_path = sys.argv[1].strip().strip('"')
    else:
        json_path = os.path.join(script_dir, "playernames.json")
        txt_path = os.path.join(script_dir, "players.txt")
        file_path = json_path if os.path.isfile(json_path) else txt_path

    if not os.path.isfile(file_path):
        print(Fore.RED + f"File not found: {file_path}")
        print("Place playernames.json or players.txt in this folder, or drag a .json/.txt file onto the .bat")
        sys.exit(1)

    file_path_lower = file_path.lower()
    if file_path_lower.endswith(".json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            lines = [str(s).strip() for s in data.get("players", []) if str(s).strip().isdigit() and len(str(s).strip()) == 17]
        except (json.JSONDecodeError, TypeError) as e:
            print(Fore.RED + f"Invalid JSON: {e}")
            sys.exit(1)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and line.strip().isdigit() and len(line.strip()) == 17]

    if not lines:
        print(Fore.RED + "No valid SteamID64 found (empty file or invalid 'players' array in JSON).")
        print("Use players.txt: one SteamID64 per line (17 digits).")
        sys.exit(1)

    banned_list = []
    for steamid in lines:
        result = check_steam_bans(steamid)
        if result:
            banned_list.append(result)

    if banned_list:
        banned_log_path = os.path.join(script_dir, BANNED_LOG)
        dayz_ban_path = os.path.join(script_dir, DAYZ_BAN_LINES)
        with open(banned_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            for r in banned_list:
                f.write(
                    f"SteamID: {r['steamid']} | DayZ UID (44): {r['dayz_uid']} | VAC: {r['vac_bans']} | Game: {r['game_bans']} | "
                    f"DaysSinceLastBan: {r['days_since_last_ban']} | Economy: {r['economy_ban']}\n"
                )
        with open(dayz_ban_path, "w", encoding="utf-8") as f:
            f.write("// Copy these lines into your server ban.txt (or just the 44-char ID)\n")
            for r in banned_list:
                f.write(f"{r['dayz_uid']}\t// SteamID {r['steamid']} VAC:{r['vac_bans']} Game:{r['game_bans']}\n")
        print(Fore.YELLOW + f"\nBanned players log: {BANNED_LOG}")
        print(Fore.YELLOW + f"DayZ ban.txt lines (44-char UID): {DAYZ_BAN_LINES}")

    print("\n" + "=" * 40)
