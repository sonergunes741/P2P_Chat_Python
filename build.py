"""
Build Script for P2P Chat Application
======================================
Creates a standalone executable using PyInstaller.

Steps:
1. Install PyInstaller: pip install pyinstaller
2. Run this script: python build.py
3. Find the executable in dist/ folder
"""

import subprocess
import sys
import os


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building P2P Chat executable...")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=P2P_Chat",
        "--onefile",           # Single executable
        "--windowed",          # No console window (GUI app)
        "--icon=NONE",         # No icon (can add later)
        "--add-data=src;src",  # Include src folder
        "--clean",             # Clean cache
        "gui_main.py"
    ]
    
    subprocess.check_call(cmd)
    print("\n✅ Build complete! Executable is in dist/P2P_Chat.exe")


def main():
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check/install PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()
    
    # Build
    build_executable()
    
    print("\n📦 To create an installer, use Inno Setup with the provided .iss file")


if __name__ == "__main__":
    main()
