"""Build explicit, credential-free customer packages from one canonical SKILL.md."""

import argparse
import hashlib
import json
import re
import tomllib
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)


def build_packages(output_dir: Path, root: Path = PROJECT_ROOT) -> dict:
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version = metadata["project"]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Package version must be a plain x.y.z version")
    name = "link-logistics-assistant"
    source = root / "skills" / name / "SKILL.md"
    if source.is_symlink():
        raise ValueError("Skill source must not be a symbolic link")
    text = source.read_text(encoding="utf-8")
    if not text.startswith(f"---\nname: {name}\ndescription: "):
        raise ValueError("Unexpected Skill frontmatter")
    contract = json.loads((root / "contracts/link-mcp-customer.json").read_text(encoding="utf-8"))
    available_tools = set(contract["business_tools"]) | set(contract["helper_tools"])
    referenced_tools = set(re.findall(r"\blink_[a-z0-9_]+\b", text))
    if referenced_tools - available_tools:
        raise ValueError("Skill refers to unavailable customer tools")
    content = text.encode("utf-8")
    source_sha = hashlib.sha256(content).hexdigest()
    package_info = {
        "name": name,
        "version": version,
        "kind": "doubao-adapter-source",
        "official_submission_ready": False,
        "platform_account_validation": "not_performed",
        "snapshot_date": contract["snapshot_date"],
        "skill_sha256": source_sha,
        "source_url": contract["source_url"],
        "minimum_mcp_version": contract["minimum_provider_version"],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    standard_name = f"{name}-v{version}.zip"
    doubao_name = f"{name}-doubao-source-v{version}.zip"
    write_zip(output_dir / standard_name, {f"{name}/SKILL.md": content})
    write_zip(
        output_dir / doubao_name,
        {
            "skill/SKILL.md": content,
            "README.md": (root / "platforms/doubao/README.md")
            .read_text(encoding="utf-8")
            .encode("utf-8"),
            "package-info.json": (
                json.dumps(package_info, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8"),
        },
    )
    manifest = {
        "version": version,
        "skill_sha256": source_sha,
        "snapshot_date": package_info["snapshot_date"],
        "files": {
            filename: hashlib.sha256((output_dir / filename).read_bytes()).hexdigest()
            for filename in (standard_name, doubao_name)
        },
    }
    (output_dir / "checksums.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="生成客户 Skill ZIP 和豆包工作流适配源包")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "downloads")
    args = parser.parse_args()
    manifest = build_packages(args.output_dir)
    print(f"Built customer Skill {manifest['version']}: " + ", ".join(manifest["files"]))


if __name__ == "__main__":
    main()
