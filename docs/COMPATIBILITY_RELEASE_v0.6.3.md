# Agent Workflow family compatibility release v0.6.3

This compatibility checkpoint selects immutable releases and source commits
for the public family contracts. The lock in `project-manifest.yaml` and the
report produced by `tools/check_compatibility.py` must agree before this
umbrella release is consumed.

| Project | Release | Immutable commit |
| --- | --- | --- |
| agent-workflow-ui | v0.6.3 | `1c0fe3a4a1fd69a5166eeb628ad865d53122de0d` |
| agent-workflow-coordinator | v0.3.22 | `da7faa08a40513254179429c9c6d5c43e980ea48` |
| agent-workflow-guidance | v0.1.2 | `4cc6fdebed62cfb8d2f05224d8438f2e0da6e035` |
| agent-workflow-quality | v0.35.0-bridge.1 | `8ec460ec99baf8061d1644a2532b5b9beb47b75b` |

Run `python3 tools/check_compatibility.py --report compatibility-report.json`
and `python3 tests/test_compatibility.py -v` from a clean checkout. The UI
release includes the local Android runner, remote transport, scenario replay,
and hosted Windows/native-x64 qualification evidence.
