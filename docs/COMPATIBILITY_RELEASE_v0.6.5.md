# Agent Workflow family compatibility release v0.6.5

This umbrella snapshot pins the UI release that initializes (or reuses) the
HTTPS service before Android pairing. Pairing therefore cannot race a service
startup, while TLS material and the public endpoint remain explicitly
operator-configured.

| project | release | commit |
|---|---|---|
| agent-workflow-ui | v0.6.5 | `b38739b85221b894c64c97b222b778cc308c5652` |
| agent-workflow-guidance | v0.1.3 | `79ae41edd7879d72f014a77499caf397a4cd46d7` |

Compatibility is checked by `tools/check_compatibility.py` and the manifest
must remain revision-bound; do not replace these pins with a moving branch.
