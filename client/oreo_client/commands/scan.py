from ..commands import Command
import socket

def scan_ip(target: str, port_range: tuple[int, int]) -> list[int]:

    openPorts = []

    for i in range(port_range[0], port_range[1] + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((target, i))
        
        if result == 0:
            openPorts.append(i)

        s.close()

    return openPorts

def pretty_print_scan(open_ports: list[int]) -> None:
    print(f"{'PORT':<10} {'SERVICE'}")
    print("-" * 25)

    for port in open_ports:
        try:
            service_name = socket.getservbyport(port)

        except OSError:
            service_name = "unknown"

        print(f"{port:<10} {service_name}")


# Example call to the functions
# You do not need to edit anything in here
if __name__ == "__main__":
    target_ip = "127.0.0.1"
    ports = (20, 8000)
    open_ports = scan_ip(target_ip, ports)
    print(f"Open ports on {target_ip}: {", ".join(map(str, open_ports))}")
    print()
    pretty_print_scan(open_ports)
    # You should (probably) see ports 22, 111, and 631 open, though exact open ports may vary.
    # Feel free to test against the autograder as many times as you'd like!

class Scan(Command):
    """
    Scan a target IP for open ports.
    Usage: scan <IP> <START_PORT> <END_PORT>
    Example: scan 127.0.0.1 5 100
    """

    def do_command(self, lines: str, *args):
        args = lines.split()

        if len(args) < 3:
            print("Error: Missing arguments.")
            print("Usage: scan <IP> <START_PORT> <END PORT>")
            return
    
        target_ip = args[0]

        try:
            start_port = int(args[1])
            end_port = int(args[2])
        except ValueError:
            print("Error: Ports must be integers.")
            return
        
        print(f"Scanning {target_ip} from port {start_port} to {end_port}...")
        
        open_ports = scan_ip(target_ip, (start_port, end_port))

        if open_ports:
            print(f"Open ports on {target_ip}: {'.'.join(map(str, open_ports))}")
            print()
            pretty_print_scan(open_ports)
        else:
            print(f"No open ports found on {target_ip} in range {start_port} - {end_port}.")

command = Scan