# Cite-Agent BULLETPROOF Installer v1.5.6
# Works on ANY Windows machine - even without Python
# Right-click → Run with PowerShell (or use one-liner)
# One-liner: iwr -useb https://raw.githubusercontent.com/Spectating101/cite-agent/main/Install-CiteAgent-BULLETPROOF.ps1 | iex

#Requires -Version 5.1

param(
    [switch]$Silent,
    [switch]$NoShortcuts,
    [switch]$Force
)

# ============================================================================
# Configuration
# ============================================================================
$ErrorActionPreference = "Stop"
$CITE_AGENT_VERSION = "1.5.6"
$MIN_PYTHON_VERSION = [version]"3.10.0"
$MAX_PYTHON_VERSION = [version]"3.13.99"
$PYTHON_DOWNLOAD_VERSION = "3.11.9"
$PYTHON_DOWNLOAD_URL = "https://www.python.org/ftp/python/$PYTHON_DOWNLOAD_VERSION/python-$PYTHON_DOWNLOAD_VERSION-embed-amd64.zip"
$GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
$INSTALL_ROOT = "$env:LOCALAPPDATA\Cite-Agent"
$VENV_PATH = "$INSTALL_ROOT\venv"
$PYTHON_EMBEDDED_PATH = "$INSTALL_ROOT\python"
$TEMP_LOG = "$env:TEMP\cite-agent-install-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$LOG_FILE = $TEMP_LOG  # Will be moved to final location after cleanup
$MAX_RETRIES = 3
$RETRY_DELAY = 2

# ============================================================================
# Logging Functions
# ============================================================================
function Initialize-Log {
    $logDir = Split-Path $LOG_FILE -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    "=== Cite-Agent BULLETPROOF Installation v$CITE_AGENT_VERSION ===" | Out-File $LOG_FILE -Encoding UTF8
    "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $LOG_FILE -Append -Encoding UTF8
    "Platform: $([Environment]::OSVersion.VersionString)" | Out-File $LOG_FILE -Append -Encoding UTF8
    "PowerShell: $($PSVersionTable.PSVersion)" | Out-File $LOG_FILE -Append -Encoding UTF8
    "User: $env:USERNAME" | Out-File $LOG_FILE -Append -Encoding UTF8
    "" | Out-File $LOG_FILE -Append -Encoding UTF8
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

    # Ensure log directory exists before writing
    $logDir = Split-Path $LOG_FILE -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force -ErrorAction SilentlyContinue | Out-Null
    }

    "$timestamp | $Level | $Message" | Out-File $LOG_FILE -Append -Encoding UTF8 -ErrorAction SilentlyContinue

    switch ($Level) {
        "INFO"    { Write-Host "[*] $Message" -ForegroundColor Cyan }
        "SUCCESS" { Write-Host "[✓] $Message" -ForegroundColor Green }
        "WARNING" { Write-Host "[!] $Message" -ForegroundColor Yellow }
        "ERROR"   { Write-Host "[✗] $Message" -ForegroundColor Red }
        "PROGRESS" { Write-Host "    $Message" -ForegroundColor Gray }
    }
}

function Move-LogToFinalLocation {
    # Move temp log to final install directory
    $finalLogDir = "$INSTALL_ROOT\logs"
    $finalLogFile = "$finalLogDir\install-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

    if (-not (Test-Path $finalLogDir)) {
        New-Item -ItemType Directory -Path $finalLogDir -Force | Out-Null
    }

    if (Test-Path $LOG_FILE) {
        Copy-Item $LOG_FILE -Destination $finalLogFile -Force -ErrorAction SilentlyContinue
        $script:LOG_FILE = $finalLogFile
        Write-Log "Log moved to final location: $finalLogFile" -Level "SUCCESS"
    }
}

