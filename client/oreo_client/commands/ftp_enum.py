from ..commands import Command
import ftplib

# to use do
# ftp_enum e1-target.local

class FtpEnum(Command):
    """
    Attempt an anonymous FTP login and search for sensitive files.
    Usage: ftp_enum <IP_OR_HOSTNAME>
    Example: ftp_enum e1-target.local
    """

    def do_command(self, lines: str, *args):
        target = lines.strip()

        if not target:
            print("Error: No target provided.")
            print("Usage: ftp_enum <IP_OR_HOSTNAME>")
            return

        print(f"[*] Attempting anonymous FTP login to {target}...")
        
        try:
            # Connect and login as anonymous
            ftp = ftplib.FTP(target, timeout=5)
            ftp.login()
            print(f"[+] Success! Logged in as anonymous to {target}")

            # Get a list of files in the current directory
            # We use nlst() to just get the names, or retrlines('LIST') for full details
            files = ftp.nlst()
            
            # Keywords you wanted to target
            targets = ["pass", "config", "key", ".env"]
            found_files = []

            for f in files:
                # Check if any of our target keywords are in the filename (case-insensitive)
                if any(keyword in f.lower() for keyword in targets):
                    found_files.append(f)

            if found_files:
                print(f"[!] Found potentially sensitive files: {', '.join(found_files)}")
                # Next step would be to implement ftp.retrbinary() to download them
            else:
                print("[-] No immediately obvious sensitive files found in current directory.")

            ftp.quit()

        except ftplib.all_errors as e:
            print(f"[-] FTP connection or login failed: {e}")

# This line is required for your app.py to load it!
command = FtpEnum