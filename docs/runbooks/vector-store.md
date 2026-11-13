# Runbook: Vector store (`vector-store`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Embeddings and retrieval indexes with row-level security.

## Ownership and escalation

- Owner: `data-platform-team` (owns data stores, ingestion and the catalog)
- Contact: `pagerduty:data-platform-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.9% (design target)
- RTO: 120 minutes; RPO: 15 minutes

## Dependencies

Depends on: `identity-provider` (sync), `network-fabric` (sync), `observability-stack` (async)

Used by: `agent-runtime`, `ingestion-pipeline`, `memory-service`

## Symptoms

- Retrieval is slow or returns nothing
- Index build fails

## First checks

1. Check index health and replica status
2. Check row-level security policy changes

## Mitigations

- Fail reads over to a replica
- Rebuild the index from the lakehouse

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
