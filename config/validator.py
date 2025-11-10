import jsonschema
from pathlib import Path
from typing import List, Dict, Any


HOST_SCHEMA = {
    "type": "object",
    "required": ["host", "username"],
    "properties": {
        "host": {"type": "string", "minLength": 1},
        "name": {"type": "string"},
        "username": {"type": "string", "minLength": 1},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
        "key_path": {"type": "string"},
        "password": {"type": "string"},
        "timeout": {"type": "number", "minimum": 1},
        "command_timeout": {"type": "number", "minimum": 1},
        "commands": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "tags": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "cpu_cores": {"type": "integer", "minimum": 1},
    },
    "additionalProperties": True,
}


def validate_hosts_config(hosts: List[Dict[str, Any]]) -> None:
    """Validate hosts configuration against schema and filesystem expectations."""
    schema = {"type": "array", "items": HOST_SCHEMA, "minItems": 1}
    try:
        jsonschema.validate(hosts, schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"配置文件校验失败: {exc.message}") from exc

    for host in hosts:
        key_path = host.get("key_path")
        if key_path:
            expanded = Path(key_path).expanduser()
            if not expanded.exists():
                raise FileNotFoundError(
                    f"主机 {host.get('name', host['host'])} 的 key_path 不存在: {expanded}"
                )
