# Runbook: Private model endpoint (`private-model-endpoint`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Self-hosted model for restricted data that may not leave the company.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.5% (design target)
- RTO: 120 minutes; RPO: 15 minutes

## Dependencies

Depends on: `network-fabric` (sync), `observability-stack` (async)

Used by: `ai-gateway`

## Symptoms

- Restricted-data requests fail
- GPU or node saturation

## First checks

1. Check node health and queue depth
2. Check network-fabric connectivity to the gateway

## Mitigations

- Scale out replicas
- Do NOT route restricted data to an external provider; return a clear error instead

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
