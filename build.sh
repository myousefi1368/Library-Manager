#!/bin/bash

# build.sh - Build Library Manager with PyQt5 and icon
# Usage: ./build.sh

echo "📚 Building Library Manager with PyQt5..."
echo "========================================="

# Check Python
if ! command -v py &> /dev/null; then
    echo "❌ Python not found!"
    exit 1
fi

# Check icon
if [ ! -f "icon.ico" ]; then
    echo "❌ icon.ico not found in current directory!"
    echo "Please place icon.ico in this folder."
    exit 1
fi

echo "✅ Found icon.ico"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec 2>/dev/null

# Build
echo "🛠️  Building executable..."
py -m PyInstaller \
    --onefile \
    --windowed \
    --clean \
    --name="LibraryManager" \
    --icon="icon.ico" \
	--add-data "icon.ico;." \
    --hidden-import=PyQt6 \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=jdatetime \
	--hidden-import=qt_material \
    --exclude-module=PyQt5 \
    --exclude-module=PySide2 \
    --exclude-module=PySide5 \
    libraryManager.py

# Check result
if [ -f "dist/LibraryManager" ]; then
    SIZE=$(du -h "dist/LibraryManager" | cut -f1)
    echo ""
    echo "✅ Build successful!"
    echo "📊 Size: $SIZE"
    echo "📍 Location: $(pwd)/dist/LibraryManager"
    echo "🎨 Icon: Applied successfully"
    echo "🎉 Done! Copy the 'dist' folder to Windows 8.1"
else
    echo "❌ Build failed!"
    exit 1
fi