import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from checker.inspector import inspect_hosts
from config.loader import load_settings
from reporter.reporter import generate_report


def setup_logging(level_name: str) -> None:
    """Configure root logger so every模块共享统一格式/Handler."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 清理旧 handler，避免重复输出
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_tags(tags_arg: str) -> dict:
    """Convert CLI tag string (k=v,k2=v2) to dict,忽略非法片段."""
    tags_filter = {}
    if not tags_arg:
        return tags_filter
    for tag in tags_arg.split(","):
        if "=" not in tag:
            continue
        k, v = tag.split("=", 1)
        tags_filter[k.strip()] = v.strip()
    return tags_filter


def main():
    """CLI entry: 解析参数→校验配置→并发巡检→生成报告。"""
    parser = argparse.ArgumentParser(description="批量主机巡检工具")
    parser.add_argument("--hosts", default="hosts.json", help="主机配置文件")
    parser.add_argument("--tags", help="过滤标签, e.g., env=prod,role=web")
    parser.add_argument("--commands", nargs="+", help="自定义命令列表")
    parser.add_argument("--max-workers", type=int, default=5, help="并发线程数，默认 5")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="日志级别，默认 INFO",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting batch inspection...")

    settings = load_settings(args.hosts)
    hosts = [host.model_dump() for host in settings.hosts]

    tags_filter = parse_tags(args.tags)

    results = inspect_hosts(
        hosts,
        tags_filter=tags_filter,
        commands=args.commands,
        max_workers=args.max_workers,
    )
    report_file = generate_report(results)
    logger.info("巡检完成，报告: %s", report_file)


if __name__ == "__main__":
    main()
