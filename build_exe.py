import PyInstaller.__main__
import os
import sys
import json
import shutil
from datetime import datetime

def build_library_app():
    """
    Build executable for Library Manager application
    """
    
    print("🔧 Starting Library Manager executable build...")
    print("-" * 50)
    
    # Build parameters - excluding PySide6
    params = [
        'libraryManager.py',
        '--onefile',
        '--windowed',
        '--name=LibraryManager',
        '--hidden-import=PyQt6',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=jdatetime',
        '--hidden-import=qt_material',
        '--exclude=PySide6',      # Exclude PySide6
        '--exclude=PySide2',      # Exclude PySide2
        '--exclude=PyQt5',        # Exclude PyQt5
        '--clean',
    ]
    
    # Add icon
    icon_file = 'icon.ico'
    if os.path.exists(icon_file):
        params.extend(['--icon', icon_file])
        print(f"✅ Icon found: {icon_file}")
    else:
        print("⚠️  Icon file not found")
    
    # Custom output directory
    build_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"builds/library_build_{build_time}"
    params.extend(['--distpath', output_dir])
    
    print("📋 Build parameters:")
    for i, param in enumerate(params, 1):
        print(f"  {i:2}. {param}")
    
    print("-" * 50)
    print("⏳ Building... (This may take several minutes)")
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(params)
        
        exe_path = os.path.join(output_dir, 'LibraryManager.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ Build successful!")
            print(f"📍 Executable: {exe_path}")
            print(f"📦 File size: {size_mb:.2f} MB")
            
            # Create additional files
            create_run_bat(output_dir)
            create_readme_file(output_dir)
            
            return True, output_dir
        else:
            print("\n❌ Executable was not created!")
            return False, None
            
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        return False, None

def check_qt_packages():
    """Check installed Qt packages"""
    import pkg_resources
    
    qt_packages = []
    for package in pkg_resources.working_set:
        name = package.key
        if 'qt' in name.lower() or 'pyside' in name.lower() or 'pyqt' in name.lower():
            qt_packages.append(f"{package.project_name}=={package.version}")
    
    return qt_packages

def cleanup_qt_packages():
    """Clean up extra Qt packages"""
    print("🔍 Checking installed Qt packages...")
    qt_packages = check_qt_packages()
    
    if qt_packages:
        print("📦 Found Qt packages:")
        for pkg in qt_packages:
            print(f"  • {pkg}")
        
        # If PySide6 is found
        if any('pyside6' in pkg.lower() for pkg in qt_packages):
            print("\n⚠️  PySide6 detected. This conflicts with PyQt6.")
            choice = input("Remove PySide6? (y/n): ").strip().lower()
            
            if choice == 'y':
                os.system("pip uninstall PySide6 pyside6-essentials -y")
                print("✅ PySide6 removed")
                
                # Install PyQt6 if not present
                if not any('pyqt6' in pkg.lower() for pkg in qt_packages):
                    print("📦 Installing PyQt6...")
                    os.system("pip install PyQt6 --upgrade")
                    print("✅ PyQt6 installed")
                    
        # Check for PyQt5 as well
        if any('pyqt5' in pkg.lower() for pkg in qt_packages):
            print("\n⚠️  PyQt5 detected. This may cause conflicts.")
            choice = input("Remove PyQt5? (y/n): ").strip().lower()
            
            if choice == 'y':
                os.system("pip uninstall PyQt5 -y")
                print("✅ PyQt5 removed")
    else:
        print("✅ No Qt packages found.")
        print("📦 Installing PyQt6...")
        os.system("pip install PyQt6 --upgrade")
        print("✅ PyQt6 installed")

def create_run_bat(output_dir):
    """Create a batch file for easy execution"""
    batch_content = """@echo off
chcp 65001 > nul
echo ========================================
echo 📚 Library Manager - Book Management System
echo ========================================
echo.
echo Starting application...
echo.
echo Note: If you encounter "VCRUNTIME140_1.dll" error:
echo 1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo 2. Run and install the file
echo 3. Restart the application
echo.
pause
echo.
LibraryManager.exe
pause
"""
    
    bat_path = os.path.join(output_dir, 'run.bat')
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"📝 Created run.bat: {bat_path}")
    return bat_path

