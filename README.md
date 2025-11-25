# Py Automation Scripts · Python 自动化巡检工具

**EN** · Headless SSH automation that inspects multiple Linux hosts, enforces resource thresholds, and exports structured JSON reports.  
**ZH** · 一款通过 SSH 并发巡检多台 Linux 主机的自动化脚本，支持资源阈值告警与结构化 JSON 报告。

---

## ✨ Features 功能特色

- **SSH key/password login** · 支持 RSA/Ed25519 密钥与密码登录，自动解析 `~/.ssh/config`。  
- **Parallel inspection** · 依赖 `ThreadPoolExecutor` 同时巡检多台主机，可通过 `--max-workers` 调整并发。  
- **Multi-metric alerts** · 监控磁盘、内存、1 分钟负载阈值，自动写入日志与报告。  
- **Config validation** · 启动前使用 `jsonschema` 校验 `hosts.json`，即时发现缺失字段或密钥路径错误。  
- **Structured logging** · `logging` + `RotatingFileHandler` 输出终端与 `logs/app.log`，可通过 `--log-level` 切换。  
- **Report insights** · 报告包含成功/失败/告警统计及耗时指标，预留 HTML 渲染扩展入口。

---

## ⚙️ Install 安装步骤

### 1. Clone the repo · 克隆仓库

```bash
git clone https://github.com/Zane-Summer/py-automation-scripts.git
cd py-automation-scripts
```

### 2. Create & activate venv · 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies · 安装依赖

```bash
pip install -r requirements.txt
```

---

## 🧩 Configure `hosts.json` · 配置示例

路径 Path: `config/hosts.json`

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

- **EN** · Each host can define custom commands, SSH auth, and optional tags for filtering.  
- **ZH** · 每台主机可定制命令、认证方式及标签，便于筛选与扩展。
- ✅ 配置文件开机即校验：项目使用 Pydantic 模型强约束端口、密钥路径等字段，写错字段名或格式会直接报 `[CONFIG ERROR]`，可参考 `config/hosts.example.json` 复制修改。

---

## 🚀 Usage 使用方式

### Basic run · 基本执行

```bash
python main.py
```

**EN** · The CLI loads `config/hosts.json`, launches concurrent SSH sessions, and drops the report in `reports/`.  
**ZH** · CLI 会读取默认配置并发发起 SSH，会话完成后在 `reports/` 目录生成 JSON 报告。

示例输出 Sample log:

```text
2025-11-10 05:23:24 | INFO | __main__ | Starting batch inspection...
2025-11-10 05:23:25 | INFO | checker.ssh_client | Connected to 124.70.88.117:22
2025-11-10 05:23:25 | WARNING | checker.inspector | WARNING: 磁盘 / 用率 85% > 80%
2025-11-10 05:23:26 | INFO | checker.inspector | → hhw: success (1.231s)
2025-11-10 05:23:26 | INFO | reporter.reporter | -----报告生成成功: reports/report_20251110_052326.json-----
```

### CLI example · 命令行示例

```bash
python main.py \
  --hosts custom_hosts.json \
  --commands uptime "free -m" \
  --tags env=prod \
  --max-workers 10 \
  --log-level DEBUG
```

- **EN** · Override hosts, inject ad-hoc commands, filter tags, tune concurrency, and raise verbosity.  
- **ZH** · 可替换主机清单、临时追加命令、按标签过滤、调整并发与日志级别。

## 🧪 Testing 测试

在项目根目录运行：

```bash
python -m pytest -q
```

---

## 🗂️ Project Structure 项目结构

```text
py-automation-scripts/
├── config/
│   ├── hosts.json          # hosts definition 主机定义
│   └── validator.py        # jsonschema validation 配置校验
├── checker/
│   ├── ssh_client.py       # SSH session + command execution
│   ├── inspector.py        # parallel inspection & alerts
│   └── reporter.py         # JSON report builder
├── main.py                 # CLI entrypoint + logging setup
├── reports/                # generated reports
├── logs/                   # rotating logs
├── tests/                  # pytest suite
└── README.md
```

---

## 🔧 Extend & Customize 扩展与自定义

- **Add commands** · 在 `hosts.json` 的 `"commands"` 中扩充检查指令。  
- **Per-host thresholds** · 支持 `memory_threshold` / `disk_threshold` / `load_multiplier` 定制。  
- **Logging & alerts** · 借助 `--log-level` 调整输出，或直接分析 `logs/app.log`。  
- **Testing** · 运行 `pytest -q` 快速验证配置校验与告警逻辑。

---

## 🤝 Contribute 贡献方式

1. **Fork** · Fork 本仓库  
2. **Branch** · `git checkout -b feature/amazing-feature`  
3. **Commit** · `git commit -m "Add amazing feature"`  
4. **Push** · `git push origin feature/amazing-feature`  
5. **PR** · 提交 Pull Request，分享你的改进。

Issues & PRs are always welcome! 欢迎通过 Issue/PR 交流想法。

---

## 📜 License 许可协议

Released under the **MIT License**. See `LICENSE` for details.  
本项目基于 **MIT License** 开源，详情见 `LICENSE`。

---

**Zane Summer | [GitHub](https://github.com/Zane-Summer) | [Email](mailto:engshix@gmail.com)**
