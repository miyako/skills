# External executable/service wrappers: targeted inspection and repair

Use after the owning [skill](../SKILL.md). These are repair specifications,
not compiled patches or a common wrapper library. Concrete source and status
are in the [dated evidence catalogue](2026-11-02-evidence.md). Revalidate
the target revision and consumer contract before applying them.

## Discover first, then trace one attempt

Run read-only searches from the authorized target checkout, not a guessed
`Project/Sources` directory. A component may be nested below the repository
root, public classes may delegate to project methods, and subclasses may
replace controller handlers.

```sh
git status --short
git rev-parse HEAD
rg --files -g '*.4DProject' -g '*.4dm' -g '*dependencies*.json' \
  -g 'AGENTS.md' -g '*test*' -g '*smoke*'
rg -n -g '*.4dm' 'Class extends|Class constructor|Function (start|stop|terminate|dispose)|#DECLARE'
rg -n -g '*.4dm' 'CALL WORKER|SystemWorker|controller\.execute|\.start\(|\.wait\('
rg -n -g '*.4dm' 'options|OB Entries|Value type|OB Instance of|escape|expand|executable|platformPath'
rg -n -g '*.4dm' 'onSuccess|onError|onDataError|onData|onStdOut|onStdErr|onTerminate|onResponse'
rg -n -g '*.4dm' 'HTTPRequest|status|download|size|oid|revision|SYSTEM_WORKER_CONTEXT|_contexts'
rg -n -g '*.json' '"compatibilityVersion"|"version"|"latest"'
```

For an authorized remote-only review, resolve one snapshot before reading:

```sh
gh api repos/OWNER/REPO/commits/HEAD --jq .sha
gh api 'repos/OWNER/REPO/git/trees/FULL_SHA?recursive=1' --jq '.tree[].path'
gh api 'repos/OWNER/REPO/contents/ACTUAL_PATH?ref=FULL_SHA' \
  --jq .content | base64 --decode
```

Replace placeholders with discovered values, retain line-numbered excerpts
and link `blob/FULL_SHA/ACTUAL_PATH#Lx-Ly`. History/checkpoints recover leads,
not current source truth; unavailable archived evidence stays unavailable.
Do not restore sessions, clone projects or execute remote scripts just to
complete an evidence matrix.

These are locators, not tests: tokenized commands such as
`This:C1470`, multiline expressions, inherited overrides and dynamic
`This[$property]` binding need manual reading. `Is real` alone does not prove
integer loss; `$isStream` without `var` does not prove a compiler error.
An empty base handler may be overridden, an `oid` may not be a digest, and
`worker.start` may wait internally. Search all producers and consumers before
classifying an omission.

Record one edge per hop:

```text
public inputs -> normalized adapter state -> worker payload -> server options
-> CLI/environment serialization -> executable/cwd -> native process
-> response/streams/errors -> readiness or command completion -> cleanup
```

Add resource acquisition only if present. At each hop record the actual
type, default, copy/reference boundary, receiver, process owner, synchronous
versus deferred completion and attempt identity. Compare the effective
port/path in the preflight, registry key, child environment, probe and
shutdown call. Read consumers/examples to learn what success promises.

## Minimal repairs and acceptance cases

### Options and preflight ordering

**Detect/root cause:** compare the normalized object with the argument
actually passed to `_main`/`CALL WORKER`. Assigning a fallback `{}` to
`This.options` does not change a Null input variable. Likewise, normalizing a
port after `isRunning` gives reuse detection a different key from launch.

**Repair:** pass the normalized object at the existing handoff, rather than
reconstructing a second partial object in the worker. LocalAI's resolved
example uses `This:C1470.options`, an `Object`, as the `_main` argument and
normalizes its `Integer` port before `isRunning`. For another wrapper first
decide whether invalid ports are rejected or mapped to its documented default;
8080 is not a universal default. Normalize before reuse/TCP checks and use
the same value throughout. Keep callbacks/attempt state out of CLI options.
Follow settings into generated configuration files/environment as well:
a getter returning a constant can discard a correctly handed-off option.
Use validated backing values with compatible defaults, not merely a new
public option that never reaches the effective configuration.

