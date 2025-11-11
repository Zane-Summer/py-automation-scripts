import json
from pathlib import Path
from typing import List

from pydantic import ValidationError

from .models import Settings


def _resolve_config_path(file: str) -> Path:
    path = Path(file)
    if path.is_absolute():
        return path
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    return config_dir / path


def load_settings(file: str = "hosts.json") -> Settings:
    file_path = _resolve_config_path(file)
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found...")

    with open(file_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    try:
        return Settings.model_validate(data)
    except ValidationError as exc:
        raise SystemExit(f"[CONFIG ERROR]\n{exc}") from exc


def load_hosts(file: str = "hosts.json") -> List[dict]:
    settings = load_settings(file)
    return [host.model_dump() for host in settings.hosts]
