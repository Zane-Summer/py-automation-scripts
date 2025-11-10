import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)


def generate_report(results: List[Dict], output_file: str = None) -> str:
    """Persist JSON report并统计耗时/告警摘要."""
    if not output_file:
        now = datetime.now()
        output_file = REPORT_DIR / f"report_{now.strftime('%Y%m%d_%H%M%S')}.json"

    durations = [r.get("duration", 0) for r in results if "duration" in r]
    longest_duration = max(durations) if durations else 0
    average_duration = round(sum(durations) / len(durations), 3) if durations else 0

    summary = {
        "report_time": datetime.now().isoformat(),
        "total_hosts": len(results),
        "success_hosts": len([r for r in results if r.get("status") == "success"]),
        "failed_hosts": len([r for r in results if r.get("status") == "failed"]),
        "alerts": sum(len(r.get("alerts", [])) for r in results),
        "longest_duration": round(longest_duration, 3),
        "average_duration": average_duration,
    }

    report_content = {
        "summary": summary,
        "results": results,
    }  # 预留给未来的 Jinja2 HTML 渲染

    logger.info("-----正在生成报告-----")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_content, f, ensure_ascii=False, indent=4)
        logger.info("-----报告生成成功: %s-----", output_file)
        return str(output_file)
    except Exception as e:
        logger.exception("[错误]: 写入报告失败: %s", e)
        return None
