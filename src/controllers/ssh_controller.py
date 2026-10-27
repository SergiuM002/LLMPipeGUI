import paramiko
import socket
from pathlib import Path
import stat

class SSHController:
    """Coordinates commands run over an SSH connection."""
    class RemoteCommandError(Exception):
        """Custom exception for when remote commands return a non-zero code."""
        def __init__(self, command, exit_code, stderr):
            super().__init__(
                f"Command '{command}' failed with exit code {exit_code}.\n"
                f"Error output:\n{stderr}"
            )
    
    # Custom exit codes
    EXIT_CODE_TIMEOUT = -1
    EXIT_CODE_SSH_ERROR = -2
    
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        self.ssh_client = None
        self.sftp_client = None
        
    def upload_file(self, local_path, remote_path):
        """Uploads file at local_path to remote_path on the server."""
        if not self.sftp_client:
            raise RuntimeError("Error: SFTP client is not connected.")
        
        try:
            self.sftp_client.put(local_path, remote_path)
        except (paramiko.SSHException, OSError) as e:
            raise RuntimeError(f"Failed to transfer file to {remote_path}: {e}") from e
        
    def download_dir(self,  remote_path: str, local_path: str):
        """Recursively downloads a remote directory to local_path."""
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._recursive_sftp_get(self.sftp_client, remote_path, local_path)
            
    def _recursive_sftp_get(self, sftp, remote_dir: str, local_dir: str):    
        """Recursive function to get all files from a directory."""
        Path(local_dir).mkdir(parents=True, exist_ok=True)

        for attr in sftp.listdir_attr(remote_dir):
            remote_path = f"{remote_dir}/{attr.filename}"
            local_path = Path(local_dir) / attr.filename
            
            # Check if remote_path is a directory
            if stat.S_ISDIR(attr.st_mode):
                self._recursive_sftp_get(sftp, remote_path, local_path)
            else:
                sftp.get(remote_path, local_path)
        
    def execute_command(self, command):
        """
        Executes specified command.
        
        Returns a tuple of (stdout, stderr, exit_code).
        """
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
        """Closes SSH and sftp clients."""
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            
    def login(self, hostname, username, password):
        """Connects the user to specified server via SSH."""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_client.connect(hostname=hostname, username=username, password=password, timeout=5)
        self.sftp_client = self.ssh_client.open_sftp()
        
    def get_tmux_sessions(self):
        """Returns the names of all the active tmux sessions."""
        tmux_sessions, _, exit_code = self.execute_command('tmux ls -F "#{session_name}"')
        if exit_code != 0 or not tmux_sessions:
            return []
                
        return tmux_sessions.splitlines()

    def open_line_by_line(self, remote_path):
        """Gets the content of a file line by line."""
        with self.sftp_client.open(remote_path, "r") as remote_file:
            for line in remote_file:
                yield line
                                
    def get_finished_remote_paths(self):
        """Get the finished (or partially finished) remote paths."""
        cmd = "find ~/LLMPipe/results -mindepth 2 -maxdepth 2 -type f | sort"
        return self.execute_command(cmd)[0] or ""
        
    def get_running_remote_sessions_info(self, tmux_sessions=None):
        """
        Return progress details for active remote sessions.

        Each output line contains a session name, input count, progress count,
        and most recent log line, separated by ``|``.
        """
        # Fetch the active sessions unless the caller supplied them
        if tmux_sessions is None:
            tmux_sessions = self.get_tmux_sessions()
        if not tmux_sessions:
            return ""
            
        # Combine per-session checks into one command to reduce SSH round trips
        cmd_parts = []
        for s in tmux_sessions:
            # Skip sessions without a log; otherwise gather counts and the last
            # log line, then print them in the format documented above
            cmd_parts.append(
                f'if [ -f ~/LLMPipe/{s}.log ]; then '
                f'sc=$(grep -c "^>" ~/LLMPipe/{s}.fa 2>/dev/null || echo 0); '
                f'sp=$(grep -c -E "Processing windows: [0-9]+it " ~/LLMPipe/{s}.log 2>/dev/null || true); '
                f'last=$(tr "\r" "\n" < ~/LLMPipe/{s}.log | tail -n 1 ); '
                f'echo "{s}|$sc|$sp|$last"; '
                f'fi'
            )
            
        # Return the combined command output, defaulting to an empty string
        batch_cmd = " ; ".join(cmd_parts)
        return self.execute_command(batch_cmd)[0] or ""