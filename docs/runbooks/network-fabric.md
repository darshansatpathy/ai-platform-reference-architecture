# Runbook: Network fabric (`network-fabric`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Private connectivity, DNS and egress control.

## Ownership and escalation

- Owner: `sre-team` (owns observability, networking and delivery pipelines)
- Contact: `pagerduty:sre-primary`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.99% (design target)
- RTO: 15 minutes; RPO: 0 minutes

## Dependencies

Depends on: nothing inside the platform

Used by: `identity-provider`, `lakehouse`, `observability-stack`, `private-model-endpoint`, `vector-store`

## Symptoms

- Private endpoints unreachable
- DNS resolution failures

## First checks

1. Check private DNS zones and links
2. Check recent route or firewall changes

## Mitigations

- Roll back the last network change
- Fail over DNS resolvers

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
