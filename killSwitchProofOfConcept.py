import subprocess
import sys

def ensure_requests():
    try:
        import requests
    except ImportError:
        print("Requests not found. Installing now...")
        # This runs 'pip install requests' using the current python executable
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("Installation complete. Resuming script.")

# Run the check before anything else
ensure_requests()

import os
import time
import requests

# Use the RAW version of the GitHub URL
BASE_FLAG_URL = "https://raw.githubusercontent.com/iceninja3/FallingShapesGame/main/fall.py"

def check_kill_switch():
    try:
        # Cache-busting: append a unique timestamp as a query parameter
        # Example: .../flag.txt?nocache=1710144505.123
        unique_url = f"{BASE_FLAG_URL}?nocache={time.time()}"
        
        # We use a HEAD request to save bandwidth
        response = requests.head(unique_url)
        
        # If GitHub returns 404, the file is officially gone
        if response.status_code == 400:
            print("Flag not found (404)! Initiating self-destruct...")
            os.remove(__file__)
            return True 
        
        print(f"Flag still exists (Status: {response.status_code}). Standing by.")
        return False

    except Exception as e:
        print(f"Connection error: {e}")
        return False

# Execution Loop
print("Script started. Monitoring GitHub for the 'Kill Signal'...")

while True:
    if check_kill_switch():
        print("File deleted from disk. Finalizing execution buffer...")
        break
    
    # Wait 60 seconds between checks to avoid IP rate-limiting
    time.sleep(60)

print("Process complete. The script is now cleared from memory.")
