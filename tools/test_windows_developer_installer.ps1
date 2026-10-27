param(
  [Parameter(Mandatory=$true)][string]$Installer,
  [Parameter(Mandatory=$true)][string]$Version
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$setup = (Resolve-Path $Installer).Path
$prefix = Join-Path $env:RUNNER_TEMP ("igc-installed-dev-" + $Version)
$log = Join-Path $env:RUNNER_TEMP "igc-developer-installer.log"
$publicDir = Join-Path $env:LOCALAPPDATA "Michels Lab\Insta Cleaner Pro"
$publicMarker = Join-Path $publicDir "developer-isolation-sentinel.txt"
New-Item -ItemType Directory -Force $prefix,$publicDir | Out-Null
"keep-public-data" | Set-Content $publicMarker -Encoding UTF8
. (Join-Path $PSScriptRoot "installer_process_guard.ps1")
function RunBounded($path, [string[]]$arguments, $label, [int]$timeout = 150) {
  Invoke-IgcBoundedProcess -Path $path -Arguments $arguments -Label $label -TimeoutSeconds $timeout
}
try {
  RunBounded $setup @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$prefix+'"'),('/LOG="'+$log+'"')) 'Developer Setup'
  $exe=Join-Path $prefix "InstaCleanerPro.exe"
  $uninstaller=Join-Path $prefix "unins000.exe"
  foreach($path in @($exe,$uninstaller,(Join-Path $prefix "BUILD-INFO.txt"))) {
    if (!(Test-Path $path)) { throw "Developer install missing $path" }
  }
  $menu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Insta Cleaner Pro Developer\Insta Cleaner Pro - Developer Edition.lnk"
  if (!(Test-Path $menu)) { throw "Independent Developer Start shortcut missing" }
  $link=(New-Object -ComObject WScript.Shell).CreateShortcut($menu)
  if ($link.Arguments -ne "--developer") { throw "Developer shortcut must always use --developer" }
  RunBounded $exe @('--healthcheck') 'Developer installed healthcheck' 75
  RunBounded $exe @('--smoke-startup','--developer') 'Developer installed startup' 100
  $devWorkspace=Join-Path $publicDir "developer-edition"
  if (!(Test-Path (Join-Path $devWorkspace "IG-Cleaner-Pro.html"))) {
    throw "Developer did not create its own UI origin"
  }
  if (!(Test-Path $publicMarker)) { throw "Developer damaged public app storage" }
  RunBounded $uninstaller @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') 'Developer uninstall' 120
  if (Test-Path $exe) { throw "Developer executable remains after uninstall" }
  if (!(Test-Path $publicMarker)) { throw "Developer uninstall deleted public user data" }
  Write-Host "PASS: independent Developer install, --developer launcher, smoke, isolated UI, uninstall, public-data preservation"
}
finally {
  if (Test-Path $publicMarker) { Remove-Item $publicMarker -Force }
  if (Test-Path $log) { Copy-Item $log -Destination "artifacts/IG-Cleaner-Pro-Developer-Installer-InstallLog.txt" -Force }
}
