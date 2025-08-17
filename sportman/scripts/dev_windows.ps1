$ErrorActionPreference = 'Stop'

function Test-PortFree {
  param([int]$Port)
  try {
    $res = Test-NetConnection -ComputerName '127.0.0.1' -Port $Port -WarningAction SilentlyContinue
    return -not $res.TcpTestSucceeded
  } catch { return $true }
}

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if (-not (Test-Path '.venv')) { throw 'Missing .venv. Run scripts/setup_windows.ps1 first.' }

$api = 8123
$api_fallback = 8130
$dbg = 3000
$dbg_fallback = 3005

if (-not (Test-PortFree -Port $api)) {
  Write-Warning "Port $api busy; using fallback $api_fallback"
  $api = $api_fallback
}
if (-not (Test-PortFree -Port $dbg)) {
  Write-Warning "Debug port $dbg busy; using fallback $dbg_fallback"
  $dbg = $dbg_fallback
}

Write-Host ("==> Starting LangGraph dev server (host 0.0.0.0, port {0}, debug {1})" -f $api, $dbg)
.\.venv\Scripts\langgraph.exe dev --host 0.0.0.0 --port $api --debug-port $dbg --no-browser
