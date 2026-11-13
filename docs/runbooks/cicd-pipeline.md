# Runbook: Delivery pipeline (`cicd-pipeline`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Builds, evaluates and promotes services, prompts and infrastructure.

## Ownership and escalation

- Owner: `sre-team` (owns observability, networking and delivery pipelines)
- Contact: `pagerduty:sre-primary`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.5% (design target)
- RTO: 240 minutes; RPO: 60 minutes

## Dependencies

Depends on: `identity-provider` (sync), `eval-service` (async)

Used by: `prompt-registry`

## Symptoms

- Promotions blocked
- Builds fail across repositories

## First checks

1. Check runner availability and identity federation
2. Check the evaluation gate result

## Mitigations

- Re-run on healthy runners
- Use the documented emergency change path with a recorded approver

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
