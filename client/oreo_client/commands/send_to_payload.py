# Example of how to send data
# File is incomplete - fill in the blanks

from ..commands import Command
import socket
import struct


# Added for multiline

def send_framed(sock, data: bytes):
    sock.sendall(struct.pack(">I", len(data)) + data)

def recv_framed(sock):
    header = b""
    while len(header) < 4:
        header += sock.recv(4 - len(header))
    msg_len = struct.unpack(">I", header)[0]
    data = b""
    while len(data) < msg_len:
        data += sock.recv(msg_len - len(data)) 
    return data


def process_lines(lines: str):
    # parts = lines.split()
    parts = lines.split(None, 2)

    dst_ip = parts[0] # TODO - should be str
    dst_port = int(parts[1]) # TODO - should be int
    data_to_send = " ".join(parts[2:])
    # data_to_send = "hello, world!" # TODO

    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((dst_ip, dst_port))

    # Send data to server and print response
    # client_socket.send(data_to_send.encode())
    # response = client_socket.recv(2048) # Can call multiple times to get more data
    #ADDED
    send_framed(client_socket, data_to_send.replace("\\n", "\n").encode())  # sends length then data
    response = recv_framed(client_socket)
    if response.startswith(b"TEXT\n"):
        print("Data received from server -->\n", response[5:].decode())
    elif response.startswith(b"FILE\n"):
        import time
        content = response[5:]
        filename = f"screenshot_{int(time.time())}.png"
        with open(filename, "wb") as f:
            f.write(content)
        print(f"Saved file as {filename}")
        import subprocess
        subprocess.run(["feh", filename], stderr=subprocess.DEVNULL)
        
    else:
        print(f"[unknown response - {len(response)} bytes]")
    # Close socket
    client_socket.close()

class SendData(Command):
    """Send data over the socket"""
    
    def do_command(self, lines: str, *args):
        process_lines(lines)

command = SendData