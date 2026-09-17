# Agent Workflow

Agent Workflow is the umbrella project for the Agent Workflow family. It is the
single entry point for an autonomous development pipeline: agents begin here,
load the registry, and consult every applicable child project before planning,
changing, reviewing, or publishing work.

This repository deliberately contains no coordinator runtime, quality engine,
guidance protocol, duplicated schemas, or copied documentation. Those contracts
remain authoritative in their child repositories. This project supplies only
the family map, routing rules, and pipeline contract that connect them.

## Family registry

The machine-readable registry is [project-manifest.yaml](project-manifest.yaml).
It currently covers:

- [Agent Workflow Coordinator](https://github.com/martin-beck/agent-workflow-coordinator): task lifecycle, claims, dependencies, durable state, and coordination authority.
- [Agent Workflow Quality](https://github.com/martin-beck/agent-workflow-quality): quality requirements, profiles, gates, adapters, and evidence contracts.
- [Agent Workflow Guidance](https://github.com/martin-beck/agent-workflow-guidance): oracle escalation, decision records, alternatives, and reusable guidance.
- [Agent Workflow TUI](https://github.com/martin-beck/agent-workflow-tui): interactive terminal rendering and revision-bound discussion, decision, and conflict-reconciliation sessions.

Each child project owns its implementation and its separate state repository.
The state repositories are listed in the manifest so an agent can locate the
durable coordination record without treating state as product source.

## Autonomous pipeline contract

For every task, an agent using this umbrella project must:

1. Read this repository's `AGENTS.md` and `project-manifest.yaml`.
2. Discover the current child-project set from the manifest and verify each
   child repository at the recorded GitHub URL and revision policy.
3. Read each applicable child's `AGENTS.md`, `README.md`, architecture and
   integration guidance, active state, and task plan before acting.
4. Route decisions to the owner: Coordinator for lifecycle and coordination,
   Quality for quality policy and evidence, and Guidance for oracle decisions.
5. Use the child project's own commands, schemas, state repository, tests, and
   publication rules to their fullest applicable extent. Do not reimplement a
   child contract in this repository.
6. Run the applicable child-owned checks and report results with their exact
   repository, revision, and evidence boundary.
7. Before adding a new `agent-workflow-*` project, check this manifest and all
   existing children for ownership overlap; add only a routing entry and link
   to the new project's authoritative contracts.

The manifest is intentionally explicit and reviewable. Future family members
become pipeline inputs by adding a registry entry; agents must not silently
ignore an entry or infer ownership from repository names alone.

## Licensing

Licensed under the MIT License. See [LICENSE](LICENSE).
