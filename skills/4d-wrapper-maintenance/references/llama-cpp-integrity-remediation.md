# First llama-cpp integrity remediation: bounded lessons

Evidence reviewed on 2026-11-03 UTC / 2026-11-04 JST. Read through the
[owning skill](../SKILL.md); use the generic
[inspection guide](inspection-and-repair.md) and
[worksheet](../templates/survey-remediation.md) for a new target.
This is one accepted consumer policy, not an instruction to install a
particular component everywhere or a claim that other wrappers are affected.

## Evidence and implementation status

The consumer session supplied `files/download-integrity-result.json`
(session `f6737562-ab51-4deb-9ba9-f81877447380`), read directly along with its
isolated worktree's `_models.4dm`, `_Model.4dm` and
`dependencies.lock.json`. Consumer baseline:
[`19616caf06d2db4b6864a2fff444ed473d5f5b0b`](https://github.com/miyako/llama-cpp/tree/19616caf06d2db4b6864a2fff444ed473d5f5b0b).
The integrity source is now published in
[`miyako/llama-cpp#17`](https://github.com/miyako/llama-cpp/pull/17), head
[`78c6f62e90a91e708a9a1d96cf5b155d46d53e70`](https://github.com/miyako/llama-cpp/commit/78c6f62e90a91e708a9a1d96cf5b155d46d53e70).
The PR merged at **2026-11-03T15:44:53Z**, merge commit
[`caca5134f1c1cd7e493415b7ecb6afb4b283a054`](https://github.com/miyako/llama-cpp/commit/caca5134f1c1cd7e493415b7ecb6afb4b283a054),
verified through GitHub metadata. The merged dependency lock retains the exact
reviewed hash 20.0.1 archive. Its tested pre-merge head's
[Download integrity run 41666662320](https://github.com/miyako/llama-cpp/actions/runs/41666662320)
has succeeded, with retained results inspected as described below.
The local test execution predates the source commit; the handoff JSON has
since been refreshed with hosted, merge and publication evidence. The post-merge
[main Download integrity run 41667085219](https://github.com/miyako/llama-cpp/actions/runs/41667085219)
also succeeded at the merge SHA. The automatic
[Publish run 41667085120](https://github.com/miyako/llama-cpp/actions/runs/41667085120)
reports success and
[component release 20.5.24](https://github.com/miyako/llama-cpp/releases/tag/20.5.24)
is published, targeting the merge SHA. The subsequent
[`2cac6f84423b186d2a278ed6d1f90b931ab72723`](https://github.com/miyako/llama-cpp/commit/2cac6f84423b186d2a278ed6d1f90b931ab72723)
changes only `package.json`; it is not the release's source target.
Published assets and a successful workflow are **not distribution acceptance**:
the producer reports failed DMG-container checks below.
The baseline link is **not** a source link to the fix.

The artifact reports a baseline controlled-worker start for an unchanged
three-byte `abd` cache when the available expected digest describes `abc`.
Equal size therefore missed the demonstrated mismatch. The consumer fix
and controlled tests address this issue, not readiness or general log routing.
Results below were inspected, not independently rerun by this documentation
task; historical consumer artifacts and public prerequisite-release evidence
remain separate.

## Owner decisions are part of the contract

The owner deliberately suppresses default stdout/stderr callbacks to avoid
large log volume from long-running servers. Absence of verbose stream
delivery is **intentional resource policy**, not itself a defect. Do not
reintroduce forwarding/buffering as incidental cleanup. Distinguish required
launch/lifecycle failure diagnostics from verbose logs; any opt-in streams
need explicit bounds, retention/overflow behavior and compatibility approval.
This clarification does not make lost real failures acceptable or reclassify
every other repository's stream contract.

The accepted change preserves public callback receivers/argument order,
router behavior and legacy `onSuccess` meaning **launch requested**, not
service/model ready. It does not import deferred controller/readiness work.
One issue is being remediated at a time; the reusable prerequisite was
released before consumer integration, and its installation is owner-accepted.

## Compute-only prerequisite versus consumer policy

The reviewed prerequisite is
[`miyako/hash` release 20.0.1](https://github.com/miyako/hash/releases/tag/20.0.1),
source
[`c0fc53089bea0746434585c152b4448db88512a0`](https://github.com/miyako/hash/tree/c0fc53089bea0746434585c152b4448db88512a0).
Its actual
[`sha256(4D.File; Object) -> Object` API](https://github.com/miyako/hash/blob/c0fc53089bea0746434585c152b4448db88512a0/hash/Project/Sources/Classes/hash.4dm#L1-L56)
computes a digest with structured success/error details; the consumer calls
`cs.hash.hash.new().sha256($file)`. It performs a bounded native CLI operation
without loading the entire file into 4D memory. It does **not** own provider
metadata, expected-digest comparison, cache/start decisions, retry/deletion,
UI/logging or the consumer's cancellation orchestration.

| Reviewed release evidence | Value / scope |
|---|---|
| Component archive | [`hash.zip`](https://github.com/miyako/hash/releases/download/20.0.1/hash.zip) |
| Exact archive SHA-256 | `7fe55bf2f552e7c6441cff5079bad5c9f2513cf694563d8b2c4f76ba8a7d71d5` |
| Byte inventories | Versioned [`SHA256SUMS`](https://github.com/miyako/hash/releases/download/20.0.1/SHA256SUMS) and [`provenance.json`](https://github.com/miyako/hash/releases/download/20.0.1/provenance.json) describe final distributions/inventories; embedded native/pre-sign provenance has a different byte scope |
| Signed installed-host evidence | [`signed-host-compile.json`](https://github.com/miyako/hash/releases/download/20.0.1/signed-host-compile.json), [`signed-runtime-verification.json`](https://github.com/miyako/hash/releases/download/20.0.1/signed-runtime-verification.json), [exact-source hosted run](https://github.com/miyako/hash/actions/runs/41659485571) |

Public release metadata and provenance confirm that archive digest and source.
The released compiled 4D library and macOS CLI payloads are signed/notarized;
DMG containers have separate signing/notarization/stapling evidence. Final
ZIP checksums describe signed payload archives; final DMG checksums follow
container signing/stapling. ZIPs/raw CLIs cannot themselves be stapled.
Do not compare a pre-sign inventory with these final bytes or transfer a
checksum between standalone and component distributions.

Install the complete reviewed component layout (`hash.4dbase`, including
compiled component, Libraries and Resources), not only the CLI or `.4DZ`.
The consumer's `dependencies.lock.json` records review evidence; it does not
by itself make 4D Dependency Manager verify checksums. The release pin above
is a **dated case**, not a forever-current dependency prescription. Each new
consumer must review platform prerequisites, actual installed bytes and an
approved compatible release separately.

## Accepted consumer gate

Source ownership:
[`_models.download/onDownload/_onFileDownload`](https://github.com/miyako/llama-cpp/blob/78c6f62e90a91e708a9a1d96cf5b155d46d53e70/llama-cpp/Project/Sources/Classes/_models.4dm#L128-L216)
owns pending records and verification scheduling;
[`_verifyFile/_expectedDigest/_hash/_integrityError`](https://github.com/miyako/llama-cpp/blob/78c6f62e90a91e708a9a1d96cf5b155d46d53e70/llama-cpp/Project/Sources/Classes/_models.4dm#L218-L308)
owns expected-digest comparison and failure;
[`_Model.start`](https://github.com/miyako/llama-cpp/blob/78c6f62e90a91e708a9a1d96cf5b155d46d53e70/llama-cpp/Project/Sources/Classes/_Model.4dm#L75-L107)
gates launch. The
[`dependency lock`](https://github.com/miyako/llama-cpp/blob/78c6f62e90a91e708a9a1d96cf5b155d46d53e70/dependencies.lock.json)
records the reviewed archive and limits.

| Condition | Observed implementation / acceptance requirement |
|---|---|
| Supported provider digest | Accept validated 64-hex Hugging Face `lfs.oid` as expected SHA-256, normalize case; do not substitute the repository Git `oid` or `xetHash` |
| Cached file with supported digest | Hash before accepting it, including equal-size data; cached existence/size must not bypass available verification |
| Fresh managed download with supported digest | Hash the completed destination before removing its pending record or permitting worker startup |
| Matching digest | Record a verified result; launch only after all required records complete under the existing schedule contract |
| Mismatch or hash computation/result failure | Latch failure, report actionable error code 3 once with path/details, block startup; no automatic deletion, replacement or redownload |
| No supported digest, legacy/offline/local-router input | Preserve accepted legacy behavior with an explicit unverified result/diagnostic; never relabel it verified |
| Repeated/reentrant/late completion | Unique destination records, dispatch/completion/verifying guards and terminal rechecks prevent a failed/completed attempt reopening or starting twice |

This gate is not immutable provider revision pinning, a provider trust audit,
a downloader rewrite or a full startup fix. A hash result authenticates bytes
only against the chosen expected digest. Copying `lfs.oid` parsing to another
provider or changing legacy/offline acceptance requires a fresh decision.

Preserve close-before-completion and destination ownership when porting.
Hashing can yield to other completions while its native worker runs; recheck
pending/terminal state after it returns, not just before invoking it.
Acceptance cases include cached/fresh match and mismatch, unavailable digest,
hash failure/malformed result, equal-size corruption, inline/all-cached/mixed
queues, duplicate/unknown/late/reentrant callbacks and failure followed by
completion. Assert callback receiver/arguments, one failure result, no
unauthorized file mutation/retry and no worker start after failure.

## Validation boundaries: retain failures as well as passes

| Evidence | Result / limit at this snapshot |
|---|---|
| Final local consumer fixture | **21 R4 build 21R4.100208**, compiled execution, 35 assertions passed, zero failed, engine exit 0; component/host compiler reports successful with no diagnostics |
| Hosted consumer fixture at PR head | Run **41666662320**, **20.8 build 20.102083**, checksum-pinned ARM64 engine on macOS 15: compiled execution, 35 assertions passed, `errors: []`, engine exit 0; event/workers/consumer compiler reports `success: true`/`errors: []` with all three compiler exits 0 |
| Hosted baseline reproduction | Same run, interpreted control: `corruptStarts: 1`, `cacheBytes: 3`, `cacheContent: "abd"`, `errors: []`, engine exit 0. Reproduces old acceptance of equal-size corrupt data, not a production server start |
| Real versus controlled dependencies | Actual released signed hash 20.0.1 and its real CLI; metadata, tiny-file transfers, event/workers facade and server are controlled/stubbed. Not the full production graph or actual startup |
| Consumer archive safeguards | Five Python archive tests reported passing: pin, permissions, traversal/symlink rejection and unambiguous layout; not wrapper runtime evidence |
| Full production compilation | Compiler reports zero errors and the same three baseline demo warnings with actual reference dependencies; engine exit **-11**. **Not accepted as a clean full build/runtime pass** |
| LSP attempt | Bridge 0.3.0 unknown external component namespaces; not a validation pass or proof of a new source defect |
| Hash component's own hosted installed-host gate | Real **20.8 build 20.102083**, signed released component, compiler `success: true`/`errors: []`, eight installed cases successful and clean hosted exit reported; separate from consumer evidence |
| Not run / not established | Exact 20.7 unavailable; Windows 4D, live provider HTTP, real facade cross-worker scheduling, native server readiness and inference not exercised |

The original consumer result artifact's final local engine is **21 R4**,
not 20.8. The now-successful separate
[`20.8 consumer CI gate`](https://github.com/miyako/llama-cpp/blob/78c6f62e90a91e708a9a1d96cf5b155d46d53e70/.github/workflows/test-download-integrity.yml)
provides independent consumer 20.8 evidence; the hash component's own hosted
20.8 gate remains a third, separate result. None is a full production-graph,
native server readiness or inference pass.

The actual retained `download-integrity-evidence` artifact (ID `13246916948`)
was downloaded and read for this documentation refresh. Its compiled fixture
directory `integrity-uqb9svvg` contains `result.json`, `invocation.json`,
`exit-status.txt`, `hash-artifact.json`, the three `*-compile.json` reports
and three `*-compiler-exit.txt` files. The baseline directory
`integrity-8mjsdfto` contains its own result, invocation and exit status.
Run logs identify the actual 20.8 build; the hash receipt records the exact
released archive SHA-256. These paired reports/exits, not a green run badge
alone, support the hosted rows above. Their controlled dependency graph has
the same limits as the local fixture; they do not erase the earlier full
production compilation's nonzero exit.

### Published 20.5.24: payload and container outcomes differ

The producer downloaded the actual 20.5.24 ZIP/DMG and reports the following
checks in the updated `files/download-integrity-result.json`, read during
this documentation refresh. These are retained producer verification results,
not new signature checks or runtime execution by this documentation task.
GitHub release metadata independently confirms the asset SHA-256 values:

| Asset | Published SHA-256 |
|---|---|
| `llama-cpp.zip` | `8f68d6ea9f2b1a8b699dac600e6deb976e72db8a5052df521021b8e5f6d95c04` |
| `llama-cpp.dmg` | `f50234e7a5781e9ceeaacfe814aec8fca2146b1e527d61e3068c9554ef887a0b` |

| Producer-reported check | Outcome / limit |
|---|---|
| Downloaded archive digests | Match the published asset digests |
| Compiled component inspection | `.4DZ` contains the exact hash 20.0.1 dependency; MX64/IX64 code and an ARM64 library reported present. Presence is not installed-host/runtime acceptance |
| Library and embedded CLI payloads | Strict signature/notary-ticket checks exit 0; Developer ID `Y69CWUC25B`, hardened runtime and secure timestamps reported |
| DMG container signature | **Fail, exit 1:** unsigned container |
| DMG stapling validation | **Fail, exit 65:** no ticket |
| DMG Gatekeeper assessment | **Fail, exit 3:** no usable signature |
| Downloaded 20.5.23 baseline DMG | Identical signature exit 1, stapler exit 65 and Gatekeeper exit 3 failures; confirmed pre-existing publisher limitation, not a new integrity regression |
| Component packaging log | 55 nonfatal warning entries reported, compared with 54 of the same missing-external-metadata pattern for 20.5.23; hash adds one. Not a diagnostic-free production compile |

Thus payload notarization does not rescue the failed container acceptance.
The clean explicitly component-loaded consumer fixture remains separate from
both the packaging warnings and the earlier full-graph engine exit -11.
The retained handoff identifies compiler comparison logs
`.build/pr17-publish.log` and `.build/pr17-baseline-publish.log` in the
consumer worktree. At that snapshot no release mutation or signing hardening
had been performed.
Baseline comparison establishes that the container limitation predates the
integrity change; it is **not fixed or waived** by that classification.
Route separately authorized signing/packaging remediation to
`native-artifact-provenance`, not a blanket wrapper rewrite.

The owner subsequently authorized separate publisher hardening; the
verified new-release outcome below does not change the historical
20.5.23/20.5.24 container results. Separately merged
[controller characterization](controller-characterization.md) preserves an
separate recovery investigation. Its later scoped synchronous-rejection
repair is not accepted-native error-without-response recovery.

### Follow-up 20.5.25: actual distribution acceptance

[`miyako/llama-cpp#21`](https://github.com/miyako/llama-cpp/pull/21) merged
[`3ff7bfde6e425701748c7f6365f14aa425123dd4`](https://github.com/miyako/llama-cpp/commit/3ff7bfde6e425701748c7f6365f14aa425123dd4).
The [source-pinned publication contract](https://github.com/miyako/llama-cpp/blob/3ff7bfde6e425701748c7f6365f14aa425123dd4/publishing.md)
records the implemented gates. Public
[20.5.25](https://github.com/miyako/llama-cpp/releases/tag/20.5.25), confirmed
as Latest at this refresh, targets
[`2d9100cd98305228d988938a9174fe5916080697`](https://github.com/miyako/llama-cpp/commit/2d9100cd98305228d988938a9174fe5916080697):
only `package.json` changed, with the reviewed merge as its sole parent.

Production [run 41725672056 attempt 2](https://github.com/miyako/llama-cpp/actions/runs/41725672056/attempts/2)
executed both candidate signing/build gates and the write-enabled publisher,
including same-attempt artifact and downloaded-draft checks. In attempt 1
the candidate passed, but the publisher was cancelled without a runner or
steps. The owner authorized one complete-workflow retry; a publish-only retry
using an earlier attempt's artifact would violate the enforced binding.
This is not a waived failed assertion or an unconditional retry policy.

For this documentation update, the coordinator's `dmg-release-verification.json`
and implementing child's `public-release-verification.json` were read.
GitHub release/run/commit metadata and the actual public `provenance.json`,
`notary-log.json`, `compiler-status.json`, `signing-receipts.json` and
`SHA256SUMS` were independently retrieved. The following binary/mount results
come from those retained producer verifications, **not** new signature,
mount or wrapper-runtime tests by this documentation session.

| Actual public-release evidence | Outcome / scope |
|---|---|
| DMG final SHA-256 | `9a3acf131b982fff07f36b44dfbafa9dc61d65e2f2d89c273cedb81da42f9c27` |
| ZIP final SHA-256 | `beb1322218b17c34018d682b65297c67a54cf4fb9fb282071b8d700542f1504d` |
| All seven downloaded assets | Child verified API digests and final checksums; coordinator separately downloaded/verified the DMG and evidence metadata |
| DMG container | Both verifiers report strict signature, stapler and Gatekeeper exit 0; Developer ID team `Y69CWUC25B`, secure timestamp, affirmative `accepted; source=Notarized Developer ID` |
| Notary submission | Request `fe5f6c94-a6e2-4ba5-b5df-76bde86a5951`, explicit `Accepted`, status code 0, `issues: null`; exact four-ticket path/architecture/CDHash coverage: container, ARM64 library, ARM64 and x86_64 CLI |
| Submitted versus final DMG bytes | Pre-staple submission SHA-256 `5e83d76a37a8f45ce3a7463f388927e54b7473e31ef88264c7681861b8f9a4b5` is intentionally distinct from the final stapled DMG checksum |
| Mounted image versus extracted ZIP | Read-only private mount and ZIP inventories match all 17 files; compiled MX64/IX64 and exact hash 20.0.1 dependency verified; verification mounts detached |
| Payload policy and preservation | Library/CLI slices passed signature, team, timestamp, hardened-runtime and notarization requirements; legacy CLI entitlements, native pre-sign inputs and Windows bytes preserved, not newly hardened |
| Actual compiler | **20.7 build 20.101905**, success with 55 explicit `isError: false` warnings. Not diagnostic-free compilation, installed-consumer execution or inference |
| Historical release | 20.5.24 asset digests/tag unchanged; new distribution acceptance does not retroactively repair prior containers |

[`miyako/llama-cpp#20`](https://github.com/miyako/llama-cpp/issues/20)
closed only after [public-download verification](https://github.com/miyako/llama-cpp/issues/20#issuecomment-6616779750).
Controller [`miyako/llama-cpp#18`](https://github.com/miyako/llama-cpp/issues/18)
was then open and later closed for the synchronous fix. The
[controller case](controller-characterization.md) separates that result from
the still-unproved native-error candidate now tracked in
[`miyako/llama-cpp#24`](https://github.com/miyako/llama-cpp/issues/24).
Exact 20.7 **compilation** here does not
fill the earlier fixture's missing exact-20.7 runtime tier. No full installed
consumer smoke, Windows 4D execution, live server readiness or inference was
established by this release.

Independent post-merge
[Publisher gates 41725614176 attempt 2](https://github.com/miyako/llama-cpp/actions/runs/41725614176/attempts/2),
[integrity 41725614260](https://github.com/miyako/llama-cpp/actions/runs/41725614260)
and [Pages 41725614258](https://github.com/miyako/llama-cpp/actions/runs/41725614258)
all completed successfully at the merge SHA. The read-only publisher gate's
first attempt was allocation-cancelled; its later passing execution is
separate from the production signing/publication and public-download evidence.

#### Reusable lessons without a publisher rollout

- Inspect the actual imported P12 identity, not an ambient matching identity.
  Keep temporary keychains, `HOME` and `CFFIXED_USER_HOME` isolated; redact
  receipts and independently clean up credentials and verification mounts.
- Require separate Accepted submission, exact ticket coverage, strict container
  signature, staple validation and affirmative Gatekeeper assessment. Apply
  hardened-runtime/entitlement requirements to the relevant code objects,
  not the DMG as though it were an executable; ZIP/raw CLI cannot be stapled.
- Preserve the project's reviewed native payloads and entitlement policy.
  Do not copy compute-only hash permissions or this legacy server allowlist
  into another wrapper without its own object/architecture/compatibility audit.
- Bind reviewed source, version-only descendant, run, attempt and final bytes.
  This publisher uses an atomic fast-forward branch/new-tag push after gates,
  then downloaded-draft verification before public visibility; never overwrite
  an existing tag/release to recover from failed gates.
- Keep allocation cancellations, read-only tests, trusted signed candidates,
  actual production publication and independent public downloads distinct.
  Accepted distribution does not establish a diagnostic-free or live adapter
  runtime result.

For implementation mechanics use `native-artifact-provenance` and the pinned
publication contract, not a new wrapper-wide signing implementation. This
verified project fix grants no skills publication or other-project rollout.

### Prerequisite release recovery does not upgrade the consumer

Later [hash 20.0.3](https://github.com/miyako/hash/releases/tag/20.0.3)
targets source `166d392f9672740f510142d299d559327cdbe6ab`; final `hash.zip`
SHA-256 is `50f557befa8e6fa24c2dee9242bf8d9b32dfd4678bf1b4a6baa1d24f3cc65679`.
The original [41741807348](https://github.com/miyako/hash/actions/runs/41741807348)
remains **failed**, not relabeled by successful release recovery.
[Uploader repair](https://github.com/miyako/hash/commit/222652cdabcb632a8f058c2171bae43298937516)
supplied the actual byte Content-Length after HTTP `Bad Content-Length`;
character counts or an unknown-length stdin stream were not equivalent.
The owner separately authorized completing the existing owned empty private
draft using the same signed candidate/source: no rebump, resigning, overwrite
or fabricated CI context. Retained producer verification records and public
source/digest metadata support the recovery, not a new successful original run.
This is a bounded recovery lesson, not permission to repair arbitrary releases.
The consumer's [reviewed manifest](https://github.com/miyako/llama-cpp/blob/e3c28a49ad4bac5f7b8d66d9fedb850f58de24e2/llama-cpp/Project/Sources/dependencies.json)
still deliberately pins **hash 20.0.1**. A newer prerequisite release does
not authorize a dependency bump, change an old local checkout or establish
consumer runtime compatibility.

The applying session also reports shutdown failures on 20.8, 21.1 and
21 R4, including a minimal unrelated project. Exact saved per-engine control
outputs were not recovered. A
[`minimal ping method`](https://github.com/miyako/hash/blob/c0fc53089bea0746434585c152b4448db88512a0/tests/compiler/Project/Sources/Methods/ping.4dm)
and the
[`build narrative`](https://github.com/miyako/hash/blob/c0fc53089bea0746434585c152b4448db88512a0/docs/BUILD.md)
are preserved source, not substitutes for those missing execution artifacts.
Preserve bounded controls,
phase/assertion markers and independent engine exit; these observations do
not establish a wrapper-caused crash or a general platform/version defect.
`errors: []` or `success: true` cannot turn a nonzero engine exit into a
runtime pass. No retry-until-green, hidden cache cleanup or extrapolation
from later passing fixtures is justified.

For broader rollout, recheck component publication and relevant target-engine
results separately from this verified merge. Keep rollback scoped to the
integrity code, reviewed dependency, docs and tests together; do not delete
user caches. Neither the prerequisite
release nor consumer publication approval authorizes another wrapper rollout
or publishing this skill.
