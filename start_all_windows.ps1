param($DashboardPort, $ApiPort, $DebuggerPort, $BindHost)

$ErrorActionPreference = 'Stop'

<#
Launches Project Dashboard (8592) and the template LangGraph dev server
(8124/3001) in separate PowerShell windows.

Run this from a native Windows PowerShell (not WSL).
#>

# Fallback defaults for broad PowerShell compatibility
if (-not $DashboardPort) { $DashboardPort = 8592 }
if (-not $ApiPort) { $ApiPort = 8124 }
if (-not $DebuggerPort) { $DebuggerPort = 3001 }
if (-not $BindHost) { $BindHost = '127.0.0.1' }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Start-Detached {
  param(
    [string]$ScriptPath,
    [string[]]$Args
  )
  Start-Process -WindowStyle Normal -FilePath 'powershell.exe' -ArgumentList (@('-NoProfile','-ExecutionPolicy','Bypass','-File', $ScriptPath) + $Args) | Out-Null
}

# Preflight checks
if ($env:WSL_DISTRO_NAME) {
  Write-Warning "Detected WSL environment ($($env:WSL_DISTRO_NAME)). Please run this script from native Windows PowerShell, not WSL."
}

# Ensure the template venv exists; if not, bootstrap it
$setup = Join-Path $root 'new-langgraph-project\scripts\setup_windows.ps1'
if (-not (Test-Path $setup)) { throw "Missing script: $setup" }
$templateRoot = Join-Path $root 'new-langgraph-project'
$venvPath = Join-Path $templateRoot '.venv'
if (-not (Test-Path $venvPath)) {
  Write-Host "==> .venv not found in new-langgraph-project. Running setup." -ForegroundColor Yellow
  Start-Detached -ScriptPath $setup -Args @()
  Start-Sleep -Seconds 8
}

# 1) Project Dashboard (Streamlit)
$dashboard = Join-Path $root 'new-langgraph-project\scripts\dashboard_windows.ps1'
if (-not (Test-Path $dashboard)) { throw "Missing script: $dashboard" }
Write-Host ("==> Launching Project Dashboard on http://{0}:{1} (includes Logs)" -f $BindHost, $DashboardPort)
Start-Detached -ScriptPath $dashboard -Args @('-Port', ($DashboardPort.ToString()))

# 2) Template LangGraph dev server
$server = Join-Path $root 'new-langgraph-project\scripts\dev_windows.ps1'
if (-not (Test-Path $server)) { throw "Missing script: $server" }
Write-Host ("==> Launching Template LangGraph Server (host {0}, api {1}, debugger {2})" -f $BindHost, $ApiPort, $DebuggerPort)
Start-Detached -ScriptPath $server -Args @('-BindHost', $BindHost, '-Port', ($ApiPort.ToString()), '-DebuggerPort', ($DebuggerPort.ToString()))

Write-Host "\nAll services launched:" -ForegroundColor Green
Write-Host ("- Project Dashboard: http://{0}:{1} (includes Logs viewer)" -f $BindHost, $DashboardPort)
Write-Host ("- Template API:      http://{0}:{1}/docs" -f $BindHost, $ApiPort)
Write-Host ("- Template Studio:   http://{0}:{1}/ (if used by Studio)" -f $BindHost, $DebuggerPort)
