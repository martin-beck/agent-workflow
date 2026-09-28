# Umbrella compatibility: Agent Workflow UI v0.6.7

The umbrella pins `agent-workflow-ui` v0.6.7 at commit
`da5e655cabceca35c99a48a1ff0ef17aa178b814`. This is the Android parity line:
the Android app, desktop GUI, and TUI consume the same batched decision
contract, Markdown documents/highlights, proposal actions, durable save and
reconnect events, and fail-closed HTTPS/SSH pairing policy.

The pin is checked by `tools/check_compatibility.py` and the compatibility
tests; downstream workers must consume this exact release rather than a moving
branch.
