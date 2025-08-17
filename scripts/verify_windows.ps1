param(
  [Alias('Host')][string]$Address = '127.0.0.1',
  [int]$DashboardPort = 8592,
  [int]$ApiPort = 8124,
  [int]$StudioPort = 3001
)

$ErrorActionPreference = 'Stop'

function Test-Port {
  param([string]$Address, [int]$Port)
  try {
    $res = Test-NetConnection -ComputerName $Address -Port $Port -WarningAction SilentlyContinue
    return $res.TcpTestSucceeded
  } catch { return $false }
}

function Test-Http {
  param([string]$Url)
  try {
    $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri $Url
    return $r.StatusCode -ge 200 -and $r.StatusCode -lt 500
  } catch { return $false }
}

Write-Host "Verifying services on $Address..." -ForegroundColor Cyan

$ok = $true

function Report($name, $okFlag) {
  if ($okFlag) { Write-Host ("[OK]   {0}" -f $name) -ForegroundColor Green }
  else { Write-Host ("[FAIL] {0}" -f $name) -ForegroundColor Red }
}

# Project Dashboard (includes Logs)
$p1 = Test-Port -Address $Address -Port $DashboardPort
$h1 = Test-Http -Url ("http://{0}:{1}" -f $Address, $DashboardPort)
Report ("Project Dashboard port $DashboardPort") $p1
Report (("Project Dashboard HTTP http://{0}:{1}") -f $Address, $DashboardPort) $h1
$ok = $ok -and $p1 -and $h1

# Template API
$p3 = Test-Port -Address $Address -Port $ApiPort
$h3 = Test-Http -Url ("http://{0}:{1}/docs" -f $Address, $ApiPort)
Report ("Template API port $ApiPort") $p3
Report (("Template API HTTP http://{0}:{1}/docs") -f $Address, $ApiPort) $h3
$ok = $ok -and $p3 -and $h3

# Template Studio (port only)
$p4 = Test-Port -Address $Address -Port $StudioPort
Report ("Template Studio port $StudioPort") $p4
$ok = $ok -and $p4

if ($ok) {
  Write-Host "All checks passed." -ForegroundColor Green
  exit 0
} else {
  Write-Host "One or more checks failed. Ensure services are started with start_all_windows.cmd or use individual scripts." -ForegroundColor Yellow
  exit 1
}
