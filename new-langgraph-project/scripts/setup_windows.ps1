$ErrorActionPreference = 'Stop'

Write-Host '==> LangGraph Windows setup starting...'

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ..

if (-not (Test-Path '.venv')) {
  Write-Host '==> Creating Python 3.11 venv (.venv)'
  try {
    py -3.11 -m venv .venv
  } catch {
    if (Test-Path 'C:\\Program Files\\Python311\\python.exe') {
      & 'C:\\Program Files\\Python311\\python.exe' -m venv .venv
    } elseif (Test-Path 'C:\\Program Files\\Python312\\python.exe') {
      & 'C:\\Program Files\\Python312\\python.exe' -m venv .venv
    } else {
      throw 'Python 3.11/3.12 not found. Install Python 3.11 from python.org.'
    }
  }
}

Write-Host '==> Upgrading pip'
.\.venv\Scripts\python.exe -m pip install -U pip

Write-Host '==> Installing project (editable) + LangGraph CLI (in-memory)'
.\.venv\Scripts\pip.exe install -e . "langgraph-cli[inmem]"

# Optional: install local mem0 if present
if (Test-Path 'D:\mem0\pyproject.toml') {
  Write-Host '==> Installing local mem0 (D:\mem0)'
  .\.venv\Scripts\pip.exe install -e D:\mem0 | Write-Host
}

if (-not (Test-Path '.env') -and (Test-Path '.env.example')) {
  Copy-Item '.env.example' '.env'
  Write-Host '==> Created .env from .env.example. Please edit .env to set keys.'
}

Write-Host '==> LangGraph CLI version:'
.\.venv\Scripts\langgraph.exe --version

Write-Host '==> Python version:'
.\.venv\Scripts\python.exe -c "import sys; print(sys.version)"

Write-Host '==> Setup complete.'
