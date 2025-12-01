📚 Library Manager - Book Management System
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
Build Date: 2025-12-01
