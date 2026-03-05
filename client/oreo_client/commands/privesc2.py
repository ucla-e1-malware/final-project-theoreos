from ..commands import Command
from .send_data import process_lines

class PrivEsc2(Command):
    """Triggers the /etc/passwd root user injection on the remote server."""
    
    def do_command(self, args: str, *ext_args):
        # Default to e1-target.local if no IP is provided
        parsed_args = args.split()
        dst_ip = parsed_args[0] if len(parsed_args) > 0 else "e1-target.local"
        dst_port = parsed_args[1] if len(parsed_args) > 1 else "5050"

        print(f"[*] Sending PrivEsc2 (passwd injection) to {dst_ip}:{dst_port}...")
        
        # This sends the 'privesc2' string which triggers your server function
        process_lines(f"{dst_ip} {dst_port} privesc2")

command = PrivEsc2