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
. (Join-Path $PSScriptRoot "installer_process_guard.ps1")
function RunBounded($path, [string[]]$arguments, $label, [int]$timeout = 150) {
  Invoke-IgcBoundedProcess -Path $path -Arguments $arguments -Label $label -TimeoutSeconds $timeout
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
  $devMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Insta Cleaner Pro - Developer Edition.lnk"
  if (!(Test-Path $devMenu)) { throw "Developer Edition Start menu shortcut missing" }
  $devShortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($devMenu)
  if ($devShortcut.Arguments -ne '--developer') { throw "Developer shortcut must launch --developer." }
  # Real installed binary, not a copied portable EXE.
  RunBounded $exe @('--healthcheck') 'Installed app binary' 75
  RunBounded $exe @('--smoke-startup') 'Installed app startup path' 100
  RunBounded $exe @('--smoke-startup','--developer') 'Installed Developer Edition startup path' 100
  $devState = Join-Path $state "developer-edition"
  if (!(Test-Path (Join-Path $devState "IG-Cleaner-Pro.html"))) {
    throw "Developer Edition did not create isolated HTML origin."
  }
  $ui = Join-Path $state "IG-Cleaner-Pro.html"
  if (!(Test-Path $ui)) { throw "Installed runtime did not prepare its persistent UI" }
  if ((Get-Item $ui).Length -lt 100000) { throw "Installed UI was incomplete" }
  if (!(Test-Path $marker)) { throw "Setup erased existing user data" }
  # Exercise the upgrade/reinstall path with the SAME stable AppId and folder.
  RunBounded $setup @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$prefix+'"')) 'In-place upgrade'
  if (!(Test-Path $exe) -or !(Test-Path $marker) -or !(Test-Path $ui)) {
    throw "In-place setup replaced or lost the persisted workspace"
  }
  RunBounded $uninstaller @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') 'Uninstall' 120
  if (Test-Path $exe) { throw "Installed executable remained after uninstall" }
  if (!(Test-Path $marker)) { throw "Uninstall deleted local review/import data" }
  if ($legacyWasPresent -and !(Test-Path $legacy)) { throw "Uninstall deleted legacy robot data" }
  Write-Host "PASS: BUILD payload, INSTALL, installed HEALTHCHECK/STARTUP, START-MENU, IN-PLACE UPGRADE, UNINSTALL and data preservation. Instagram live session was NOT tested."
}
finally {
  if (Test-Path $marker) { Remove-Item $marker -Force }
  if (Test-Path $log) { Copy-Item $log -Destination "artifacts/IG-Cleaner-Pro-Installer-InstallLog.txt" -Force }
}
