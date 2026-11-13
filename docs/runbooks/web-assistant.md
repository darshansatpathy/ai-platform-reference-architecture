# Runbook: Customer web assistant (`web-assistant`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Customer-facing chat assistant embedded in the web and mobile apps.

## Ownership and escalation

- Owner: `product-teams` (build the assistants and pipelines that use the platform)
- Contact: `pagerduty:product-oncall`
- Tier: 1
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99% (design target)
- RTO: 60 minutes; RPO: 15 minutes

## Dependencies

Depends on: `agent-runtime` (sync), `identity-provider` (sync), `observability-stack` (async)

Used by: nothing (entry point)

## Symptoms

- Chat requests time out or return generic errors
- Rising abandonment on the assistant widget

## First checks

1. Is `agent-runtime` healthy? Check its dashboard first
2. Did a prompt or routing change ship in the last hour?
3. Are token budgets being hit for a tenant or for everyone?

## Mitigations

- Switch the widget to the static help page (feature flag)
- Roll back the last prompt-registry promotion
- Reduce concurrency per user while capacity recovers

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
