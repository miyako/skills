---
name: 4d-wrapper-maintenance
description: >
  Survey, verify, plan and surgically fix recurring patterns in 4D
  external-process, CLI and server wrappers: inheritance, worker and
  callback lifecycles, process-launched versus service-ready semantics,
  downloads and cache reentrancy, argument construction, errors, platform
  and runtime gates. Use for wrapper audits, startup failures, missing
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
| Survey, lifecycle invariants and staged gates | this file |
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

## Done gate

- [ ] Authorized scope, versions, flow inventory and consumer contracts recorded.
- [ ] Evidence distinguishes defects, intentional behavior, stale docs and proposals.
- [ ] Plan states what to fix, where, how, compatibility decisions and blockers.
- [ ] Approved patch is isolated; exact regressions covered at appropriate tiers.
- [ ] Unsupported/unavailable validation is explicit; no inference claims from doubles.
- [ ] Handoff and per-project rollout matrix persisted; no unauthorized rollout.
