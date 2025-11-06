@echo off
echo Library Manager - Build Script
echo ===========================

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building EXE...
python -m PyInstaller --onefile --windowed --name "Library Manager" libraryManager.py

if exist "dist\Library Manager.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo 📁 EXE location: dist\Library Manager.exe
) else (
    echo.
    echo ❌ BUILD FAILED!
)

echo.
pause