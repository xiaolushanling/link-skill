import hashlib
import json
import re
import tomllib
import zipfile
from pathlib import Path

import yaml

from scripts.build_skill import build_packages

ROOT = Path(__file__).resolve().parents[1]


def test_skill_metadata_and_tool_references():
    text = (ROOT / "skills/link-logistics-assistant/SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert match
    metadata = yaml.safe_load(match[1])
    assert metadata["name"] == "link-logistics-assistant"
    assert len(metadata["description"]) <= 1024
    referenced = set(re.findall(r"\blink_[a-z0-9_]+\b", text))
    contract = json.loads((ROOT / "contracts/link-mcp-customer.json").read_text(encoding="utf-8"))
    assert referenced == set(contract["business_tools"]) | set(contract["helper_tools"])


def test_reproducible_customer_and_doubao_source_archives(tmp_path):
    first = build_packages(tmp_path / "first")
    second = build_packages(tmp_path / "second")
    assert first == second
    source = (
        (ROOT / "skills/link-logistics-assistant/SKILL.md")
        .read_text(encoding="utf-8")
        .encode("utf-8")
    )
    assert first["skill_sha256"] == hashlib.sha256(source).hexdigest()
    for filename, checksum in first["files"].items():
        archive_path = tmp_path / "first" / filename
        assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == checksum
        with zipfile.ZipFile(archive_path) as archive:
            if "doubao-source" in filename:
                assert set(archive.namelist()) == {
                    "skill/SKILL.md",
                    "README.md",
                    "package-info.json",
                }
                assert archive.read("skill/SKILL.md") == source
                info = json.loads(archive.read("package-info.json"))
                assert info["official_submission_ready"] is False
                assert info["platform_account_validation"] == "not_performed"
            else:
                assert archive.namelist() == ["link-logistics-assistant/SKILL.md"]
                assert archive.read(archive.namelist()[0]) == source
            assert not any(
                name.endswith(".env") or name.startswith("/") or ".." in name
                for name in archive.namelist()
            )


def test_customer_configuration_uses_current_profile_and_git_entrypoint():
    config = json.loads((ROOT / "mcp-config.customer.example.json").read_text(encoding="utf-8"))
    server = config["mcpServers"]["link-mcp"]
    assert server["command"] == "uvx"
    assert server["args"] == [
        "--from",
        "git+https://github.com/xiaolushanling/link-mcp.git",
        "link-mcp",
    ]
    assert server["env"]["LINK_PROFILE"] == "customer"
    assert server["env"]["LINK_API_BASE_URL"].endswith("/api")
    assert server["env"]["LINK_CUSTOMER_KEY"] == "YOUR_CUSTOMER_KEY"


def test_downloads_match_sources_and_current_version(tmp_path):
    result = build_packages(tmp_path)
    committed = json.loads((ROOT / "downloads/checksums.json").read_text(encoding="utf-8"))
    assert result == committed
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    assert result["version"] == version
    for filename, digest in result["files"].items():
        assert hashlib.sha256((ROOT / "downloads" / filename).read_bytes()).hexdigest() == digest
