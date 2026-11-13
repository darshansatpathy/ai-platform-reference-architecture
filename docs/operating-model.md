# Operating model

Who does what, how change is classified, and how a team gets onto the platform. Team names
match the catalog; the contacts there are placeholders.

## Responsibilities (RACI)

R = does the work, A = accountable, C = consulted, I = informed.

| Activity | platform-team | security-team | data-platform-team | ml-quality-team | product-teams | finops-team | vendor-management |
|---|---|---|---|---|---|---|---|
| Run the gateway, runtime and registries | A/R | C | I | I | I | I | I |
| Set guardrail and approval policy | R | A | I | C | C | I | I |
| Classify data and clear components | C | A | R | I | C | I | I |
| Maintain evaluation sets and gates | C | C | C | A/R | R | I | I |
| Build assistants and pipelines | C | C | C | C | A/R | I | I |
| Choose and contract model providers | C | C | I | C | I | C | A/R |
| Own budgets and unit economics | C | I | I | I | R | A | C |
| Respond to a tier 1 incident | A/R | R | R | I | R | I | C |
| Approve a change to the catalog | R | C | C | C | C | I | I |

## Change classes

| Class | Examples | Path |
|---|---|---|
| Standard | New prompt version, routing weights, new tool with read-only access | Pull request, automated evaluation gate, auto-promote |
| Normal | New component, new data flow, new write tool, new provider | Pull request to the catalog, `archfit check` green, security and data review, ADR if a principle changes |
| Emergency | Rollback, provider failover, disabling a tool | Immediate by the on-call, recorded afterwards with a named approver, reviewed within two working days |

Changing the catalog is how the architecture changes. A pull request that makes
`archfit check` fail is a pull request that breaks a stated design rule; the fix is either to
change the change or to change the rule by ADR.

## Onboarding a use case

1. Register the use case with an owner, a cost tag and a data classification.
2. Declare which tools it needs and their side-effect class. Writes need an approver.
3. Provide an evaluation set with at least a regression and a safety slice.
4. Receive a gateway identity and token budget in dev, then staging, then production.
5. Agree the tier. A use case that needs tier 1 recovery gets a runbook and a pager rotation
   before launch, not after.

## Governance cadence

- **Weekly:** platform operations review (incidents, budget burn, evaluation trends).
- **Monthly:** architecture and risk review against the [risk register](risk-register.md);
  catalog changes since last month; waivers and their expiry dates.
- **Quarterly:** provider review (quality, cost, concentration), availability register against
  measured availability, adoption roadmap.

## Waivers

A fitness function can be waived for a specific component with a reason (20 or more
characters), and the waiver **expires**. After the expiry date the build fails again, so a
temporary exception cannot quietly become permanent.
