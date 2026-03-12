from ..commands import Command
from .send_to_payload import SendData

class Click(Command):
    """
    Usage:
      click <dst_ip> <dst_port>
    """

    def do_command(self, lines: str, *args):
        parts = lines.split()
        if len(parts) < 2:
            raise ValueError("Usage: click <dst_ip> <dst_port>")

        dst_ip, dst_port = parts
        msg = f"{dst_ip} {dst_port} CLICK"
        SendData().do_command(msg)

command = Click()