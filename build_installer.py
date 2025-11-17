#!/usr/bin/env python3
"""
Cite Agent Installer Builder

Cross-platform build script for creating Windows installers.
Can be run from any OS to prepare the build artifacts.

Usage:
    python build_installer.py           # Full build
    python build_installer.py --spec    # Generate spec only
    python build_installer.py --pyinst  # PyInstaller only (no NSIS)
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


VERSION = "1.4.8"
PRODUCT_NAME = "Cite Agent"


def print_banner():
    print("=" * 60)
    print(f"  {PRODUCT_NAME} Installer Builder v{VERSION}")
    print("=" * 60)
    print()


def check_prerequisites():
    """Check if required tools are installed"""
    print("Checking prerequisites...")

    # Check Python version
    if sys.version_info < (3, 9):
        print(f"ERROR: Python 3.9+ required (found {sys.version})")
        return False
    print(f"  ✓ Python {sys.version.split()[0]}")

    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print("  ✓ pip")
    except:
        print("  ✗ pip not found")
        return False

    # Check PyInstaller (will install if missing)
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  ⚠ PyInstaller not found (will install)")

    # Check NSIS (optional, Windows only)
    if sys.platform == "win32":
        nsis = shutil.which("makensis")
        if nsis:
            print(f"  ✓ NSIS ({nsis})")
        else:
            print("  ⚠ NSIS not found (optional, for installer creation)")

    return True


def install_dependencies():
    """Install build dependencies"""
    print("\nInstalling build dependencies...")

    # Upgrade pip
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                   check=True)

    # Install PyInstaller
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                   check=True)

    # Install package in development mode
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."],
                   check=True)

    print("  ✓ Dependencies installed")


def clean_build():
    """Clean previous build artifacts"""
    print("\nCleaning previous builds...")

    for folder in ["build", "dist", "__pycache__"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"  ✓ Removed {folder}/")

    # Clean .pyc files
    for pyc in Path(".").rglob("*.pyc"):
        pyc.unlink()

    print("  ✓ Build directory cleaned")


def build_with_pyinstaller():
    """Build executable with PyInstaller"""
    print("\nBuilding standalone executable...")

    # Check if spec file exists
    if not Path("cite_agent.spec").exists():
        print("  ERROR: cite_agent.spec not found")
        return False

    # Run PyInstaller
    result = subprocess.run(
        ["pyinstaller", "cite_agent.spec", "--clean"],
        capture_output=False
    )

    if result.returncode != 0:
        print("  ✗ PyInstaller build failed")
        return False

    # Verify output
    if sys.platform == "win32":
        exe_path = Path("dist/cite-agent/cite-agent.exe")
    else:
        exe_path = Path("dist/cite-agent/cite-agent")

    if not exe_path.exists():
        print(f"  ✗ Executable not found at {exe_path}")
        return False

    print(f"  ✓ Executable created: {exe_path}")

    # Test the executable
    print("\nTesting executable...")
    try:
        result = subprocess.run(
            [str(exe_path), "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"  ✓ Executable test passed")
            print(f"    {result.stdout.strip().split(chr(10))[0]}")
        else:
            print(f"  ⚠ Executable returned error code {result.returncode}")
    except Exception as e:
        print(f"  ⚠ Could not test executable: {e}")

    return True


def build_nsis_installer():
    """Build Windows installer with NSIS"""
    if sys.platform != "win32":
        print("\nSkipping NSIS installer (Windows only)")
        return True

    if not shutil.which("makensis"):
        print("\nSkipping NSIS installer (makensis not found)")
        print("  Install NSIS from https://nsis.sourceforge.io/Download")
        return True

    print("\nBuilding Windows installer with NSIS...")

    if not Path("installer.nsi").exists():
        print("  ✗ installer.nsi not found")
        return False

    result = subprocess.run(["makensis", "installer.nsi"])

    if result.returncode != 0:
        print("  ✗ NSIS build failed")
        return False

    installer_path = Path(f"CiteAgentSetup-{VERSION}.exe")
    if installer_path.exists():
        print(f"  ✓ Windows installer created: {installer_path}")
        print(f"    Size: {installer_path.stat().st_size / 1024 / 1024:.1f} MB")

    return True


def create_portable_zip():
    """Create a portable ZIP distribution"""
    print("\nCreating portable ZIP distribution...")

    dist_folder = Path("dist/cite-agent")
    if not dist_folder.exists():
        print("  ✗ dist/cite-agent not found")
        return False

    zip_name = f"CiteAgent-{VERSION}-portable"
    shutil.make_archive(zip_name, "zip", "dist", "cite-agent")

    zip_path = Path(f"{zip_name}.zip")
    if zip_path.exists():
        print(f"  ✓ Portable ZIP created: {zip_path}")
        print(f"    Size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

    return True


def print_summary():
    """Print build summary"""
    print("\n" + "=" * 60)
    print("  BUILD SUMMARY")
    print("=" * 60)

    # List created artifacts
    artifacts = []

    if Path("dist/cite-agent").exists():
        artifacts.append(("Standalone Executable", "dist/cite-agent/"))

    if Path(f"CiteAgentSetup-{VERSION}.exe").exists():
        artifacts.append(("Windows Installer", f"CiteAgentSetup-{VERSION}.exe"))

    if Path(f"CiteAgent-{VERSION}-portable.zip").exists():
        artifacts.append(("Portable ZIP", f"CiteAgent-{VERSION}-portable.zip"))

    if artifacts:
        print("\nCreated artifacts:")
        for name, path in artifacts:
            print(f"  • {name}: {path}")
    else:
        print("\nNo artifacts created")

    print("\n" + "=" * 60)
    print("  NEXT STEPS")
    print("=" * 60)

    if sys.platform == "win32":
        print("""
For Windows users:
  1. Distribute CiteAgentSetup-{VERSION}.exe
  2. Users double-click to install
  3. Type 'cite-agent' in any terminal
  4. First run will auto-setup account
""".format(VERSION=VERSION))
    else:
        print("""
For Windows distribution (from non-Windows):
  1. Copy these files to a Windows machine:
     - cite_agent.spec
     - installer.nsi
     - EnvVarUpdate.nsh
     - LICENSE
     - All source files
  2. Run: python build_installer.py
  3. Distribute the generated .exe installer
""")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Build Cite Agent installer")
    parser.add_argument("--spec", action="store_true", help="Generate spec file only")
    parser.add_argument("--pyinst", action="store_true", help="PyInstaller build only")
    parser.add_argument("--clean", action="store_true", help="Clean only")
    parser.add_argument("--no-zip", action="store_true", help="Skip ZIP creation")
    args = parser.parse_args()

    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    if args.clean:
        clean_build()
        sys.exit(0)

    if args.spec:
        print("Spec file already exists: cite_agent.spec")
        sys.exit(0)

    # Full build process
    install_dependencies()
    clean_build()

    if not build_with_pyinstaller():
        print("\nBuild failed!")
        sys.exit(1)

    if not args.no_zip:
        create_portable_zip()

    if not args.pyinst:
        build_nsis_installer()

    print_summary()
    print("\n✓ Build completed successfully!")


if __name__ == "__main__":
    main()
