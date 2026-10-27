# Real Windows-only child-process tests. No Instagram, sessions, installs, or user data.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot '..\tools\installer_process_guard.ps1')
$cmd = Join-Path $env:WINDIR 'System32\cmd.exe'
$timer = [Diagnostics.Stopwatch]::StartNew()
Invoke-IgcBoundedProcess -Path $cmd -Arguments @('/d','/c','exit 0') -Label 'expected success' -TimeoutSeconds 15
function Assert-GuardFailure([string]$Path,[string[]]$Arguments,[int]$TimeoutSeconds,[string]$Pattern) {
  $failure = $null
  try {
    Invoke-IgcBoundedProcess -Path $Path -Arguments $Arguments -Label 'expected failure' -TimeoutSeconds $TimeoutSeconds
  } catch {
    $failure = $_.Exception.Message
  }
  if ($null -eq $failure -or $failure -notmatch $Pattern) {
    throw "Expected $Pattern; received: $failure"
  }
}
Assert-GuardFailure $cmd @('/d','/c','exit 7') 15 'exited 7'
$pwsh = (Get-Process -Id $PID).Path
Assert-GuardFailure $pwsh @('-NoLogo','-NoProfile','-NonInteractive','-Command','Start-Sleep -Seconds 25') 2 'timed out after 2 seconds'
$timer.Stop()
if ($timer.Elapsed.TotalSeconds -ge 20) { throw "Child did not fail promptly: $($timer.Elapsed.TotalSeconds)s" }
Write-Host ("PASS: 0, nonzero and hung children handled in {0:n1}s" -f $timer.Elapsed.TotalSeconds)
