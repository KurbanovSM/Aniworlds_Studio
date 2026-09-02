@echo off
setlocal
set "STUDIO_PYTHON=%~dp0.venv\Scripts\pythonw.exe"
if not exist "%STUDIO_PYTHON%" (
  echo Studio is not installed. Follow the setup steps in README.md.
  pause
  exit /b 1
)
set "PYTHONPATH=%~dp0src"
start "" "%STUDIO_PYTHON%" -m aniworlds_studio
