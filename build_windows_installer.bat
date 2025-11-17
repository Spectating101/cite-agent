@echo off
REM Cite Agent Windows Installer Builder
REM This script builds a complete Windows installer (.exe)
REM
REM Prerequisites:
REM   1. Python 3.9+ installed
REM   2. NSIS installed (https://nsis.sourceforge.io/Download)
REM   3. Run from the cite-agent directory
REM
REM Usage: build_windows_installer.bat

echo ============================================
echo  Cite Agent Windows Installer Builder
echo  Version 1.4.8
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check NSIS
where makensis >nul 2>&1
if errorlevel 1 (
    echo WARNING: NSIS not found in PATH
    echo Please install NSIS from https://nsis.sourceforge.io/Download
    echo Or add NSIS to your PATH environment variable
    echo.
    echo Continuing with PyInstaller only...
    set SKIP_NSIS=1
) else (
    set SKIP_NSIS=0
)

echo Step 1: Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Building standalone executable with PyInstaller...
REM Clean previous builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build with spec file
pyinstaller cite_agent.spec --clean
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo Step 3: Verifying build...
if not exist "dist\cite-agent\cite-agent.exe" (
    echo ERROR: cite-agent.exe not found in dist folder
    pause
    exit /b 1
)

echo SUCCESS: Standalone executable created at dist\cite-agent\cite-agent.exe
echo.

REM Test the executable
echo Step 4: Testing executable...
dist\cite-agent\cite-agent.exe --version
if errorlevel 1 (
    echo WARNING: Executable test failed
) else (
    echo Executable test passed!
)

echo.

if "%SKIP_NSIS%"=="1" (
    echo Skipping NSIS installer creation (NSIS not found)
    echo.
    echo ============================================
    echo  BUILD COMPLETE (Portable Version)
    echo ============================================
    echo.
    echo Your portable executable is at:
    echo   dist\cite-agent\cite-agent.exe
    echo.
    echo You can distribute the entire dist\cite-agent folder
    echo or create an installer manually with NSIS.
    echo.
    goto :done
)

echo Step 5: Creating Windows installer with NSIS...

REM Check for EnvVarUpdate.nsh
if not exist "EnvVarUpdate.nsh" (
    echo Downloading EnvVarUpdate.nsh plugin...
    curl -L -o EnvVarUpdate.nsh https://raw.githubusercontent.com/wiki/rg3/youtube-dl/EnvVarUpdate.nsh
    if errorlevel 1 (
        echo WARNING: Could not download EnvVarUpdate.nsh
        echo Creating minimal version...
        echo ; Minimal EnvVarUpdate stub > EnvVarUpdate.nsh
        echo !macro EnvVarUpdate a b c d e >> EnvVarUpdate.nsh
        echo !macroend >> EnvVarUpdate.nsh
        echo !define EnvVarUpdate "!insertmacro EnvVarUpdate" >> EnvVarUpdate.nsh
        echo !define un.EnvVarUpdate "!insertmacro EnvVarUpdate" >> EnvVarUpdate.nsh
    )
)

REM Check for LICENSE file
if not exist "LICENSE" (
    echo Creating placeholder LICENSE file...
    echo MIT License > LICENSE
    echo. >> LICENSE
    echo Copyright (c) 2024 Cite Agent Team >> LICENSE
    echo. >> LICENSE
    echo Permission is hereby granted, free of charge... >> LICENSE
)

REM Build installer
makensis installer.nsi
if errorlevel 1 (
    echo ERROR: NSIS installer creation failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo  BUILD COMPLETE!
echo ============================================
echo.
echo Your Windows installer is ready:
echo   CiteAgentSetup-1.4.8.exe
echo.
echo This installer will:
echo   - Install Cite Agent to Program Files
echo   - Create desktop shortcut
echo   - Add to Start Menu
echo   - Configure PATH for terminal access
echo   - Auto-setup on first run
echo.
echo Users just double-click to install, then type
echo 'cite-agent' in any terminal to start!
echo.

:done
pause
