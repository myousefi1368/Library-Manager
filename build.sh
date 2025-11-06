#!/bin/bash
echo "Library Manager - Build Script"
echo "==========================="

echo "Installing dependencies..."
pip install -r requirements.txt

echo
echo "Building EXE..."
python -m PyInstaller --onefile --windowed --name "LibraryManager" libraryManager.py

if [ -f "dist/LibraryManager.exe" ]; then
    echo
    echo "✅ BUILD SUCCESSFUL!"
    echo "📁 EXE location: dist/LibraryManager.exe"
else
    echo
    echo "❌ BUILD FAILED!"
fi