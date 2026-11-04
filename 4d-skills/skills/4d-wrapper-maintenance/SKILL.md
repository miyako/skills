---
name: 4d-wrapper-maintenance
description: >
  Survey, verify, plan and surgically fix recurring patterns in 4D
  external-process, CLI and server wrappers: inheritance, worker and
  callback lifecycles, process-launched versus service-ready semantics,
  downloads and cache reentrancy, component-to-native path resolution,
  argument construction, errors, platform and runtime gates, release
  version contracts. Use for wrapper audits, startup failures, missing
  streams, premature success, duplicate starts, or comparing wrappers
  across user-selected projects. Require per-project evidence and
  compatibility decisions, not blanket rewrites.
---

# 4D Wrapper Maintenance

## Scope and ownership

This skill owns the **survey-to-remediation workflow**, not a universal
wrapper implementation. Similar class names do not establish identical
contracts. Apply it to one authorized project at a time; compare only
additional projects explicitly selected by the user.

| Need | Read |
|---|---|
| Survey, lifecycle invariants, component-to-native paths and release gates | this file |
| Copyable inventory, evidence ledger, plan and rollout checklist | [templates/survey-remediation.md](templates/survey-remediation.md) |
| Concrete, revision-limited candidate evidence and regression lessons | [references/basert-candidates.md](references/basert-candidates.md) |
| 4D syntax, `Formula` / `This` / `.call()`, HTTP request signatures | [4dlang](../4dlang/SKILL.md), then its routed references |
| Source navigation and `.4dm` compiler validation | [4dlsp](../4dlsp/SKILL.md) |
| Executing real 4D / tool4d tests | [4dcli](../4dcli/SKILL.md) |
| Project version and source conventions | [4dproject](../4dproject/SKILL.md) |
| AI Kit consumers, if present | [4daikit](../4daikit/SKILL.md) |

Use the language lookup and version-matched official 4D documentation
before adding unfamiliar calls. Verify `4D.SystemWorker` and
`4D.HTTPRequest` callback signatures, event fields, stream encodings,
callback receiver and process lifetime against the actual 4D build and
component revisions. Do not copy AI Kit callback rules to SystemWorker
or invent a shared event schema. This skill intentionally supplies no
unverified 4D source implementation.

## Safety boundary

Start read-only. Record authorized repositories, exact checkout paths and
allowed operations. Do not edit another repository, install globally,
update shared dependencies, or roll out to every similar wrapper without
authorization. Never download models, build upstream runtimes, or execute
tests/scripts in a primary checkout as part of this workflow. Authorized
execution belongs in an isolated worktree with bounded output, caches,
network use and cleanup. Read test scripts before executing them: even a
test can download, rebuild or mutate a shared cache.

Use existing tools and test harnesses. If required validation is unavailable,
record the blocker and the narrower evidence obtained; do not imply a
runtime pass. Missing tools do not authorize an installation or expensive
run outside the task's scope.

## Staged workflow

### 1. Read-only survey

Create the inventory and ledger from the template before proposing fixes.
Record repository revision and dirty state, project compatibility version,
actual 4D engine build if known, OS/architecture, component/dependency
revisions, upstream executable version/build provenance, documentation
revision and existing test coverage. A declaration such as `latest` is
not a resolved dependency version; mark it unknown until resolved.

Trace actual files and symbols, including inheritance and overrides:

- Public constructor/start/stop/dispose and all consumers, examples and docs.
- Model/local-file resolution -> metadata/download -> completion -> worker
  registry/queue -> controller -> SystemWorker -> termination/cleanup.
- Callback producers, bind/copy/adaptation sites, receiver and argument order;
  stdout, stderr, launch errors, response and termination routing.
- Adapter-owned options versus upstream arguments; model ordering, quoting,
  numeric coercion, executable lookup and working directory.
- Port preflight, service readiness, runtime/model compatibility and
  OS/architecture checks; all unsupported and unknown branches.

Capture an edge list (`caller -> callee`, synchronous/asynchronous,
parameters, owning process, cancellation owner) rather than assuming an
inheritance diagram explains callback behavior. Locate mutable shared state,
constructor side effects and callbacks that can run synchronously.

Compare implementation with **this project's** documented contract and
existing consumers. Classify each finding as confirmed defect, intentional
behavior, proposal, stale documentation, or unverified candidate. Static
evidence can prove a missing binding, but not a successful server startup
or an unsupported upstream flag without version evidence.

