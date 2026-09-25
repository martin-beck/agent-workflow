# Agent Workflow family compatibility release v0.6.4

This umbrella pin selects the exact UI release that contains configurable SSH
rendezvous discovery, consented Android tunnel enrollment, and the
cross-platform qualification matrix.

| Component | Release | Immutable commit |
| --- | --- | --- |
| agent-workflow-ui | v0.6.4 | `72162d786df53a09e45736e1716288d721e0e751` |
| agent-workflow-guidance | v0.1.3 | `79ae41edd7879d72f014a77499caf397a4cd46d7` |
| agent-workflow-coordinator | v0.3.22 | `da7faa08a40513254179429c9c6d5c43e980ea48` |
| agent-workflow-quality | v0.35.0-bridge.1 | `8ec460ec99baf8061d1644a2532b5b9beb47b75b` |
| agent-workflow-runtime | v0.1.9 | `023093ee429242121baf159dfccdad371ee4c867` |

The UI rendezvous alias is deployment configuration (`--ssh-host` or
`AWUI_SSH_HOST`); no test host is embedded in this manifest.
