import subprocess
import time
import sys
import os

# Define users and ports
users = [
    ("CANER", 5000),
    ("MERT", 5001),
    ("SONER", 5002),
    ("BEYZA", 5003)
]

print("Launching 4 P2P Chat instances...")

python_exe = sys.executable
script_path = os.path.join(os.path.dirname(__file__), "gui_main.py")

for name, port in users:
    print(f"Starting {name} on port {port}...")
    
    cmd = [python_exe, script_path, "--auto", "--username", name, "--port", str(port)]
    
    # creationflags=subprocess.CREATE_NEW_CONSOLE ensures separate console windows on Windows
    # This allows viewing logs for each instance separately.
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    time.sleep(1.5)

print("All instances launched!")
