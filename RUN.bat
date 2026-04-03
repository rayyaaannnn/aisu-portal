@echo off
REM =============================================================
REM  Run AISU Project (Frontend + Backend)
REM =============================================================

title AISU - Full Stack

echo.
echo ============================================================
echo   AISU Project Startup
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "login.html" (
    echo Error: login.html not found
    echo Make sure you're in the project root directory
    pause
    exit /b 1
)

echo Starting AISU Frontend and Backend...
echo.

REM Start frontend web server in background
echo [1/2] Starting Frontend Web Server on port 8000...
start "AISU Frontend" cmd /k python -m http.server 8000

timeout /t 2 /nobreak

REM Start backend
echo [2/2] Starting Backend on port 5000...
cd backend
echo.
echo ============================================================
echo   AISU Backend v2.1
echo   Frontend: http://localhost:8000
echo   Backend:  http://localhost:5000
echo   Login:    http://localhost:8000/login.html
echo ============================================================
echo.

python app.py

pause
