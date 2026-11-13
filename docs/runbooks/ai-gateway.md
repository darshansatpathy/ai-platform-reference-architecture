# Runbook: AI gateway (`ai-gateway`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Single entry to every model: authentication, token budgets, routing, guardrails, logging.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.9% (design target)
- RTO: 30 minutes; RPO: 5 minutes

## Dependencies

Depends on: `identity-provider` (sync), `guardrails-service` (sync), `model-router` (library), `primary-model-provider` (sync, fallback `secondary-model-provider`), `private-model-endpoint` (sync, optional), `observability-stack` (async), `cost-management` (async)

Used by: `agent-runtime`, `eval-service`

## Symptoms

- 429s or 5xx from the gateway
- Latency above target at p95
- Spend alerts firing

## First checks

1. Is one caller consuming its whole token budget? Check per-caller metrics
2. Is the primary provider degraded? Check provider status and fallback rate
3. Is the guardrails service slow? It is on the request path

## Mitigations

- Fail over to the secondary provider (routing rule, no deploy)
- Lower the offending caller's token budget
- Scale out gateway instances

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
