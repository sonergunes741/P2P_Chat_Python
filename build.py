import subprocess
import sys
import os


def check_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_executable():
    print("Building P2P Chat executable...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=P2P_Chat",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--add-data=src;src",
        "--clean",
        "gui_main.py"
    ]
    
    subprocess.check_call(cmd)
    print("\n✅ Build complete! Executable is in dist/P2P_Chat.exe")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if not check_pyinstaller():
        install_pyinstaller()
    
    build_executable()
    
    print("\n📦 To create an installer, use Inno Setup with the provided .iss file")


if __name__ == "__main__":
    main()
