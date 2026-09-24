<!-- Copyright (C) Huawei Technologies Co., Ltd. 2026. All rights reserved. -->

# Contributor instructions

This is the umbrella and routing project for the Agent Workflow family. Keep
it small: do not copy child implementations, schemas, requirements, decision
protocols, generated state, test suites, or release procedures here.

Before changing this project, read `README.md` and `project-manifest.yaml`, then
read the `AGENTS.md`, README, architecture/integration guidance, and active
coordination state of every affected child project:

- `agent-workflow-coordinator` owns task lifecycle, claims, dependencies,
  durable coordination, and coordinator authority.
- `agent-workflow-quality` owns requirements, profiles, gates, adapters, and
  evidence policy.
- `agent-workflow-guidance` owns oracle escalation and durable decision
  guidance.
- `agent-workflow-ui` owns interactive rendering and revision-bound human
  interaction sessions.
- `agent-workflow-runtime` owns bounded agent execution, worker supervision
  and recovery, and integration across child contracts; it does not replace
  Coordinator, Quality, Guidance, or UI authority.

Use each child project's own state repository and `handoffctl`/quality/guidance
contracts. Keep this repository's manifest as links, ownership boundaries,
discovery metadata, and pipeline routing only. A new `agent-workflow-*` child
must have a distinct owner and an explicit manifest entry; reject overlap and
do not make an umbrella change a substitute for a child-project change.

Public changes must not contain credentials, private paths, prompts,
transcripts, host identifiers, or unbounded logs. Commits must include a
matching DCO `Signed-off-by` trailer and be published through a reviewed pull
request when branch policy requires it.
