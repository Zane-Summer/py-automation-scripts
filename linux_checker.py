#!/usr/bin/env python3
"""
linux_checker.py - V0.2 : Simplified client.connect()
author: zane
"""

import paramiko
import sys
import os
import socket

USERNAME = "root"
PRIVATE_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
HOST = "hhw"
PORT = 22

def main():
    client = paramiko.SSHClient()
    # 自动接受服务器的主机密钥（仅限开发/受信任环境）
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"connecting to {USERNAME}@{HOST}:{PORT} via SSH key...")

    try:
        
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USERNAME,
            key_filename=PRIVATE_KEY_PATH,
            timeout=30,          # 整个连接的超时时间
            banner_timeout=45,   # 等待 banner 的超时时间
            auth_timeout=45      # 认证超时
        )
        
        print("SSH connection established!")

        # === 在这里执行你的 SSH 命令 ===
        print("Executing 'ls -l'...")
        stdin, stdout, stderr = client.exec_command('ls -l /')
        print(stdout.read().decode())
        
        if stderr.channel.recv_exit_status() != 0:
             print("===Error executing command:===")
             print(stderr.read().decode())
        # ===============================

    except paramiko.ssh_exception.AuthenticationException as e:
        print(f"===Authentication failed: {e}===")
        sys.exit(1)
    except (socket.timeout, paramiko.ssh_exception.SSHException) as e:
        print(f"===Connection failed (timeout or SSH error): {e}===")
        sys.exit(1)
    except Exception as e:
        print(f"===An unexpected error occurred: {e}===")
        sys.exit(1)
    finally:
        if client:
            client.close()
            print("SSH connection closed.")

if __name__ == "__main__":
    main()