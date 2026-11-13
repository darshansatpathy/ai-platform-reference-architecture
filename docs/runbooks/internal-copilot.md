# Runbook: Employee copilot (`internal-copilot`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Employee-facing assistant for knowledge search and task automation.

## Ownership and escalation

- Owner: `product-teams` (build the assistants and pipelines that use the platform)
- Contact: `pagerduty:product-oncall`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99% (design target)
- RTO: 240 minutes; RPO: 60 minutes

## Dependencies

Depends on: `agent-runtime` (sync), `identity-provider` (sync), `observability-stack` (async)

Used by: nothing (entry point)

## Symptoms

- Employees report slow or failing answers
- Spikes in `denied` tool calls

## First checks

1. Check `agent-runtime` and `ai-gateway` status
2. Check identity-provider token issuance latency

## Mitigations

- Disable write tools for the copilot (read-only mode)
- Fail over to the secondary provider via the gateway

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
