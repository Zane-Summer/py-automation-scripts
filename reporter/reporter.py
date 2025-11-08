# checker/reporter.py
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

REPORT_DIR = Path('reports')
REPORT_DIR.mkdir(exist_ok=True)

def generate_report(results: List[Dict], output_file: str = None) -> str:
    if not output_file:
        now = datetime.now()
        output_file = REPORT_DIR / f"report_{now.strftime('%Y%m%d_%H%M%S')}.json"
    
    summary = {
        "report_time": datetime.now().isoformat(),
        "total_hosts": len(results),
        "success_hosts": len([r for r in results if r["status"] == "success"]),
        "failed_hosts": len([r for r in results if r["status"] == "failed"]),
        "alerts": len([r for r in results if "alert" in r])
    }

    report_content = {
        "summary": summary,
        "results": results
    }

    print("-----正在生成报告...-----")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_content, f, ensure_ascii=False, indent=4)
        print(f"-----报告生成成功: {output_file}-----")
        return str(output_file)
    except Exception as e:
        print(f"[错误]: 写入报告失败: {e}")
        return None