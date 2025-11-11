import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.models import Settings


def test_valid_settings():
    settings = Settings(
        hosts=[
            {
                "host": "1.2.3.4",
                "name": "srv",
                "username": "root",
                "port": 22,
                "commands": ["uptime"],
            }
        ],
        timeout_sec=5,
    )
    assert settings.timeout_sec == 5
    assert settings.hosts[0].port == 22
    assert settings.hosts[0].host == "1.2.3.4"


def test_invalid_port():
    with pytest.raises(ValidationError):
        Settings(
            hosts=[
                {
                    "host": "invalid",
                    "username": "root",
                    "port": 70000,
                }
            ]
        )
