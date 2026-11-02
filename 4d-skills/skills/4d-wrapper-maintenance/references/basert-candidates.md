# BaseRT candidate evidence: a bounded worked example

This is **not a generic defect list or a patch prescription**. Surveyed
read-only on 2026-11-02: `miyako/BaseRT` primary checkout
`/Users/miyako/.copilot/repos/BaseRT`, clean HEAD
`bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f` (`20.0.3`).
Source links below are pinned to that revision. Re-survey the actual
implementation target before planning fixes: this local snapshot is older
than the later integration/fixes reported by the requesting coordinator.

No BaseRT files were edited and no BaseRT scripts, binaries, builds,
downloads or tests were run. `scripts/test-4d.py` was not present in this
primary snapshot's tracked files.

An additional authorized **read-only** inspection covered the prior isolated
worktree `/Users/miyako/.copilot/repos/copilot-worktrees/BaseRT/miyako-verbose-parakeet`,
clean HEAD `7a6fa134346fae36b37049e255dec14c5358d597`, branch
`miyako-basert-build-and-docs`. GitHub PR metadata independently confirmed
[`miyako/BaseRT#1`](https://github.com/miyako/BaseRT/pull/1) merged at
`2026-11-02T05:53:54Z`, head revision `7a6fa134346fae36b37049e255dec14c5358d597`,
merge commit `7e911a8c4cceb61f740fad4ffd1efc9718d20fc5`. This is evidence
of that PR's merge, not a claim about subsequent remote main or the stale
primary checkout. Previous runtime-test passes remain coordinator-reported,
not rerun or independently verified here.

## Version and flow inventory

All source paths below are relative to `BaseRT/Project/Sources/`.

- `BaseRT.4DProject` declares `compatibilityVersion: 2007`; actual 4D
  engine build was not measured. `dependencies.json` declares version 2100
  and `tcp`, `workers`, `event` dependencies as `latest`: resolved component
  revisions and their callback/worker behavior remain unknown.
- Public `Classes/BaseRT.4dm` extends `_interface`; constructor calls
  `workers.worker.isRunning`, then `_main` -> `Methods/main.4dm`.
  `_interface._onTCP` dispatches `Methods/start.4dm` through `CALL WORKER`.
  The external `tcp` and `workers` internals were not surveyed.
- `start` constructs `_Model` extending `_models`. `_models` resolves
  remote metadata synchronously using HTTPRequest `.wait()`, then `_Model`
  constructor calls `download` unless offline. `onDownload` eventually
  dispatches `_Model.start` through virtual method dispatch.
- `_Model.start` calls external `workers.worker.start` with `_server`.
  `_server` extends `_BaseRT` extending `_CLI`; `_BaseRT_Controller`
  extends `_CLI_Controller`. Controller `_execute` creates SystemWorker;
  `_onExecute` advances queued commands and `_onComplete` forwards exit.
- Public `_interface.terminate` calls the external worker facade.
  `Methods/onModel.4dm` handles a failed model status by reporting error
  and removing the worker registration. `DatabaseMethods/onStartup.4dm`
  demonstrates stream/download/termination consumers.
- README claims macOS/Apple Silicon, internal ARM checking, router support
  and success when serving. Native executable version, supported flags,
  readiness endpoints and model/runtime compatibility were **not** executed
  or established by this survey.

## Candidate ledger

Priorities are proposed triage, not proven production severity. Each entry
must be expanded with the [worksheet](../templates/survey-remediation.md)
when the real target revision, dependency implementations and consumers
are available. Reproductions below are **pending**, not runtime results.

### B1: launch versus readiness (P1 candidate)

- **Location/evidence:** [`Classes/_Model.4dm:84-92`](https://github.com/miyako/BaseRT/blob/bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f/BaseRT/Project/Sources/Classes/_Model.4dm#L84-L92)
  calls `onSuccess` immediately after `workers.worker.start`, with no local
  readiness check. README "How it starts up" and "Events" describe serving.
- **Classification/confidence:** confirmed local call ordering and
  documentation mismatch risk (high); premature runtime success remains a
  candidate (medium), because external `worker.start` semantics are unknown.
- **Consumers/impact:** README callers and startup's commented "loaded!"
  callback could issue requests before model availability.
- **Repro/test:** trace callback timing against a deliberately delayed
  server/model-ready signal in real 4D; include early exit, timeout,
  cancellation and late response races. Inspect resolved worker facade first.
- **Proposed fix/gate:** preserve legacy launch success if consumers depend
  on it; approve separate/opt-in bounded readiness before implementing it.
  Actual supported readiness protocol and process identity are blockers.

### B2: stream/error routing (P1 candidate)

- **Location/evidence:** [`Classes/_models.4dm:15-17`](https://github.com/miyako/BaseRT/blob/bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f/BaseRT/Project/Sources/Classes/_models.4dm#L15-L17)
  copies stream options; [`Classes/_server.4dm:7-9`](https://github.com/miyako/BaseRT/blob/bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f/BaseRT/Project/Sources/Classes/_server.4dm#L7-L9)
  binds only termination. `_BaseRT_Controller:1-28` supplies no stream/error
  forwarding; `_CLI_Controller:15-19,109-123` installs an empty default
  `_onEvent`. `_BaseRT` uses native names `onData`/`onDataError`, whereas
  options use `onStdOut`/`onStdErr`.
- **Classification/confidence:** missing local forwarding confirmed statically
  (high); end-to-end callback loss pending resolved components/version (medium).
- **Consumers/impact:** event stream subscribers lose diagnostics; launch
  failure may be hard to distinguish from slow startup.
- **Repro/test:** child emits distinct stdout/stderr and fails launch/exits
  nonzero; assert receiver, original payload, stream identity and terminal
  ordering in real 4D. Verify exact SystemWorker signatures for that build.
- **Proposed fix/gate:** explicit adaptation at the owning binding/controller
  layer, not a rename across all wrappers; preserve existing download callbacks
  and termination behavior. Event component API is an unresolved blocker.

### B3: legacy router options (P2 candidate / contract decision)

- **Location/evidence:** [`Classes/_Model.4dm:13-25`](https://github.com/miyako/BaseRT/blob/bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f/BaseRT/Project/Sources/Classes/_Model.4dm#L13-L25)
  and `Methods/start.4dm:7-12` accept `models_preset`/`models_dir`; README
  advertises router mode.
- **Classification/confidence:** router branches confirmed (high); claim
  that current BaseRT CLI rejects them is coordinator-supplied and unverified
  for the bundled binary (low until CLI version/source/help is examined).
- **Consumers/impact:** documented router users; possible invalid upstream
  flags or misleading success/model information.
- **Repro/test:** compare exact target binary grammar, then a controlled
  supported/unsupported router fixture in an authorized isolated checkout.
- **Proposed fix/gate:** retain, adapt, deprecate or explicitly reject only
  after a project decision and consumer inventory. No automatic feature removal.

### B4: size cache and mutable revision (P2 proposal)

- **Location/evidence:** [`Classes/_models.4dm:29,121-147`](https://github.com/miyako/BaseRT/blob/bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f/BaseRT/Project/Sources/Classes/_models.4dm#L121-L147)
  uses `main` for resolution and accepts an existing file by size; `oid`
  identifies completion, not a verified content hash.
- **Classification/confidence:** size-only check and mutable branch confirmed
  locally (high); corruption/reproducibility impact not reproduced (medium).
- **Consumers/impact:** existing online/offline caches and unpinned references;
  same-size wrong content can be accepted by this check.
- **Repro/test:** same-size changed bytes, changed revision, interrupted
  download and offline legacy-cache fixtures; assert the approved policy.
- **Proposed fix/gate:** evaluate immutable revision/digest verification with
  actual provider metadata, cache migration and verification cost. Mandatory
  pins, cache invalidation or redownload are decisions, not universal fixes.

### B5: platform and architecture behavior (P2 candidate)

- **Location/evidence:** [`Classes/_CLI.4dm:9-17,153-157`](https://github.com/miyako/BaseRT/blob/bc6f7ee5ada5f80ed4b4dcf2cd6e9cb4b316c25f/BaseRT/Project/Sources/Classes/_CLI.4dm#L9-L17)
  returns during Windows construction; `_isArm` has no call site in the
  surveyed project source. README says Windows unsupported and ARM checked.
- **Classification/confidence:** return/unused helper/documentation discrepancy
  confirmed statically (high); native runtime support matrix unknown.
- **Consumers/impact:** unsupported callers may obtain partial objects or
  delayed errors; supported architecture/translation callers could be
  wrongly rejected by a naive new gate.
- **Repro/test:** real supported host plus controlled unsupported-platform/
  architecture doubles, then relevant available native variants; assert
  explicit error before download/launch and no partial initialization.
- **Proposed fix/gate:** approve runtime-specific support policy and failure
  channel before adding fail-fast checks. No generic ARM-only restriction.

## Later integration: static follow-up, not a new runtime test

The prior worktree's pinned
[`scripts/test-4d.py`](https://github.com/miyako/BaseRT/blob/7a6fa134346fae36b37049e255dec14c5358d597/scripts/test-4d.py)
copies production classes/start into a temporary fixture under `.build`,
invokes a supplied tool4d with a 120-second subprocess timeout and inspects
JSON errors. It requires a tool4d path and writes fixture/output files, so
it was **read, not executed**. It explicitly says no model/engine was loaded.

Its
[`smoke.4dm`](https://github.com/miyako/BaseRT/blob/7a6fa134346fae36b37049e255dec14c5358d597/tests/4d/Project/Sources/Methods/smoke.4dm)
checks command substrings, runtime environment, local-model dispatch,
invalid/incomplete source runtime, missing model and absent event behavior.
`SmokeController.execute` captures a command instead of launching a child;
the worker component counts start calls. Thus, even a passing execution is
real 4D with **controlled worker/event doubles**, not real native readiness
or inference. Current assertions do not cover the full generic matrix:
for example, readiness/stream races, all-cached reentrancy, Unicode/embedded
quotes and native argv round trips still need dedicated cases.

Static inspection of this later revision confirms:

| Candidate | Later revision evidence | Remaining limitation / decision |
|---|---|---|
| B1 | `_Model.start:111-119` still calls success immediately after worker facade start | Facade blocking semantics/readiness protocol and legacy consumer contract remain unresolved |
| B2 | `_server.start:9` still binds only termination; both controller files are unchanged from primary snapshot | Real event dependency/signatures and end-to-end routing need verification |
| B3 | `_Model._isRouterMode` and `Methods/start` retain router branches | Unsupported-current-CLI claim still requires actual binary/version evidence |
| B4 | `_models:31,123-149` still uses `main` and size-only acceptance | Hash/revision/cache migration is a proposal pending policy |
| B5 | `_CLI` retains Windows early return and unused `_isArm` | Approved architecture/runtime matrix still needed |

Project/dependency declarations and controller files are unchanged between
the inspected revisions; resolved external dependency versions remain unknown.

## Earlier fixes: regression lessons and evidence limits

The coordinator reports these were fixed in the later implementation.
The first table below records the old snapshot to explain each lesson;
the follow-up paragraph records changes actually read at the PR head.
Neither constitutes runtime verification of the fixes.

| Reported lesson | Local snapshot evidence or limitation | Required regression assertion |
|---|---|---|
| Missing single-model separator; path/argument quoting | `_server:12-19` appends first file without a preceding separator; `_CLI.escape/quote` are launch-mechanism-specific | Child receives executable plus exact single/multiple model tokens, spaces, quotes and Unicode intact |
| Cached inline completion double-starts worker | `_models.download:121-147` calls completion inline; `Methods/start` also has explicit start paths; duplicate start not reproduced | All-cached/mixed/deferred/reentrant/duplicate schedules start once |
| Absent/null events | `_models:15-17` dereferences event before local guard; external event defaults unknown | Missing/null/wrong-type event/callback gives defined behavior, no crash or hidden failure |
| Local model startup downloads unexpectedly | `_Model` constructor calls `download` unless offline; `_models` resolves supplied remote references first | Valid local-only mode performs no remote lookup/download and starts once |
| Adapter options leak upstream | `_server:43-46` excludes only model/help/version before generic forwarding | Actual adapter-owned keys absent from native argv; supported extension flags preserved |
| Numeric flag coercion | `_server:50,65` handles `Is real` only, versus controller's explicit integer/real branches | Real 4D scalar/collection integer and real values generate correct native tokens |
| Incomplete runtime/model fail-closed handling | No complete compatibility contract established in this survey | Known unsupported/missing/corrupt runtime/model gives explicit error, never success |

At `7a6fa134346fae36b37049e255dec14c5358d597`, `_server.start` adds the
single-model separator, handles integer/real scalar and collection values,
and excludes callback/source-runtime/engine options from generic flags.
`_models` guards null/wrong-type event copying. `_Model` no longer downloads
in its constructor; `Methods/start` chooses download versus local/offline
start and explicitly reports a missing model. `_Model.start` adds
source-runtime/engine-file validation with an error callback/log fallback.
These are observed source changes, not proof of complete fail-closed
coverage. `_CLI.escape/quote` remain mechanism-specific; the reported
quoting lesson must not be interpreted as a universally replaced helper.
Removal of constructor download addresses one reentrancy path but does not
establish that every cached/duplicate-completion schedule starts once.

## Next-stage decision gates

### Application-session follow-up (reported evidence, resolution pending)

The applying session supplied artifacts under its session-local `files/`
directory, inspected read-only on 2026-11-02. These are application-session
records, **not independently rerun tests or a verified final patch revision**.
Its `survey-remediation.md` names baseline
`7e911a8c4cceb61f740fad4ffd1efc9718d20fc5` and reports real tool4d execution
with controlled completion/worker dependencies plus a native shell stream
probe. `survey-result.json` records start counts `0,1,2,3` after first,
last, duplicate and unknown completions; one equal-oid completion removes
both destinations. It also records stdout/stderr present in the native
control but absent in production-controller subscribers despite retained
response/responseError payloads. These strengthen the reported reproduction
evidence, but do not prove actual duplicate native servers, final fix
correctness, installed-host dependency resolution or inference.

The resulting reusable lessons are destination-plus-generation callback
identity, registration of the complete pending set before inline callbacks,
terminal-attempt monotonicity, shared cancellation identity across workers,
registry-generation cleanup and launch/cancel serialization. Adapter state
must remain outside native CLI options. Default inherited empty error handlers
need explicit subscriber-versus-no-op policy so fallback logging is not lost
or delivered twice. The generic workflow and worksheet now include those
boundary assertions; they do not prescribe one component implementation.

The application also reported Object-type constraints for instance checks
and cross-component subclass fixture failures. These language contracts
were independently checked against official `OB Instance of` and
`Class extends` documentation; their owning guidance is now in
[4dlang's routed pitfalls reference](../../4dlang/references/pitfalls.md),
not inferred from a failed BaseRT test.

`tool4d-crash-analysis.md` records one initialization failure before the
startup method, not an observed wrapper callback stack. `boot-probe-result.json`
records three predetermined startup-only samples with exit 0 and a reached
method marker. These artifacts support phase separation, not a diagnosed
root cause, a runtime fix or stability. No machine-specific crash identifier
or cache workaround is generalized here. Preserve the failed invocation
and scoped diagnostics; do not retry until green or mutate shared caches.

### Final application handoff: bounded implementation status

The later `implementation-handoff.md` and `final-4d-native.log` were read
read-only on 2026-11-02. They report **uncommitted** application changes in
branch `miyako-apply-4d-wrapper-maintenance`, based on
`7e911a8c4cceb61f740fad4ffd1efc9718d20fc5`. There is no fixed implementation
commit or merged status to cite. The following results are application
artifacts inspected here, not tests independently rerun by this skill task.

| Area | Reported implementation and bounded evidence | Status / remaining boundary |
|---|---|---|
| Stream routing (B2 subset) | Alias/reset/type guards and forwarding; real production controller with harmless native children checks payload, receiver, exit 7, one termination and component-local subclass | Implemented and tested for these fixtures, not full installed-host integration |
| Error diagnostics (B2 subset) | Error bridge preserves native metadata and compatible receiver; live scoped logging reports zero fallback messages with subscriber, one without | Controlled native-shaped error injection verifies translation, not an actual synchronous launch-error callback |
| Completion/cancellation follow-up | Destination/generation identities, all-record registration, terminal guards and shared registry; real 4D deterministic lifecycle fixtures include real cross-worker tokens | Implemented and tested at controlled lifecycle tier; external transfer cancellation and full public constructor/TCP runtime path not established |
| Error without response | Owned command/message/context queues aborted so termination releases worker; controlled injection reports complete=true, workerRetained=false and distinct PID on reuse | Narrow reproduced lifecycle fixed in application; not constructor-exception recovery |
| B1 readiness; B3 router; B4 cache; B5 platform policy | Launch-requested success, router branches, mutable-main/size-only cache and platform selection retained | Unchanged/deferred; no readiness or inference implementation |

The final native command was
`python3 scripts/test-4d-native.py --tool4d '<tool4d executable>' --check-logs`
on tool4d 21 R4.100208, exit 0. The log distinguishes actual timeout/response/
termination reuse from a controlled error-without-response schedule: the
latter records zero responses, one error and one termination, completed state,
released worker and a new process on reuse. This supports a transferable
queue-cleanup regression requirement, not an undocumented universal native
event-order guarantee.

Two negative observations remain explicit. Blob-mode stderr events on that
engine have empty text although `responseError` retains exact stderr; a
controlled Blob event forwarding pass does not erase this native limitation.
An actual missing executable throws POSX error 2 in `SystemWorker.new`, then
inherited `_execute` reaches error -10716 without a worker; no native error
or termination callback fires. The bridge tests **do not** establish recovery
from this synchronous construction failure.

The handoff also reports controlled real-4D lifecycle execution and genuine
compiler checking of the fixture with zero errors/two fixture warnings,
five Python safeguard tests, two-page static validation and whitespace
checks passing. These do not establish whole installed-component compilation,
resolved production dependencies, older 20.7-host compatibility or full
public-constructor/TCP integration. An optional constructor/TCP runtime probe
was inconclusive, not counted as a pass. Native BaseRT readiness, licensed
engine/model behavior and inference were not exercised.

The previously recorded package-initialization crash remains unexplained:
later passing invocations do not establish its cause, fix or stability.
External facade waiting and ongoing transfer I/O also remain outside the
bounded fix. Thus the application has implemented/tested **narrow findings**,
not resolved every B1-B5 concern or the full launch/error lifecycle. Obtain
the eventual committed revision and deployment-specific results before
claiming a shipped fix or broader resolution.

Use the pinned later revision as the next-stage baseline and resolve
component versions; run its harness only with authorization in an isolated
checkout. Reproduce every candidate there, prioritize demonstrated failures,
and seek decisions
on callback meaning, readiness identity/protocol, router compatibility,
pin/cache migration and platform support. Plan small authorized BaseRT
patches only in a second stage. No additional projects were surveyed.