def create_readme_file(output_dir):
    """Create README file with instructions"""
    readme_content = """📚 Library Manager - Book Management System
===========================================

🔧 Features:
• Library member management
• Book catalog management
• Loan and return system
• Automatic fine calculation
• Comprehensive reporting
• Backup and restore functionality
• Persian interface with Jalali calendar support

🚀 How to Run:
1. Double-click LibraryManager.exe
2. Or run via run.bat

📂 Required Files:
• LibraryManager.exe    (Main application)
• library_data.json     (Application data - created automatically)
• backup/               (Backup folder)

⚙️ System Requirements:
• Windows 7 or higher (64-bit recommended)
• Microsoft Visual C++ Redistributable 2015-2022

🔄 Updating:
To update, replace the LibraryManager.exe file.
Your data is stored in library_data.json.

🔧 Troubleshooting:

1. "VCRUNTIME140_1.dll not found" error:
   - Install Visual C++ Redistributable:
     https://aka.ms/vs/17/release/vc_redist.x64.exe

2. Application won't start:
   - Run as Administrator
   - Temporarily disable antivirus
   - Check Windows Event Viewer for errors

3. Persian text display issues:
   - Install Persian fonts on system
   - Try Tahoma or Arial font

4. Data file issues:
   - If library_data.json is corrupted, delete it and restart
   - Restore from backup in backup/ folder

📞 Support:
[Your contact information here]

⚠️ Important Notes:
• Do NOT delete library_data.json (contains all your data)
• Regularly backup library_data.json
• No Python or libraries installation required
• Data is stored locally in JSON format

🎯 Quick Start:
1. Add members in "Members" section
2. Add books in "Books" section
3. Loan books in "Loans" section
4. Use "Dashboard" for overview

🔐 Data Safety:
• Backups are automatically created in backup/ folder
• You can restore from any backup file
• Data is saved automatically after each operation

📊 Reports:
• Overdue books report in Dashboard
• Member loan history
• Book loan history
• Fine calculations

Version: 1.0.0
Build Date: """ + datetime.now().strftime("%Y-%m-%d") + """
"""
    
    readme_path = os.path.join(output_dir, 'README.txt')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📘 Created README.txt: {readme_path}")
    return readme_path

def show_post_build_instructions(output_dir):
    """Display instructions after successful build"""
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📌 NEXT STEPS:")
    print("1. Go to the output folder:")
    print(f"   📁 {os.path.abspath(output_dir)}")
    print("\n2. For distribution, copy these files together:")
    print("   • LibraryManager.exe")
    print("   • library_data.json (if exists)")
    print("   • README.txt")
    print("   • run.bat")
    print("\n3. To run the application:")
    print("   • Double-click LibraryManager.exe")
    print("   • Or run run.bat")
    
    print("\n🔧 TROUBLESHOOTING TIPS:")
    print("• If app doesn't start, install VC++ Redistributable:")
    print("  https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print("• Run as Administrator if you have permission issues")
    print("• Check Windows Event Viewer for detailed errors")
    
    print("\n📊 APPLICATION INFO:")
    exe_path = os.path.join(output_dir, 'LibraryManager.exe')
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"• Executable size: {size_mb:.2f} MB")
        print(f"• Build date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n✅ Ready for distribution!")

def main():
    """Main function"""
    print("=" * 60)
    print("📚 LIBRARY MANAGER - EXECUTABLE BUILDER")
    print("=" * 60)
    
    # Clean up Qt packages
    cleanup_qt_packages()
    
    # Build options
    print("\n🔧 BUILD OPTIONS:")
    print("1. Standard build (Recommended)")
    print("2. Optimized build (Smaller size)")
    print("3. Debug build (With console)")
    
    choice = input("\nSelect option (1-3, default=1): ").strip() or "1"
    
    # Note: Build parameters are fixed in this version
    # You could modify params based on choice if needed
    
    # Build the executable
    success, output_dir = build_library_app()
    
    if success and output_dir:
        show_post_build_instructions(output_dir)
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED!")
        print("=" * 60)
        print("\nPossible solutions:")
        print("1. Run as Administrator")
        print("2. Check if antivirus is blocking PyInstaller")
        print("3. Clean Python cache: pyinstaller --clean")
        print("4. Try in a virtual environment")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)