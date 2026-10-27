# Shared Windows-only process watchdog: no installer or frozen runtime may hang indefinitely.
function Invoke-IgcBoundedProcess {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string[]]$Arguments,
    [Parameter(Mandatory=$true)][string]$Label,
    [ValidateRange(1,900)][int]$TimeoutSeconds = 150
  )
  $started = [DateTime]::UtcNow
  $process = $null
  try {
    $process = Start-Process -FilePath $Path -ArgumentList $Arguments -PassThru -ErrorAction Stop
    Write-Host ("START: {0} (pid={1}, deadline={2}s)" -f $Label, $process.Id, $TimeoutSeconds)
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
      try { $process.Kill($true) }
      catch { try { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue } catch {} }
      try { [void]$process.WaitForExit(5000) } catch {}
      throw "$Label timed out after $TimeoutSeconds seconds; process tree terminated. Inspect CI step and saved installer logs."
    }
    if ($process.ExitCode -ne 0) {
      throw "$Label exited $($process.ExitCode) after $([math]::Round(([DateTime]::UtcNow - $started).TotalSeconds, 1)) seconds."
    }
    Write-Host ("PASS: {0} finished in {1:n1}s" -f $Label, ([DateTime]::UtcNow - $started).TotalSeconds)
  } finally {
    if ($null -ne $process) { $process.Dispose() }
  }
}
