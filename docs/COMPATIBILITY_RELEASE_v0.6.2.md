# Agent Workflow family compatibility release v0.6.2

This compatibility checkpoint selects immutable releases and source commits
for the four public family contracts. The lock in `project-manifest.yaml` and
the report produced by `tools/check_compatibility.py` must agree before this
umbrella release is consumed.

| Project | Release | Immutable commit | Qualification boundary |
| --- | --- | --- | --- |
| agent-workflow-ui | v0.6.2 | `3ceee11e302be267f8c0e83cfbac47345e8b8162` | Linux POSIX TUI and Windows native x64; ARM64 unqualified |
| agent-workflow-coordinator | v0.3.22 | `da7faa08a40513254179429c9c6d5c43e980ea48` | Revision, event, and durable-state contract only |
| agent-workflow-guidance | v0.1.2 | `4cc6fdebed62cfb8d2f05224d8438f2e0da6e035` | Trigger, request, and routing schemas |
| agent-workflow-quality | v0.35.0-bridge.1 | `8ec460ec99baf8061d1644a2532b5b9beb47b75b` | Evidence and gate contract; not a runtime qualification claim |

## Release gate

Run the probe from a clean checkout and retain its JSON output with the
release review:

```text
python3 tools/check_compatibility.py --report compatibility-report.json
python3 tests/test_compatibility.py -v
```

The probe verifies that every release tag resolves to the pinned commit and
that each required bridge schema is present at that exact commit. The UI
qualification additionally passed hosted Windows native-x64 and Linux
scenario/replay checks. Cross-platform bootstrap evidence covers the tested
Windows/POSIX paths, but does not certify an arbitrary external SSH host,
display server, credential, or unenabled native ARM64 runner.
