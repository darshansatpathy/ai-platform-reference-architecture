# Runbook: Data catalog and lineage (`data-catalog`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Classification, ownership and lineage for every dataset.

## Ownership and escalation

- Owner: `data-platform-team` (owns data stores, ingestion and the catalog)
- Contact: `pagerduty:data-platform-primary`
- Tier: 3
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.5% (design target)
- RTO: 1440 minutes; RPO: 240 minutes

## Dependencies

Depends on: `identity-provider` (sync)

Used by: `ingestion-pipeline`, `lakehouse`

## Symptoms

- New datasets lack classification
- Lineage missing

## First checks

1. Check the catalog sync job

## Mitigations

- Re-run the sync
- Block publishing of unclassified datasets until it recovers

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
