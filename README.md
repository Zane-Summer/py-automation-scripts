# Py Automation Scripts

**Python 自动化巡检工具**  
支持 SSH 批量检查云服务器（如华为云 ECS），生成 JSON 报告 + 警报（如磁盘使用率 >80%）。

---

## ✨ 功能

- **SSH 密钥/密码登录**：支持 RSA / Ed25519，自动解析 `~/.ssh/config`  
- **并发巡检**：使用 `ThreadPoolExecutor` 同时 SSH 多台主机，可自定义 `--max-workers`  
- **多维警报**：磁盘/内存/1 分钟负载阈值检测，告警写入日志与报告  
- **配置校验**：启动前用 `jsonschema` 验证 `hosts.json`，提前发现缺失字段/密钥不存在  
- **结构化日志**：`logging` + `RotatingFileHandler` 输出到终端 & `logs/app.log`，支持 `--log-level`  
- **报告增强**：JSON 报告包含成功/失败/告警计数 & 平均/最长耗时，保留“未来 HTML 渲染”入口  

---

## ⚙️ 安装

### 1. 克隆仓库

```bash
git clone https://github.com/Zane-Summer/py-automation-scripts.git
cd py-automation-scripts
```

### 2. 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

---

## 🧩 配置 `hosts.json`

路径：`config/hosts.json`

```json
{
  "hosts": [
    {
      "host": "124.70.88.117",
      "name": "hhw",
      "username": "root",
      "port": 22,
      "key_path": "~/.ssh/id_rsa",
      "commands": ["uptime", "df -h"],
      "tags": {"env": "prod"}
    }
  ]
}
```

---

## 🚀 使用

### 基本运行

```bash
python main.py
```

**输出示例：**

```
2025-11-10 05:23:24 | INFO | __main__ | Starting batch inspection...
2025-11-10 05:23:25 | INFO | checker.ssh_client | Connected to 124.70.88.117:22
2025-11-10 05:23:25 | WARNING | checker.inspector | WARNING: 磁盘 / 用率 85% > 80%
2025-11-10 05:23:26 | INFO | checker.inspector | → hhw: success (1.231s)
2025-11-10 05:23:26 | INFO | reporter.reporter | -----报告生成成功: reports/report_20251110_052326.json-----
```

### CLI 示例

```bash
python main.py \
  --hosts custom_hosts.json \
  --commands uptime "free -m" \
  --tags env=prod \
  --max-workers 10 \
  --log-level DEBUG
```

---

## 🗂️ 项目结构

```
py-automation-scripts/
├── config/
│   ├── hosts.json          # 主机配置
│   └── validator.py        # jsonschema 校验
├── checker/
│   ├── __init__.py
│   ├── ssh_client.py       # SSH 连接 + 命令执行
│   ├── inspector.py        # 并行巡检 + 告警
│   └── reporter.py         # 报告生成
├── main.py                 # 入口 + CLI + 日志初始化
├── reports/                # 生成报告
├── logs/                   # 轮转日志
├── tests/                  # pytest
└── README.md
```

---

## 🔧 扩展功能

- **加命令**：在 `hosts.json` 的 `"commands"` 列表中添加命令即可  
- **阈值自定义**：每台主机可配置 `memory_threshold` / `disk_threshold` / `load_multiplier`  
- **日志/告警**：通过 `--log-level` 切换输出级别，或解析 `logs/app.log` 定位问题  
- **测试**：运行 `pytest -q`，覆盖配置校验 & 告警解析  

---

## 🤝 贡献

欢迎 Issue 或 Pull Request！

1. Fork 本仓库  
2. 创建特性分支  
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. 提交修改  
   ```bash
   git commit -m "Add amazing feature"
   ```
4. 推送到分支  
   ```bash
   git push origin feature/amazing-feature
   ```
5. 提交 Pull Request  

---

## 📜 License

本项目基于 **MIT License** 开源。  
详情见 [LICENSE](LICENSE) 文件。

---

**Zane-Summer | [GitHub](https://github.com/Zane-Summer) | Email**