### 2. Reproduce and establish a baseline

For each candidate, specify expected versus observed behavior and the
smallest safe reproduction. Record commands, environment, assertions,
exit status, callback trace and artifact paths; redact secrets. Establish
what existing tests already pass before changing code.

Prioritize demonstrated P1 failures (unusable startup, incorrect success,
lost errors or duplicate workers with material impact) ahead of P2
reliability/compatibility work. These are triage candidates, not universal
severity assignments: record reachability, impact and confidence separately.
Do not promote a suspected issue merely because it resembles another project.

### 3. Remediation plan and compatibility gate

For each accepted finding, name the smallest owning layer, precise change,
consumers affected, preservation/deprecation strategy, tests, rollback and
blockers. Reuse an existing helper only after verifying its actual contract.
Do not bulk replace classes across projects.

Obtain a project decision before changing legacy callback meaning, removing
router/multi-model support, requiring pinned models, invalidating caches,
adding platform gates or rejecting formerly accepted arguments. If no
decision is available, leave that change blocked and document alternatives;
an audit is not approval for behavioral changes.

### 4. Small isolated patch

Implement one coherent approved fix in the authorized worktree. Preserve
public signatures and callback receiver/argument order unless an approved
migration says otherwise. Update directly related docs and regression tests.
Keep unrelated cleanup out of the diff. Apply the invariants below to all
paths touched, including errors and disposal.

### 5. Targeted verification

Use the template's matrix and the existing harness. Compile-check changed
`.4dm` through `4dlsp`; run real 4D through `4dcli` only in the authorized
isolated project. Pair deterministic scheduling doubles with relevant
real-engine tests. Verify exact argument tokens and callback counts/order,
not only source fragments or process exit code.

Route Object guards for `OB Instance of` and project/component inheritance
boundaries through `4dlang`'s pitfalls reference. Test subclasses belong in
their parent's owning fixture component, not a host project extending it.

Separate project/component initialization or tooling failures from startup
method execution and failed code assertions. Preserve nonzero status, exact
invocation/build, redacted scoped diagnostics and the last fresh checkpoint.
A stack before the startup method does not establish a wrapper callback
defect, nor does a subsequent passing run establish a fix or stability.
If needed, predefine a small bounded startup-only diagnostic with independent
exit and fresh-output assertions, stopping on failure. Do not retry until
green, hide the initial failure, or mutate shared caches to make tests pass.

