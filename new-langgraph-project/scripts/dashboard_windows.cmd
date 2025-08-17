@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dashboard_windows.ps1" %*
exit /b %errorlevel%

