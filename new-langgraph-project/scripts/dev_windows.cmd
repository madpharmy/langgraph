@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev_windows.ps1" %*
exit /b %errorlevel%

