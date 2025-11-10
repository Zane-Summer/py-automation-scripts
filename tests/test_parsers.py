import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from checker.inspector import (
    parse_disk_alert,
    parse_memory_alert,
    parse_load_alert,
)


def test_parse_disk_alert_detects_high_usage():
    df_output = (
        "Filesystem      Size  Used Avail Use% Mounted on\n"
        "/dev/sda1        50G   45G    5G  90% /\n"
    )
    alert = parse_disk_alert(df_output, threshold=80)
    assert "90%" in alert


def test_parse_memory_alert_detects_threshold():
    free_output = "              total        used        free      shared  buff/cache   available\nMem:           1000         900         100          10           50          80\nSwap:          2048         100        1948\n"
    alert = parse_memory_alert(free_output, threshold=80)
    assert "内存用率" in alert


def test_parse_load_alert_uses_cpu_multiplier():
    uptime_output = " 21:23:26 up 11 days,  load average: 4.00, 3.00, 2.00"
    alert = parse_load_alert(uptime_output, cpu_cores=2, multiplier=1.5)
    assert "负载" in alert
