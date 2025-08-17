param($Port, $DebuggerPort, $BindHost)

$ErrorActionPreference = 'Stop'
if (-not $Port) { $Port = 8124 }
if (-not $DebuggerPort) { $DebuggerPort = 3001 }
if (-not $BindHost) { $BindHost = '127.0.0.1' }

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if (-not (Test-Path '.venv')) { throw 'Missing .venv. Run scripts/setup_windows.ps1 first.' }

# Start transcript to capture server output
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$logDir = Join-Path $repoRoot 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$logPath = Join-Path $logDir 'server.log'
try {
  Start-Transcript -Path $logPath -Append | Out-Null
} catch {}

Write-Host "==> Starting LangGraph dev server (host $BindHost, port $Port, debug $DebuggerPort)"
try {
  .\.venv\Scripts\langgraph.exe dev --host $BindHost --port $Port --debug-port $DebuggerPort --no-browser
} catch {
  Write-Warning $_
  throw $_
} finally {
  try { Stop-Transcript | Out-Null } catch {}
}
