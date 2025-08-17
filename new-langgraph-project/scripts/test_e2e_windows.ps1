param(
  [string]$BaseUrl = 'http://127.0.0.1:8123',
  [string]$DebuggerUrl = 'http://127.0.0.1:3000',
  [switch]$UseCodex
)

$ErrorActionPreference = 'Stop'

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if (-not (Test-Path '.venv')) { throw 'Missing .venv. Run scripts/setup_windows.ps1 first.' }

# Optional: signal to tests
$env:SPORTMAN_BASE_URL = $BaseUrl
$env:STUDIO_URL = $DebuggerUrl
if ($UseCodex) { $env:USE_CODEX = '1' }

Write-Host "==> Running e2e tests against $BaseUrl (Debugger: $DebuggerUrl)"
try {
  .\.venv\Scripts\python.exe -m pytest -m e2e tests/e2e -q
} catch {
  Write-Warning $_
  throw $_
}

