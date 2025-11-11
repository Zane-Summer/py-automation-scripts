from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Host(BaseModel):
    host: str = Field(..., min_length=1, description="hostname or IP")
    name: Optional[str] = Field(default=None, min_length=1)
    username: str = Field(..., min_length=1)
    port: int = Field(default=22, ge=1, le=65535)
    password: Optional[str] = None
    key_path: Optional[str] = None
    timeout: int = Field(default=30, ge=1)
    command_timeout: int = Field(default=10, ge=1)
    commands: List[str] = Field(default_factory=list)
    tags: Dict[str, str] = Field(default_factory=dict)
    disk_threshold: Optional[int] = Field(default=None, ge=1, le=100)
    memory_threshold: Optional[int] = Field(default=None, ge=1, le=100)
    load_multiplier: Optional[float] = Field(default=None, gt=0)
    cpu_cores: Optional[int] = Field(default=None, ge=1)
    retries: Optional[int] = Field(default=None, ge=1)

    @field_validator("commands")
    @classmethod
    def strip_empty_commands(cls, value: List[str]) -> List[str]:
        return [cmd for cmd in value if cmd]

    @field_validator("key_path")
    @classmethod
    def ensure_key_path_exists(cls, value: Optional[str]) -> Optional[str]:
        if value:
            expanded = Path(value).expanduser()
            if not expanded.exists():
                raise ValueError(f"key_path 不存在: {expanded}")
        return value


class Settings(BaseModel):
    hosts: List[Host] = Field(..., min_length=1)
    timeout_sec: int = Field(default=10, ge=1)
