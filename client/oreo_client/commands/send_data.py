from ..commands import Command
import socket
import struct

def send_framed(sock, data: bytes):
    sock.sendall(struct.pack(">I", len(data)) + data)

def recv_framed(sock):
    header = b""
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk: # Connection closed by server
            return None
        header += chunk
        
    # If we somehow broke out but don't have 4 bytes
    if len(header) < 4:
        return None
        
    msg_len = struct.unpack(">I", header)[0]
    data = b""
    while len(data) < msg_len:
        chunk = sock.recv(msg_len - len(data))
        if not chunk: # Connection closed midway through data
            break
        data += chunk 
    return data

def process_lines(lines: str):
    parts = lines.split(None, 2)

    if len(parts) < 3:
        print("[-] Usage: send_data <ip> <port> <command>")
        return

    dst_ip = parts[0] 
    dst_port = int(parts[1]) 
    data_to_send = " ".join(parts[2:])

    try:
        # Connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10.0)
        client_socket.connect((dst_ip, dst_port))

        # Send data to server
        send_framed(client_socket, data_to_send.replace("\\n", "\n").encode())  
        
        # Get response
        response = recv_framed(client_socket)
        
        if response:
            try: 
                print("Data received from server -->\n", response.decode()) 
            except UnicodeDecodeError:
                print(f"[binary output - {len(response)} bytes]")
        else:
            print("[+] Server closed connection (expected if os.execv restarted the script).")

        # Close socket
        client_socket.close()
        
    except ConnectionRefusedError:
        print(f"[-] Connection refused to {dst_ip}:{dst_port}.")
    except Exception as e:
        print(f"[-] Error: {e}")

class SendData(Command):
    """Send framed data over the socket"""
    
    def do_command(self, lines: str, *args):
        process_lines(lines)

command = SendData