**Accept:** Null, empty and custom options retain defaults and user overrides
through the captured worker payload; original-input mutation follows the
existing contract. Exercise ports -1, 0, 1, 65535, 65536, and wrong types at
any untyped boundary. Invalid input must not reach preflight/download/launch
under a reject policy; under a default policy every layer sees that default.
A typed `Integer` parameter alone says nothing about an untyped `.port` field.

### File/Folder values, separators and launch-specific quoting

**Detect/root cause:** in an `OB Entries($option)` loop, compare the value
type-checked with the value serialized. A branch checking `$arg.value`
but expanding `$option.model` uses the wrong operand for other File fields.
Do not confuse `4D.File` with `4D.Folder`, an identifier string or an output
path. Check spaces before and after each argument, not only path escaping.

**Repair:** retain the repository's `Value type`/`OB Instance of` guards and
its `expand`/`escape` helpers; serialize the checked entry. TEI's conditional
File branch would use `This:C1470.escape(This:C1470.expand($arg.value).path)`
instead of expanding `$option.model`, with an explicit token separator.
Preserve the leading separators already supplied by the flag branches; lack
of a trailing space alone does not establish concatenation.
This is an uncompiled repair expression, not a claim that TEI's default
Folder-valued embedding path uses this branch. LocalAI demonstrates separate
Folder guards and explicit reserved-key exclusion; preserve the engine's
actual `--key=value`, `--key value`, positional or environment grammar.

**Accept:** a File field distinct from `model`, two adjacent File fields,
Folder input and unsupported objects produce the intended result/explicit
error. Round-trip paths with spaces, Unicode, quotes, shell metacharacters
and trailing Windows backslashes through a harmless argv-echo child on each
supported launch mechanism. Static substring checks do not prove argv
fidelity. Do not copy a cmd.exe escape helper into a direct-argv or Unix
launcher; do not make a blanket quoting rewrite.

### Executable/platform discovery

**Detect/root cause:** enumerate architecture-specific resources, legacy
flat resources and system-PATH candidates independently. A bundled filename
such as `ollama-x86_64` need not equal the system command `ollama`.
Inspect supported host/process architectures and translation policy; an
unused `_isArm` helper is not a policy.

**Repair:** retain architecture-first resource lookup and the compatible
legacy resource fallback. Separate the bundled executable name from a verified
system command name, and choose a working directory valid for that selection.
For explicitly unsupported combinations, report through the adapter's existing
error channel before resource acquisition/launch, rather than returning a
partially initialized instance. Do not introduce a blanket ARM-only gate.

**Accept:** architecture resource present, only legacy present, only system
command present, no executable, unsupported host and translated process.
Assert exact selected path/cwd, diagnostic and zero unauthorized launches.
Resource-folder names alone cannot prove executable architecture/version.

### Launch, readiness, early exit, deadline and cancellation

If startup runs prerequisite commands (registration, install, conversion),
retain each `4D.SystemWorker`, wait or observe its actual completion, inspect
its exit/diagnostic result, and gate dependent work on success. Swama's
unchecked `create` and LocalAI's repaired install-before-start are concrete
comparisons. Verify any existing-resource query before making initialization
idempotent; do not overwrite/delete resources based only on a name. Test
already-present, new, failed and cancelled prerequisites and assert no server
launch after failure. Successful initialization is still not service readiness.

**Detect/root cause:** follow `onSuccess` back to its producer and resolve
external worker dependencies. A call immediately following `.start` proves
local ordering, not whether the dependency waits. A subprocess running or a
port being free is not a usable service. CLI converters instead need exit and
output validation, not an invented HTTP health check.

**Repair:** keep legacy launch-success semantics unless a migration is
approved. Add an adapter-owned opt-in/separate readiness transition only
after identifying the service/version's real protocol, identity and response
shape. Own a deadline, polling request and attempt generation; observe early
exit, timeout and cancel in the same terminal-state gate. A proposed
`onReady` is a project callback, not a 4D built-in. Keep state out of forwarded
flags. Terminate only owned processes; never construct a process-starting
object merely to stop it.

**Accept:** delayed ready, never ready, unrelated listener, early exit with
stderr/exit detail, readiness racing timeout/cancel, stop then late response,
restart then stale response. Use a predeclared short deadline and loopback
fixture; assert exactly one terminal startup result, no late success and no
owned worker/request left behind. Then verify native readiness separately;
application-level useful work (including inference where relevant) is another
tier.

