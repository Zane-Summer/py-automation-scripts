# checker/ssh_client.py
import paramiko
from pathlib import Path
from typing import Optional, Tuple

class SSHClient:
    def __init__(self, host_alias: str, username: str = "root", port: int = 22, 
                 key_path: str = "~/.ssh/id_rsa", timeout: int = 30):
        self.alias = host_alias
        self.username = username
        self.port = port
        self.key_path = str(Path(key_path).expanduser())
        self.timeout = timeout
        self.client = None

    def _resolve_host(self) -> Tuple[str, str]: 
        # Analyse alias from ~/.ssh/config
        config_path = Path("~/.ssh/config").expanduser()
        if config_path.exists():
            config = paramiko.SSHConfig()
            config.parse(config_path.open())
            cfg = config.lookup(self.alias)
            return cfg.get("hostname", self.alias), cfg.get("user", self.username)
        return self.alias, self.username
    
    def connect(self) -> bool:
        host, user = self._resolve_host()  
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # 支持 RSA（如果 ed25519，需调整）
            pkey = paramiko.RSAKey.from_private_key_file(self.key_path)
            self.client.connect(
                hostname=host,
                port=self.port,
                username=user,
                pkey=pkey,
                timeout=self.timeout,
                banner_timeout=self.timeout * 4
            )
            print(f"Connected to {self.alias} ({host})")
            return True
        except Exception as e:
            print(f"Failed to connect to {self.alias} ({host}): {e}")
            return False
        
    def exec_command(self, command: str):
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