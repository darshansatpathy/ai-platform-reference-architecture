# ADR 0007: Non-interactive work is asynchronous, durable and idempotent

## Status

Accepted

## Context

Batch enrichment, ingestion and long multi-step workflows share the platform with interactive
assistants. Run synchronously, they compete for the same capacity and fail in the same way.

## Decision

Non-interactive work runs through `workflow-orchestrator` and `batch-pipelines` with durable
state, retries and idempotent steps, using provider batch interfaces where available. Human
steps are asynchronous waits, not blocked threads. Their traffic uses separate token budgets at
the gateway so it cannot starve interactive callers.

## Consequences

- Lower tiers and looser recovery targets for batch components (tier 2 and 3), which the
  fitness functions allow because nothing tier 1 hard-depends on them.
- Every step must tolerate being run twice.
- Results arrive later and out of order; consumers match on identifiers.
