# 链路物流助手 Skill

面向链路物流客户，在支持 Skill 和业务工具的 AI 客户端中，通过自然语言查价、下单、查询运单与轨迹、获取标签文件、查询余额和维护订单。

本仓库维护客户业务工作流、安装包、使用指南和平台适配材料。[link-mcp](https://github.com/xiaolushanling/link-mcp) 另行维护真实业务接口的执行服务。

## 客户开始使用

1. 下载 [客户 Skill v0.2.0](downloads/link-logistics-assistant-v0.2.0.zip)，导入支持自定义 Skill 的客户端。
2. 根据 [客户使用指南](docs/customer-guide.md) 配置自己的链路连接器与凭证。
3. 启用「链路物流助手」，尝试“帮我比较发美国的渠道”或“查询这票的轨迹”。

Skill 文件本身不包含凭证，也不会自动建立业务连接。完整业务能力依赖支持 `customer` 模式及分段文档查询的 link-mcp 0.2.0 或更高兼容版本。若远端尚未发布该 MCP 版本，请使用 [客户本地连接配置](mcp-config.customer.local.example.json) 指向已安装的本地 MCP；不要把旧 Git 版本当作本地新代码。

## 交付内容

| 内容 | 位置 |
| --- | --- |
| 客户主 Skill | [skills/link-logistics-assistant/SKILL.md](skills/link-logistics-assistant/SKILL.md) |
| 客户 ZIP | [downloads/link-logistics-assistant-v0.2.0.zip](downloads/link-logistics-assistant-v0.2.0.zip) |
| 豆包工作流适配源包 | [downloads/link-logistics-assistant-doubao-source-v0.2.0.zip](downloads/link-logistics-assistant-doubao-source-v0.2.0.zip) |
| 文件校验摘要 | [downloads/checksums.json](downloads/checksums.json) |
| 客户使用指南 | [docs/customer-guide.md](docs/customer-guide.md) |
| 23 个客户对话验收场景 | [docs/customer-acceptance.md](docs/customer-acceptance.md) |
| 豆包适配范围 | [platforms/doubao/README.md](platforms/doubao/README.md) |

标准 ZIP 只有一份完整 `SKILL.md`。豆包源包提供单文件业务工作流与适配说明，尚未经过真实豆包账号联调或官方上架，不是完整应用插件提审包。

## Git 使用

可以克隆仓库后，按客户端支持的方式导入 `skills/link-logistics-assistant`：

```shell
git clone https://github.com/xiaolushanling/link-skill.git
```

更新时拉取仓库，重新导入所需版本的 ZIP 或 Skill 目录。不同客户端的安装目录、技能入口及工具支持不同，以该客户端说明和实际验证为准。

## 维护与验证

客户导入 ZIP 无需安装本项目的 Python 开发依赖。维护者重新打包或运行测试时，需要 Python 3.11+：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,mcp]"
.\.venv\Scripts\python.exe scripts/build_skill.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

打包仅使用本仓库源码和 `contracts/link-mcp-customer.json`，不要求旁边存在 link-mcp 目录，也不会读取 `.env` 或联网调用业务接口。两种 ZIP 共用一份源 Skill，构建结果可重复。

工具合同记录兼容的 22 个客户业务工具、3 个文档工具和必要能力。更新 Skill 或 MCP 接口后，可显式连接 MCP 验证合同：

```powershell
.\.venv\Scripts\python.exe scripts/check_mcp.py --command ./link-mcp/.venv/Scripts/python.exe -- .//link-mcp/server.py
```

将示例路径改成实际 MCP 安装位置。检查只发现工具、读取连接状态和接口说明，不发送业务请求；会话中不需要提供真实凭证。这个检查不等于真实客户业务或目标 AI 客户端验收。