# ============================================================================
# UI Functions
# ============================================================================
function Show-Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                        ║" -ForegroundColor Cyan
    Write-Host "║   CITE-AGENT BULLETPROOF INSTALLER v$CITE_AGENT_VERSION            ║" -ForegroundColor Cyan
    Write-Host "║   AI Research Assistant for Windows                    ║" -ForegroundColor Cyan
    Write-Host "║   Works on ANY machine - even without Python!          ║" -ForegroundColor Cyan
    Write-Host "║                                                        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Progress {
    param(
        [string]$Activity,
        [int]$PercentComplete,
        [string]$Status
    )
    Write-Progress -Activity $Activity -Status $Status -PercentComplete $PercentComplete
}

# ============================================================================
# Network Retry Logic
# ============================================================================
function Invoke-WithRetry {
    param(
        [scriptblock]$ScriptBlock,
        [string]$Description,
        [int]$MaxRetries = $MAX_RETRIES,
        [int]$RetryDelay = $RETRY_DELAY
    )

    $attempt = 1
    $success = $false

    while (-not $success -and $attempt -le $MaxRetries) {
        try {
            Write-Log "$Description (Attempt $attempt/$MaxRetries)" -Level "INFO"
            & $ScriptBlock
            $success = $true
            Write-Log "$Description succeeded" -Level "SUCCESS"
        } catch {
            if ($attempt -eq $MaxRetries) {
                Write-Log "$Description failed after $MaxRetries attempts: $_" -Level "ERROR"
                throw
            } else {
                $waitTime = $RetryDelay * [Math]::Pow(2, $attempt - 1)
                Write-Log "$Description failed (attempt $attempt), retrying in $waitTime seconds..." -Level "WARNING"
                Start-Sleep -Seconds $waitTime
                $attempt++
            }
        }
    }
}

