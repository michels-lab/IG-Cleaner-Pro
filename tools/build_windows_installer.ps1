param(
  [Parameter(Mandatory=$true)][string]$PayloadDir,
  [Parameter(Mandatory=$true)][string]$Version
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($Version -notmatch '^\d+\.\d+$') { throw "Invalid governed installer version: $Version" }
$manifest = Get-Content "release/distribution-manifest.json" -Raw | ConvertFrom-Json
$next = $manifest.releasePolicy.nextRelease
if ($next -ne "v$Version") { throw "Installer version $Version does not match the governed next release $next" }
$payload = (Resolve-Path $PayloadDir).Path
foreach ($name in @("InstaCleanerPro.exe","README.txt","BUILD-INFO.txt","EXECUTABLE-SHA256.txt",
                     "chrome-extension\manifest.json","chrome-extension\popup.html",
                     "chrome-extension\collector.js","chrome-extension\popup.js")) {
  if (!(Test-Path (Join-Path $payload $name))) { throw "Installer input missing: $name" }
}
$expected = (Get-Content (Join-Path $payload "EXECUTABLE-SHA256.txt") -Raw).Trim().ToLowerInvariant()
$actual = (Get-FileHash (Join-Path $payload "InstaCleanerPro.exe") -Algorithm SHA256).Hash.ToLowerInvariant()
if ($expected -ne $actual) { throw "Embedded robot executable checksum mismatch" }
$compiler = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (!(Test-Path $compiler)) { throw "Inno Setup 6 is required. Install with 'choco install innosetup --yes --no-progress'." }
& $compiler "/DMyAppVersion=$Version" "/DPayloadDir=$payload" "packaging/windows-installer/InstaCleanerPro.iss"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed with $LASTEXITCODE" }
$filename = "IG-Cleaner-Pro-Windows-Setup-v$Version.exe"
$installer = Join-Path (Resolve-Path "artifacts").Path $filename
if (!(Test-Path $installer) -or (Get-Item $installer).Length -lt 10000000) {
  throw "The installer is missing or too small: $installer"
}
$sha = (Get-FileHash $installer -Algorithm SHA256).Hash.ToLowerInvariant()
"$sha  $filename" | Set-Content "artifacts/$filename.sha256" -Encoding ascii
Write-Host "PASS: compiled branded setup with complete payload + digest: $filename"
