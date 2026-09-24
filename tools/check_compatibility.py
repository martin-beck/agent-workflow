#!/usr/bin/env python3
"""Fail-closed validation of the umbrella cross-project compatibility lock."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.yaml"
SHA = re.compile(r"^[0-9a-f]{40}$")
RELEASE = re.compile(r"^v[0-9][0-9A-Za-z.+-]*$")
PROJECTS = {"agent-workflow-ui", "agent-workflow-coordinator", "agent-workflow-guidance", "agent-workflow-quality"}


def _section(text: str) -> str:
    marker = "\ncompatibility:\n"
    if marker not in text:
        raise ValueError("manifest has no compatibility lock")
    return text.split(marker, 1)[1]


def parse_manifest(text: str) -> dict[str, Any]:
    section = _section(text)
    def scalar(key: str) -> str:
        match = re.search(rf"^  {re.escape(key)}: ([^\n]+)$", section, re.M)
        if match is None:
            raise ValueError(f"missing {key}")
        return match.group(1).strip().strip('"')
    bridge, trigger = scalar("bridge_contract_version"), scalar("guidance_trigger_schema_version")
    if bridge != "1.0":
        raise ValueError("unsupported Coordinator/TUI bridge contract")
    if trigger != "1.0":
        raise ValueError("unsupported Guidance trigger schema")
    pins: dict[str, dict[str, str]] = {}
    pattern = r"^    (?:repository: )?([^\n]+)\n    release: ([^\n]+)\n    commit: ([0-9a-f]+)$"
    for match in re.finditer(pattern, section, re.M):
        repository = match.group(1).strip()
        if repository.startswith("repository:"):
            repository = repository.removeprefix("repository:").strip()
        project = repository.removeprefix("martin-beck/")
        if project not in PROJECTS:
            continue
        if project in pins:
            raise ValueError(f"duplicate compatibility pin for {project}")
        release, commit = match.group(2).strip(), match.group(3).strip()
        if not RELEASE.fullmatch(release) or not SHA.fullmatch(commit):
            raise ValueError(f"invalid compatibility pin for {project}")
        pins[project] = {"repository": repository, "release": release, "commit": commit}
    if set(pins) != PROJECTS:
        raise ValueError(f"compatibility pins must cover exactly {sorted(PROJECTS)}")
    contracts = []
    for match in re.finditer(r"^    - repository: ([^\n]+)\n      path: ([^\n]+)\n      schema_version: \"([^\"]+)\"$", section, re.M):
        repository, path, version = match.groups()
        project = repository.removeprefix("martin-beck/")
        if project not in PROJECTS or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError(f"invalid required contract: {repository}/{path}")
        contracts.append({"project": project, "path": path, "schema_version": version})
    if not contracts:
        raise ValueError("compatibility lock has no required contracts")
    return {"bridge_contract_version": bridge, "guidance_trigger_schema_version": trigger, "pins": pins, "contracts": contracts}


def _run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def _remote_probe(pin: dict[str, str], contracts: list[dict[str, str]]) -> dict[str, Any]:
    repository, release, commit = pin["repository"], pin["release"], pin["commit"]
    url = f"https://github.com/{repository}.git"
    output = _run("git", "ls-remote", "--refs", url, f"refs/tags/{release}")
    refs = {ref: sha for line in output.splitlines() if "\t" in line for sha, ref in [line.split("\t", 1)]}
    tag_sha = refs.get(f"refs/tags/{release}")
    if tag_sha != commit:
        peeled = _run("git", "ls-remote", url, f"refs/tags/{release}^{{}}")
        peeled_sha = peeled.split("\t", 1)[0] if "\t" in peeled else ""
        if peeled_sha != commit:
            raise ValueError(f"{repository}: release {release} does not resolve to pinned commit")
    results = []
    with tempfile.TemporaryDirectory(prefix="aw-compat-") as checkout:
        _run("git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", url, checkout)
        _run("git", "-C", checkout, "fetch", "--quiet", "origin", commit)
        for contract in contracts:
            raw = _run("git", "-C", checkout, "show", f"{commit}:{contract['path']}")
            try:
                document = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError(f"{repository}: contract {contract['path']} is not JSON") from error
            declared = document.get("schema_version")
            if declared is None:
                declared = document.get("properties", {}).get("schema_version", {}).get("const")
            if str(declared) != contract["schema_version"]:
                raise ValueError(f"{repository}: schema mismatch for {contract['path']}")
            results.append({"path": contract["path"], "schema_version": contract["schema_version"]})
    return {"repository": repository, "release": release, "commit": commit, "tag_verified": True, "contracts": results}


def validate(manifest: dict[str, Any], resolver: Callable[[dict[str, str], list[dict[str, str]]], dict[str, Any]] = _remote_probe) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, str]]] = {project: [] for project in PROJECTS}
    for contract in manifest["contracts"]:
        grouped[contract["project"]].append(contract)
    return {"status": "compatible", "bridge_contract_version": manifest["bridge_contract_version"], "guidance_trigger_schema_version": manifest["guidance_trigger_schema_version"], "projects": [resolver(manifest["pins"][project], grouped[project]) for project in sorted(PROJECTS)]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = validate(parse_manifest(args.manifest.read_text(encoding="utf-8")))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        report = {"status": "incompatible", "error": str(error).splitlines()[-1]}
        if args.report:
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"compatibility check failed: {report['error']}", file=sys.stderr)
        return 1
    if args.report:
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