# ============================================================================
# PHASE 1: UNINSTALL OLD INSTALLATIONS
# ============================================================================
function Remove-OldInstallation {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  PHASE 1: Cleaning Up Old Installations" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""

    Write-Log "Checking for old cite-agent installations..." -Level "INFO"

    # 1. Remove from pip (global)
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            Write-Log "Removing global cite-agent package..." -Level "INFO"
            & python -m pip uninstall -y cite-agent 2>&1 | Out-File $LOG_FILE -Append -Encoding UTF8
            Write-Log "Global package removed" -Level "SUCCESS"
        }
    } catch {
        Write-Log "No global package found (this is fine)" -Level "INFO"
    }

    # 2. Remove pipx installation
    try {
        $pipxCmd = Get-Command pipx -ErrorAction SilentlyContinue
        if ($pipxCmd) {
            Write-Log "Removing pipx cite-agent installation..." -Level "INFO"
            & pipx uninstall cite-agent 2>&1 | Out-File $LOG_FILE -Append -Encoding UTF8
            Write-Log "Pipx installation removed" -Level "SUCCESS"
        }
    } catch {
        Write-Log "No pipx installation found (this is fine)" -Level "INFO"
    }

    # 3. Remove desktop shortcut
    Write-Log "Removing old shortcuts..." -Level "INFO"
    $desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Cite-Agent.lnk"
    if (Test-Path $desktopShortcut) {
        Remove-Item $desktopShortcut -Force -ErrorAction SilentlyContinue
        Write-Log "Desktop shortcut removed" -Level "SUCCESS"
    }

    # 4. Remove Start Menu folder
    $startMenuFolder = Join-Path ([Environment]::GetFolderPath("Programs")) "Cite-Agent"
    if (Test-Path $startMenuFolder) {
        Remove-Item $startMenuFolder -Recurse -Force -ErrorAction SilentlyContinue
        Write-Log "Start Menu folder removed" -Level "SUCCESS"
    }

    # 5. Remove old installation directory (but keep logs)
    if (Test-Path $INSTALL_ROOT) {
        Write-Log "Backing up logs before cleanup..." -Level "INFO"
        $logBackup = "$env:TEMP\cite-agent-logs-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        if (Test-Path "$INSTALL_ROOT\logs") {
            Copy-Item "$INSTALL_ROOT\logs" -Destination $logBackup -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log "Logs backed up to: $logBackup" -Level "SUCCESS"
        }

        Write-Log "Removing old installation directory..." -Level "INFO"
        Remove-Item $INSTALL_ROOT -Recurse -Force -ErrorAction SilentlyContinue
        Write-Log "Old installation removed" -Level "SUCCESS"

        # Restore log backup
        if (Test-Path $logBackup) {
            New-Item -ItemType Directory -Path "$INSTALL_ROOT\logs" -Force | Out-Null
            Copy-Item "$logBackup\*" -Destination "$INSTALL_ROOT\logs\" -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # 6. Clean PATH
    Write-Log "Cleaning PATH environment variable..." -Level "INFO"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $pathsToRemove = @(
        "$env:LOCALAPPDATA\Cite-Agent\venv\Scripts",
        "$env:LOCALAPPDATA\Cite-Agent\python\Scripts",
        "$env:LOCALAPPDATA\Cite-Agent",
        "$HOME\.local\bin"
    )

    $newPath = $currentPath
    $pathCleaned = $false
    foreach ($pathToRemove in $pathsToRemove) {
        if ($newPath -like "*$pathToRemove*") {
            $escapedPath = [regex]::Escape($pathToRemove)
            $newPath = $newPath -replace ";$escapedPath", ''
            $newPath = $newPath -replace "$escapedPath;", ''
            $newPath = $newPath -replace "$escapedPath", ''
            $pathCleaned = $true
        }
    }

    if ($pathCleaned) {
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Log "PATH cleaned successfully" -Level "SUCCESS"
    } else {
        Write-Log "PATH already clean" -Level "INFO"
    }

    # 7. Clean up stale py launcher registry entries
    Write-Log "Cleaning py launcher registry for stale Python installations..." -Level "INFO"
    try {
        # Remove any py launcher entries pointing to our deleted installation
        $pyLauncherPaths = @(
            "HKCU:\Software\Python\PythonCore",
            "HKLM:\Software\Python\PythonCore"
        )

        foreach ($regPath in $pyLauncherPaths) {
            if (Test-Path $regPath) {
                Get-ChildItem $regPath -ErrorAction SilentlyContinue | ForEach-Object {
                    $installPath = (Get-ItemProperty "$($_.PSPath)\InstallPath" -ErrorAction SilentlyContinue).'(default)'
                    if ($installPath -and $installPath -like "*Cite-Agent*" -and -not (Test-Path $installPath)) {
                        Write-Log "Removing stale registry entry: $($_.PSChildName)" -Level "PROGRESS"
                        Remove-Item $_.PSPath -Recurse -Force -ErrorAction SilentlyContinue
                    }
                }
            }
        }
    } catch {
        Write-Log "Registry cleanup skipped (non-critical)" -Level "PROGRESS"
    }

    Write-Log "Cleanup complete - ready for fresh installation" -Level "SUCCESS"
    Start-Sleep -Seconds 1
}

