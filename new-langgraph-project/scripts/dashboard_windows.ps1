param($Port)

$ErrorActionPreference = 'Stop'
if (-not $Port) { $Port = 8592 }

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if (-not (Test-Path '.venv')) { throw 'Missing .venv. Run scripts/setup_windows.ps1 first.' }

# Start transcript to capture output
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$logDir = Join-Path $repoRoot 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$logPath = Join-Path $logDir 'dashboard.log'
try {
  Start-Transcript -Path $logPath -Append | Out-Null
} catch {}

Write-Host '==> Ensuring Streamlit is installed in venv'
.\.venv\Scripts\pip.exe install -q streamlit

Write-Host "==> Launching Project Dashboard (Streamlit) on port $Port"
try {
  .\.venv\Scripts\python.exe -m streamlit run .\src\dashboard\app.py --server.address 127.0.0.1 --server.port $Port --server.headless true
} finally {
  try { Stop-Transcript | Out-Null } catch {}
}
