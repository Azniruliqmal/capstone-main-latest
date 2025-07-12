@echo off
REM SceneSplit Setup Script for Windows
REM This script sets up the complete SceneSplit application

echo 🎬 Setting up SceneSplit - AI-Powered Film Production Management System
echo ==================================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed

REM Backend Setup
echo.
echo 🔧 Setting up Backend...
cd backend

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv myvenv

REM Activate virtual environment
echo Activating virtual environment...
call myvenv\Scripts\activate

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    copy .env.example .env
    echo 📝 Created .env file. Please add your GEMINI_API_KEY to backend\.env
)

cd ..

REM Frontend Setup
echo.
echo 🎨 Setting up Frontend...
cd frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

cd ..

echo.
echo ✅ Setup Complete!
echo.
echo 🚀 To start the application:
echo.
echo 1. Backend (Terminal 1):
echo    cd backend
echo    myvenv\Scripts\activate
echo    python main.py
echo.
echo 2. Frontend (Terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open your browser to: http://localhost:5173
echo.
echo 📚 Don't forget to:
echo    - Add your GEMINI_API_KEY to backend\.env
echo    - Check the README.md for detailed instructions
echo.
echo 🎬 Happy filmmaking!
pause
