import paramiko
import socket

class SSHController:
    # Custom exception for when remote commands return a non-zero code
    class RemoteCommandError(Exception):
        def __init__(self, command, exit_code, stderr):
            super().__init__(
                f"Command '{command}' failed with exit code {exit_code}.\n"
                f"Error output:\n{stderr}"
            )
    
    EXIT_CODE_TIMEOUT = -1
    EXIT_CODE_SSH_ERROR = -2
    
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        self.ssh_client = None
        self.sftp_client = None
        
    def transfer_file(self, local_path, remote_path):
        if not self.sftp_client:
            raise RuntimeError("Error: SFTP client is not connected.")
        
        try:
            self.sftp_client.put(local_path, remote_path)
        except (paramiko.SSHException, OSError) as e:
            raise RuntimeError(f"Failed to transfer file to {remote_path}: {e}") from e
        
    def retrieve_file(self, remote_path, local_path):
        if not self.sftp_client:
            raise RuntimeError("Error: SFTP client is not connected.")
                
        try:
            self.sftp_client.get(remote_path, local_path)
        except (paramiko.SSHException, OSError) as e:
            raise RuntimeError(f"Failed to retrieve file from {remote_path}: {e}") from e
        
    def execute_command(self, command):
        out, err = "", ""
        exit_code = None
        
        try:
            _, stdout, stderr = self.ssh_client.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
   
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                raise self.RemoteCommandError(command, exit_code, err)
            
            return out, err, exit_code
        except socket.timeout as e:
            return out, f"Connection timeout: {e}", self.EXIT_CODE_TIMEOUT
        except (paramiko.ssh_exception.SSHException, socket.error) as e:
            return out, f"SSH connection error: {e}", self.EXIT_CODE_SSH_ERROR
        except self.RemoteCommandError as e:
            return out, str(e), exit_code
        
        
    def close_clients(self):
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            
    def login(self, hostname, username, password):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_client.connect(hostname=hostname, username=username, password=password, timeout=5)
        self.sftp_client = self.ssh_client.open_sftp()

    def open_line_by_line(self, remote_path):
        with self.sftp_client.open(remote_path, "r") as remote_file:
            for line in remote_file:
                yield line