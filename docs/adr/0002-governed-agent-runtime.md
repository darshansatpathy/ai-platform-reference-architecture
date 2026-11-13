# ADR 0002: Agents run in one governed runtime, not in each product

## Status

Accepted

## Context

If every product embeds its own agent loop, every product reinvents retries, limits, tool
validation and audit, and each gets some of them wrong. A runaway loop in one product spends the
whole company's quota.

## Decision

Agents execute in a shared `agent-runtime` that enforces hard budgets (turns, tool calls,
tokens, cost, time, repeated calls), validates tool input, records an audit trail and reports
non-normal endings as results. Products supply prompts, tools and policy; they do not own the
loop. [claude-agent-reference](https://github.com/darshansatpathy/claude-agent-reference) is a
reference implementation of this runtime.

## Consequences

- One place to fix a loop bug and one place to prove limits hold (its harness evals).
- The runtime is a tier 1 dependency of every assistant, with its own availability ceiling
  (see the register).
- Products with unusual needs must justify leaving the shared runtime.
