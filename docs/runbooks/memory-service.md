# Runbook: Memory service (`memory-service`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Per-user and per-task memory with retention and erasure.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.8% (design target)
- RTO: 120 minutes; RPO: 15 minutes

## Dependencies

Depends on: `vector-store` (sync), `identity-provider` (sync), `observability-stack` (async)

Used by: `agent-runtime`

## Symptoms

- Agents lose context between turns
- Erasure requests not completed

## First checks

1. Check vector-store health and the fallback path
2. Check the retention and erasure job status

## Mitigations

- Run agents stateless (feature flag) while memory recovers
- Re-run the erasure job; it is idempotent

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
