@echo off
setlocal
set "STUDIO_EXE=%~dp0.venv\Scripts\aniworlds-studio.exe"
if not exist "%STUDIO_EXE%" (
  echo Studio is not installed. Follow the setup steps in README.md.
  pause
  exit /b 1
)
start "" "%STUDIO_EXE%"
