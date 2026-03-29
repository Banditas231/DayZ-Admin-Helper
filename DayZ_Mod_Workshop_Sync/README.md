# DayZ Mod Workshop Sync

Small **Python** tool for **DayZ dedicated servers**: it reads your mod list from a launch `.bat` file, compares each `@ModFolder` with the copy under Steam’s **DayZ Workshop** folder, and **copies the Workshop version to the server** when Workshop is newer. It also copies matching **`.bikey`** files into the server `keys` folder.

Works from **any folder** — paths are set in `config.json` (not hardcoded).

## Requirements

- **Python 3.8+** on Windows ([python.org](https://www.python.org/downloads/)) — use the installer option **Add python.exe to PATH**.
- DayZ client with mods subscribed (so Workshop downloads exist).
- A server root folder containing `@YourMod` folders and a launch `.bat` with a `-mod=@A;@B;...` line.

## First-time setup

1. Copy **`config.example.json`** to **`config.json`** (same folder as the script).
2. Edit **`config.json`**:
   - **`server_root`** — full path to your **DayZ server** directory (where `@mods` and `keys` live).
   - **`workshop_path`** — full path to DayZ’s **`!Workshop`** folder (Steam Workshop download location for DayZ).
   - **`server_bat`** — name of the `.bat` file that contains your **`-mod=`** line (e.g. `TestingMods.bat` or `start.bat`). The file must sit inside **`server_root`**.

Use forward slashes in JSON paths if you like; Windows accepts them.

## Modlist.txt

The script uses **`Modlist.txt`** in **`server_root`**. Each line:

```text
WORKSHOP_ID,@FolderName
```

Example:

```text
1559212036,@CF
```

- If a mod from your `.bat` is missing from `Modlist.txt`, the script **appends** it with workshop ID **`0`**. Mods with ID **`0`** are **skipped** for updates until you set the real **Steam Workshop item ID**.
- Lines starting with `#` are ignored.

## How to run

- Double-click **`Run_DayZ_Mod_Updater.bat`**, or  
- In this folder: `python check_and_update_mods.py`

If `config.json` is missing, the script prints short setup instructions.

## What it does (summary)

1. Reads **`-mod=`** from the configured `.bat`.
2. Loads **`Modlist.txt`** (creates it if missing).
3. For each mod with a non-zero Workshop ID: if **`!Workshop/@FolderName`** is newer than **`server_root/@FolderName`**, replaces the server copy and copies **`.bikey`** files to **`server_root/keys`**.

## Sharing

Zip the whole **`DayZ_Mod_Workshop_Sync`** folder. Recipients only need Python, their own **`config.json`**, and a valid server + Workshop layout — the tool does not need to live inside the server directory.

**Redistribution:** **MIT License** — the full legal text is on **GitHub** (`LICENSE` in the repo root). Use and share the tool under those terms.

## Author & license

- **Author:** Kestas / Banditas.
- **License:** **MIT** — full legal text is in the **`LICENSE`** file on this project’s **GitHub** repository.
