setlocal enabledelayedexpansion

REM Sectorfile Installer Auto-Updater Script
REM This script replaces the old application files with the new version
REM Reads configuration from updater_config.json

echo Sectorfile Installer - Auto Updater
echo ====================================
echo.

REM Read config from updater_config.json using PowerShell
echo Reading configuration file...

for /f "delims=" %%i in ('powershell -Command "& {(Get-Content -Raw -Path 'updater_config.json' | ConvertFrom-Json).new_version_path}"') do set NEW_VERSION_PATH=%%i
for /f "delims=" %%i in ('powershell -Command "& {(Get-Content -Raw -Path 'updater_config.json' | ConvertFrom-Json).install_path}"') do set INSTALL_PATH=%%i
for /f "delims=" %%i in ('powershell -Command "& {(Get-Content -Raw -Path 'updater_config.json' | ConvertFrom-Json).exe_path}"') do set EXE_PATH=%%i

echo Config loaded:
echo - New version: %NEW_VERSION_PATH%
echo - Install path: %INSTALL_PATH%
echo - Executable: %EXE_PATH%
echo.
echo Waiting for application to close...

REM Wait for main process to fully exit (5 second delay)
timeout /t 5 /nobreak >nul

echo Removing old files...

REM Delete old files (except updater.bat and updater_config.json)
for /d %%d in ("%INSTALL_PATH%\*") do (
    if /i not "%%~nxd"=="updater.bat" (
        rmdir /s /q "%%d" 2>nul
    )
)

for %%f in ("%INSTALL_PATH%\*") do (
    if /i not "%%~nxf"=="updater.bat" (
        if /i not "%%~nxf"=="updater_config.json" (
            del /f /q "%%f" 2>nul
        )
    )
)

echo Installing update...

REM Copy new files to installation directory
xcopy /e /i /h /y "%NEW_VERSION_PATH%\*" "%INSTALL_PATH%\"

REM Clean up temp directory
echo Cleaning up temporary files...
rmdir /s /q "%TEMP%\sectorfile_installer_update"

echo Update complete!
echo Starting updated application...

REM Launch new version
start "" "%EXE_PATH%"
timeout 2

exit
exit
exit
exit
