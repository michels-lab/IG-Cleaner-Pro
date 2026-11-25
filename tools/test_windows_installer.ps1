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
  RunBounded $exe @('--smoke-chooser') 'Installed native account chooser (real Win32 Cancel)' 45
  RunBounded $exe @('--smoke-startup') 'Installed primary startup path' 100
  RunBounded $exe @('--smoke-startup','--workspace','secondary') 'Installed second-window startup path' 100
  RunBounded $exe @('--smoke-startup','--developer') 'Installed Developer Edition startup path' 100
  $devState = Join-Path $state "developer-edition"
  if (!(Test-Path (Join-Path $devState "IG-Cleaner-Pro.html"))) {
    throw "Developer Edition did not create isolated HTML origin."
  }
  $ui = Join-Path $state "IG-Cleaner-Pro.html"
  if (!(Test-Path $ui)) { throw "Installed runtime did not prepare its persistent UI" }
  if ((Get-Item $ui).Length -lt 100000) { throw "Installed UI was incomplete" }
  # The second launch must not reuse the first file:// origin or Chrome
  # user-data-dir. Both locations persist across in-place upgrade/uninstall.
  $secondUi = Join-Path $state 'second-window\IG-Cleaner-Pro.html'
  $firstChrome = Join-Path $state 'workspace-browser'
  $secondChrome = Join-Path $state 'workspace-browser-secondary'
  foreach ($file in @($secondUi)) {
    if (!(Test-Path -LiteralPath $file)) { throw "Second account entrypoint not created: $file" }
    if ((Get-Item -LiteralPath $file).Length -lt 100000) { throw "Second account UI is incomplete: $file" }
  }
  if ($ui -eq $secondUi) { throw 'Two app windows must not share the HTML entrypoint.' }
  if (!(Test-Path -LiteralPath $firstChrome) -or !(Test-Path -LiteralPath $secondChrome)) {
    throw 'Two independent Chrome data directories were not created.'
  }
  $firstMarker = Join-Path $firstChrome 'installer-test-primary-do-not-delete.txt'
  $secondMarker = Join-Path $secondChrome 'installer-test-secondary-do-not-delete.txt'
  'keep-primary' | Set-Content -LiteralPath $firstMarker -Encoding utf8
  'keep-secondary' | Set-Content -LiteralPath $secondMarker -Encoding utf8
  $firstUiDigest = (Get-FileHash -LiteralPath $ui -Algorithm SHA256).Hash
  $secondUiDigest = (Get-FileHash -LiteralPath $secondUi -Algorithm SHA256).Hash
  if ($firstUiDigest -ne $secondUiDigest) { throw 'Different window slots received mismatched versioned interface bytes.' }
  if (!(Test-Path $marker)) { throw "Setup erased existing user data" }
  # Exercise the upgrade/reinstall path with the SAME stable AppId and folder.
  RunBounded $setup @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$prefix+'"')) 'In-place upgrade'
  if (!(Test-Path $exe) -or !(Test-Path $marker) -or !(Test-Path $ui) -or
      !(Test-Path $secondUi) -or !(Test-Path $firstMarker) -or !(Test-Path $secondMarker)) {
    throw "In-place setup replaced or lost either persisted account"
  }
  if ((Get-FileHash -LiteralPath $ui -Algorithm SHA256).Hash -ne $firstUiDigest -or
      (Get-FileHash -LiteralPath $secondUi -Algorithm SHA256).Hash -ne $secondUiDigest) {
    throw 'In-place upgrade altered the saved UI origin or source bytes.'
  }
  RunBounded $uninstaller @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') 'Uninstall' 120
  if (Test-Path $exe) { throw "Installed executable remained after uninstall" }
  if (!(Test-Path $marker)) { throw "Uninstall deleted local review/import data" }
  if (!(Test-Path $ui) -or !(Test-Path $secondUi) -or
      !(Test-Path $firstMarker) -or !(Test-Path $secondMarker)) {
    throw 'Uninstall must not erase either account or its Chrome data.'
  }
  if ($legacyWasPresent -and !(Test-Path $legacy)) { throw "Uninstall deleted legacy robot data" }
  Write-Host "PASS: installed public app, BOTH account slots, unchanged profile data across upgrade/uninstall and isolated UI origins. Physical two-window Instagram acceptance is still open."
}
finally {
  if (Test-Path $marker) { Remove-Item $marker -Force }
  # Only remove synthetic CI markers. Never clear Chrome profiles/history.
  if (Get-Variable -Name firstMarker -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $firstMarker) { Remove-Item -LiteralPath $firstMarker -Force }
  }
  if (Get-Variable -Name secondMarker -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $secondMarker) { Remove-Item -LiteralPath $secondMarker -Force }
  }
  if (Test-Path $log) { Copy-Item $log -Destination "artifacts/IG-Cleaner-Pro-Installer-InstallLog.txt" -Force }
}