### Streams and error forwarding

**Detect/root cause:** trace aliases (`onStdOut`/`onStdErr` versus native
`onData`/`onDataError`) through option copy, bind, controller override and event
component, then check the owner's resource/logging contract. Quiet stdout/stderr
may be intentional for a long-running server, not a missing feature. Distinguish
verbose logs from launch/lifecycle errors; an empty stream handler alone is
not evidence of lost failures. Default empty error handlers can make an error
look "handled". Read exact versioned signatures before adapting event payloads.

**Repair:** only repair an edge required by the accepted contract. Keep
deliberate default suppression; do not add blanket forwarding or unbounded
buffers. If opt-in streams are approved, specify byte/retention limits and
overflow behavior before wiring them. Adapt at the missing owning edge,
preserving the original native diagnostic, stream, exit code, receiver and
argument order. The inspected
controller convention is
`($worker : 4D:C1709.SystemWorker; $params : Object)` and forwarding via
`.call(This:C1470; $worker; $params)`; public event callbacks may have
different arguments and must not be blindly substituted. LocalAI's `_error`
uses a callable `4D.Function`, `cs.event.error.new` and `LOG EVENT` fallback.
Resolve whether an inherited no-op counts as a subscriber; do not duplicate
delivery or treat every stderr chunk as fatal.

**Accept:** distinct stdout/stderr, nonzero exit, absent subscriber, inherited
no-op, explicit subscriber and malformed event. Assert payload, receiver,
count/order and exactly one diagnostic route. Under quiet policy, assert no
default verbose forwarding/buffering while real failures still surface;
exercise sustained opt-in output against its bound. Test error then termination
without response, and synchronous `SystemWorker.new` failure separately:
injected callbacks do not establish constructor-exception recovery.

