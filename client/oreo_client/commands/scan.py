from ..commands import Command
import socket

def scan_ip(target: str, port_range: tuple[int, int]) -> list[int]:
    openPorts = []
    # Loop through the port range
    for i in range(port_range[0], port_range[1] + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5) # Add a small timeout to speed up scanning closed ports
        result = s.connect_ex((target, i))
        
        if result == 0:
            openPorts.append(i)

        s.close()
    
    # NOTE: We removed the identify() call here. 
    # We only want to identify services if the user specifically asks for it.
    return openPorts

def get_banner(target: str, port: int) -> str:
    """
    Attempts to grab a service banner.
    1. Tries to receive data immediately (for SSH/FTP).
    2. If that times out, sends an HTTP GET request (for Web Servers).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0) # Requirement: Set timeout so it doesn't hang 
        s.connect((target, port))
        
        try:
            # Case 1: Services that speak first (SSH, FTP) 
            banner = s.recv(1024).decode().strip()
            if banner:
                return banner
                
        except socket.timeout:
            # Case 2: Web Servers wait for us to speak. 
            # If we timed out, send a generic HTTP request 
            try:
                # Send the exact HTTP GET string required
                s.sendall(b"GET / HTTP/1.1\r\n\r\n")
                response = s.recv(2048).decode(errors='ignore')
                
                # Parse the response for the "Server:" header 
                for line in response.split('\n'):
                    if line.startswith("Server:"):
                        return line.strip()
            except:
                return "No Response"
                
    except Exception as e:
        return "Connection Error"
    finally:
        s.close()
        
    return "Unknown Service"

def pretty_print_scan(open_ports: list[int], target_ip: str = None, do_service_scan: bool = False) -> None:
    print(f"{'PORT':<10} {'SERVICE':<20} {'VERSION' if do_service_scan else ''}")
    print("-" * 60)

    for port in open_ports:
        try:
            service_name = socket.getservbyport(port)
        except OSError:
            service_name = "unknown"

        version_info = ""
        if do_service_scan and target_ip:
            version_info = get_banner(target_ip, port)

        print(f"{port:<10} {service_name:<20} {version_info}")


class Scan(Command):
    """
    Scan a target IP for open ports.
    Usage: scan <IP> <START_PORT> <END_PORT> [--service-scan]
    Example: scan 127.0.0.1 20 100 --service-scan
    """

    def do_command(self, lines: str, *args):
        args_list = lines.split()
        
        # Requirement: Check for the --service-scan flag 
        do_service_scan = False
        if "--service-scan" in args_list:
            do_service_scan = True
            args_list.remove("--service-scan")

        if len(args_list) < 3:
            print("Error: Missing arguments.")
            print("Usage: scan <IP> <START_PORT> <END PORT> [--service-scan]")
            return
    
        target_ip = args_list[0]

        try:
            start_port = int(args_list[1])
            end_port = int(args_list[2])
        except ValueError:
            print("Error: Ports must be integers.")
            return
        
        print(f"Scanning {target_ip} from port {start_port} to {end_port}...")
        
        open_ports = scan_ip(target_ip, (start_port, end_port))

        if open_ports:
            print(f"Open ports on {target_ip}: {', '.join(map(str, open_ports))}")
            print()
            # Pass the new flag and IP to the print function so it can run the banner grab
            pretty_print_scan(open_ports, target_ip, do_service_scan)
        else:
            print(f"No open ports found on {target_ip} in range {start_port} - {end_port}.")

command = Scan