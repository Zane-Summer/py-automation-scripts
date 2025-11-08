# main.py
import json
import argparse
from pathlib import Path
from checker.inspector import inspect_hosts
from reporter.reporter import generate_report

def load_hosts(file="hosts.json"):
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    file_path = config_dir / file  # e.g. file="hosts.json" → "config/hosts.json"
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found...")
    with open(file_path) as f:  # 用 file_path
        data = json.load(f)
    return data.get("hosts", [])

def main():
    parser = argparse.ArgumentParser(description="批量主机巡检工具")
    parser.add_argument("--hosts", default="hosts.json", help="主机配置文件")
    parser.add_argument("--tags", help="过滤标签, e.g., env=prod,role=web")
    parser.add_argument("--commands", nargs="+", help="自定义命令列表")
    args = parser.parse_args()

    print("Starting batch inspection...")
    hosts = load_hosts(args.hosts)
    
    # 解析 tags 过滤
    tags_filter = {}
    if args.tags:
        for tag in args.tags.split(","):
            k, v = tag.split("=")
            tags_filter[k] = v

    results = inspect_hosts(hosts, tags_filter, args.commands)
    report_file = generate_report(results)
    print(f"\n巡检完成，报告: {report_file}")

if __name__ == "__main__":
    main()