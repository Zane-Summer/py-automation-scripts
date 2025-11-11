from pathlib import Path
from typing import Any, Dict, List

from pydantic import ValidationError

from .models import Settings


def validate_hosts_config(hosts: List[Dict[str, Any]]) -> None:
    """Validate hosts configuration using the Pydantic models."""
    try:
        Settings.model_validate({"hosts": hosts})
    except ValidationError as exc:
        raise ValueError(f"配置文件校验失败: {exc}") from exc

    for host in hosts:
        key_path = host.get("key_path")
        if key_path:
            expanded = Path(key_path).expanduser()
            if not expanded.exists():
                raise FileNotFoundError(
                    f"主机 {host.get('name', host['host'])} 的 key_path 不存在: {expanded}"
                )
