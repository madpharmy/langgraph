param(
  [int]$ApiPort = 8123,
  [int]$DebugPort = 3000
)

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

Write-Host '==> Ensuring pytest + Playwright present' -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install -q pytest pytest-playwright playwright
.\.venv\Scripts\python.exe -m playwright install

# Pick free ports if needed
if (-not (Test-PortFree -Port $ApiPort)) { $ApiPort = 8130 }
if (-not (Test-PortFree -Port $DebugPort)) { $DebugPort = 3005 }
$omitDebug = $false
if (-not (Test-PortFree -Port $DebugPort)) { $omitDebug = $true }

$env:SPORTMAN_BASE_URL = "http://127.0.0.1:$ApiPort"
$env:SPORTMAN_DEBUGGER_URL = "http://127.0.0.1:$DebugPort"

$repo = (Split-Path -Parent (Split-Path -Parent $pwd))
$logDir = Join-Path $repo 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$out = Join-Path $logDir 'sportman_e2e_server.out.log'
$err = Join-Path $logDir 'sportman_e2e_server.err.log'

if ($omitDebug) {
  Write-Host "==> Starting server on $($env:SPORTMAN_BASE_URL) (no debug)" -ForegroundColor Cyan
  $args = @('dev','--host','127.0.0.1','--port',"$ApiPort",'--no-browser')
} else {
  Write-Host "==> Starting server on $($env:SPORTMAN_BASE_URL) (debug $DebugPort)" -ForegroundColor Cyan
  $args = @('dev','--host','127.0.0.1','--port',"$ApiPort",'--debug-port',"$DebugPort",'--no-browser')
}
$p = Start-Process -FilePath ".\.venv\Scripts\langgraph.exe" -ArgumentList $args -WorkingDirectory $pwd -RedirectStandardOutput $out -RedirectStandardError $err -PassThru

try {
  for ($i=0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1
    try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 -Uri "$($env:SPORTMAN_BASE_URL)/docs"; if ($r.StatusCode -ge 200) { break } } catch {}
  }
  if ($i -ge 20) { throw "Server didn't start; see $err" }

  Write-Host '==> Running E2E docs + (optional) debugger tests' -ForegroundColor Cyan
  .\.venv\Scripts\pytest.exe -q tests\e2e\test_docs_page.py::test_docs_page_loads -q --maxfail=1 --browser chromium
  .\.venv\Scripts\pytest.exe -q tests\e2e\test_debugger_page.py::test_debugger_page_loads -q --maxfail=1 --browser chromium
} finally {
  Write-Host '==> Stopping server' -ForegroundColor Yellow
  try { Stop-Process -Id $p.Id -Force } catch {}
}

Write-Host '==> Sportman E2E complete.' -ForegroundColor Green
