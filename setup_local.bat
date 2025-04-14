@echo off
:: Set console code page to UTF-8
chcp 65001 >nul

:: Enable command extensions
verify on
setlocal enableextensions

:: WJX Automation System Local Deployment Script
:: Author: Ignorant-lu
:: Version: 2.6 - Fixed Port Conflict

:: Set title
title WJX Automation System Local Deployment

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Set ports (changed frontend port to avoid conflict with Docker)
set BACKEND_PORT=5000
set BACKEND_HOST=127.0.0.1
set FRONTEND_PORT=5174

echo ===============================================================
echo              WJX Automation System Local Setup v2.6
echo ===============================================================
echo.
echo This script will help you set up the WJX Automation System locally.
echo.
echo The deployment process includes:
echo  - System environment check
echo  - Python virtual environment setup
echo  - Dependencies installation
echo  - Environment configuration
echo  - Service startup
echo.

:: Create temp file for command output
set "TEMP_FILE=%TEMP%\setup_output.txt"
if exist "%TEMP_FILE%" del "%TEMP_FILE%"

:: Confirm to continue
set /p confirm=Continue with deployment? (y/N):
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    goto :eof
)

:: Check system requirements
echo Checking system requirements...
echo [Step 1/5] Checking components...

:: Check Python
echo  - Checking Python...
python --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Please install Python 3.9 or higher: https://www.python.org/downloads/
    type "%TEMP_FILE%"
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + Python check passed

:: Check pip
echo  - Checking pip...
pip --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo Error: pip not found
    echo Please ensure pip is installed with Python
    type "%TEMP_FILE%"
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + pip check passed

:: Check Node.js
echo  - Checking Node.js...
node --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js not found
    echo Please install Node.js 16 or higher: https://nodejs.org/
    type "%TEMP_FILE%"
    start https://nodejs.org/
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + Node.js check passed

:: Check npm
echo  - Checking npm...
call npm --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo Error: npm not found
    echo Please ensure npm is installed with Node.js
    type "%TEMP_FILE%"
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + npm check passed

echo System check passed!
echo.

:: Check project directory
echo [Step 2/5] Checking project environment...
echo  - Checking project files...

if not exist "backend" (
    echo Error: Not in project root directory
    echo Please run this script in the project root directory
    pause
    exit /b 1
)
echo   + Project files check passed

:: Create necessary directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "data\surveys" mkdir data\surveys
if not exist "data\tasks" mkdir data\tasks
if not exist "logs\api" mkdir logs\api
echo   + Data directories created

:: Create Python virtual environment
echo [Step 3/5] Creating Python virtual environment...

set "VENV_CREATED=0"

if exist "venv" (
    set /p "RECREATE=Virtual environment exists. Recreate? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q venv
        set "VENV_CREATED=0"
    ) else (
        echo   + Using existing virtual environment
        set "VENV_CREATED=1"
    )
)

if "%VENV_CREATED%"=="0" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   + Virtual environment created
)

:: Install backend dependencies
echo [Step 4/5] Installing dependencies...
echo  - Installing backend dependencies...

call venv\Scripts\activate.bat
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install backend dependencies
    pause
    exit /b 1
)
echo   + Backend dependencies installed

:: Install frontend dependencies
echo  - Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo Error: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)

:: Ensure vite is installed
call npm install --save-dev vite @vitejs/plugin-vue
if errorlevel 1 (
    echo Error: Failed to install Vite
    cd ..
    pause
    exit /b 1
)
echo   + Frontend dependencies installed
cd ..

:: Start services
echo [Step 5/5] Starting services...
echo  - Starting backend service...
start "WJX Backend API - %BACKEND_HOST%:%BACKEND_PORT%" cmd /k "call venv\Scripts\activate.bat && python backend\app.py"
echo   + Backend service started

echo  - Starting frontend service...
cd frontend
:: Set PORT environment variable to use custom port
start "WJX Frontend - %FRONTEND_PORT%" cmd /k "set PORT=%FRONTEND_PORT% && npm run dev"
cd ..
echo   + Frontend service started

echo.
echo ===============================================================
echo Setup completed! Services are starting...
echo.
echo You can access the application at:
echo Frontend: http://localhost:%FRONTEND_PORT%
echo Backend API: http://%BACKEND_HOST%:%BACKEND_PORT%
echo.

echo Press any key to open frontend in browser...
pause >nul
start http://localhost:%FRONTEND_PORT%
