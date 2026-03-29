#!/usr/bin/env python3
# DayZ Mod Workshop Sync — original tool by the author named in LICENSE (same folder).
# Do not remove LICENSE or misrepresent authorship when sharing.

"""
DayZ Mod Update Checker and Updater
Compares mod folders on the server with Steam Workshop downloads and copies newer Workshop files to the server.

Paths are read from config.json next to this script, so the tool can live in any folder.
Requires: Python 3.8+ (standard library only).

Copyright and sharing terms: see LICENSE in this folder.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"


def load_config():
    """Load server_root, workshop_path, and optional server_bat from config.json."""
    if not CONFIG_FILE.exists():
        print("=" * 60)
        print("  Configuration missing")
        print("=" * 60)
        print()
        print(f'  No file: {CONFIG_FILE}')
        print()
        print("  First-time setup:")
        print('    1. Copy "config.example.json" to "config.json"')
        print("    2. Edit config.json: set server_root and workshop_path to your PC")
        print("    3. Run this script again")
        print()
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in config.json: {e}")
        return None

    server_root = data.get("server_root", "").strip()
    workshop_path = data.get("workshop_path", "").strip()
    server_bat = data.get("server_bat", "TestingMods.bat").strip() or "TestingMods.bat"

    if not server_root or not workshop_path:
        print("Error: config.json must define non-empty 'server_root' and 'workshop_path'.")
        return None

    return {
        "server_root": Path(server_root),
        "workshop_path": Path(workshop_path),
        "server_bat": Path(server_root) / server_bat,
        "modlist_file": Path(server_root) / "Modlist.txt",
    }


def parse_mods_from_server_bat(server_bat_path):
    """Extract mod folder names from the -mod= line in a .bat file."""
    if not server_bat_path.exists():
        print(f"Error: launch .bat not found: {server_bat_path}")
        return []

    with open(server_bat_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    mods_string = ""
    found_mod_line = False

    for line in lines:
        if "-mod=" in line or found_mod_line:
            clean_line = line.rstrip().rstrip("^").strip()
            if "-mod=" in clean_line:
                found_mod_line = True
                if '-mod="' in clean_line:
                    mods_string = clean_line.split('-mod="', 1)[1]
                else:
                    mods_string = clean_line.split("-mod=", 1)[1]
                if mods_string.startswith('"'):
                    mods_string = mods_string[1:]
            else:
                mods_string += " " + clean_line

            if not line.rstrip().endswith("^"):
                if mods_string.endswith('"'):
                    mods_string = mods_string[:-1]
                for param in ["-cpuCount", "-dologs", "-adminlog", "-netlog", "-freezecheck", "-profiles", "-port", "-config"]:
                    if param in mods_string:
                        mods_string = mods_string.split(param)[0].strip().rstrip('"').rstrip()
                        break
                break

    if not mods_string:
        print("Warning: no -mod= line found in the .bat file")
        return []

    mods = [m.strip().lstrip("@") for m in mods_string.split(";") if m.strip()]
    return mods


def load_modlist(modlist_path):
    """Load Modlist.txt. Returns dict: folder_name -> (workshop_id, folder_name)."""
    mod_mapping = {}
    if modlist_path.exists():
        with open(modlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    workshop_id = parts[0].strip()
                    folder_name = parts[1].strip().lstrip("@")
                    mod_mapping[folder_name] = (workshop_id, folder_name)
    return mod_mapping


def append_mod_to_modlist(modlist_path, folder_name, workshop_id="0"):
    """Append one mod line to Modlist.txt if missing."""
    line = f"{workshop_id},@{folder_name}\n"
    try:
        with open(modlist_path, "a", encoding="utf-8") as f:
            f.write(line)
        return True
    except Exception as e:
        print(f"  Error: could not append to Modlist.txt: {e}")
        return False


def check_mod_needs_update(workshop_id, folder_name, workshop_path, server_path):
    needs_update, workshop_found = False, False
    workshop_mod_path = workshop_path / f"@{folder_name}"
    server_mod_path = server_path / f"@{folder_name}"

    if not workshop_mod_path.exists():
        return (False, False)
    if not server_mod_path.exists():
        return (True, True)

    workshop_time = get_mod_last_modified(workshop_mod_path)
    server_time = get_mod_last_modified(server_mod_path)
    if not workshop_time:
        return (False, True)
    if not server_time:
        return (True, True)
    return (workshop_time > server_time, True)


def sync_mod_to_server(workshop_id, folder_name, workshop_path, server_path):
    import shutil
    source = workshop_path / f"@{folder_name}"
    target = server_path / f"@{folder_name}"
    if not source.exists():
        return False
    try:
        target.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        keys_folder = server_path / "keys"
        keys_folder.mkdir(exist_ok=True)
        for bikey_file in source.rglob("*.bikey"):
            shutil.copy2(bikey_file, keys_folder)
        return True
    except Exception as e:
        print(f"  Error syncing mod: {e}")
        return False


def get_mod_last_modified(folder_path):
    if not folder_path.exists():
        return None
    try:
        latest = max(folder_path.rglob("*"), key=lambda p: p.stat().st_mtime if p.is_file() else 0, default=None)
        return datetime.fromtimestamp(latest.stat().st_mtime) if latest and latest.is_file() else None
    except Exception:
        return None


def main():
    print("=" * 60)
    print("  DayZ Mod Update Checker & Updater")
    print("=" * 60)
    print()

    cfg = load_config()
    if not cfg:
        return 1

    server_path = cfg["server_root"]
    workshop_path = cfg["workshop_path"]
    server_bat = cfg["server_bat"]
    modlist_file = cfg["modlist_file"]

    if not server_path.is_dir():
        print(f"Error: server_root is not a directory: {server_path}")
        return 1

    if not workshop_path.exists():
        print(f"Error: Workshop folder not found: {workshop_path}")
        print("  (Steam: DayZ -> Properties -> Workshop path, usually .../DayZ/!Workshop)")
        return 1

    mods_from_bat = parse_mods_from_server_bat(server_bat)
    if not mods_from_bat:
        return 1
    print(f"OK: {len(mods_from_bat)} mod(s) listed in {server_bat.name}")
    print()

    mod_mapping = load_modlist(modlist_file)
    if not modlist_file.exists():
        print("Warning: Modlist.txt not found — it will be created.")
        modlist_file.parent.mkdir(parents=True, exist_ok=True)
        modlist_file.touch()
    print(f"OK: Modlist.txt has {len(mod_mapping)} mapped mod(s)")
    added_to_list = 0
    for mod_name in mods_from_bat:
        if mod_name in mod_mapping:
            continue
        for key in mod_mapping:
            if mod_name.lower() in key.lower() or key.lower() in mod_name.lower():
                break
        else:
            if append_mod_to_modlist(modlist_file, mod_name):
                mod_mapping[mod_name] = ("0", mod_name)
                added_to_list += 1
                print(
                    f"  Added to Modlist.txt: @{mod_name} (workshop_id=0 — set the Steam Workshop ID to enable updates)"
                )
    if added_to_list:
        print()
    print()

    updated_count = skipped_count = error_count = 0
    for mod_name in mods_from_bat:
        workshop_id, folder_name = None, None
        if mod_name in mod_mapping:
            workshop_id, folder_name = mod_mapping[mod_name]
        else:
            for key, (wid, fname) in mod_mapping.items():
                if mod_name.lower() in key.lower() or key.lower() in mod_name.lower():
                    workshop_id, folder_name = wid, fname
                    break
        if not workshop_id:
            skipped_count += 1
            continue
        if workshop_id == "0":
            skipped_count += 1
            continue

        needs_update, workshop_found = check_mod_needs_update(
            workshop_id, folder_name, workshop_path, server_path
        )
        if not workshop_found:
            skipped_count += 1
        elif needs_update:
            if sync_mod_to_server(workshop_id, folder_name, workshop_path, server_path):
                updated_count += 1
            else:
                error_count += 1

    print("=" * 60)
    print(f"Updated: {updated_count} | Skipped: {skipped_count} | Errors: {error_count}")
    print("=" * 60)
    return 0 if error_count == 0 else 2


if __name__ == "__main__":
    sys.exit(main() or 0)
