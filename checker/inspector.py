"""Concurrent SSH inspection orchestration and alert parsing."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging
import re
import time
from typing import Optional, Dict, Any, List

import paramiko

from .ssh_client import SSHClient

logger = logging.getLogger(__name__)

DEFAULT_COMMANDS = ["uptime"]
RETRY_ATTEMPTS = 2
RETRY_BASE_DELAY = 0.5
DEFAULT_MEM_THRESHOLD = 80
DEFAULT_DISK_THRESHOLD = 80
LOAD_MULTIPLIER = 1.5


def inspect_single_host(
    host_config: Dict[str, Any],
    default_commands: List[str],
) -> Dict[str, Any]:
    """Run the inspection flow for a single host (connect→exec→收集结果)."""
    ssh = SSHClient(host_config)
    result = {
        "name": host_config.get("name", host_config["host"]),
        "host": host_config["host"],
        "status": "failed",
        "error": "",
        "errors": [],
        "alerts": [],
        "checks": {},
        "timestamp": datetime.now().isoformat(),
        "duration": 0.0,
    }

    start = time.perf_counter()
    commands_to_run = default_commands + host_config.get("commands", [])
    retries = host_config.get("retries", RETRY_ATTEMPTS)
    command_timeout = host_config.get("command_timeout", ssh.command_timeout)

    try:
        connect_with_retry(ssh, retries=retries)
        for cmd in commands_to_run:
            try:
                output = exec_with_retry(
                    ssh,
                    cmd,
                    retries=retries,
                    timeout=command_timeout,
                )
                result["checks"][cmd] = output
                alerts = collect_alerts(cmd, output, host_config)
                if alerts:
                    result["alerts"].extend(alerts)
                    # 兼容旧字段
                    result.setdefault("alert", alerts[0])
            except Exception as cmd_err:
                message = f"{result['name']} 命令 {cmd} 失败: {cmd_err}"
                result["errors"].append(message)
                logger.error(message)

        if not result["errors"]:
            result["status"] = "success"
        else:
            result["error"] = "; ".join(result["errors"])
    except paramiko.AuthenticationException as auth_err:
        msg = f"{result['name']} 认证失败: {auth_err}"
        result["errors"].append(msg)
        result["error"] = msg
        logger.error(msg)
    except paramiko.SSHException as ssh_err:
        msg = f"{result['name']} SSH 异常: {ssh_err}"
        result["errors"].append(msg)
        result["error"] = msg
        logger.error(msg)
    except Exception as exc:
        msg = f"{result['name']} 未知错误: {exc}"
        result["errors"].append(msg)
        result["error"] = msg
        logger.exception(msg)
    finally:
        ssh.close()
        result["duration"] = round(time.perf_counter() - start, 3)
        logger.info("→ %s: %s (%.3fs)", result["name"], result["status"], result["duration"])

    return result


def connect_with_retry(ssh: SSHClient, retries: int = RETRY_ATTEMPTS) -> None:
    """Try establishing SSH connection with轻量重试,认证失败不重试."""
    delay = RETRY_BASE_DELAY
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            ssh.connect()
            return
        except paramiko.AuthenticationException:
            raise
        except Exception as exc:
            last_exc = exc
            logger.warning("连接失败(第 %s 次): %s", attempt, exc)
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
    if last_exc:
        raise paramiko.SSHException(last_exc)
    raise paramiko.SSHException("连接失败且无异常信息")


def exec_with_retry(ssh: SSHClient, command: str, retries: int, timeout: float) -> str:
    """执行命令并重试 SSHException, 每次延迟翻倍."""
    delay = RETRY_BASE_DELAY
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            return ssh.exec_command(command, timeout=timeout)
        except paramiko.SSHException as exc:
            last_exc = exc
            logger.warning("%s 失败(第 %s 次): %s", command, attempt, exc)
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
    raise paramiko.SSHException(last_exc or "command execution failed")


def inspect_hosts(
    hosts: List[dict],
    tags_filter: Optional[Dict[str, str]] = None,
    commands: List[str] = None,
    max_workers: int = 5,
) -> List[Dict[str, Any]]:
    """Filter hosts by tag and run inspect_single_host concurrently."""
    default_commands = DEFAULT_COMMANDS if not commands else commands

    filtered_hosts = []
    for host_config in hosts:
        if tags_filter and not all(
            host_config.get("tags", {}).get(k) == v for k, v in tags_filter.items()
        ):
            logger.info(
                "Skipping %s (tag mismatch)",
                host_config.get("name", host_config["host"]),
            )
            continue
        filtered_hosts.append(host_config)

    if not filtered_hosts:
        logger.warning("无匹配主机，巡检中止")
        return []

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(inspect_single_host, host_config, default_commands): host_config
            for host_config in filtered_hosts
        }
        for future in as_completed(future_map):
            try:
                results.append(future.result())
            except Exception as exc:
                logger.exception("巡检任务异常: %s", exc)

    return results


def collect_alerts(command: str, output: str, host_config: Dict[str, Any]) -> List[str]:
    """Dispatch to对应解析器, 聚合磁盘/内存/负载告警."""
    alerts = []
    if command == "df -h":
        alert = parse_disk_alert(output, threshold=host_config.get("disk_threshold", DEFAULT_DISK_THRESHOLD))
        if alert:
            alerts.append(alert)
            logger.warning("WARNING: %s", alert)
    if command in {"free -m", "free -h"}:
        alert = parse_memory_alert(output, threshold=host_config.get("memory_threshold", DEFAULT_MEM_THRESHOLD))
        if alert:
            alerts.append(alert)
            logger.warning("WARNING: %s", alert)
    if command == "uptime":
        alert = parse_load_alert(
            output,
            cpu_cores=host_config.get("cpu_cores", 1),
            multiplier=host_config.get("load_multiplier", LOAD_MULTIPLIER),
        )
        if alert:
            alerts.append(alert)
            logger.warning("WARNING: %s", alert)
    return alerts


def parse_disk_alert(df_output: str, threshold: int = DEFAULT_DISK_THRESHOLD) -> Optional[str]:
    """Parse df -h output to detect partitions exceeding阈值."""
    lines = df_output.splitlines()
    for line in lines[1:]:
        if line.strip() and not line.startswith("tmpfs"):
            parts = line.split()
            if len(parts) >= 5:
                usage = parts[4].rstrip("%")
                if usage.isdigit() and int(usage) > threshold:
                    mount = parts[5] if len(parts) > 5 else "unknown"
                    return f"磁盘 {mount} 用率 {usage}% > {threshold}%"
    return None


def parse_memory_alert(free_output: str, threshold: int = DEFAULT_MEM_THRESHOLD) -> Optional[str]:
    """Parse free 输出, 依据 Mem: 行估算使用率."""
    for line in free_output.splitlines():
        if line.lower().startswith("mem:"):
            parts = [p for p in line.split(" ") if p]
            if len(parts) >= 3:
                try:
                    total = float(parts[1])
                    used = float(parts[2])
                    usage = (used / total) * 100 if total else 0
                except ValueError:
                    return None
                if usage > threshold:
                    return f"内存用率 {usage:.1f}% > {threshold}%"
    return None


def parse_load_alert(uptime_output: str, cpu_cores: int = 1, multiplier: float = LOAD_MULTIPLIER) -> Optional[str]:
    """Compare 1-min load average against cpu_cores*multiplier."""
    match = re.search(r"load average:\s*([0-9.]+),", uptime_output)
    if not match:
        return None
    try:
        load_1 = float(match.group(1))
    except ValueError:
        return None
    threshold = max(cpu_cores, 1) * multiplier
    if load_1 > threshold:
        return f"1 分钟负载 {load_1:.2f} 超过阈值 {threshold:.2f}"
    return None
