@echo off
REM Cite-Agent Easy Installer
REM Just double-click this file to install!

echo.
echo ========================================
echo   Cite-Agent Easy Installer
echo ========================================
echo.
echo Starting installation...
echo This will take 2-3 minutes.
echo.

REM Run the PowerShell installer
PowerShell.exe -ExecutionPolicy Bypass -File "%~dp0Backend-Installer.ps1"

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To use Cite-Agent:
echo 1. Open Command Prompt or PowerShell
echo 2. Type: cite-agent
echo 3. Start asking questions!
echo.
echo Press any key to exit...
pause >nul
