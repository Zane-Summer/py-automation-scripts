# Cloud Inspector V2.0 - 云服务器自动化巡检系统

**作者：Zane Summer**  
**目标**：批量 SSH 巡检华为云 ECS，支持密钥认证、JSON 报告生成。  

## 功能
- 支持 `~/.ssh/config` 别名（如 `hhw` → IP 解析）
- 批量执行命令（`uptime`、`df -h`）
- 结构化 JSON 报告（带时间戳）
- 配置驱动（`hosts.json`）

## 技术栈
- Python 3 + Paramiko
- OOP 封装 + pathlib + JSON
- SSH 密钥认证

## 快速启动
1. 克隆仓库：`git clone git@github.com:your-username/py-automation-scripts.git`
2. 安装依赖：`pip install paramiko`
3. 配置主机：编辑 `config/hosts.json`
4. 运行：`python main.py`
   - 输出：`reports/report_YYYYMMDD_HHMMSS.json`

## 示例报告
```json
{
  "generated_at": "2025-11-02T14:30:22",
  "total_hosts": 1,
  "success": 1,
  "results": [
    {
      "host": "hhw",
      "status": "success",
      "outputs": {
        "uptime": "14:30 up 12 days...",
        "df -h": "Filesystem Size Used..."
      }
    }
  ]
}