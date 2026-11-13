# Runbook: Workflow orchestrator (`workflow-orchestrator`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Durable multi-step workflows and batch fan-out with retries and human steps.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99% (design target)
- RTO: 240 minutes; RPO: 60 minutes

## Dependencies

Depends on: `agent-runtime` (sync), `human-review-inbox` (async), `observability-stack` (async)

Used by: `batch-pipelines`

## Symptoms

- Workflows stuck in a waiting state
- Duplicate steps after a restart

## First checks

1. Check the human-review queue depth
2. Inspect the stuck run's event history

## Mitigations

- Resume or cancel individual runs; steps are idempotent
- Scale workers if the queue is growing

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
