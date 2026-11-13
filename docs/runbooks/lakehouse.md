# Runbook: Lakehouse (`lakehouse`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Governed analytical storage for evaluation sets, logs and training data.

## Ownership and escalation

- Owner: `data-platform-team` (owns data stores, ingestion and the catalog)
- Contact: `pagerduty:data-platform-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.95% (design target)
- RTO: 240 minutes; RPO: 60 minutes

## Dependencies

Depends on: `identity-provider` (sync), `network-fabric` (sync), `data-catalog` (async)

Used by: `batch-pipelines`, `eval-service`, `ingestion-pipeline`

## Symptoms

- Queries fail or are slow
- Writes rejected

## First checks

1. Check storage account health and permissions
2. Check catalog availability

## Mitigations

- Restore the affected table from a snapshot
- Throttle heavy ad hoc queries

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
