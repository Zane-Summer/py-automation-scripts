# test_v21.py - V2.1 单元测试
from main import parse_disk_alert  # 导入你的函数（假设 main.py 有）

# 模拟 df -h 输出（>80% 案例）
df_high = """Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        40G   35G   5G   88% /
tmpfs           1.9G     0  1.9G    0% /dev/shm"""

alert = parse_disk_alert(df_high)
print(f"高用率测试: {alert}")  # 期望: "磁盘 / 用率 88% > 80%"

# 模拟 <80% 案例
df_low = """Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        40G   20G   20G   50% /"""
alert_low = parse_disk_alert(df_low)
print(f"低用率测试: {alert_low}")  # 期望: None