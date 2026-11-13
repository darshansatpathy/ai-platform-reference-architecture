# ADR 0005: Prompts, routing rules and policies are versioned config promoted through evaluation gates

## Status

Accepted

## Context

In an AI system the behaviour changes when a prompt, a routing rule, a policy or a model
version changes, not only when code does. Editing those in a console is a deployment with no
review, no test and no rollback.

## Decision

Prompts, tool descriptions, routing rules and guardrail policies live in `prompt-registry` as
versioned artifacts. They change by pull request and are promoted dev to staging to production
by `cicd-pipeline`, which requires a passing run from `eval-service` (regression, safety and
quality sets) and records the approver. Model changes follow the same path. Rollback is
re-promoting the previous version.

## Consequences

- Behavioural change is reviewable and reversible. The prompt registry is tier 1 because every
  request reads from it, so services cache the last good version.
- Evaluation sets are a maintained asset with an owner (`ml-quality-team`).
- The gate adds minutes to a change. An emergency path exists, requires a named approver and is
  reviewed after use.
