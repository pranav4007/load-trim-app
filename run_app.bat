@echo off
cd /d "%~dp0"
echo Launching Load and Trim Calculator...

REM Start Flask app
start "" /b cmd /c "python app.py"

REM Wait for Flask to start
timeout /t 3 >nul

REM Open in browser
start http://127.0.0.1:5000

exit
