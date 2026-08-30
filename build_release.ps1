# build_release.ps1
# Package release: one-click installer + RAR portable
# Usage: .\build_release.ps1  (run with: powershell -ExecutionPolicy Bypass -File .\build_release.ps1)

$ErrorActionPreference = "Stop"
$Version = "4.0.20260830"

Write-Host "== Clean old build/dist ==" -ForegroundColor Cyan
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "== 1/4 Build folder version (for installer) ==" -ForegroundColor Cyan
pyinstaller build.spec --noconfirm --clean

Write-Host "== 2/4 Build onefile version (for portable) ==" -ForegroundColor Cyan
$env:PYI_ONEFILE = "1"
pyinstaller build.spec --noconfirm --clean
$env:PYI_ONEFILE = "0"

Write-Host "== 3/4 Compile installer (Inno Setup) ==" -ForegroundColor Cyan
$ISCC = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (Test-Path $ISCC) {
    cmd /c """$ISCC"" installer.iss"
} else {
    Write-Warning "Inno Setup not found, skip installer (product in dist\ServerRemoteInfoManager\)"
}

Write-Host "== 4/4 Compress portable RAR ==" -ForegroundColor Cyan
$WinRAR = "C:\Program Files (x86)\WinRAR\WinRAR.exe"
if (-not (Test-Path $WinRAR)) {
    $WinRAR = "C:\Program Files\WinRAR\WinRAR.exe"
}
if (Test-Path $WinRAR) {
    cmd /c """$WinRAR"" a -r -m5 -s ""dist\ServerRemoteInfoManager-$Version-Portable.rar"" ""dist\ServerRemoteInfoManager\*"""
} else {
    Write-Warning "WinRAR not found, please compress dist\ServerRemoteInfoManager\ manually"
}

Write-Host "== Done ==" -ForegroundColor Green
Get-ChildItem dist\*.exe, dist\*.rar -ErrorAction SilentlyContinue | Format-Table Name, Length
