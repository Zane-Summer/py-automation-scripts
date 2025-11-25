"""Paramiko-based SSH client wrapper for inspection tasks."""

import logging
from pathlib import Path
from typing import Optional

import paramiko

logger = logging.getLogger(__name__)


class SSHClient:
    """Establishes SSH connections and executes commands with timeouts."""
    def __init__(self, host_config: dict, timeout: int = 30):
        self.config = host_config
        self.host = host_config.get("host", "localhost")
        self.username = host_config.get("username", "root")
        self.port = host_config.get("port", 22)
        raw_key_path = host_config.get("key_path")
        if raw_key_path is None and not host_config.get("password"):
            raw_key_path = "~/.ssh/id_rsa"
        self.key_path = str(Path(raw_key_path).expanduser()) if raw_key_path else None
        self.password = host_config.get("password")
        self.timeout = host_config.get("timeout", timeout)
        self.command_timeout = host_config.get("command_timeout", 10)
        self.client = None

    def connect(self) -> bool:
        """建立 SSH 连接，优先用密钥，退回密码."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.key_path and Path(self.key_path).exists():
            pkey = paramiko.RSAKey.from_private_key_file(self.key_path)
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                pkey=pkey,
                timeout=self.timeout,
                banner_timeout=self.timeout * 4,
            )
        elif self.password:
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                banner_timeout=self.timeout * 4,
            )
        else:
            raise ValueError("No key or password provided")

        logger.info("Connected to %s:%s", self.host, self.port)
        return True

    def exec_command(self, command: str, timeout: Optional[float] = None) -> str:
        """Execute remote command with可配置超时, 返回 stdout 或包装错误."""
        if not self.client:
            raise RuntimeError("SSH client is not connected")
        _stdin, stdout, stderr = self.client.exec_command(
            command,
            timeout=timeout or self.command_timeout,
        )
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        return output if not error else f"ERROR: {error}"

    def close(self):
        """释放底层 Paramiko 连接."""
        if self.client:
            self.client.close()
            self.client = None
