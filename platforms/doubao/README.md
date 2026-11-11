# 豆包适配说明

面向客户的能力名称是「链路物流助手」，业务规则与标准客户 Skill 使用同一份源文件。打包脚本将它放入适配源包的 `skill/SKILL.md`，不依赖 references、scripts 或本地绝对路径。

## 客户自行启用

若客户当前的豆包工作模式提供自定义 Skill 和连接器入口，先导入标准客户 ZIP，再按该入口实际支持的协议配置链路工具。入口是否开放、认证方式和连接器传输方式须在目标账号与客户端版本中验证，不能依据文件格式推断已经可用。

仅接收远程 MCP URL 的入口不能直接使用 `uvx` stdio 配置。当前提供的客户配置首先适用于支持本地 stdio 的客户端；若由服务方提供远程连接，每位客户应使用与其身份绑定的授权服务。

## 官方应用插件渠道

依据当前豆包官方文档，该渠道需要独立完成应用身份、Manifest、可访问的远程 MCP、Skill 和平台要求的其他产物，并经过联调和审核。MCP 不会随 Skill 一起打包到云端；单文件工作流不自动获得网络或账号权限。

本仓库交付的 `link-logistics-assistant-doubao-source-v0.2.0.zip` 是工作流适配素材，**不是完整可提审应用插件**。它包含：

- `skill/SKILL.md`：与标准版一致的客户业务规则。
- `README.md`：本适配说明。
- `package-info.json`：版本、文档快照与源文件校验信息，明确尚未完成平台提审。

没有真实 AppID 和已部署的客户授权服务时，不生成伪造的 `manifest.yaml`、公网 MCP 地址或登录入口。

正式接入前需要完成：

1. 确认该应用渠道的开发者准入和真实应用身份。
2. 实现面向用户的账号绑定、按授权身份解析客户凭证、运单归属校验及令牌撤销。进程环境的一组固定凭证不构成多客户登录体系。
3. 部署符合该渠道要求的远程 MCP，增加入站认证；不能直接公开当前不带入站认证的本地 HTTP 入口。
4. 按平台规范适配工具结果：查询实体需要稳定业务 ID 和实体类型，错误需要数字 code 与 message；现有通用 MCP 的 success/result 包装不能当作已经符合官方实体协议。
5. 配置真实 Manifest，确保其中的工具、权限和结果类型与服务一致；需要卡片时再提供卡片产物。
6. 在目标账号、客户端和授权测试环境中验收查询、下单、取消、空结果、过期授权和异常恢复，然后走平台打包与审核。

以上属于官方渠道上线工作，不能仅用 Skill 格式校验代替。该适配源包不标记为“豆包已认证”“已上架”或“所有版本通用”。

官方依据：

- [Skill 开发](https://open.doubao.com/apps-plugin/docs/skill-development/overview)
- [MCP Server 协议规范](https://open.doubao.com/apps-plugin/docs/skill-development/mcp-server-protocol)
- [打包与提审](https://open.doubao.com/apps-plugin/docs/release/package-and-submit)
