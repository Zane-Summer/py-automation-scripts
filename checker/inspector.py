# checker/inspector.py
from .ssh_client import SSHClient
import paramiko
from typing import Optional, Dict, Any, List
from datetime import datetime

def inspect_hosts(hosts: List[dict], tags_filter: Optional[Dict[str, str]] = None, commands: List[str] = None) -> List[Dict[str, Any]]:
    results = []
    default_commands = ["uptime"] if not commands else commands

    for host_config in hosts:
        # 支持 tags 过滤
        if tags_filter and not all(host_config.get("tags", {}).get(k) == v for k, v in tags_filter.items()):
            print(f"Skipping {host_config.get('name', host_config['host'])} (tag mismatch)")
            continue

        ssh = SSHClient(host_config)
        result = {
            "name": host_config.get("name", host_config["host"]),
            "host": host_config["host"],
            "status": "failed",
            "error": "",
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }

        try:
            if ssh.connect():
                for cmd in default_commands + host_config.get("commands", []):
                    output = ssh.exec_command(cmd)
                    result["checks"][cmd] = output
                    if cmd == 'df -h' and output:
                        alert = parse_disk_alert(output)
                        if alert:
                            result["alert"] = alert
                            print(f"WARNING: {alert}")
                result["status"] = "success"
        except paramiko.AuthenticationException as auth_err:  # 认证失败
            result["error"] = f"Auth failed: {auth_err}"
        except paramiko.SSHException as ssh_err:  # SSH 错误
            result["error"] = f"SSH error: {ssh_err}"
        finally:
            ssh.close()

        results.append(result)
        print(f"  → {result['status']}")

    return results

def parse_disk_alert(df_output: str) -> Optional[str]:
    lines = df_output.splitlines()
    for line in lines[1:]:
        if line.strip() and not line.startswith('tmpfs'):
            parts = line.split()
            if len(parts) >= 5:
                usage = parts[4].rstrip('%')
                if usage.isdigit() and int(usage) > 80:
                    mount = parts[5] if len(parts) > 5 else 'unknown'
                    return f"磁盘 {mount} 用率 {usage}% > 80%"
    return None