# DayZ Client AppData Log Cleanup

Free up disk space on **Windows** by removing old DayZ **client** logs, RPT files, crash dumps (`.mdmp`), and ADM files from AppData.

**Not for dedicated servers** — this does not clean `DayZServer\profiles`. It only targets the DayZ **game client** on your PC (live or test install).

---

## What you get

| File | Purpose |
|------|---------|
| **`Run_Clear_DayZ_AppData_Logs.bat`** | Double-click to run (easiest) |
| **`clear_dayz_appdata_logs.ps1`** | PowerShell script (called by the .bat) |
| **`README.md`** | This guide |

No setup. No API keys. No config file.

---

## Quick start

1. Download this folder (or clone [DayZ-Admin-Helper](https://github.com/Banditas231/DayZ-Admin-Helper)).
2. Double-click **`Run_Clear_DayZ_AppData_Logs.bat`**
3. Choose:
   - **`A`** + Enter → **preview only** (dry-run, nothing deleted)
   - **Any other key** + Enter → **delete** all matching files

You get a summary at the end: file count and approximate MB freed.

---

## What gets deleted

Only these extensions under DayZ AppData folders (if they exist):

| Extension | Type |
|-----------|------|
| `.log` | Log files |
| `.rpt` | Report files |
| `.mdmp` | Crash dumps |
| `.adm` | ADM logs |

Only these folders are scanned:

| Path | Typical location |
|------|------------------|
| `%LOCALAPPDATA%\DayZ\` | `C:\Users\<you>\AppData\Local\DayZ\` |
| `%APPDATA%\DayZ\` | `C:\Users\<you>\AppData\Roaming\DayZ\` |

**Never touched:** server `profiles`, Documents saves, other apps, other file types.

---

## Requirements

- **Windows**
- **PowerShell** (built into Windows)

---

## PowerShell (optional)

Run from this folder:

```powershell
# Preview
.\clear_dayz_appdata_logs.ps1 -DryRun

# Delete
.\clear_dayz_appdata_logs.ps1

# Preview with full file list
.\clear_dayz_appdata_logs.ps1 -DryRun -ShowFiles
```

---

## Tips

- **Close DayZ** before deleting — locked files may fail until the game is closed.
- Use **dry-run first** if unsure (`A` in the .bat).
- To add another scan folder, edit the `$roots` array in `clear_dayz_appdata_logs.ps1`.

---

## Server vs client

| You want to clean… | Use… |
|--------------------|------|
| **Client PC** (AppData) | **This tool** |
| **Dedicated server** (`DayZServer\profiles`) | Your server log cleanup scripts |

---

## Part of DayZ Admin Helper

Shared in [Banditas231/DayZ-Admin-Helper](https://github.com/Banditas231/DayZ-Admin-Helper).

Other tools in the same repo: Steam ban checker, Workshop mod sync, and more.

## License

Use and share as you like.
