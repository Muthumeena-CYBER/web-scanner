@echo off
REM Web Security Scanner - Quick Start Script for Windows

echo.
echo =============================================
echo  Web Security Scanner - Quick Start
echo =============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [+] Python version:
python --version

echo [+] Node.js version:
node --version

echo.
echo [+] Installing backend dependencies...
pip install -r requirements-api.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)
echo [✓] Backend dependencies installed

echo.
echo [+] Installing frontend dependencies...
cd frontend
call npm install >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
echo [✓] Frontend dependencies installed
cd ..

echo.
echo =============================================
echo  Setup Complete!
echo =============================================
echo.
echo To start the application:
echo.
echo 1. Open Terminal 1 and run:
echo    python api.py
echo.
echo 2. Open Terminal 2 and run:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open your browser and go to:
echo    http://localhost:3000
echo.
echo =============================================
echo.
pause
