#!/usr/bin/env python3
"""Validate the umbrella's reviewed cross-project compatibility lock."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.yaml"
HEX = re.compile(r"^[0-9a-f]{40}$")


def _section() -> str:
    text = MANIFEST.read_text(encoding="utf-8")
    marker = "\ncompatibility:\n"
    if marker not in text:
        raise ValueError("manifest has no compatibility lock")
    return text.split(marker, 1)[1]


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
        "agent-workflow-ui": ("v0.4.1", "4b66ab6d21aec40046caf24a59bf90d280a749a3"),
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
    try:
        check()
    except (OSError, ValueError) as error:
        print(f"compatibility check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print("compatibility lock OK")
