import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.validator import validate_hosts_config


def test_validate_hosts_config_passes_with_minimum_fields():
    hosts = [
        {
            "host": "127.0.0.1",
            "username": "root",
            "password": "secret",
        }
    ]
    validate_hosts_config(hosts)  # 不应抛异常


def test_validate_hosts_config_requires_username():
    hosts = [{"host": "127.0.0.1"}]
    with pytest.raises(ValueError):
        validate_hosts_config(hosts)
