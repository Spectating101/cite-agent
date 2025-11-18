@echo off
REM ============================================================================
REM Cite-Agent Windows Installer (Double-Click to Install)
REM This launcher runs the PowerShell installer with proper permissions
REM ============================================================================

title Cite-Agent Installer
color 0B

echo.
echo ========================================================================
echo    CITE-AGENT INSTALLER v1.4.8
echo    AI Research Assistant for Windows
echo ========================================================================
echo.
echo This will install Cite-Agent on your computer.
echo.
echo What will be installed:
echo   - Python 3.11.9 (if you don't have it)
echo   - Cite-Agent v1.4.8
echo   - Desktop shortcut
echo   - Start Menu entry
echo.
echo Installation location: %LOCALAPPDATA%\Cite-Agent
echo.
pause

echo.
echo Starting installation...
echo.

REM Run PowerShell installer (no admin needed - installs to user directory)
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0Install-CiteAgent-BULLETPROOF.ps1"

echo.
echo.
echo ========================================================================
echo Installation process completed.
echo.
echo If installation was successful, you can now:
echo   1. Double-click the "Cite-Agent" icon on your desktop
echo   2. Or search for "Cite-Agent" in the Start menu
echo   3. Or open PowerShell and type: cite-agent
echo ========================================================================
echo.
pause
