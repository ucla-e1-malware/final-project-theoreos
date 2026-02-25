from ..commands import Command
import shlex
import subprocess
import shutil


class PasswordBash(Command):
    """
    Conceptual wrapper for an external password auditing tool.
    Usage: password_bash <target> <service> <user_list> <pass_list>
    """

    def check_and_install_patator(self):
        # 1. Check if it exists in the system PATH
        if shutil.which("patator") is not None:
            print("[+] 'patator' is installed and ready to use.")
            return True

        # 2. If not found, warn the user and prompt for installation
        print("[-] Error: 'patator' is not installed.")
        choice = input("[?] Would you like to install it now via apt? (y/n): ").strip().lower()

        if choice == 'y':
            print("[*] Attempting to install 'patator'...")
            try:
                # 3. Execute the installation command
                # Using 'sudo' might prompt the user to type their password in the terminal
                # The '-y' flag tells apt to automatically answer "yes" to confirmation prompts
                subprocess.run(["sudo", "apt", "install", "-y", "patator"], check=True)
                
                print("[+] Installation successful!")
                return True
                
            except subprocess.CalledProcessError:
                # This triggers if the apt command fails (e.g., bad package name or no internet)
                print("[-] Installation failed. Please install 'patator' manually.")
                return False
        else:
            print("[-] Cannot proceed with this command without 'patator'.")
            return False

    def do_command(self, lines: str, *args):
        # 1. Parse the options from the user input

        parts = lines.split()
        if len(parts) < 2:
            print("Error: Missing arguments.")
            print("Usage: password_bash <target> <service> <user_list> <pass_list>")
            return

        target = parts[0]
        service = parts[1]
        # user_list = parts[2]
        # pass_list = parts[3]

        if not self.check_and_install_patator(): # check if package installed
            return

        print(f"[*] Preparing to audit {service} on {target}...")

        # 2. Construct the command list
        # We use a list rather than a single string to avoid shell injection vulnerabilities
        # if the user inputs something unexpected like "target.com; rm -rf /"
        user_list = "userlist.txt" 
        pass_list = "passwords.txt"  

        audit_command = [
            "patator",
            f"{service}_login",                      # Service specific command (e.g., ftp_login or ssh_login)
            "host=" + target,                        # Target URI
            "user=" + user_list,                    # Username list
            "password=" + pass_list,                # Password list
            "-x", "ignore:10"                       # Allow up to 10 ignored failures
        ]  # patator ftp_login host=e1-target.local user=usernames.txt password=rockyou.txt -x ignore:10


        print(f"[*] Abstract command constructed: {' '.join(audit_command)}")

        try:
            # This is the line that actually runs the tool in the terminal
            result = subprocess.run(
                audit_command, 
                capture_output=True,  # Tells Python to grab what the tool prints
                text=True,            # Decodes the output from bytes into a normal string
                check=False           # Prevents Python from crashing if patator fails/errors out
            )
        
            # Print the standard output (what the tool successfully did)
            if result.stdout:
                print("[+] patator Output:\n")
                print(result.stdout)
            
            # Print the standard error (if the tool complained about something)
            if result.stderr:
                print("[-] patator reported errors:\n")
                print(result.stderr)
            
        except FileNotFoundError:
            # This happens if the OS literally can't find the "patator" program installed
            print("[-] Error: The 'patator' tool is not installed or not in your system's PATH.")
        except Exception as e:
            # Catch-all for any other weird OS-level errors
            print(f"[-] An unexpected error occurred: {e}")

command = PasswordBash