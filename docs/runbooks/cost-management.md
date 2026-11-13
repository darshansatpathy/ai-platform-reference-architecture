# Runbook: Cost management (`cost-management`)

> A starting point. Adapt the commands and dashboards to your implementation; keep the structure.

## Purpose

Tag-based allocation, budgets and anomaly alerts.

## Ownership and escalation

- Owner: `finops-team` (owns cost allocation and unit economics)
- Contact: `slack:#finops`
- Tier: 3
- Escalate to the owning team's primary; if no response in 15 minutes, to the engineering manager on call.

## Recovery targets

- Availability target: 99% (design target)
- RTO: 1440 minutes; RPO: 1440 minutes

## Dependencies

Depends on: `observability-stack` (async)

Used by: `ai-gateway`

## Symptoms

- Budget alerts missing
- Untagged spend increases

## First checks

1. Check the tag-compliance report
2. Check the billing export job

## Mitigations

- Re-run the allocation job
- Escalate untagged resources to their owners

## After the incident

- Record the timeline and request ids; link the incident to this component's cost tag and tier.
- If a target was missed, update the availability register through a pull request, not by editing a dashboard.
- Add a regression test or fitness function where the failure could have been caught earlier.
