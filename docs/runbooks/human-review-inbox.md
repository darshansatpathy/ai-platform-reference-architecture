# Runbook: Human review inbox (`human-review-inbox`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Queue where people approve, correct or reject agent actions.

## Ownership and escalation

- Owner: `ml-quality-team` (owns evaluation, human review and quality gates)
- Contact: `pagerduty:ml-quality-business-hours`
- Tier: 2
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99.5% (design target)
- RTO: 240 minutes; RPO: 15 minutes

## Dependencies

Depends on: `identity-provider` (sync), `observability-stack` (async)

Used by: `workflow-orchestrator`

## Symptoms

- Reviews pile up
- Approvals time out

## First checks

1. Check queue depth and reviewer availability
2. Check identity-provider sign-in issues

## Mitigations

- Pull in the backup reviewer group
- Extend approval timeouts for low-risk actions only

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
