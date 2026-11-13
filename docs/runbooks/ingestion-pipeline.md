# Runbook: Document ingestion (`ingestion-pipeline`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Parses, chunks, classifies and indexes documents.

## Ownership and escalation

- Owner: `data-platform-team` (owns data stores, ingestion and the catalog)
- Contact: `pagerduty:data-platform-primary`
- Tier: 3
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99% (design target)
- RTO: 1440 minutes; RPO: 240 minutes

## Dependencies

Depends on: `lakehouse` (sync), `vector-store` (async), `data-catalog` (async), `observability-stack` (async)

Used by: nothing (entry point)

## Symptoms

- Documents missing from search
- Classification backlog

## First checks

1. Check failed-document dead-letter queue
2. Check lakehouse write access

## Mitigations

- Re-drive the dead-letter queue
- Pause ingestion of a bad source

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
