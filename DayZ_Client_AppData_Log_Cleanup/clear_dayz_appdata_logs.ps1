# Clears DayZ CLIENT logs / RPT / crash dumps from Windows AppData (not server profiles).
# Safe by design: only known extensions under fixed root folders.

param(
    [switch]$DryRun,
    [switch]$ShowFiles
)

$ErrorActionPreference = "Stop"

$extensions = @(".log", ".rpt", ".mdmp", ".adm")
$roots = @(
    @(
        (Join-Path $env:LOCALAPPDATA "DayZ"),
        (Join-Path $env:APPDATA "DayZ")
    ) | Where-Object { Test-Path -LiteralPath $_ }
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DayZ AppData log cleanup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($roots.Count -eq 0) {
    Write-Host "No folders found:" -ForegroundColor Yellow
    Write-Host "  $(Join-Path $env:LOCALAPPDATA 'DayZ')" -ForegroundColor Gray
    Write-Host "  $(Join-Path $env:APPDATA 'DayZ')" -ForegroundColor Gray
    Write-Host ""
    Write-Host "If you play under another Windows user or PC, check those paths." -ForegroundColor Yellow
    exit 0
}

Write-Host "Folders:" -ForegroundColor Yellow
foreach ($r in $roots) { Write-Host "  $r" -ForegroundColor Gray }
Write-Host "Extensions: $($extensions -join ', ')" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "Mode: DRY-RUN (nothing will be deleted)" -ForegroundColor Magenta
    if (-not $ShowFiles) {
        Write-Host "(Per-file list hidden; summary at the end.)" -ForegroundColor DarkGray
    }
}
Write-Host ""

$all = @()
foreach ($root in $roots) {
    foreach ($ext in $extensions) {
        $pat = "*" + $ext
        $items = Get-ChildItem -LiteralPath $root -Recurse -File -Filter $pat -ErrorAction SilentlyContinue
        if ($items) { $all += $items }
    }
}

if ($all.Count -eq 0) {
    Write-Host "No matching files found." -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "SUMMARY" -ForegroundColor Cyan
    Write-Host "  Files: 0" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    exit 0
}

$bytes = ($all | Measure-Object -Property Length -Sum).Sum
$mb = [math]::Round($bytes / 1MB, 2)
Write-Host "Scan complete: $($all.Count) file(s) (~ $mb MB on disk)" -ForegroundColor Yellow
Write-Host ""

$deleted = 0
$failed = 0
$bytesFreed = [int64]0

foreach ($f in $all) {
    try {
        if ($DryRun) {
            if ($ShowFiles) {
                Write-Host "[DRY] $($f.FullName)" -ForegroundColor DarkGray
            }
        }
        else {
            $bytesFreed += $f.Length
            Remove-Item -LiteralPath $f.FullName -Force
            $deleted++
        }
    }
    catch {
        Write-Host "[ERROR] $($f.FullName) - $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "SUMMARY (preview only, nothing deleted)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Total files:     $($all.Count)" -ForegroundColor White
    Write-Host "  Approx. size:    ~ $mb MB" -ForegroundColor White
    Write-Host ""
    if (-not $ShowFiles) {
        Write-Host "  Full file list (PowerShell):" -ForegroundColor DarkGray
        Write-Host '    .\clear_dayz_appdata_logs.ps1 -DryRun -ShowFiles' -ForegroundColor DarkGray
    }
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To delete for real, run the .bat without A, or run the .ps1 without -DryRun." -ForegroundColor Yellow
}
else {
    $freedMb = [math]::Round($bytesFreed / 1MB, 2)
    Write-Host "SUMMARY" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Files removed:       $deleted" -ForegroundColor White
    Write-Host "  Space freed approx.: ~ $freedMb MB" -ForegroundColor White
    if ($failed -gt 0) {
        Write-Host "  Failed to delete:    $failed" -ForegroundColor Red
    }
    Write-Host "========================================" -ForegroundColor Cyan
}