# ============================================================================
# PHASE 2: PYTHON DETECTION AND INSTALLATION
# ============================================================================
function Find-PythonExecutable {
    Write-Log "Searching for compatible Python installation..." -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 15 -Status "Detecting Python..."

    # Strategy 1: Check py launcher (Windows Python Launcher)
    $pythonCandidates = @()

    try {
        Write-Log "Checking py launcher..." -Level "PROGRESS"
        $pyVersions = py -0 2>&1 | Select-String -Pattern '-(\d+\.\d+)-' | ForEach-Object {
            if ($_.Matches.Groups.Count -gt 1) {
                $version = $_.Matches.Groups[1].Value
                $fullPath = (py "-$version" -c "import sys; print(sys.executable)" 2>$null)
                if ($fullPath -and (Test-Path $fullPath)) {
                    [PSCustomObject]@{
                        Path = $fullPath
                        Version = [version]$version
                    }
                }
            }
        }
        $pythonCandidates += $pyVersions
        Write-Log "Found $($pyVersions.Count) Python version(s) via py launcher" -Level "PROGRESS"
    } catch {
        Write-Log "py launcher not available" -Level "PROGRESS"
    }

    # Strategy 2: Check common installation paths
    Write-Log "Checking common Python installation paths..." -Level "PROGRESS"
    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:ProgramFiles\Python3*\python.exe",
        "$env:ProgramFiles(x86)\Python3*\python.exe",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python3*\python.exe",
        "C:\Python3*\python.exe"
    )

    foreach ($pathPattern in $commonPaths) {
        Get-Item $pathPattern -ErrorAction SilentlyContinue | ForEach-Object {
            $versionOutput = & $_.FullName --version 2>&1 | Select-String -Pattern '(\d+\.\d+\.\d+)'
            if ($versionOutput -and $versionOutput.Matches.Groups.Count -gt 1) {
                $version = [version]$versionOutput.Matches.Groups[1].Value
                $pythonCandidates += [PSCustomObject]@{
                    Path = $_.FullName
                    Version = $version
                }
            }
        }
    }

    # Strategy 3: Check PATH
    Write-Log "Checking system PATH..." -Level "PROGRESS"
    $pathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($pathPython) {
        try {
            $versionOutput = & $pathPython.Path --version 2>&1
            # Check if it's the Windows Store stub (error message contains "Microsoft Store")
            if ($versionOutput -like "*Microsoft Store*") {
                Write-Log "Found Windows Store Python stub (not actual Python)" -Level "PROGRESS"
            } elseif ($versionOutput -match '(\d+\.\d+\.\d+)') {
                $version = [version]$Matches[1]
                $pythonCandidates += [PSCustomObject]@{
                    Path = $pathPython.Path
                    Version = $version
                }
            }
        } catch {
            Write-Log "Python command failed (likely Windows Store stub)" -Level "PROGRESS"
        }
    }

    # Filter for compatible versions and remove duplicates
    $compatiblePython = $pythonCandidates |
        Where-Object { $_.Version -ge $MIN_PYTHON_VERSION -and $_.Version -le $MAX_PYTHON_VERSION } |
        Sort-Object -Property @{Expression = {$_.Version}; Descending = $true} |
        Select-Object -First 1 -Unique

    if ($compatiblePython) {
        Write-Log "Selected Python: $($compatiblePython.Path) (v$($compatiblePython.Version))" -Level "SUCCESS"

        # Verify pip and venv are available
        $pipCheck = & $compatiblePython.Path -m pip --version 2>&1
        $venvCheck = & $compatiblePython.Path -m venv --help 2>&1

        if ($LASTEXITCODE -ne 0) {
            Write-Log "Python found but pip/venv missing - will install Python" -Level "WARNING"
            return $null
        }

        return $compatiblePython.Path
    }

    Write-Log "No compatible Python found - will install Python $PYTHON_DOWNLOAD_VERSION" -Level "WARNING"
    return $null
}

