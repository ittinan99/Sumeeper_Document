chcp 65001 >nul
@echo off
cd /d "%~dp0"
echo Running Sumeeper combat sim...
python sumeeper_sim_report.py
if errorlevel 1 (
  echo.
  echo [ERROR] run failed - read the message above
  pause
  exit /b 1
)
start "" sim_report.html
