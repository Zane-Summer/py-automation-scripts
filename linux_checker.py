#!/usr/bin/env python3
"""
linux_checker.py - V1.0: Huawei Cloud ECS SSH connection
Author: Zane Summer
"""

import paramiko
import sys
import os

USERNAME = "root"
PRIVATE_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
HOST = "124.70.88.117"
PORT = 22

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"connecting to {USERNAME}@{HOST}:{PORT} via SSH key...")

    try:
        KEY = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)

        client.connect(
            hostname=HOST,
            port=PORT,
            username=USERNAME,
            pkey=KEY,
            timeout=30,
            banner_timeout=120
        )
        print("SSH connection established!")

        # 测试命令
        stdin, stdout, stderr = client.exec_command("uptime")
        print("\n=== Remote uptime ===")
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"connection failed: {e}")
        sys.exit(1)
    finally:
        client.close()
        print("SSH connection closed.")

if __name__ == "__main__":
    main()