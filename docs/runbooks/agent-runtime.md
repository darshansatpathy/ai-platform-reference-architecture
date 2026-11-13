# Runbook: Agent runtime (`agent-runtime`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Runs tool-using agents with budgets, approvals and audit.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.5% (design target)
- RTO: 60 minutes; RPO: 15 minutes

## Dependencies

Depends on: `ai-gateway` (sync), `tool-registry` (sync, optional), `memory-service` (sync, fallback `vector-store`), `prompt-registry` (library), `observability-stack` (async)

Used by: `internal-copilot`, `web-assistant`, `workflow-orchestrator`

## Symptoms

- Runs end with `budget:*` or `error:*` outcomes more often
- Increase in `invalid` or `error` tool outcomes

## First checks

1. Is `ai-gateway` returning 429 or 5xx? Check request ids in the audit log
2. Did a tool schema change without a registry update?
3. Run the harness evals against the deployed version

## Mitigations

- Roll back to the previous runtime version
- Lower `max_turns` to cap cost while investigating
- Disable the failing tool in the tool registry

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
