# Adoption roadmap

A sequence that lets value arrive early without building the platform last. Each phase has exit
criteria that can be checked, and several are enforced by `archfit check` on the catalog.

| Phase | Goal | Builds | Exit criteria |
|---|---|---|---|
| 0. Foundations | A safe place to run | identity-provider, network-fabric, secrets-manager, observability-stack; the landing zone | Private connectivity and workload identity in dev and prod; telemetry flowing; tier 1 owners have pagers |
| 1. First use case | One assistant, read-only | ai-gateway (single provider), agent-runtime, guardrails-service, web-assistant or internal-copilot | Per-caller token budgets; audit trail; evaluation set with a pass threshold; runbooks for tier 1 and 2 |
| 2. Governed actions | Writes with people in the loop | tool-registry, human-review-inbox, prompt-registry, eval-service, cicd-pipeline | No write tool runs without approval; promotion requires a passing evaluation; rollback rehearsed |
| 3. Resilience and economics | Survive provider failure, know the cost | secondary-model-provider, model-router, cost-management, caching | Failover exercised in staging; cost per request reported by use case; availability register matches measurements |
| 4. Knowledge and memory | Use enterprise data safely | vector-store, ingestion-pipeline, lakehouse, data-catalog, memory-service | Classification enforced end to end; row-level security tested; erasure works |
| 5. Scale and self-service | Teams onboard without the platform team | workflow-orchestrator, batch-pipelines, private-model-endpoint | Onboarding in days, not weeks; restricted workloads served privately; platform team's change queue shrinking |

## Sequencing rules

- **Do not build a later phase's component on an earlier phase that is not done.** The
  dependency graph says what depends on what; the roadmap follows it.
- **Evaluation arrives in phase 1, not phase 3.** A use case without a way to measure quality
  is a demo.
- **Cost reporting arrives before scale.** Unit economics at 50x volume is not a surprise if it
  was visible at 1x ([unit economics](generated/finops.md)).

## Measuring adoption

Use outcomes: use cases in production, share of model traffic through the gateway (target
100%), time to onboard, evaluation pass rate, cost per request by use case, and incidents by
tier. Avoid counting components built.
