# Controller characterization versus scoped construction recovery

Evidence refreshed 2026-11-04 JST. Read through the
[owning skill](../SKILL.md). This bounded follow-up to the
[llama-cpp integrity case](llama-cpp-integrity-remediation.md) adds evidence
gates and a later narrowly verified repair, not a generic controller rewrite
or a full public-facade recovery claim.

## Historical characterization scope

[`miyako/llama-cpp#19`](https://github.com/miyako/llama-cpp/pull/19) merged at
[`c87eba512e7a471ac85d3260a01170ce2836ebc5`](https://github.com/miyako/llama-cpp/commit/c87eba512e7a471ac85d3260a01170ce2836ebc5)
on 2026-11-03T21:11:58Z. Its changed files are investigation fixtures,
runner/tests, read-only CI and documentation; **no production cleanup fix**.
The [source README](https://github.com/miyako/llama-cpp/blob/c87eba512e7a471ac85d3260a01170ce2836ebc5/tests/controller/README.md)
defines the fixture graph and limits. The
[PR handoff](https://github.com/miyako/llama-cpp/pull/19#issuecomment-6615607476)
and [issue update](https://github.com/miyako/llama-cpp/issues/18#issuecomment-6615607845)
recorded [`miyako/llama-cpp#18`](https://github.com/miyako/llama-cpp/issues/18)
as **open at that snapshot**: `recoveryFixed: false` and
`acceptedNativeErrorWithoutResponseReproduced: false`.

## Read the predicate, not just the green count

The fixture byte-copies the actual unchanged
[`_CLI_Controller.4dm`](https://github.com/miyako/llama-cpp/blob/c87eba512e7a471ac85d3260a01170ce2836ebc5/llama-cpp/Project/Sources/Classes/_CLI_Controller.4dm) and
records its SHA-256. A stub `_CLI` owns its working directory. A `Schedule`
subclass overrides dispatch for deterministic schedules; separate native
controls use real `4D.SystemWorker` execution without that override.
No released worker/event components, public registry facade or server startup
are exercised.

| Evidence class | What it establishes | What it does not |
|---|---|---|
| Regression checks | Observed normal response dispatch, ownership, callback/context preservation, handler restoration, reuse and native success/nonzero/timeout queues | Recovery from every native error sequence |
| Candidate checks | Synthetic no-response retention, pending parallel queues, stranded execute, abort queue leftovers, very-late and duplicate termination | A repaired state: these green assertions deliberately confirm current gaps |
| Native matrix | Accepted true/false/signal-attempt/timeout controls emitted response then termination; false exited 1 | Accepted native `onError` without response was **not** reproduced |
| Constructor rejection | Missing executable returned null, no callbacks, synchronous POSX error 2 | An accepted-worker runtime failure or recovery from it |

The shell signal attempt reported exit 0. Record that observation; do not
relabel it a verified signalled exit merely because the command attempted TERM.
Synthetic callbacks use typed worker identities but do not prove native
event-order reachability. The reference `workers` 20.0.19 source described
in the README constructs a new server/controller after a terminated worker;
direct-controller retention therefore does not prove a public restart defect.
Moving `latest` declarations do not resolve the actual installed facade.
Abort-versus-continue policy for accepted runtime error remains undecided.

An eventual fix needs both the accepted failure policy and a demonstrated
owning-layer failure, or an explicitly approved defensive change. Do not
silently convert characterization predicates into success claims or bulk-copy
another wrapper's queue cleanup.

## Retained hosted evidence

The post-merge
[main run 41719600331](https://github.com/miyako/llama-cpp/actions/runs/41719600331)
completed successfully. Its actual `controller-characterization-evidence`
artifact (ID `13271610795`) was downloaded and inspected for this documentation
update, without executing the fixture again.

| Retained file in `controller-0q1mo1kn` | Observed result |
|---|---|
| `source.json` | `head` equals merge SHA; copied controller SHA-256 `138b4d376a6abe2aee2966bd14db5be6c6f9306f83599e53780ac29c168aa865`; graph explicitly excludes components/facade |
| `engine-version.txt` | 20.8 build 20.102083 |
| `compile.json`, `compile-exit.json` | `success: true`, `errors: []`; return code 0, no timeout |
| `schedules.json`, `native.json` | Fresh complete compiled-mode reports, empty errors; 22 schedule/controller checks plus two native-matrix checks, all passed with explicit `regression`/`candidate` kinds |
| `schedules-exit.json`, `native-exit.json` | Both return code 0, no timeout |
| `native.json.rejection.json` | Expected POSX 2 diagnostic, not an accepted native error callback |
| `summary.json` | Characterization complete; recovery **not fixed**, accepted native no-response trigger **not reproduced** |

Thus compilation, compiled execution, native controls and artifact provenance
passed at their stated tiers. Full facade integration, exact 20.7, Windows 4D,
server readiness and inference remain unverified. These checks do not repair
or waive the historical 20.5.23/20.5.24 DMG-container failure. The separate
20.5.25 publisher repair and public-distribution acceptance are recorded in
the integrity case; neither establishes controller recovery.

## Later scoped repair: initial-idle synchronous rejection

Production [`miyako/llama-cpp#22`](https://github.com/miyako/llama-cpp/pull/22)
merged at
[`2fdb9e66add2526d529d2d849d7b9ea0bbba7f72`](https://github.com/miyako/llama-cpp/commit/2fdb9e66add2526d529d2d849d7b9ea0bbba7f72).
The [actual controller](https://github.com/miyako/llama-cpp/blob/2fdb9e66add2526d529d2d849d7b9ea0bbba7f72/llama-cpp/Project/Sources/Classes/_CLI_Controller.4dm)
stages a newly submitted batch on an empty idle controller until
`4D.SystemWorker.new` succeeds. Rejection commits no queues or wrapper slots;
original callbacks, prior context and native POSX error remain intact.
The [inspection guide](inspection-and-repair.md#initial-idle-native-constructor-rejection)
describes the repair and acceptance boundary.

Fixture-only [`miyako/llama-cpp#23`](https://github.com/miyako/llama-cpp/pull/23)
subsequently merged at
[`e3c28a49ad4bac5f7b8d66d9fedb850f58de24e2`](https://github.com/miyako/llama-cpp/commit/e3c28a49ad4bac5f7b8d66d9fedb850f58de24e2).
The existing [run 41742885552](https://github.com/miyako/llama-cpp/actions/runs/41742885552)
tested PR head `187c168187ca1f91b692402ea2f04d61ee68e539` through checkout
`b4a1b7c2ca6b1b9af75a633f270ebcd0d84f6492`, not the later merge commit.
Its actual artifact `13282955845`, directory `controller-4qw5yv_2`, was
downloaded and inspected for this update. `source.json` records controller
SHA-256 `4d840f8014f149156fcb393e2945908814ce4b98c5897057a2a56e3e73b82bf6`;
the later merged controller bytes independently match that hash.

| Retained result | Scope |
|---|---|
| Actual engine | 20.8 build 20.102083; report version `F0012008` |
| `compile.json` and all four phase exit reports | `success: true`, `errors: []`; compiler/native/schedules/rejection exits 0 without timeouts |
| `native.json`, `schedules.json`, `rejection.json` | Fresh complete compiled reports: 2 native-matrix, 22 schedule/controller and 17 persistent-worker checks; all exact check IDs passed |
| Persistent worker | Four original POSX2 rejection stacks and four state guards **before** reuse; three actual harmless reuses, ten callbacks, 32 later mailbox turns, bounded late window, owner identity and five owned children terminated |
| `summary.json` | `idleConstructorRejectionCleanupVerified: true`, but `recoveryFixed: false` and accepted native error-without-response still not reproduced |

This verifies the empty-idle transaction and safe reuse, not constructor
rejection of B during A's response, a previously corrupted/nonempty controller,
public facade equivalence, exact 20.7 execution, server readiness or inference.
The automatic 20.5.26 publication after the production merge was not proof
this regression passed; the separately bound compiled run supplies that proof.

### Compatible fixture APIs and actual lifetime matter

The [pinned fixture documentation](https://github.com/miyako/llama-cpp/blob/e3c28a49ad4bac5f7b8d66d9fedb850f58de24e2/tests/controller/README.md)
records inspection of the actual 20.8 catalog: 1827 command entries, no C1843.
21 R4's object-returning `Process info:C1843` is not the renamed procedural
C336. The successful helper uses `PROCESS PROPERTIES:C336` and
`Current process:C322`, preserving tokens across renaming. A compiler's
name-resolution failure or a newer manual's 404 is not proof of ID absence;
a suffix cannot add a command missing from the older engine. Route general
command/version lookup through [4dlang](../../4dlang/SKILL.md).

The earlier C1495 helper compiled but exposed no usable headless `processes`
collection; [41742023358](https://github.com/miyako/llama-cpp/actions/runs/41742023358)
correctly failed without a worker report despite clean native/schedule exits.
Missing owner metadata now stops before rejection/reuse, never invents owner
fields or waives a gate. The disposable driver waits boundedly while callbacks
run in the real dedicated worker after the submitting method returns.

The two user-supplied local 21 R4 reports and producer's corrected interpreted
report are separate from compiled hosted evidence: source/compiled mode was
not attested by the manual reports, and the corrected local engine exited -11.
Neither all-true assertions nor a later hosted pass turns those attempts into
a local runtime pass. No known-unsafe baseline reuse or local retry was run
for this documentation task.

**Track separate problems separately:** issue 18 remains closed for the
confirmed synchronous fix. The still-unreproduced accepted-native
error-without-response candidate was separately tracked in
[`miyako/llama-cpp#24`](https://github.com/miyako/llama-cpp/issues/24), with a
[clarification on the closed issue](https://github.com/miyako/llama-cpp/issues/18#issuecomment-6620023999).
The tracker closed after the approved handling change and post-merge gates
described below. Neither administrative closure nor synthetic regression
coverage proves native/public-facade reachability: an actual accepted-error
trigger is still required for a native-reproduction claim.
Likewise, a GitHub merge does not update a user's old checkout or installed
component; inspect the actual local manifest and loaded artifact.

## Verified follow-up: native status and queue ordering

[`miyako/llama-cpp#25`](https://github.com/miyako/llama-cpp/pull/25) merged at
[`70887cabcb6c1ed63f8bbcbe7b2b5ca9a4a0d543`](https://github.com/miyako/llama-cpp/commit/70887cabcb6c1ed63f8bbcbe7b2b5ca9a4a0d543)
on 2026-11-04T02:18:20Z. Verified implementation
head `2561509cbe46a864957998a3b43b3c6797323633` was tested through checkout
`e85734b5885732cc2fecad87a3550877054f83ea` by
[41758980017](https://github.com/miyako/llama-cpp/actions/runs/41758980017).
The actual downloaded artifact `13289257081`, directory `controller-48s9k_pg`,
records source SHA-256
`e73f3429f2536d2db686df59e56281c50d2080e0eb5d34206763920a26fc5f13`.
On checksum-pinned ARM64 **20.8 build 20.102083 / F0012008**, compiler
`success: true`/`errors: []`, all five compiler/runtime exits 0 and fresh
complete compiled reports cover **2 native aggregate, 72 mixed schedule,
17 original persistent-rejection and 16 mixed persistent-lifecycle checks**.
The doc-only successor `7c0455b2e42dd79b1490d32f8a0b8bce1b92d4b9`
changes only the fixture README, not production/fixture/workflow source;
its separate final [run 41759422723](https://github.com/miyako/llama-cpp/actions/runs/41759422723)
also passed through checkout `561c7450da0cc823fcaf221d4a4b92d916948399`.
Downloaded artifact `13289432909`, directory `controller-k_3uz9zt`, retains
the same controller hash, exact check counts and five clean exits.
Final PR checks `characterize`, `consumer` and `gates` were successful.

The actual post-merge [controller run 41759864418](https://github.com/miyako/llama-cpp/actions/runs/41759864418)
also passed. Its downloaded artifact `13289188277` was inspected: `source.json`
names the merge SHA and identical controller hash; the same engine, exact
2/72/17/16 compiled check sets, fresh complete reports and five clean exits
remain verified. Post-merge [Publish 41759864593](https://github.com/miyako/llama-cpp/actions/runs/41759864593)
and [Download integrity 41759864856](https://github.com/miyako/llama-cpp/actions/runs/41759864856)
succeeded at that source. Issue 24 closed at 2026-11-04T02:22:28Z.

Normal automatic [release 20.5.27](https://github.com/miyako/llama-cpp/releases/tag/20.5.27)
targets version commit
[`855500a38092dac53d748fd6fc12bde1acba599a`](https://github.com/miyako/llama-cpp/commit/855500a38092dac53d748fd6fc12bde1acba599a),
which changes only `package.json` and has the merge as its sole parent.
Publication metadata/workflow success is **not independent acceptance of its
downloaded distribution**; no such binary verification is claimed here.
Keep the separately verified 20.5.25 payload/container evidence in the
[integrity case](llama-cpp-integrity-remediation.md) distinct. The merged
consumer still pins hash 20.0.1; the later prerequisite recovery is not a bump.

The [pinned reviewed contract](https://github.com/miyako/llama-cpp/blob/2561509cbe46a864957998a3b43b3c6797323633/llama-cpp/Documentation/Classes/_CLI_Controller.md)
and [fixture clarification](https://github.com/miyako/llama-cpp/blob/7c0455b2e42dd79b1490d32f8a0b8bce1b92d4b9/tests/controller/README.md)
support these portable inspection lessons, not a universal ordering rewrite:

- Actual true/false controls emit response `{type: "response"}` with
  `worker.exitCode` undefined; exit 0/1 appears at termination. Do not invent
  response status fields or interpret undefined as nonzero. Abnormal termination
  may still lack numeric status and needs its own policy.
- The owner approved retaining native response/error timing but advancing only
  **after the optional existing termination callback returns normally**.
  That callback can explicitly `abortQueue()` before dependents start: the
  native false-command marker remained absent through the late window.
  Default/no-handler and `False` callback returns continue; return values
  are not an abort protocol. This changes ordering and requires compatibility
  review rather than silently transplanting it.
- Private per-dispatch identity/generation ownership must not depend on public
  forwarding. Recheck ownership after reentrant terminate/restart; stale or
  duplicate events cannot release a replacement worker. `abortQueue()` clears
  pending commands/messages/contexts, not the active worker or history.
  Quiet streams and deliberate absence of aggregate response/error forwarding
  remain intact.
- A caller's deliberately resumptive 20 LTS error handler permits normal
  continuation; it must explicitly abort if desired. Production installs no
  handler. The real resumptive POSX2/owner checks are distinct from the
  **synthetic** interrupted-notification state. The destructive callback
  POSX2/`ABORT` attempt [41757854630](https://github.com/miyako/llama-cpp/actions/runs/41757854630)
  remains **failed**: original error captured, later owner ticks stopped,
  driver timed out even with a prequeued heartbeat. It does not prove surviving
  owner cleanup; do not retry unchanged destructive paths to force green.
- Fixture handlers cannot assume owning-process variables exist in the engine
  handler's context. Use a unique invocation report destination and actual
  C336 metadata for original stack/identity evidence. In these identity
  schedules, `Collection.copy()` deep-copied object/native identities; construct
  collections from the original worker references instead.

Accepted native error without response remains **unreproduced**; manually
dispatching it is not native proof. Exact 20.7, Windows, installed facade and
live inference remain unverified. Known local shutdown-crash paths were not
rerun. The 17 original constructor-rejection checks still guard state before
three actual reuses. These source/report inspections execute no wrapper
runtime and authorize no other-project rollout or further release operation.

## Attempts and failures stay distinguishable

The corrected PR run
[41672752068 attempt 3](https://github.com/miyako/llama-cpp/actions/runs/41672752068/attempts/3)
passed. GitHub job metadata for attempts 1 and 2 records cancellation,
empty runner identity and no steps: allocation-only cancellations, not
executed code failures or extra successful samples.

Separately, the initial
[41672156148](https://github.com/miyako/llama-cpp/actions/runs/41672156148)
failed on fixture compiler diagnostics; the fixture was corrected without
production changes or waived diagnostics. The source README also retains a
corrected local 21 R4 invocation with fresh clean compiler JSON but shutdown
exit -11; its runner stopped before the test methods. The producer's retained
`controller-review-result.json` handoff separately records a corrected local
20.8 attempt with the same compiler/exit split and no test-method execution;
that local raw report was not independently inspected for this update.
Later hosted 20.8 success does not erase either local failure or establish
its cause/stability.
Preserve phase, source, check IDs, freshness and independent exits; neither
runner-allocation cancellation nor subsequent green checks justify
retry-until-green or shared-cache mutation.
