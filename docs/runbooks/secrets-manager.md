# Runbook: Secrets manager (`secrets-manager`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Secrets, keys and certificates with rotation.

## Ownership and escalation

- Owner: `security-team` (owns identity, secrets, guardrail policy and model risk review)
- Contact: `pagerduty:security-oncall`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.99% (design target)
- RTO: 15 minutes; RPO: 0 minutes

## Dependencies

Depends on: `identity-provider` (sync)

Used by: `tool-registry`

## Symptoms

- Services cannot read secrets
- Rotation job failures

## First checks

1. Check identity-provider and access policies
2. Check the audit log for denied reads

## Mitigations

- Services use cached secrets until TTL; fix before they expire
- Roll back the access-policy change

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
