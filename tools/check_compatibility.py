#!/usr/bin/env python3
"""Validate the umbrella's reviewed cross-project compatibility lock."""

from __future__ import annotations

import json
import re
import sys
import argparse
from typing import Any, Callable
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.yaml"
HEX = re.compile(r"^[0-9a-f]{40}$")
RELEASE = re.compile(r"^v[0-9][0-9A-Za-z.+-]*$")
PROJECTS = {"agent-workflow-ui", "agent-workflow-coordinator", "agent-workflow-guidance", "agent-workflow-quality"}


def _section(text: str | None = None) -> str:
    text = MANIFEST.read_text(encoding="utf-8") if text is None else text
    marker = "\ncompatibility:\n"
    if marker not in text:
        raise ValueError("manifest has no compatibility lock")
    return text.split(marker, 1)[1]


def parse_manifest(text: str) -> dict[str, Any]:
    section = _section(text)
    bridge = _value(section, "bridge_contract_version")
    trigger = _value(section, "guidance_trigger_schema_version")
    if bridge != "1.0" or trigger != "1.0":
        raise ValueError("unsupported compatibility contract")
    pins: dict[str, dict[str, str]] = {}
    pattern = r"^    (?:repository: )?([^\n]+)\n    release: ([^\n]+)\n    commit: ([0-9a-f]+)$"
    for match in re.finditer(pattern, section, re.MULTILINE):
        repository, release, commit = (item.strip() for item in match.groups())
        project = repository.removeprefix("martin-beck/")
        if project not in PROJECTS:
            continue
        if project in pins or not RELEASE.fullmatch(release) or not HEX.fullmatch(commit):
            raise ValueError(f"invalid or duplicate compatibility pin for {project}")
        pins[project] = {"repository": repository, "release": release, "commit": commit}
    if set(pins) != PROJECTS:
        raise ValueError("compatibility pins must cover all reviewed children")
    contracts = []
    for match in re.finditer(r"^    - repository: ([^\n]+)\n      path: ([^\n]+)\n      schema_version: \"([^\"]+)\"$", section, re.MULTILINE):
        repository, path, version = match.groups()
        if path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("invalid required contract path")
        contracts.append({"project": repository.removeprefix("martin-beck/"), "path": path, "schema_version": version})
    if not contracts:
        raise ValueError("compatibility lock has no required contracts")
    return {"bridge_contract_version": bridge, "guidance_trigger_schema_version": trigger, "pins": pins, "contracts": contracts}


def validate(manifest: dict[str, Any], resolver: Callable[[dict[str, str], list[dict[str, str]]], dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, str]]] = {project: [] for project in PROJECTS}
    for contract in manifest["contracts"]:
        grouped[contract["project"]].append(contract)
    return {"status": "compatible", "projects": [resolver(manifest["pins"][project], grouped[project]) for project in sorted(PROJECTS)]}


def _value(section: str, key: str) -> str:
    match = re.search(rf"^  {re.escape(key)}: ([^\n]+)$", section, re.MULTILINE)
    if match is None:
        raise ValueError(f"compatibility lock is missing {key}")
    return match.group(1).strip().strip('"')


def check() -> None:
    section = _section()
    if _value(section, "bridge_contract_version") != "1.0":
        raise ValueError("unsupported Coordinator/TUI bridge contract")
    if _value(section, "guidance_trigger_schema_version") != "1.0":
        raise ValueError("unsupported Guidance trigger schema")

    expected = {
        "agent-workflow-ui": ("v0.6.2", "3ceee11e302be267f8c0e83cfbac47345e8b8162"),
        "agent-workflow-coordinator": (
            "v0.3.22",
            "da7faa08a40513254179429c9c6d5c43e980ea48",
        ),
        "agent-workflow-guidance": (
            "v0.1.2",
            "4cc6fdebed62cfb8d2f05224d8438f2e0da6e035",
        ),
        "agent-workflow-quality": (
            "v0.35.0-bridge.1",
            "8ec460ec99baf8061d1644a2532b5b9beb47b75b",
        ),
        "agent-workflow-runtime": (
            "v0.1.9",
            "023093ee429242121baf159dfccdad371ee4c867",
        ),
    }
    for repository, (release, commit) in expected.items():
        pattern = rf"repository: martin-beck/{re.escape(repository)}\n    release: ([^\n]+)\n    commit: ([0-9a-f]+)"
        match = re.search(pattern, section)
        if match is None or (match.group(1).strip(), match.group(2).strip()) != (release, commit):
            raise ValueError(f"compatibility pin mismatch for {repository}")
        if not HEX.fullmatch(commit):
            raise ValueError(f"compatibility pin for {repository} is not a full commit")

    required = {
        "schema/human-decision-trigger.schema.json": "1.0",
        "schema/decision-request.schema.json": "0.2",
        "schema/agent-decision-routing.schema.json": "1.0",
        "schemas/coordinator-tui-bridge.schema.json": "1.0",
    }
    for path, version in required.items():
        if f"path: {path}\n      schema_version: \"{version}\"" not in section:
            raise ValueError(f"required contract pin missing or changed: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        check()
    except (OSError, ValueError) as error:
        if args.report:
            args.report.write_text(json.dumps({"status": "incompatible", "error": str(error)}) + "\n", encoding="utf-8")
        print(f"compatibility check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    if args.report:
        args.report.write_text(json.dumps({"status": "compatible"}) + "\n", encoding="utf-8")
    print("compatibility lock OK")
