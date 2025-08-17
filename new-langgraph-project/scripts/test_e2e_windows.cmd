@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_e2e_windows.ps1" %*
exit /b %errorlevel%

