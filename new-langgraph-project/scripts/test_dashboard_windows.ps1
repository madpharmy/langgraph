param(
  [string]$DashboardUrl = 'http://127.0.0.1:8592'
)

$ErrorActionPreference = 'Stop'

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if (-not (Test-Path '.venv')) { throw 'Missing .venv. Run scripts/setup_windows.ps1 first.' }

Write-Host "==> Installing Playwright + pytest in template venv" -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install -q pytest pytest-playwright playwright
.\.venv\Scripts\python.exe -m playwright install

$env:DASHBOARD_URL = $DashboardUrl

Write-Host "==> Running dashboard E2E (Console tab) against $DashboardUrl" -ForegroundColor Cyan
$repoRoot = Split-Path -Parent (Split-Path -Parent $pwd)
$tracePath = Join-Path $repoRoot 'logs\dashboard_console_trace.zip'
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_dashboard_console.py::test_console_runs_command_and_shows_output -vv -s --maxfail=1
$code = $LASTEXITCODE
if ($code -ne 0) {
  Write-Warning "Dashboard E2E failed with exit code $code"
  if (Test-Path $tracePath) { Write-Host "Trace saved to: $tracePath" -ForegroundColor Yellow }
  $consoleLog = Join-Path $repoRoot 'logs\codex_console.log'
  if (Test-Path $consoleLog) {
    Write-Host '--- codex_console.log (tail) ---' -ForegroundColor Cyan
    Get-Content -Tail 80 $consoleLog
  }
  exit $code
}

Write-Host '==> Dashboard E2E complete.' -ForegroundColor Green
