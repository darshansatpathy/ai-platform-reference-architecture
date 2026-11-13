# Runbook: Guardrails service (`guardrails-service`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Input and output policy: PII redaction, injection screening, tool-call policy.

## Ownership and escalation

- Owner: `security-team` (owns identity, secrets, guardrail policy and model risk review)
- Contact: `pagerduty:security-oncall`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.95% (design target)
- RTO: 30 minutes; RPO: 5 minutes

## Dependencies

Depends on: `identity-provider` (sync), `observability-stack` (async)

Used by: `ai-gateway`

## Symptoms

- Gateway latency rises
- Spike in blocked requests or in missed detections

## First checks

1. Check policy version and recent changes
2. Sample blocked requests for false positives

## Mitigations

- Roll back the policy version
- If the service is down, the gateway fails closed: confirm that behaviour, do not bypass it

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
