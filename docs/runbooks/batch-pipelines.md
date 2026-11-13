# Runbook: Batch AI pipelines (`batch-pipelines`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Scheduled classification, summarisation and enrichment jobs.

## Ownership and escalation

- Owner: `product-teams` (build the assistants and pipelines that use the platform)
- Contact: `pagerduty:product-oncall`
- Tier: 3
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 98% (design target)
- RTO: 1440 minutes; RPO: 240 minutes

## Dependencies

Depends on: `workflow-orchestrator` (sync), `lakehouse` (sync), `observability-stack` (async)

Used by: nothing (entry point)

## Symptoms

- Nightly jobs not finished by the morning
- Growing queue of unprocessed items

## First checks

1. Look at `workflow-orchestrator` run history for the failing step
2. Check gateway token budgets for the batch tenant

## Mitigations

- Re-run failed items; the pipeline is idempotent per item
- Lower batch concurrency so interactive traffic is not starved

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
