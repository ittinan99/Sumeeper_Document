chcp 65001 >nul
@echo off
cd /d "%~dp0"
echo Saving current values as the new reference baseline...
python make_reference.py
if errorlevel 1 (
  echo.
  echo [ERROR] failed - read the message above
  pause
  exit /b 1
)
pause