For dependent-command gating, observe exit-status timing on the actual engine.
The [verified lifecycle case](controller-characterization.md#verified-follow-up-native-status-and-queue-ordering)
found no response-time exit code and requires an approved termination-order
migration for status-based aborts. Test a harmless dependent marker remains
absent through a bounded late window, not merely that the abort callback ran.
Keep queue clearing distinct from active-worker termination and context history.
Identity-sensitive schedules must retain original worker references; do not
deep-copy them into substitute objects and then claim identity preservation.

### Initial-idle native-constructor rejection

**Detect/root cause:** find queue insertion, handler replacement and completion
state changes that precede `4D.SystemWorker.new`. A synchronous rejection may
leave state committed without an accepted worker. Capture original error and
logical state **before** any reuse; do not retry an already-corrupted controller.
Constructor rejection is not an accepted worker's asynchronous error callback.

**Repair:** the source-verified
[llama-cpp transaction](https://github.com/miyako/llama-cpp/blob/2fdb9e66add2526d529d2d849d7b9ea0bbba7f72/llama-cpp/Project/Sources/Classes/_CLI_Controller.4dm)
passes local `Collection` batches into `_execute`, constructs initial `Object`
options with captured handlers, and commits the three queues/saved handlers
only after native acceptance. `_onInitialEvent` forwards through the original
controller's `.call(This:C1470; $worker; $params)` convention. Rejection leaves
`worker` Null, `complete` True, new queues empty and prior callbacks/context
unchanged; the original POSX error propagates without a new production error
handler or a language-floor-raising `Try`/`throw` rewrite.
This is a repair specification, not a copied implementation for every wrapper.

**Accept:** missing single command, missing first command of a batch, repeated
rejections and three actual harmless reuses, with state/error guards before
each reuse. Preserve receiver, worker/event arguments, stdin/context ordering,
old/new termination ownership and the actual worker identity after method
return. Use bounded private workers and no model/server. The
[retained compiled evidence](controller-characterization.md) covers only an
empty idle submission, not rejection of B during A's response, contaminated
idle state or accepted native error without response.

### PID context, queues and cleanup

**Detect/root cause:** compare writes to
`SYSTEM_WORKER_CONTEXT[String(worker.pid)]` with removal on every terminal
path. Clearing `_contexts` (pending queue) does not remove PID-map entries.
Advancing only on response can retain an errored worker forever.

**Repair:** attach the completing PID's context before forwarding the callback,
then remove that PID only after its last documented consumer. The actual
map is an `Object`; the documented command is
[`OB REMOVE(object; property)`](https://developer.4d.com/docs/commands/ob-remove),
not setting a property to Null. For shared maps use the target's required
synchronization and generation ownership. Reconcile command/message/context
queues together according to the existing abort/continue policy. Do not clear
the entire map while another command or generation owns entries.

**Accept:** many sequential commands, interleaved old/new completions, same
registry key restarted, PID reuse, explicit terminate, error without response
and callback reentrancy. Every final consumer receives its context; map/queue
sizes return to baseline; an old completion cannot remove new ownership.

### Optional downloads, caches and dependency contracts

**Detect/root cause:** follow HTTP failure/status through metadata parsing,
transfer completion and startup. Successful transport is not successful HTTP;
equal size is not equal content. Identify destination, revision and digest
semantics; do not assume provider object IDs are downloaded-byte hashes.
Inspect declared and actually resolved component versions.

**Repair:** use the target `4D.HTTPRequest` API's real error/HTTP fields and
existing error channel; reject bad status/shape before creating pending files.
Validate completed bytes before marking a record usable; keep partial-file
ownership explicit. Register the whole pending set before any inline cache
completion, identify records by destination plus attempt, and accept each once.
Pin/verify revisions and digests only with a documented legacy-cache/offline
migration policy. Resolve compatible `event`/`workers`/other dependencies,
then record tested versions; replacing `latest` with arbitrary numbers is
not a compatibility fix.

If a reusable hash dependency is selected, keep its computation separate from
the consumer's provider/cache/start policy. First verify the approved prerequisite release
and complete installed component layout; record its exact source, release
asset and final signed/stapled-byte checksum, not a moving `latest` or a
pre-sign digest for a different distribution. A package digest authenticates
the dependency bytes, not any downloaded application resource.

When verification is accepted, run it for both cached and fresh files.
Validate authoritative expected SHA-256 metadata before comparing; preserve
an explicit unverified result where legacy/offline metadata provides none.
Keep mismatch, computation failure and unavailable metadata distinct. Under
llama-cpp's accepted policy, mismatch blocks startup with an actionable error
without automatic deletion/redownload; other consumers need their own policy.
Preserve callback receiver/arguments, launch-success meaning and completion
generation/dedup guards while adding this gate.

**Accept:** 401/404/429/500, transport failure, malformed metadata, interrupted
transfer, equal-size wrong bytes, changed revision, offline legacy cache,
empty/all-cached/mixed queues, duplicate/out-of-order/inline completion and
cancel. No worker starts from incomplete/failed resources; local-only inputs
perform no unintended network. Capture compile results, not just a packaging
action's exit status.
Also assert valid and mismatched SHA-256 for cached/fresh files, hash failure,
unverified legacy/offline files, no destructive retry on mismatch, and duplicate/
out-of-order/stale completion schedules. See the
[bounded llama-cpp case](llama-cpp-integrity-remediation.md) for accepted
policy and released-dependency evidence, not a universal dependency pin.

## Bounded validation and handoff

First run existing bounded/static checks in the authorized worktree after
reading their side effects. Add assertions of exact payloads/tokens and
terminal counts; source-string presence alone is weak evidence. Route actual
`.4dm` changes through `4dlsp`, and real execution through `4dcli`. Run optional
native/service fixtures only with explicit resource/network limits, temporary
cache directories and owned-process cleanup. Stop on failure; retain evidence.

Require independent engine exit and fresh assertions alongside structured
compiler results. `success: true`/`errors: []` plus engine exit -11 is not a
runtime pass or clean build. Record baseline warnings, compiled/interpreted
mode and the real-versus-stub dependency graph. If a minimal unrelated project
also crashes, retain that bounded control; it does not identify a wrapper bug,
a supported-version defect or a reason to clear shared caches. Do not retry
until green or promote a later isolated pass into resolution of the crash.

Report static source, deterministic doubles, 4D compilation, 4D execution,
native service readiness and useful operation separately. A published binary,
a successful packaging action or a historical session summary establishes none
of those higher-tier results for the current adapter. Use the existing
[worksheet](../templates/survey-remediation.md) for precise evidence and
compatibility decisions.
