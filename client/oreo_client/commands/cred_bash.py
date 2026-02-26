from ..commands import Command
import subprocess
import shutil
import os

# to use just do 
# cred_bash e1-target.local ftp
class PasswordBash(Command):
    """
    Usage: cred_bash <target> <service>
    Example: cred_bash e1-target.local ftp
    """
    def check_and_install_hydra(self):
        # 1. Check if hydra is in the system PATH
        if shutil.which("hydra") is not None:
            return True

        # 2. Prompt for installation if missing
        print("[-] Error: 'hydra' is not installed.")
        choice = input("[?] Would you like to install it now via apt? (y/n): ").strip().lower()

        if choice == 'y':
            print("[*] Attempting to install 'hydra'...")
            try:
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "hydra"], check=True)
                print("[+] Installation successful!")
                return True
            except subprocess.CalledProcessError:
                print("[-] Installation failed. Please run 'sudo apt install hydra' manually.")
                return False
        return False

    def do_command(self, lines: str, *args):
        def check_hydra():
            if shutil.which("hydra") is not None:
                return True
            print("[-] Error: 'hydra' is not installed.")
            choice = input("[?] Install via apt? (y/n): ").strip().lower()
            if choice == 'y':
                try:
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "-y", "hydra"], check=True)
                    return True
                except: return False
            return False

        # 1. Parse the options from the user input
        parts = lines.split()
        if len(parts) < 2:
            print("Error: Missing arguments.")
            print("Usage: password_bash <target> <service> <user_list> <pass_list>")
            return

        if not check_hydra():
            return

        target = parts[0]
        service = parts[1].lower()
        # user_list = parts[2]
        # pass_list = parts[3]
        user_list = "oreo_client/commands/usernames.txt" #change these two lines to paths of relevant files
        pass_list = "oreo_client/commands/passwords.txt"  

        # Check if the files actually exist before running to avoid Hydra errors
        if not os.path.exists(user_list) or not os.path.exists(pass_list):
            print(f"[-] Error: Ensure '{user_list}' and '{pass_list}' exist in this directory.")
            return

        print(f"[*] Preparing to audit {service} on {target}...")

        # 2. Construct the command list
        # We use a list rather than a single string to avoid shell injection vulnerabilities
        # if the user inputs something unexpected like "target.com; rm -rf /"

       # Updated audit_command using Hydra
        audit_command = [
            "hydra",
            "-I", #skip 10s wait from previous restore file
            "-q", #supresses starting info. "quiet mode"
            "-L", user_list,        # -L for a file containing users
            "-P", pass_list,        # -P for a file containing passwords
            "-f",                   # Exit when the first valid pair is found
            "-V",                   # Verbose (show attempts)
            f"{target}",            # Target IP/Hostname
            f"{service}"            # Service name (e.g., "ftp" or "ssh")
        ]

        print(f"[*] Running command: {' '.join(audit_command)}")

        try:
            # Run the tool and stream output directly to the terminal
            # This is better for Hydra so you can see the progress live
            result = subprocess.run(audit_command, check=False)
            
            if result.returncode == 0:
                print("\n[+] Audit completed successfully.")
            else:
                print(f"\n[!] Hydra finished with exit code {result.returncode}")

        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")

command = PasswordBash