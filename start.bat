@echo off
REM My - Universal AI App Generator
REM Startup script for Windows

echo.
echo ========================================
echo   MY - UNIVERSAL AI APP GENERATOR
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js found

echo.
echo Installing dependencies...
echo.

REM Install backend dependencies
echo Installing backend dependencies (Python)...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

REM Install frontend dependencies
echo.
echo Installing frontend dependencies (Node.js)...
cd frontend
if not exist node_modules (
    call npm install
)
cd ..

echo.
echo ========================================
echo   STARTING SERVICES
echo ========================================
echo.

REM Create necessary directories
if not exist "C:\temp\my_workspace" mkdir "C:\temp\my_workspace"
if not exist "C:\temp\my_uploads" mkdir "C:\temp\my_uploads"
if not exist "C:\temp\my_database" mkdir "C:\temp\my_database"
if not exist "C:\temp\my_generated" mkdir "C:\temp\my_generated"
if not exist "C:\temp\my_builds" mkdir "C:\temp\my_builds"

REM Start backend
echo Starting backend on http://localhost:8000
cd backend
call venv\Scripts\activate.bat
start /B python main.py > ..\backend.log 2>&1
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend on http://localhost:3000
cd frontend
start /B npm run dev > ..\frontend.log 2>&1
cd ..

REM Wait for services
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   MY IS NOW RUNNING!
echo ========================================
echo.
echo Frontend:  http://localhost:3000
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo To stop: Press Ctrl+C or run stop.bat
echo.
echo Logs:
echo   Backend:  type backend.log
echo   Frontend: type frontend.log
echo.

REM Keep window open
pause
