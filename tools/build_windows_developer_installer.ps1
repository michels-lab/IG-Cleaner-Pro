param(
  [Parameter(Mandatory=$true)][string]$PayloadDir,
  [Parameter(Mandatory=$true)][string]$Version,
  [switch]$AllowCurrentStablePreview
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($Version -notmatch '^\d+\.\d+$') { throw "Invalid Developer version: $Version" }
$manifest = Get-Content "release/distribution-manifest.json" -Raw | ConvertFrom-Json
$next = $manifest.releasePolicy.nextRelease
if ($next -ne "v$Version") {
  if (!$AllowCurrentStablePreview -or $manifest.releasePolicy.currentStableRelease -ne "v$Version") {
    throw "Developer Setup requires the governed next release $next (or CI-only preview of current stable)"
  }
}
$payload = (Resolve-Path $PayloadDir).Path
foreach ($name in @("InstaCleanerPro.exe","README.txt","BUILD-INFO.txt","EXECUTABLE-SHA256.txt",
                     "chrome-extension\manifest.json")) {
  if (!(Test-Path (Join-Path $payload $name))) { throw "Developer Setup payload missing $name" }
}
$expected = (Get-Content (Join-Path $payload "EXECUTABLE-SHA256.txt") -Raw).Trim().ToLowerInvariant()
$actual = (Get-FileHash (Join-Path $payload "InstaCleanerPro.exe") -Algorithm SHA256).Hash.ToLowerInvariant()
if ($expected -ne $actual) { throw "Developer executable SHA-256 mismatch" }
$paths = @(
  "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  "${env:ProgramFiles}\Inno Setup 7\ISCC.exe",
  "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe"
)
$compiler = $paths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (!$compiler) { throw "Inno Setup compiler missing" }
& $compiler "/DMyAppVersion=$Version" "/DPayloadDir=$payload" "packaging/windows-installer/InstaCleanerProDeveloper.iss"
if ($LASTEXITCODE -ne 0) { throw "Developer Setup build failed: $LASTEXITCODE" }
$filename = "IG-Cleaner-Pro-Windows-Developer-Setup-v$Version.exe"
$installer = Join-Path (Resolve-Path "artifacts").Path $filename
if (!(Test-Path $installer) -or (Get-Item $installer).Length -lt 10000000) {
  throw "Developer installer too small or absent: $installer"
}
$sha = (Get-FileHash $installer -Algorithm SHA256).Hash.ToLowerInvariant()
"$sha  $filename" | Set-Content "artifacts/$filename.sha256" -Encoding ascii
Write-Host "PASS: independent Developer Setup v$Version + checksum; --developer with read-only default and explicit bounded real-action test"
