# main.py
#!/usr/bin/env python3
"""
Cloud Inspector V2.0 - 批量巡检 + JSON 报告
Author: zane
"""

import json
from datetime import datetime
from pathlib import Path
from checker.ssh_client import SSHClient

CONFIG_PATH = Path("config/hosts.json")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def load_hosts():
    with open(CONFIG_PATH) as f:
        return json.load(f)["hosts"]

def generate_report(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORT_DIR / f"report_{timestamp}.json"
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_hosts": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "results": results
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Report saved: {report_file}")

def parse_disk_alert(df_output:str):
    # 解析df -h,检查用率>80%
    alert = []
    lines = df_output.splitlines()

    for line in lines[1:]:
        if not line or line.lstrip().startswith('tmpfs') or line.lstrip().startswith('udev'):
            continue

        parts = line.split()
        if len(parts) < 5:
            continue

        usage = parts[4].rstrip('%')
        if usage.isdigit() and int(usage) > 80:
            mount = parts[5] if len(parts) > 5 else 'unknown'
            alert.append(f"Disk {mount} usage {usage}% > 80%")
    return alert if alert else None





def main():
    print("Starting Cloud Inspector V2.0...")
    hosts = load_hosts()
    results = []

    for h in hosts:
        client = SSHClient(
            host_alias=h["alias"],
            username=h.get("username"),
            port=h.get("port", 22),
            key_path=h.get("key")
        )

        host_result = {
            "host": h["alias"],
            "status": "failed",
            "outputs": {}
        }

        if client.connect():
            host_result["status"] = "success"

            for cmd in h.get("commands", []):  
                output = client.exec_command(cmd).strip()
                
                if cmd == 'df -h' and output:
                    host_result["outputs"][cmd] = output.splitlines()
                    alert = parse_disk_alert(output)
                    if alert:
                        host_result['alert'] = alert
                        print(f"WARNING: {h['alias']} disk alert detected: {alert}")
                else:
                    host_result["outputs"][cmd] = output


        else:
            host_result["outputs"]["error"] = "Connection failed"

        results.append(host_result)
        client.close()

    generate_report(results)
    print("Inspection completed!")

if __name__ == "__main__":
    main()