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
- [ ] Prerequisite release/source, exact installed artifact/checksum and signing-byte scope:
- [ ] Owner-approved stdout/stderr policy: suppressed by default or bounded opt-in; required lifecycle diagnostics:
- [ ] Versioned upstream CLI/docs and model metadata source:
- [ ] Existing tests and safety review (writes, downloads, builds, network):
- [ ] Baseline command, exit status, assertions, logs and tier:
- [ ] Compiler result versus engine exit; baseline warnings; compiled/interpreted mode; real/stub dependency graph:
- [ ] If publishing: exact source/version/run/attempt, downloaded asset digests, post-mutation checksum scope, container versus payload acceptance and remaining runtime gaps:

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
Owner decision: intentional resource/log policy versus missing required diagnostics:
Expected behavior:
Minimal safe reproduction (command or exact event schedule / inputs):
Observed behavior; evidence tier; logs/artifacts; not-yet-run steps:
Check kind/predicate: desired regression invariant versus observed candidate gap:
Native trigger reproduced? Facade/controller lifetime and queue-policy decision:
Impact:
Confidence: high | medium | low; what remains unverified:
Proposed surgical fix and owning layer (what / where / how):
Compatibility implications, alternatives and migration/rollback:
Approval decision / owner / status:
Regression assertion and required validation tier:
Blockers (tools, versions, fixtures, budget or permissions):
Disposition: fix | characterize | defer | intentional | docs-only; reason:
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
- [ ] Verify approved prerequisite release before consumer use; keep computation separate from consumer acceptance policy.

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
| Cancellation crosses worker boundary; cancel races final launch | Same shared token observed; both orderings serialized per contract | |
| Registry terminal cleanup races new attempt at same key | Only owning generation removed; all terminal paths release ownership | |
| Missing/null/wrong-type event or callback | No unsafe field access/invocation; explicit diagnosis per contract | |
| No error subscriber / inherited no-op / explicit subscriber | Exactly one intended diagnostic path; compatible receiver/signature | |
| Error then termination with no response | Owned command/message/context queues reconciled; complete and worker released; independent restart gets a distinct worker | |
| Synthetic error/late/duplicate event replay | Record current candidate state separately from desired recovery; no native/facade reachability claim from injection alone | |
| Synchronous native constructor throw before worker/callback exists | Separate engine-error evidence and recovery assertion; injected onError is not a substitute | |
| New batch rejected on empty idle controller | Stage until acceptance; original error and prior context/handlers preserved; safe-state guard before any actual reuse; later-command rejection remains separate | |
| Callback after method return / later mailbox turns | Actual native owner identity and bounded fixture lifetime; no invented identity or early headless-driver exit | |
| stdout/stderr text and configured binary chunks | Correct stream, encoding, receiver and event signature | |
| Intentional quiet default / sustained opt-in streams | No default verbose forwarding/buffering; approved output bound/overflow policy; lifecycle failures still explicit | |
| Single/multiple model, spaced/Unicode/quoted paths | Exact token order/separators and paths received by child | |
| Integer/real/zero/negative/decimal and collections | Supported numeric flags survive actual 4D coercion | |
| Boolean/null/reserved adapter arguments | No accidental adapter flags; documented forwarding preserved | |
| Empty/all-cached/uncached/mixed downloads | Exactly one start only when all required files validate | |
| Inline cache callback during iteration/construction | No double start, skipped item or uninitialized state | |
| Duplicate/out-of-order completion; failure/cancel mid-download | Deduped completion; no start on failed/cancelled attempt | |
| Same oid at distinct destinations; unknown or old-generation completion | Independent pending records; unknown/stale callback cannot start | |
| First cached callback fires inline before dispatch loop advances | Whole pending set already registered; no premature terminal transition | |
| Existing local file; absent/corrupt/incompatible file | Local path uses no unintended network; explicit invalid-input error | |
| Equal-size changed data; revision change; offline legacy cache | Approved integrity/migration policy, no silent data replacement | |
| Cached/fresh SHA-256 match, mismatch, hash failure, missing legacy/offline digest | Distinct verified/error/unverified status; approved startup gate; no automatic deletion/redownload unless authorized | |
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
Record compiler JSON, assertion count/result and engine exit independently.
A clean JSON report with a nonzero engine exit is not a clean build/runtime
pass. State which real released dependencies are installed and which are
stubbed; an isolated compiled fixture is not the full production graph.
Preserve per-check kind/predicate and explicit investigation status: passing
candidate checks may intentionally confirm a gap, not prove it fixed.
Record hosted attempt allocation/execution status; a cancelled job with no
runner or executed steps establishes neither a code failure nor a pass.
For authorized publication, verify the actual uploaded/downloaded bytes and
source/run/attempt binding. Record compiler warnings and container/payload
acceptance separately from installed-consumer execution; a publisher badge
does not establish any of these. Never reuse an earlier attempt's artifact
to bypass an enforced same-attempt handoff after an allocation cancellation.

For tooling/initialization failures record exact invocation and engine build,
redacted scoped diagnostics, independent exit status and last fresh checkpoint.
Classify phase: project/component initialization, startup entered, code
assertion, native process or service operation. If using a startup-only probe,
predeclare sample count, deadline and stop-on-failure rule; retain the original
failure even if samples pass. No retry-until-green or shared-cache mutation.

| Project / checkout / revision | Contract differences | Approved patch / changed files | Validation tiers | Open decisions / rollout owner | Rollback/cache notes |
|---|---|---|---|---|---|
| Surveyed project | | | | | |
| Additional user-selected project (not yet surveyed) | unknown | none | not run | authorization/survey required | unknown |

- [ ] Deliver entry path, artifacts, findings and exact changed files.
- [ ] State explicitly what was not changed or validated.
- [ ] Leave blocked compatibility changes unapplied.
- [ ] Stop at authorized handoff; no implicit commit/push/install/mass rollout.
