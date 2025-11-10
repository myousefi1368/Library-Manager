@echo off
echo Library Manager - 32-bit Dependency Fix
echo =====================================

echo Checking current Python environment...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" --version

echo.
echo Step 1: Upgrading pip...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -m pip install --upgrade pip

echo.
echo Step 2: Installing PyQt5...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -m pip install PyQt5

echo.
echo Step 3: Installing jdatetime...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -m pip install jdatetime

echo.
echo Step 4: Installing qt_material...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -m pip install qt_material

echo.
echo Step 5: Installing PyInstaller...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -m pip install pyinstaller

echo.
echo Step 6: Verifying all installations...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -c "from PyQt5 import QtWidgets; import jdatetime; from qt_material import apply_stylesheet; print('✅ All imports successful!')"

echo.
echo Building EXE...
"C:\Users\Yousefi\AppData\Local\Programs\Python\Python312-32\python.exe" -m PyInstaller --onefile --windowed --name "Library Manager x86" --icon=icon.ico --hidden-import jdatetime libraryManager_x86.py

if exist "dist\Library Manager x86.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo 📁 EXE location: dist\Library Manager x86.exe
) else (
    echo.
    echo ❌ BUILD FAILED!
)

echo.
pause