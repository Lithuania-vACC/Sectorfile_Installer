@echo off
setlocal enabledelayedexpansion

REM Sectorfile Installer Auto-Updater Script
REM This script replaces the old application files with the new version

REM Arguments:
REM %1 = Path to new version files (extracted main.dist folder)
REM %2 = Path to current installation directory
REM %3 = Path to main executable to restart

set NEW_VERSION_PATH=%~1
set INSTALL_PATH=%~2
set EXE_PATH=%~3

echo Sectorfile Installer - Auto Updater
echo ====================================
echo.
echo Waiting for application to close...

REM Wait for main process to fully exit (5 second delay)
timeout /t 5 /nobreak >nul

echo Removing old files...

REM Delete old files (except updater.bat itself)
for /d %%d in ("%INSTALL_PATH%\*") do (
    if /i not "%%~nxd"=="updater.bat" (
        rmdir /s /q "%%d" 2>nul
    )
)

for %%f in ("%INSTALL_PATH%\*") do (
    if /i not "%%~nxf"=="updater.bat" (
        del /f /q "%%f" 2>nul
    )
)

echo Installing update...

REM Copy new files to installation directory
xcopy /e /i /h /y "%NEW_VERSION_PATH%\*" "%INSTALL_PATH%\" >nul

REM Clean up temp directory
echo Cleaning up temporary files...
rmdir /s /q "%TEMP%\sectorfile_installer_update" 2>nul

echo Update complete!
echo Starting updated application...

REM Launch new version
start "" "%EXE_PATH%"

REM Self-delete this updater script
(goto) 2>nul & del "%~f0"
