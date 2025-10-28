@echo off
echo Building Sectorfile Installer with Nuitka...

REM Build with Nuitka
nuitka src/main.py --windows-console-mode=disable --msvc=latest --deployment --standalone --assume-yes-for-downloads --windows-icon-from-ico=src/assets/icon.ico

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b %ERRORLEVEL%
)

echo Build completed successfully!
echo Output is in main.dist folder