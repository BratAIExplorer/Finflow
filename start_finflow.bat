@echo off
echo ==========================================
echo Starting FinFlow Dashboard...
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python Setup...
if not exist "venv\Scripts\activate.bat" (
    echo First time setup: Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing backend dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo [2/3] Checking Node.js Setup...
cd frontend
if not exist "node_modules\" (
    echo First time setup: Installing frontend dependencies...
    call npm install
)
cd ..

echo.
echo [3/3] Launching Servers...
echo - Starting Backend Server (minimized)...
start "FinFlow Backend" /MIN cmd /c "title FinFlow Backend && call venv\Scripts\activate.bat && uvicorn backend.main:app --reload"

echo - Starting Frontend Server (minimized)...
start "FinFlow Frontend" /MIN cmd /c "title FinFlow Frontend && cd frontend && npm run dev"

echo.
echo Waiting a few seconds for servers to start up...
timeout /t 7 /nobreak >nul

echo Opening your browser to the Dashboard...
start http://localhost:3000

echo.
echo ==========================================
echo FinFlow is running!
echo Note: Keep the two black command windows 
echo open while using the dashboard.
echo Close them when you're done.
echo ==========================================
pause
