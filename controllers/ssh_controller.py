import paramiko
import socket

class SSHController:
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        self.ssh_client = None
        self.sftp_client = None
        
    def transfer_file(self, local_path, remote_path):
        try:
            self.sftp_client.put(local_path, remote_path)
            return True
        except (paramiko.SSHException, socket.error) as e:
            print(f"Error transferring file: {e}")
            return False
        
    def retrieve_file(self, remote_path, local_path):
        try:
            self.sftp_client.get(remote_path, local_path)
            return True
        except (paramiko.SSHException, socket.error) as e:
            print(f"Error retrieving file: {e}")
            return False
        
    def execute_command(self, command):
        try:
            _, stdout, stderr = self.ssh_client.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
            try:
                exit_code = stdout.channel.recv_exit_status()
            except Exception:
                exit_code = None
            return out, err, exit_code
        except (paramiko.SSHException, socket.error) as e:
            print(f"Error executing command: {e}")
            return None, str(e), None    
        
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