Label results by tier: static inspection; mocked command construction /
deterministic lifecycle; real 4D compile; real 4D execution; real native
worker/server readiness; end-to-end inference (or the service's equivalent).
No lower tier establishes a higher tier. An HTTP response or a fake server
does not prove model loading or inference.

### 6. Honest handoff and rollout gate

Report exact checkout/revision, changed files, confirmed and unconfirmed
findings, commands/results by tier, unavailable validation and open decisions.
Provide a per-project rollout matrix with rollback/cache compatibility notes.
Do not claim unsurveyed projects are fixed or affected. Commit, push,
publication, installation and rollout require their own authorization.

## Invariants to verify, not blanket edits

### Launch, readiness and cancellation

Process launch accepted, process running, service listening, model loaded
and usable inference are different milestones. Trace what legacy
`onSuccess` actually promises and what callers rely on. Never silently
move it from "launched" to "ready": prefer a compatible opt-in readiness
mode or a separate callback (for example `onReady`, a proposed name, not
a built-in 4D API), or obtain an explicit migration decision.

Derive readiness from the actual executable's documented/versioned
protocol and supported endpoint/command. A listening port, a TCP preflight
or a successful response from an unrelated process is not readiness.
Establish process/service identity, expected model and response shape;
do not probe an arbitrary port or invent `/health` support.

For each start attempt, design explicit state and generation ownership
(conceptual states may be resolving, starting, ready, failed, cancelled,
disposed). Bound polling by deadline and retry interval. Cancellation,
timeout, launch error, early exit and late responses must race safely:
one terminal **startup result** per attempt, no ready-after-failure,
no stale callback completing a restarted attempt. A later normal process
termination may still be a distinct documented lifecycle notification.
Cancel pending requests/timers, detach callbacks and release owned workers
on disposal; no consumer callbacks after disposal. Preserve approved
cancellation/termination notifications before detaching, and test that order.

Across worker/process boundaries, verify that cancellation observes the
same shared attempt token, not a copied ordinary object. Document ownership
and synchronization using the target 4D shared-object contract. Test both
orders at the final launch-versus-cancel boundary: checking a flag earlier
is not serialization. Registry cleanup must remove only the owning generation
on each terminal path and must not remove a newer attempt at the same key.
Carry tokens/registries in adapter context, not upstream CLI options.

### Errors and streams

Map native stdout/stderr/error/termination to the actual adapter callbacks.
Keep stream identity and original diagnostic/exit details; do not treat all
stderr as fatal or hide launch errors in an empty default handler. Verify
native event signatures and optional/null/malformed handling before reading
fields or invoking callbacks. Route invalid events through the project's
explicit diagnostic/error mechanism, not a success-shaped fallback.
Guard callbacks by callable type and active lifetime, not just non-null.

Callable does not necessarily mean subscribed: an inherited default empty
`onError` can consume a failure and suppress fallback logging. Inventory how
the project distinguishes an actual subscriber from its default no-op;
preserve receiver/signature compatibility and select one diagnostic delivery
path. Test no subscriber, inherited default and explicit subscriber, including
forwarding failures, without silently swallowing or duplicating delivery.

Exercise an error followed by termination **without a response**. In a
queue-based controller, advancing/marking completion only on response can
retain the failed worker indefinitely. Reconcile or abort owned command,
message and context queues together under the approved failure policy, then
verify terminal release and a later independent start with a distinct worker.
This is a lifecycle test requirement derived from application evidence,
not a claim that every native failure produces the same event sequence.
Test synchronous process-constructor exceptions separately: injecting an
error callback does not prove recovery when construction throws before any
callback or worker object exists. Preserve engine errors and do not claim
callback forwarding repairs that boundary.

### Downloads, local models and cache compatibility

Cached completions may run inline inside construction or iteration;
uncached completions may arrive later, out of order or more than once.
Register **all** pending records before dispatching any cached or asynchronous
completion. Give each record an identity including its destination and attempt
generation; a provider oid alone must not collapse equal content at different
destinations. Accept a completion only for a currently pending record in the
active attempt, deduplicate it, and gate worker start exactly once after all
required artifacts validate. Unknown/duplicate completions cannot start a
worker; failed/cancelled/stale callbacks cannot reopen a terminal attempt.
Avoid a constructor-completion plus explicit-start double path. Test empty,
all-cached, mixed and failed queues, cancellation and reentrant callbacks.

Local models must not accidentally trigger remote metadata/download work.
Validate existence, readability, format and runtime compatibility to the
extent the project can substantiate; fail closed on known incompatible or
incomplete inputs with explicit errors. Unknown support is not proven
compatibility. Identify who owns partial files and their cleanup.

Size-only cache hits cannot establish content integrity; mutable revisions
cannot establish reproducibility. Compare current cache identity and actual
provider digest/revision semantics. Immutable revision selection and
validated hashes may be **proposals**, not immediate mandatory fixes.
Specify legacy cache acceptance, verification cost, migration/offline use,
redownload consent and rollback. Never equate every provider `oid` with
the downloaded file's checksum.

### Component-to-native file paths

Resolve 4D context in the **component boundary**, then materialize an
absolute native path before launching the CLI. Keep the low-level executable
unaware of 4D aliases. A public Text parameter such as `fontFile` may accept
`/DATA/MyFont.otf`, `/RESOURCES/Fonts/foo.otf`, an absolute native POSIX path,
or a supported platform spelling (for example macOS HFS or Windows paths).
Distinguish these spellings before choosing `fk posix path` versus
`fk platform path`; do not reinterpret every string as the same path kind.

Validate type, empty/invalid input, embedded NUL and relative paths **before**
construction. Explicitly reject relative input: 4D can normalize it instead
of raising an error. Classify aliases separately from native absolute paths;
on Windows a drive-relative spelling is not an absolute path. Copy the
caller's request before canonicalizing its path fields; preserve the original
request and use the copy for native arguments. Capture construction,
expansion and file-access errors through the project's explicit error path;
never silently substitute a path, omit the argument or report success.

When initially constructing a host-context alias **inside a component**,
`File($path; fk posix path; *)` selects the host context (and `Folder`
has the equivalent context choice). This is separate from expansion:
`*` is not needed to expand an already-bound File/Folder object or an
absolute native path. Do not blanket-add `*`: component-owned executable
and resource lookups must retain their intended component context.

For a bound File or Folder, the generic expansion prior art is
[`miyako/llama-cpp`, `llama-cpp/Project/Sources/Classes/_CLI.4dm`](https://github.com/miyako/llama-cpp/blob/main/llama-cpp/Project/Sources/Classes/_CLI.4dm):

```4d
Function expand($in : Object)->$out : Object
    $out:=OB Class($in).new($in.platformPath; fk platform path)
```

The `.platformPath` roundtrip is mandatory for reliable materialization:
the original object's `.path` can still contain `/DATA` even after context
selection. `OB Class($in)` preserves File versus Folder. This helper is
correct; do not diagnose it as a llama.cpp expansion bug or replace it with
a direct read of the original `.path`. After expansion, pass the resulting
object's **`.path` on macOS** to a POSIX CLI, not its HFS `.platformPath`;
on Windows pass the resulting **`.platformPath`**. Materialization does not
replace the actual launch mechanism's argument quoting.

Prove this boundary with source **and compiled component** tests in a real
host, calling the public API with actual host DATA and RESOURCES fixtures,
absolute native paths, supported HFS/platform spellings, and Unicode/spaces.
Use distinct host/component resources to detect wrong-context resolution.
Assert the child receives the fully materialized path, compare useful
outputs for equivalent inputs, and assert the caller's request is unchanged.
Test wrong type, empty, NUL, relative and missing-file inputs with explicit
errors and no launch. A Python/native-only test with an already-expanded
path bypasses the failing boundary and cannot establish this behavior.

For font wrappers, keep path resolution distinct from glyph coverage:
`missing_glyph` from ZapfDingbats for `Office café` is a valid coverage
error, not evidence of failed expansion. Preserve it; do not add implicit
font fallback to make a path regression pass.

### Arguments, platform and runtime

Verify the real upstream CLI grammar for that binary version; do not
inherit another runtime's flags. Separate adapter options from forwarded
options explicitly while preserving documented extension mechanisms.
Test a single positional model and multiple-model ordering, separators,
quoted/spaced/Unicode paths, embedded quotes/metacharacters and trailing
separators using the actual launch mechanism (shell versus direct argv).
Do not assume one quoting helper works for bash, cmd.exe and direct argv.

Check scalar and collection numbers, including integer/real distinctions,
zero, negatives, decimals and locale-independent formatting where supported.
Cover true/false, missing/null, repeated arguments and reserved adapter keys.
Reject or report invalid input through the project-standard error path.

Inventory supported platforms, host/process architecture (including
translation), executable architecture, executable availability/permissions,
model format/version and required runtime capabilities. Approved unsupported
combinations should fail explicitly before launch/download, not return a
partially initialized object. An unused ARM helper alone does not justify
rejecting every non-ARM machine in a generic wrapper.

### Release versions and publication evidence

For a component/CLI version change, bind the native version macro,
CMake/package configuration, the 4D strict version decoder and host test
assertions to the same intended version contract. Search all those surfaces,
not only release metadata. Regression-test the newly built CLI's version
through the public 4D API so a hardcoded previous-version check cannot reject
the new patch release. Preserve the documented rejection of unsupported
versions; do not relax a strict decoder to accept arbitrary output.

Distinguish **release published** from **read-only post-publication
verification**. Inspect live CI state for the exact revision/run before
claiming work is waiting; a completed failed run requires prompt log
inspection and diagnosis, not more waiting. Report publication status
separately from pending or failed verification. Publishing does not authorize
retagging, replacing assets, merging or rolling out to consumers.

## Done gate

- [ ] Authorized scope, versions, flow inventory and consumer contracts recorded.
- [ ] Evidence distinguishes defects, intentional behavior, stale docs and proposals.
- [ ] Plan states what to fix, where, how, compatibility decisions and blockers.
- [ ] Approved patch is isolated; exact regressions covered at appropriate tiers.
- [ ] Unsupported/unavailable validation is explicit; no inference claims from doubles.
- [ ] Handoff and per-project rollout matrix persisted; no unauthorized rollout.
