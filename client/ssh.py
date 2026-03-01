import paramiko

print("hi")

# SSH connection parameters
host = "e1-target.local"  # Replace with your server's address
port = 22  # Default SSH port
username = "e1-target"  # Replace with your username
password = "aotismyfavoriteanime"  # Replace with your password

try:
    # Create an SSH client instance
    client = paramiko.SSHClient()
    
    # Automatically add untrusted hosts (make sure to use this only in a trusted environment)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect to the server
    client.connect(hostname=host, port=port, username=username, password=password)
    
    print(f"Successfully connected to {host}")
    
    # Execute a command (optional)
    stdin, stdout, stderr = client.exec_command('ls -l')  # Example command
    print(stdout.read().decode())  # Print the command output
    
except paramiko.AuthenticationException:
    print("Authentication failed, please verify your credentials")
except paramiko.SSHException as e:
    print(f"Failed to connect to {host}: {e}")
finally:
    client.close()  # Close the connection
