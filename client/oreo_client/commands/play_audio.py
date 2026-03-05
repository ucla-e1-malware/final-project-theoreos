from ..commands import Command
from .send_to_payload import process_lines
from .send_to_payload import SendData


from ..commands import Command
from .send_to_payload import SendData

class PlayAudio(Command):
    """
    Usage (example):
      play_audio <dst_ip> <dst_port> <payload_text>
    This only forwards data; it does NOT execute audio playback.
    """
    def do_command(self, lines: str, *args):
        parts = lines.split(maxsplit=2)
        if len(parts) < 3:
            raise ValueError("Usage: play_audio <dst_ip> <dst_port> <payload_text>")

        dst_ip, dst_port, payload_text = parts

        # Forward a structured message to the payload.
        # (Keep it simple; your receiver can parse the prefix.)
        msg = f"{dst_ip} {dst_port} PLAY_AUDIO {payload_text}"
        SendData().do_command(msg)

command = PlayAudio