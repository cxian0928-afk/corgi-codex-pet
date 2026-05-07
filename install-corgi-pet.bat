@echo off
setlocal
set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\install_to_codex_pet.ps1"
if errorlevel 1 (
  echo.
  echo Install failed.
  pause
  exit /b 1
)
echo.
echo Install finished. You can close this window.
pause