function Install-Python {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Installing Python $PYTHON_DOWNLOAD_VERSION (Embeddable)" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""

    Write-Log "Installing Python embeddable package..." -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 20 -Status "Downloading Python..."

    $tempZip = Join-Path ([System.IO.Path]::GetTempPath()) "python-$PYTHON_DOWNLOAD_VERSION-embed.zip"

    # Download Python embeddable package
    Invoke-WithRetry -Description "Python download" -ScriptBlock {
        Write-Log "Downloading Python from: $PYTHON_DOWNLOAD_URL" -Level "PROGRESS"
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($PYTHON_DOWNLOAD_URL, $tempZip)

        if (-not (Test-Path $tempZip)) {
            throw "Python download failed"
        }

        $fileSize = (Get-Item $tempZip).Length / 1MB
        $fileSizeMB = [math]::Round($fileSize, 2)
        Write-Log "Downloaded Python package ($fileSizeMB MB)" -Level 'PROGRESS'
    }

    Write-Log "Extracting Python to: $PYTHON_EMBEDDED_PATH" -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 30 -Status "Extracting Python..."

    # Extract Python
    if (Test-Path $PYTHON_EMBEDDED_PATH) {
        Remove-Item $PYTHON_EMBEDDED_PATH -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $PYTHON_EMBEDDED_PATH -Force | Out-Null

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($tempZip, $PYTHON_EMBEDDED_PATH)

    Remove-Item $tempZip -Force -ErrorAction SilentlyContinue

    # Enable pip by uncommenting import site in python311._pth
    $pthFile = Get-ChildItem $PYTHON_EMBEDDED_PATH -Filter "python*._pth" | Select-Object -First 1
    if ($pthFile) {
        Write-Log "Enabling pip support..." -Level "PROGRESS"
        $content = Get-Content $pthFile.FullName
        $content = $content -replace "#import site", "import site"
        $content | Set-Content $pthFile.FullName -Force
    }

    # Download and install pip
    Write-Log "Installing pip..." -Level "INFO"
    $getPipPath = Join-Path $PYTHON_EMBEDDED_PATH "get-pip.py"

    Invoke-WithRetry -Description "Pip download" -ScriptBlock {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($GET_PIP_URL, $getPipPath)
    }

    $pythonExe = Join-Path $PYTHON_EMBEDDED_PATH "python.exe"
    $oldErrorActionPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"  # Allow warnings to pass through
    $pipInstall = & $pythonExe $getPipPath 2>&1 | Out-String
    $ErrorActionPreference = $oldErrorActionPref

    # Check if pip actually installed (Scripts\pip.exe should exist)
    if (Test-Path (Join-Path $PYTHON_EMBEDDED_PATH "Scripts\pip.exe")) {
        Write-Log "Pip installed successfully" -Level "SUCCESS"
    } else {
        Write-Log "Pip installation output: $pipInstall" -Level "WARNING"
        throw "Pip installation failed"
    }

    Remove-Item $getPipPath -Force -ErrorAction SilentlyContinue

    Write-Log "Python installed successfully: $pythonExe" -Level "SUCCESS"
    return $pythonExe
}

# ============================================================================
# PHASE 3: VIRTUAL ENVIRONMENT
# ============================================================================
function New-VirtualEnvironment {
    param([string]$PythonPath)

    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Creating Virtual Environment" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""

    Write-Log "Creating virtual environment at: $VENV_PATH" -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 40 -Status "Creating virtual environment..."

    # Remove old venv if exists
    if (Test-Path $VENV_PATH) {
        Write-Log "Removing existing virtual environment..." -Level "WARNING"

        # Kill any Python processes using the venv
        try {
            Get-Process python -ErrorAction SilentlyContinue | Where-Object {
                $_.Path -like "$VENV_PATH*"
            } | Stop-Process -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
        } catch {
            # Ignore errors killing processes
        }

        # Aggressive removal with retries
        $retries = 0
        while ((Test-Path $VENV_PATH) -and $retries -lt 5) {
            try {
                Remove-Item $VENV_PATH -Recurse -Force -ErrorAction Stop
            } catch {
                Start-Sleep -Milliseconds 500
                $retries++
            }
        }

        if (Test-Path $VENV_PATH) {
            Write-Log "Warning: Could not fully remove old venv, will overwrite" -Level "WARNING"
        }
    }

    # For embeddable Python, we need to use virtualenv instead of venv
    # First check if this is embeddable Python (no venv module)
    $oldErrorActionPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $hasVenv = & $PythonPath -m venv --help 2>&1 | Out-String
    $venvExitCode = $LASTEXITCODE
    $ErrorActionPreference = $oldErrorActionPref

    $useVirtualenv = $venvExitCode -ne 0

    if ($useVirtualenv) {
        Write-Log "Using virtualenv (embeddable Python detected)" -Level "INFO"
        # Install virtualenv
        $pipExe = Join-Path (Split-Path $PythonPath -Parent) "Scripts\pip.exe"

        $oldErrPref = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $pipExe install virtualenv 2>&1 | Out-File $LOG_FILE -Append -Encoding UTF8
        $pipResult = $LASTEXITCODE
        $ErrorActionPreference = $oldErrPref

        if ($pipResult -ne 0) {
            throw "virtualenv installation failed"
        }

        # Create venv using virtualenv
        Invoke-WithRetry -Description "Virtual environment creation" -ScriptBlock {
            $oldErrPref2 = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            & $PythonPath -m virtualenv "$VENV_PATH" 2>&1 | Out-File $LOG_FILE -Append -Encoding UTF8
            $venvResult = $LASTEXITCODE
            $ErrorActionPreference = $oldErrPref2

            if ($venvResult -ne 0) {
                throw "virtualenv creation failed with exit code: $venvResult"
            }
        }
    } else {
        Write-Log "Using built-in venv module" -Level "INFO"
        # Create fresh venv with retry
        Invoke-WithRetry -Description "Virtual environment creation" -ScriptBlock {
            & $PythonPath -m venv "$VENV_PATH" 2>&1 | Out-File $LOG_FILE -Append -Encoding UTF8

            if ($LASTEXITCODE -ne 0) {
                throw "venv creation failed with exit code: $LASTEXITCODE"
            }
        }
    }

    $venvPython = "$VENV_PATH\Scripts\python.exe"
    $venvPip = "$VENV_PATH\Scripts\pip.exe"

    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment Python not found at: $venvPython"
    }

    if (-not (Test-Path $venvPip)) {
        throw "Virtual environment pip not found at: $venvPip"
    }

    Write-Log "Virtual environment created successfully" -Level "SUCCESS"
    Write-Log "venv Python: $venvPython" -Level "PROGRESS"
    Write-Log "venv pip: $venvPip" -Level "PROGRESS"

    return $venvPython
}

