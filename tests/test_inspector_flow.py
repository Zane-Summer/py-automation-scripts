import sys
from pathlib import Path
from typing import List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from checker import inspector


def test_inspect_hosts_filters_by_tags():
    hosts = [
        {"host": "1.2.3.4", "username": "root", "tags": {"env": "prod"}},
        {"host": "5.6.7.8", "username": "root", "tags": {"env": "dev"}},
    ]

    results = inspector.inspect_hosts(hosts, tags_filter={"env": "qa"})

    assert results == []  # no matching host should be scheduled


def test_inspect_hosts_passes_overridden_commands(monkeypatch):
    captured_commands: List[str] = []

    def fake_inspect_single_host(host_config, default_commands):
        captured_commands.extend(default_commands)
        return {"host": host_config["host"], "status": "success", "alerts": [], "duration": 0}

    monkeypatch.setattr(inspector, "inspect_single_host", fake_inspect_single_host)

    hosts = [{"host": "1.2.3.4", "username": "root"}]
    results = inspector.inspect_hosts(hosts, commands=["whoami"])

    assert captured_commands == ["whoami"]
    assert results and results[0]["status"] == "success"
