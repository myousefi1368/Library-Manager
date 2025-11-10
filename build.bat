@echo off
echo Library Manager - Build Script
echo ===========================

echo Installing dependencies...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" pip install -r requirements.txt

echo.
echo Step 1: Upgrading pip...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" -m pip install --upgrade pip

echo.
echo Step 2: Installing PyQt5...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" -m pip install PyQt6

echo.
echo Step 3: Installing jdatetime...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" -m pip install jdatetime

echo.
echo Step 4: Installing qt_material...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" -m pip install qt_material

echo Step 5: Installing PyInstaller...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" -m pip install pyinstaller
echo.
echo Building EXE...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312\python.exe" -m PyInstaller --onefile --windowed --name "Library Manager" --icon=icon.ico libraryManager.py

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