# ============================================================================
# PHASE 4: PACKAGE INSTALLATION
# ============================================================================
function Install-CiteAgent {
    param([string]$VenvPython)

    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Installing Cite-Agent v$CITE_AGENT_VERSION" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""

    Write-Log "Upgrading pip, setuptools, wheel..." -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 50 -Status "Upgrading pip..."

    # Upgrade pip with retry
    Invoke-WithRetry -Description "pip upgrade" -ScriptBlock {
        $upgradeOutput = & $VenvPython -m pip install --upgrade pip setuptools wheel 2>&1
        $upgradeOutput | Out-File $LOG_FILE -Append -Encoding UTF8

        if ($LASTEXITCODE -ne 0) {
            throw "pip upgrade failed: $upgradeOutput"
        }

        # Verify pip version
        $pipVersion = & $VenvPython -m pip --version 2>&1
        Write-Log "pip upgraded: $pipVersion" -Level "PROGRESS"
    }

    Write-Log "Installing cite-agent==$CITE_AGENT_VERSION from PyPI..." -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 60 -Status "Downloading and installing cite-agent..."

    # Install cite-agent with retry
    Invoke-WithRetry -Description "cite-agent installation" -ScriptBlock {
        $installOutput = & $VenvPython -m pip install --no-cache-dir "cite-agent==$CITE_AGENT_VERSION" 2>&1
        $installOutput | Out-File $LOG_FILE -Append -Encoding UTF8

        if ($LASTEXITCODE -ne 0) {
            # Try without version pin as fallback
            Write-Log "Version-pinned install failed, trying latest version..." -Level "WARNING"
            $installOutput = & $VenvPython -m pip install --no-cache-dir cite-agent 2>&1
            $installOutput | Out-File $LOG_FILE -Append -Encoding UTF8

            if ($LASTEXITCODE -ne 0) {
                throw "cite-agent installation failed: $installOutput"
            }
        }
    }

    # Verify installation
    Write-Log "Verifying cite-agent installation..." -Level "INFO"
    $verifyOutput = & $VenvPython -c "import cite_agent; print(cite_agent.__version__)" 2>&1

    if ($LASTEXITCODE -eq 0) {
        $installedVersion = $verifyOutput.Trim()
        Write-Log "cite-agent v$installedVersion installed successfully!" -Level "SUCCESS"
    } else {
        throw "Installation verification failed: $verifyOutput"
    }
}

