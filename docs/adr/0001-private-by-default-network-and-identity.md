# ADR 0001: Private connectivity and workload identity are the default everywhere

## Status

Accepted

## Context

AI workloads move prompts, documents and customer data. A public endpoint plus a shared API key
turns any leaked credential into a data breach, and shared keys cannot be attributed to a
caller. Each team solving this separately produces a different answer each time.

## Decision

Every platform service is reachable only over private connectivity (`network-fabric`) and
authenticates callers with short-lived workload or user identity (`identity-provider`). No
long-lived shared keys between platform components. Third-party model providers are reached
only from egress components, over controlled egress. The Terraform for this on Azure is in
[azure-ai-landing-zone](https://github.com/darshansatpathy/azure-ai-landing-zone).

## Consequences

- `identity-provider` and `network-fabric` are tier 1: everything else is bounded by them, and
  the availability register shows it.
- Developers need a private path to the platform (VPN, bastion or a dev environment inside the
  network).
- Onboarding a caller is an identity and a role assignment, reviewed in a pull request.
