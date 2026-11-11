import copy
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.check_mcp import validate_tools

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "contracts/link-mcp-customer.json").read_text(encoding="utf-8"))


def provider_tools():
    tools = [
        SimpleNamespace(name=name, input_schema={})
        for name in CONTRACT["business_tools"] + CONTRACT["helper_tools"]
    ]
    next(tool for tool in tools if tool.name == "link_describe_api").input_schema = {
        "properties": {
            "section": {"enum": ["all", "summary", "input", "responses"]},
            "field_path": {"type": "string"},
        },
    }
    return tools


def test_provider_contract_accepts_customer_capabilities():
    validate_tools(provider_tools(), CONTRACT)


@pytest.mark.parametrize("change", ["missing_tool", "extra_tool", "missing_schema_sections"])
def test_provider_contract_rejects_incompatible_execution_service(change):
    tools = copy.deepcopy(provider_tools())
    if change == "missing_tool":
        tools.pop(0)
    elif change == "extra_tool":
        tools.append(SimpleNamespace(name="link_lms_push_post", input_schema={}))
    else:
        next(tool for tool in tools if tool.name == "link_describe_api").input_schema = {}
    with pytest.raises(ValueError):
        validate_tools(tools, CONTRACT)


def test_build_works_from_an_unrelated_directory_without_provider_source(tmp_path):
    result = subprocess.run(
        [sys.executable, "-I", str(ROOT / "scripts/build_skill.py"), "--output-dir", str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((tmp_path / "checksums.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 2
