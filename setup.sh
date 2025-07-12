#!/bin/bash

# SceneSplit Setup Script
# This script sets up the complete SceneSplit application

echo "🎬 Setting up SceneSplit - AI-Powered Film Production Management System"
echo "=================================================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Backend Setup
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv myvenv

# Activate virtual environment (Linux/macOS)
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    source myvenv/bin/activate
# Activate virtual environment (Windows)
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source myvenv/Scripts/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please add your GEMINI_API_KEY to backend/.env"
fi

cd ..

# Frontend Setup
echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "1. Backend (Terminal 1):"
echo "   cd backend"
echo "   # Activate virtual environment:"
echo "   # Linux/macOS: source myvenv/bin/activate"
echo "   # Windows: myvenv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo "2. Frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to: http://localhost:5173"
echo ""
echo "📚 Don't forget to:"
echo "   - Add your GEMINI_API_KEY to backend/.env"
echo "   - Check the README.md for detailed instructions"
echo ""
echo "🎬 Happy filmmaking!"