# ============================================================================
# PHASE 5: SHORTCUTS AND PATH
# ============================================================================
function Install-DesktopShortcutBAT {
    # Create a simple BAT file on desktop that launches cite-agent
    # This avoids COM object issues entirely
    
    try {
        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $batPath = Join-Path $desktopPath "Cite-Agent.bat"
        $citeAgentExe = Join-Path $VENV_PATH "Scripts\cite-agent.exe"
        
        Write-Host "  [→] Creating desktop shortcut..." -ForegroundColor Gray
        
        # Create BAT file content
        $batContent = @"
@echo off
title Cite-Agent
cd /d "%USERPROFILE%"
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
"$citeAgentExe"
pause
"@
        
        # Write BAT file (simple file write - no COM needed!)
        $batContent | Out-File -FilePath $batPath -Encoding ASCII -Force
        
        Write-Host "  [✓] Desktop shortcut created!" -ForegroundColor Green
        Write-Log "Created desktop shortcut: $batPath" -Level "SUCCESS"
        return $true
        
    } catch {
        Write-Host "  [✗] Failed to create shortcut: $($_.Exception.Message)" -ForegroundColor Red
        Write-Log "Failed to create desktop shortcut: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Install-PathOnly {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Adding cite-agent to PATH" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""

    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 70 -Status "Adding to PATH..."
    
    # Add to PATH first (critical for command-line access)
    Write-Host "  [->] Adding cite-agent to PATH..." -ForegroundColor Gray
    Write-Log "Adding cite-agent to PATH..." -Level "INFO"
    $scriptsPath = "$VENV_PATH\Scripts"
    Write-Host "  [->] Reading current PATH environment variable..." -ForegroundColor Gray
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($currentPath -notlike "*$scriptsPath*") {
        Write-Host "  [->] Updating PATH with: $scriptsPath" -ForegroundColor Gray
        $newPath = "$currentPath;$scriptsPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$env:Path;$scriptsPath"
        Write-Host "  [OK] cite-agent added to PATH successfully!" -ForegroundColor Green
        Write-Log "cite-agent added to PATH: $scriptsPath" -Level "SUCCESS"
    } else {
        Write-Host "  [OK] cite-agent already in PATH" -ForegroundColor Cyan
        Write-Log "cite-agent already in PATH" -Level "INFO"
    }
}

# ============================================================================
# PHASE 6: VERIFICATION
# ============================================================================
function Test-Installation {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Verifying Installation" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""

    Write-Log "Running installation verification..." -Level "INFO"
    Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 90 -Status "Verifying installation..."

    $venvPython = "$VENV_PATH\Scripts\python.exe"

    # Test 1: Python executable exists
    if (-not (Test-Path $venvPython)) {
        Write-Log "FAIL: Python executable not found" -Level "ERROR"
        return $false
    }
    Write-Log "✓ Python executable found" -Level "SUCCESS"

    # Test 2: cite_agent module can be imported
    $importTest = & $venvPython -c "import cite_agent; print('OK')" 2>&1
    if ($importTest -ne "OK") {
        Write-Log "FAIL: cite_agent module cannot be imported: $importTest" -Level "ERROR"
        return $false
    }
    Write-Log "✓ cite_agent module importable" -Level "SUCCESS"

    # Test 3: Version check
    $versionTest = & $venvPython -c "import cite_agent; print(cite_agent.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✓ cite-agent version: $versionTest" -Level "SUCCESS"
    } else {
        Write-Log "FAIL: Version check failed: $versionTest" -Level "ERROR"
        return $false
    }

    # Test 4: CLI entry point exists
    $cliExe = "$VENV_PATH\Scripts\cite-agent.exe"
    if (Test-Path $cliExe) {
        Write-Log "✓ CLI executable found: $cliExe" -Level "SUCCESS"
    } else {
        Write-Log "WARNING: CLI executable not found (will use python -m cite_agent.cli)" -Level "WARNING"
    }

    # Test 5: Desktop shortcut exists (BAT file)
    $desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Cite-Agent.bat"
    if (Test-Path $desktopShortcut) {
        Write-Log "✓ Desktop shortcut created" -Level "SUCCESS"
    } else {
        Write-Log "WARNING: Desktop shortcut not found" -Level "WARNING"
    }

    # Test 6: PATH check
    $scriptsPath = "$VENV_PATH\Scripts"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -like "*$scriptsPath*") {
        Write-Log "✓ cite-agent in PATH" -Level "SUCCESS"
    } else {
        Write-Log "WARNING: cite-agent not in PATH" -Level "WARNING"
    }

    Write-Log "All critical checks passed!" -Level "SUCCESS"
    return $true
}

