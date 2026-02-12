#!/bin/bash

# Web Security Scanner - Quick Start Script for Linux/macOS

echo ""
echo "============================================="
echo " Web Security Scanner - Quick Start"
echo "============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

echo "[+] Python version:"
python3 --version

echo "[+] Node.js version:"
node --version

echo ""
echo "[+] Installing backend dependencies..."
pip3 install -r requirements-api.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install backend dependencies"
    exit 1
fi
echo "[✓] Backend dependencies installed"

echo ""
echo "[+] Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install frontend dependencies"
    cd ..
    exit 1
fi
echo "[✓] Frontend dependencies installed"
cd ..

echo ""
echo "============================================="
echo " Setup Complete!"
echo "============================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Open Terminal 1 and run:"
echo "   python3 api.py"
echo ""
echo "2. Open Terminal 2 and run:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser and go to:"
echo "   http://localhost:3000"
echo ""
echo "============================================="
echo ""
