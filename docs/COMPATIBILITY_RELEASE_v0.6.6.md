# Agent Workflow family compatibility release v0.6.6

This umbrella snapshot consumes the UI release that makes the SSH rendezvous
endpoint the first Android bootstrap path. When configured, the service's TLS
listener is reverse-forwarded before QR creation and the allocated HTTPS
endpoint is encoded in the QR.

| project | release | commit |
|---|---|---|
| agent-workflow-ui | v0.6.6 | `84652fe8dac5604a8e53bbc0c19f573948a9697c` |
| agent-workflow-guidance | v0.1.3 | `79ae41edd7879d72f014a77499caf397a4cd46d7` |

The rendezvous SSH server must permit the configured public reverse-forward
bind and the TLS certificate must be valid for the hostname placed in the QR.