# ============================================================================
# Main Installation Flow
# ============================================================================
function Start-Installation {
    try {
        Show-Banner
        Initialize-Log

        Write-Log "=== Starting Cite-Agent BULLETPROOF Installation ===" -Level "INFO"
        Write-Log "Version: $CITE_AGENT_VERSION" -Level "INFO"
        Write-Log "Install location: $INSTALL_ROOT" -Level "INFO"
        Write-Host ""

        # PHASE 1: Uninstall old installations
        Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 5 -Status "Cleaning up old installations..."
        Remove-OldInstallation

        # Move log to final location now that install directory is ready
        Move-LogToFinalLocation

        # PHASE 2: Find or install Python
        Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 10 -Status "Detecting Python..."
        $pythonPath = Find-PythonExecutable

        if (-not $pythonPath) {
            $pythonPath = Install-Python
        }

        # PHASE 3: Create virtual environment
        $venvPython = New-VirtualEnvironment -PythonPath $pythonPath

        # PHASE 4: Install cite-agent
        Install-CiteAgent -VenvPython $venvPython

        # PHASE 5: Add to PATH (critical for command-line access)
        Install-PathOnly

        # PHASE 6: Create desktop shortcut (BAT file approach - no COM objects!)
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
        Write-Host "  Creating Desktop Shortcut" -ForegroundColor Yellow
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
        Write-Host ""
        Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 85 -Status "Creating desktop shortcut..."
        Install-DesktopShortcutBAT

        # PHASE 7: Verify installation
        $verified = Test-Installation

        if (-not $verified) {
            throw "Installation verification failed - see log for details"
        }

        # Complete
        Show-Progress -Activity "Installing Cite-Agent" -PercentComplete 100 -Status "Installation complete!"
        Write-Progress -Activity "Installing Cite-Agent" -Completed

        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║                                                        ║" -ForegroundColor Green
        Write-Host "║   ✓ INSTALLATION SUCCESSFUL!                           ║" -ForegroundColor Green
        Write-Host "║                                                        ║" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        Write-Host "Cite-Agent v$CITE_AGENT_VERSION is now installed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "To start cite-agent:" -ForegroundColor Cyan
        Write-Host "  • Double-click the 'Cite-Agent' shortcut on your desktop" -ForegroundColor White
        Write-Host "  • OR type 'cite-agent' in any terminal" -ForegroundColor White
        Write-Host ""
        Write-Host "Installation log: $LOG_FILE" -ForegroundColor Gray
        Write-Host ""

        if (-not $Silent) {
            $launch = Read-Host "Launch Cite-Agent now? (Y/n)"
            if ($launch -eq "" -or $launch -eq "Y" -or $launch -eq "y") {
                Write-Host ""
                Write-Host "Launching Cite-Agent..." -ForegroundColor Cyan
                Write-Host ""
                $launcherScript = "$INSTALL_ROOT\launch-cite-agent.bat"
                Start-Process -FilePath $launcherScript -NoNewWindow
            }
        }

    } catch {
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║                                                        ║" -ForegroundColor Red
        Write-Host "║   ✗ INSTALLATION FAILED                                ║" -ForegroundColor Red
        Write-Host "║                                                        ║" -ForegroundColor Red
        Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Red
        Write-Host ""
        Write-Log "Installation failed: $($_.Exception.Message)" -Level "ERROR"
        Write-Log "Stack trace: $($_.ScriptStackTrace)" -Level "ERROR"
        Write-Host ""
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "  1. Check your internet connection" -ForegroundColor White
        Write-Host "  2. Try running as administrator (right-click → Run as administrator)" -ForegroundColor White
        Write-Host "  3. Check the log file for details: $LOG_FILE" -ForegroundColor White
        Write-Host "  4. Report issues: https://github.com/Spectating101/cite-agent/issues" -ForegroundColor White
        Write-Host ""

        if (-not $Silent) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
}

# ============================================================================
# Entry Point
# ============================================================================
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Start-Installation

if (-not $Silent) {
    Read-Host "`nPress Enter to exit"
}
