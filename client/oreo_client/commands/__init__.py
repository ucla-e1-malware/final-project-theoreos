from abc import ABC

# Commands must be added here to be used. Add the file name minus the ".py"
__all__ = [
    "exit",
    "send_data",
    "brick",
    "scan",
    "phish",
    "send_to_payload"
]


class Command(ABC):
    """A command that does something"""

    def do_command(self, lines: str, *args):
        raise NotImplementedError()
