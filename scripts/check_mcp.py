"""Verify the provider contract by introspection only; never call business tools."""

import argparse
import asyncio
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_tools(tools, contract: dict) -> None:
    by_name = {tool.name: tool for tool in tools}
    expected = set(contract["business_tools"]) | set(contract["helper_tools"])
    if set(by_name) != expected:
        raise ValueError("MCP 工具范围与客户合同不一致，请检查版本、客户模式及服务过滤配置。")
    properties = by_name["link_describe_api"].input_schema.get("properties", {})
    sections = properties.get("section", {}).get("enum", [])
    if (
        not set(contract["describe_api_sections"]).issubset(sections)
        or "field_path" not in properties
    ):
        raise ValueError("MCP 缺少大型模型的分段查询能力，请升级兼容版本。")


async def check_provider(command: str, args: list[str], contract: dict) -> dict:
    from mcp import Client, StdioServerParameters

    # Introspection does not need credentials. Override them to avoid reading a real
    # account's secrets from the provider's local dotenv file during this check.
    parameters = StdioServerParameters(
        command=command,
        args=args,
        env={
            **os.environ,
            "LINK_PROFILE": "customer",
            "LINK_TOKEN": "",
            "LINK_CUSTOMER_KEY": "",
            "LINK_SERVICES": "",
            "LINK_READ_ONLY": "false",
            "PYTHONIOENCODING": "utf-8",
        },
    )
    async with Client(parameters, read_timeout_seconds=30) as client:
        tools = await client.list_tools()
        validate_tools(tools.tools, contract)
        status = await client.call_tool("link_list_services", {})
        state = (status.structured_content or {}).get("result", {})
        if (
            status.is_error
            or state.get("profile") != "customer"
            or not state.get("customer_identity_locked")
        ):
            raise ValueError("MCP 没有启用固定客户身份的客户模式。")
        description = await client.call_tool(
            "link_describe_api",
            {
                "tool_name": "link_lms_express_order",
                "section": "summary",
            },
        )
        result = description.structured_content or {}
        if (
            description.is_error
            or result.get("truncated")
            or not result.get("result", {}).get("input_fields")
        ):
            raise ValueError("MCP 未返回可用的大型模型字段目录。")
        return {
            "verified": True,
            "profile": "customer",
            "tools": len(tools.tools),
            "business_requests_sent": 0,
            "contract_version": contract["contract_version"],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="通过只读工具发现验证 link-mcp 客户能力合同")
    parser.add_argument("--command", required=True)
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command_args = args.args[1:] if args.args[:1] == ["--"] else args.args
    contract = json.loads((ROOT / "contracts/link-mcp-customer.json").read_text(encoding="utf-8"))
    try:
        result = asyncio.run(
            asyncio.wait_for(check_provider(args.command, command_args, contract), 45)
        )
    except ImportError:
        parser.exit(2, "请先安装本项目的 mcp 额外依赖：pip install -e '.[mcp]'\n")
    except (ValueError, TimeoutError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
