# Runbook: Identity provider (`identity-provider`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Workforce and workload identity, tokens, conditional access.

## Ownership and escalation

- Owner: `security-team` (owns identity, secrets, guardrail policy and model risk review)
- Contact: `pagerduty:security-oncall`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.99% (design target)
- RTO: 15 minutes; RPO: 0 minutes

## Dependencies

Depends on: `network-fabric` (sync)

Used by: `ai-gateway`, `cicd-pipeline`, `data-catalog`, `guardrails-service`, `human-review-inbox`, `internal-copilot`, `lakehouse`, `memory-service`, `secrets-manager`, `tool-registry`, `vector-store`, `web-assistant`

## Symptoms

- Sign-in failures across services
- Token issuance slow

## First checks

1. Check the provider's status page and conditional-access changes
2. Check network-fabric DNS and connectivity

## Mitigations

- Use the documented break-glass accounts for operators
- Extend token lifetimes only with security approval

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
