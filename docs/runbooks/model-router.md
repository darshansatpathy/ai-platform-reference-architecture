# Runbook: Model router (`model-router`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Chooses model and provider by task, cost and health. Embedded in the gateway as a library.

## Ownership and escalation

- Owner: `platform-team` (owns the AI gateway, routing, registries and agent runtime)
- Contact: `pagerduty:ai-platform-primary`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.9% (design target)
- RTO: 30 minutes; RPO: 5 minutes

## Dependencies

Depends on: `prompt-registry` (library)

Used by: `ai-gateway`

## Symptoms

- Requests routed to an unexpected model
- Cost per request jumps

## First checks

1. Check the active routing rules version in the prompt-registry
2. Compare router decisions with the last known good version

## Mitigations

- Roll back the routing rules
- Pin traffic to a single model while investigating

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
