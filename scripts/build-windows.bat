@echo off
echo Building Sectorfile Installer with Nuitka...

REM Build with Nuitka
nuitka src/main.py --windows-console-mode=disable --msvc=latest --deployment --standalone --assume-yes-for-downloads --windows-icon-from-ico=src/assets/icon.ico --include-data-file=src/assets/icon.ico=assets/icon.ico --include-data-file=src/assets/updater.bat=updater.bat

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b %ERRORLEVEL%
)

echo Build completed successfully!
echo Output is in main.dist folder