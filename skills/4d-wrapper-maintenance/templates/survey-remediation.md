# Wrapper survey and remediation worksheet

Copy only the sections needed into an authorized task artifact. Replace
placeholders with evidence; `unknown`, `not run` and `blocked` are valid
answers with reasons. This is an operational checklist, not executable 4D
code, and creates no permission to modify a consumer project.

## Scope and baseline

- [ ] Authorized repositories/checkouts and allowed reads/writes/execution:
- [ ] Excluded repositories, primary checkouts and global/shared caches:
- [ ] Repository HEAD/branch/dirty state and survey date:
- [ ] Project compatibility version; actual 4D/tool4d build (or unknown):
- [ ] OS, host/process/executable architecture; runtime version/provenance:
- [ ] Resolved dependency revisions (distinguish `latest` declarations):
- [ ] Versioned upstream CLI/docs and model metadata source:
- [ ] Existing tests and safety review (writes, downloads, builds, network):
- [ ] Baseline command, exit status, assertions, logs and tier:

## Inventory and contracts

| Surface | File:symbol:lines / revision | Incoming -> outgoing edges | Contract / consumers | Unknowns |
|---|---|---|---|---|
| Public API, inheritance/overrides | | | | |
| Local/remote resolution and downloads/cache | | | | |
| Startup/worker registry/controller/native process | | | | |
| Callbacks, receiver, arguments and owning process | | | | |
| stdout/stderr/launch error/exit/cleanup | | | | |
| Arguments and executable/cwd/environment | | | | |
| Listening/model-ready/inference/cancellation/disposal | | | | |
| Platform/architecture/runtime/model gates | | | | |

For each edge record inline versus deferred execution, mutable state,
ownership and cancellation. Compare projects in separate rows/worksheets;
do not infer equivalence from matching class names.

## Evidence ledger (repeat per finding)

```text
ID / project / revision:
Classification: confirmed defect | intentional | proposal | stale docs | candidate
Priority: P1 | P2 | other; rationale and reachability:
Location: file, symbol, line range; immutable source link if available:
Contract/version evidence and existing consumers:
Expected behavior:
Minimal safe reproduction (command or exact event schedule / inputs):
Observed behavior; evidence tier; logs/artifacts; not-yet-run steps:
Impact:
Confidence: high | medium | low; what remains unverified:
Proposed surgical fix and owning layer (what / where / how):
Compatibility implications, alternatives and migration/rollback:
Approval decision / owner / status:
Regression assertion and required validation tier:
Blockers (tools, versions, fixtures, budget or permissions):
Disposition: fix | defer | intentional | docs-only; reason:
```

## Plan and gates

- [ ] Finish read-only inventory before editing.
- [ ] Reproduce/baseline each accepted finding, or label static-only evidence.
- [ ] Rank P1/P2 by demonstrated impact, then confidence.
- [ ] Resolve callback meaning/API changes, removed features, required model
  pins, cache migration and platform restrictions before implementation.
- [ ] List authorized files and minimal patch sequence; reuse verified helpers.
- [ ] Choose deterministic doubles plus real-4D/native tests and cost limits.
- [ ] Define rollback including callbacks, cache identity and consumer docs.
- [ ] Apply one isolated patch; review full diff and directly related docs.

## Targeted test matrix

Fill expected/actual traces, exact callback counts and worker-start counts.
Mark inapplicable cases with a reason; avoid a single ambiguous "tested".

| Case / input or schedule | Required assertion | Tier / command / result / artifact |
|---|---|---|
| Valid launch then verified readiness | Correct milestone and callback arguments; one startup terminal result | |
| Launch failure / missing executable | Explicit original error; no readiness or download-after-rejection | |
| Early exit before ready; exit after ready | Correct failure versus later lifecycle event; exit detail retained | |
| Readiness failure / timeout / foreign listener | Bounded deadline; identity checked; never false ready | |
| Timeout, cancel, terminate and ready at same boundary | One winning startup result; all owned tasks cleaned | |
| Dispose, then delayed callbacks; restart, then old completion | No callbacks after disposal; no stale-generation state change | |
| Missing/null/wrong-type event or callback | No unsafe field access/invocation; explicit diagnosis per contract | |
| stdout/stderr text and configured binary chunks | Correct stream, encoding, receiver and event signature | |
| Single/multiple model, spaced/Unicode/quoted paths | Exact token order/separators and paths received by child | |
| Integer/real/zero/negative/decimal and collections | Supported numeric flags survive actual 4D coercion | |
| Boolean/null/reserved adapter arguments | No accidental adapter flags; documented forwarding preserved | |
| Empty/all-cached/uncached/mixed downloads | Exactly one start only when all required files validate | |
| Inline cache callback during iteration/construction | No double start, skipped item or uninitialized state | |
| Duplicate/out-of-order completion; failure/cancel mid-download | Deduped completion; no start on failed/cancelled attempt | |
| Existing local file; absent/corrupt/incompatible file | Local path uses no unintended network; explicit invalid-input error | |
| Equal-size changed data; revision change; offline legacy cache | Approved integrity/migration policy, no silent data replacement | |
| Supported and unsupported OS/architecture/runtime/model | Correct approved gates, explicit errors and no partial object | |
| Real service's minimal useful request | Expected output shape/model identity; no inference claim without this tier | |

## Evidence tiers and handoff

| Tier | Result (pass/fail/not run) | Exact command/build/fixture and evidence | Limitation/blocker |
|---|---|---|---|
| Static inspection | | | Cannot establish runtime behavior |
| Mocked command construction / deterministic lifecycle doubles | | | Not actual 4D/native execution |
| Real 4D compile / LSP | | | Not worker launch or runtime semantics |
| Real 4D execution | | | State whether native process is doubled |
| Real native worker/server readiness | | | Not necessarily inference |
| End-to-end inference / useful service operation | | | State exact model, request and output assertions |

No undocumented promotion between tiers. Record failures and unavailable
tools, not just successes.

| Project / checkout / revision | Contract differences | Approved patch / changed files | Validation tiers | Open decisions / rollout owner | Rollback/cache notes |
|---|---|---|---|---|---|
| Surveyed project | | | | | |
| Additional user-selected project (not yet surveyed) | unknown | none | not run | authorization/survey required | unknown |

- [ ] Deliver entry path, artifacts, findings and exact changed files.
- [ ] State explicitly what was not changed or validated.
- [ ] Leave blocked compatibility changes unapplied.
- [ ] Stop at authorized handoff; no implicit commit/push/install/mass rollout.
