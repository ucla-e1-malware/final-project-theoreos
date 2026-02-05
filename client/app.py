# Client cmd interface
# You should not need to edit anything in this file,
# except for the couple locations marked with a comment


# Rename the cybersploit_client folder to whatever you want to call your project
# Put the name of that folder here
PROJECT_NAME = "oreo_client" 

from cmd import Cmd
import importlib
commands = importlib.import_module(f"{PROJECT_NAME}.commands") 
import sys # Do not remove even if vscode complains it is unused
import readline # Do not remove even if vscode complains it is unused


def add_command(cmd_name, func, docstring, cmd):
    """Add a new command to the cmdclass."""
    setattr(cmd, "do_" + cmd_name, func)
    setattr(cmd, "help_" + cmd_name, lambda self: print(docstring))


class CustomCommand(Cmd):

    def parse_args(self, provided_args, expected_args=""):
        return provided_args.split(" ")

    def __init__(self):
        super().__init__()
        # Change this string to change the default prompt.
        # In a command, you can also do self.prompt to change the prompt if you'd like
        self.prompt = "> "

if __name__ == "__main__":
    all_commands = commands.__all__
    for command in all_commands:
        # module:
        module = importlib.import_module(
            f"{PROJECT_NAME}.commands.{command}"
        ).command
        # Add the command function to MyCmd class
        add_command(
            command, getattr(module, "do_command"), module.__doc__, CustomCommand
        )

    # Add an exit handler alias for ^D
    exit_module = importlib.import_module(f"{PROJECT_NAME}.commands.exit").command
    add_command(
        "EOF", getattr(exit_module, "do_command"), exit_module.__doc__, CustomCommand
    )

    main_shell = CustomCommand()

    main_shell.cmdloop()
