# Example of how to send data
# File is incomplete - fill in the blanks

from ..commands import Command
import socket


def process_lines(lines: str):
    dst_ip = ... # TODO - should be str
    dst_port = ... # TODO - should be int
    data_to_send = "hello, world!" # TODO

    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((dst_ip, dst_port))

    # Send data to server and print response
    client_socket.send(data_to_send.encode())
    response = client_socket.recv(2048) # Can call multiple times to get more data
    print(
        "Data received from server -->\n", response.decode()
    )  # Decode bytes to string before printing

    # Close socket
    client_socket.close()

class SendData(Command):
    """Send data over the socket"""
    
    def do_command(self, lines: str, *args):
        process_lines(lines)

command = SendData






# original send_data.py
# # Example of how to send data
# # File is incomplete - fill in the blanks

# from ..commands import Command
# import socket


# def process_lines(lines: str):
#     dst_ip = ... # TODO - should be str
#     dst_port = ... # TODO - should be int
#     data_to_send = "hello, world!" # TODO

#     # Connect to server
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect((dst_ip, dst_port))

#     # Send data to server and print response
#     client_socket.send(data_to_send.encode())
#     response = client_socket.recv(2048) # Can call multiple times to get more data
#     print(
#         "Data received from server -->\n", response.decode()
#     )  # Decode bytes to string before printing

#     # Close socket
#     client_socket.close()

# class SendData(Command):
#     """Send data over the socket"""
    
#     def do_command(self, lines: str, *args):
#         process_lines(lines)

# command = SendData
