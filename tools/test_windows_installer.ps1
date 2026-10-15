param(
  [Parameter(Mandatory=$true)][string]$Installer,
  [Parameter(Mandatory=$true)][string]$Version
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$setup = (Resolve-Path $Installer).Path
$prefix = Join-Path $env:RUNNER_TEMP ("igc-installed-" + $Version)
$log = Join-Path $env:RUNNER_TEMP "igc-installer-install.log"
New-Item -ItemType Directory -Force $prefix | Out-Null
# Keep a sentinel outside the installation directory to prove uninstall/update
# do not erase real user app data or historical robot state.
$state = Join-Path $env:LOCALAPPDATA "Michels Lab\Insta Cleaner Pro"
New-Item -ItemType Directory -Force $state | Out-Null
$marker = Join-Path $state "installer-test-user-data-do-not-delete.txt"
"must-survive-installer-and-uninstall" | Set-Content -Path $marker -Encoding utf8
$legacy = Join-Path $env:USERPROFILE ".ig-cleaner-pro"
$legacyWasPresent = Test-Path $legacy
function RunBounded($path, [string[]]$arguments, $label) {
  $p = Start-Process -FilePath $path -ArgumentList $arguments -Wait -PassThru
  if ($p.ExitCode -ne 0) { throw "$label exited $($p.ExitCode)" }
}
try {
  RunBounded $setup @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$prefix+'"'),('/LOG="'+$log+'"')) 'Setup'
  $exe = Join-Path $prefix "InstaCleanerPro.exe"
  $uninstaller = Join-Path $prefix "unins000.exe"
  foreach ($file in @($exe,$uninstaller,(Join-Path $prefix "README.txt"),
    (Join-Path $prefix "BUILD-INFO.txt"),(Join-Path $prefix "chrome-extension\manifest.json"),
    (Join-Path $prefix "chrome-extension\popup.js"),(Join-Path $prefix "TaskbarPinning.txt"))) {
    if (!(Test-Path $file)) { throw "Installed payload is missing: $file" }
  }
  $startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Insta Cleaner Pro.lnk"
  if (!(Test-Path $startMenu)) { throw "Windows Start menu shortcut missing" }
  # Real installed binary, not a copied portable EXE.
  RunBounded $exe @('--healthcheck') 'Installed app binary'
  RunBounded $exe @('--smoke-startup') 'Installed app startup path'
  $ui = Join-Path $state "IG-Cleaner-Pro.html"
  if (!(Test-Path $ui)) { throw "Installed runtime did not prepare its persistent UI" }
  if ((Get-Item $ui).Length -lt 100000) { throw "Installed UI was incomplete" }
  if (!(Test-Path $marker)) { throw "Setup erased existing user data" }
  RunBounded $uninstaller @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') 'Uninstall'
  if (Test-Path $exe) { throw "Installed executable remained after uninstall" }
  if (!(Test-Path $marker)) { throw "Uninstall deleted local review/import data" }
  if ($legacyWasPresent -and !(Test-Path $legacy)) { throw "Uninstall deleted legacy robot data" }
  Write-Host "PASS: BUILD payload, INSTALL, installed HEALTHCHECK/STARTUP, START-MENU, UNINSTALL and data preservation. Instagram live session was NOT tested."
}
finally {
  if (Test-Path $marker) { Remove-Item $marker -Force }
  if (Test-Path $log) { Copy-Item $log -Destination "artifacts/IG-Cleaner-Pro-Installer-InstallLog.txt" -Force }
}
