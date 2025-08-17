@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_all_windows.ps1" %*
exit /b %errorlevel%

