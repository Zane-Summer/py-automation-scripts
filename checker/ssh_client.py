# checker/ssh_client.py
import paramiko
from pathlib import Path
from typing import Optional, Tuple

class SSHClient:
    def __init__(self, host_config: dict, timeout: int = 30):
        self.config = host_config
        self.host = host_config.get("host", "localhost") 
        self.username = host_config.get("username", "root")
        self.port = host_config.get("port", 22)
        self.key_path = str(Path(host_config.get("key_path", "~/.ssh/id_rsa")).expanduser())
        self.password = host_config.get("password")
        self.timeout = host_config.get("timeout", timeout)
        self.client = None

    def connect(self) -> bool:
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.key_path and Path(self.key_path).exists():
                pkey = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=pkey,
                    timeout=self.timeout,
                    banner_timeout=self.timeout * 4
                )
            elif self.password:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout,
                    banner_timeout=self.timeout * 4
                )
            else:
                raise ValueError("No key or password provided")
            print(f"Connected to {self.host}")
            return True
        except Exception as e:
            print(f"Failed to connect to {self.host}: {e}")
            return False
        
    def exec_command(self, command: str) -> Optional[str]:
        if not self.client:
            return None
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        return output if not error else f"ERROR: {error}"
    
    def close(self):
        if self.client:
            self.client.close()
            self.client = None