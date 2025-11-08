# Py Automation Scripts

**Python 自动化巡检工具**  
支持 SSH 批量检查云服务器（如华为云 ECS），生成 JSON 报告 + 警报（如磁盘使用率 >80%）。

---

## ✨ 功能

- **SSH 密钥/密码登录**：支持 RSA / Ed25519，自动解析 `~/.ssh/config`  
- **批量巡检**：从 `config/hosts.json` 加载多主机，循环执行 `uptime`, `df -h` 等命令  
- **警报**：实时检测磁盘使用率，>80% 打印 `WARNING` 并在报告中标记  
- **报告**：JSON 输出到 `reports/`，包含摘要（成功/失败数）、时间戳  
- **CLI 支持**：`--hosts-file` 切换配置，`--commands` 自定义命令  

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
pip install paramiko
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
      "commands": ["uptime", "df -h"]
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
Starting batch inspection...
Connected to 124.70.88.117
WARNING: 磁盘 / 用率 85% > 80%
→ success
Report generated: reports/report_20251107_192604.json
```

### CLI 示例

```bash
python main.py --hosts-file custom_hosts.json --commands "uptime" "free -h"
```

---

## 🗂️ 项目结构

```
py-automation-scripts/
├── config/
│   └── hosts.json          # 主机配置
├── checker/
│   ├── __init__.py
│   ├── ssh_client.py       # SSH 连接
│   ├── inspector.py        # 巡检 + 警报
│   └── reporter.py         # 报告生成
├── main.py                 # 入口
├── reports/                # 生成报告
└── README.md
```

---

## 🔧 扩展功能

- **加命令**：在 `hosts.json` 的 `"commands"` 列表中添加命令即可  
- **并行巡检**：修改 `inspector.py` 使用 `concurrent.futures` 实现多线程  
- **警报扩展**：修改 `inspector.py` 增加 `parse_memory_alert()` 等函数  
- **测试**：`pytest tests/`

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
