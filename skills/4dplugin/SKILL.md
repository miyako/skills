---
name: 4dplugin
description: >
  Native 4D plugin string ownership and maintenance: PA_Unistring lifetimes,
  PA_SetStringInArray transfer, borrowed getters, scalar/callback aliases,
  ownership regressions, and non-release build validation. Use when developing
  or auditing C/C++ 4D plugins, investigating text-array crashes, or reviewing
  PA_* string allocation, assignment and cleanup.
---

# Native 4D Plugin String Ownership

## Scope and evidence

This skill owns native plugin string-lifetime guidance, not 4D component
releases or general `.4dm` development. Use [4dlsp](../4dlsp/SKILL.md) for
syntax checking changed 4D test methods and [4dcli](../4dcli/SKILL.md) for
running them in 4D/tool4d.

Inspect the SDK headers and implementation actually compiled by the plugin,
including wrappers and platform-specific copies, before changing cleanup.
Record the repository revision and SDK provenance; identical API names do
not prove identical ownership across versions.

The baseline below is the bundled
[4DPluginAPI.c at Poppler commit 39a961c](https://github.com/miyako/4d-plugin-poppler/blob/39a961c8fbe543640fcb3c53d483fb90bbe22586/4D%20Plugin%20API/4DPluginAPI.c).
Its header says `rev : v14`; this is not a verified upstream SDK release
identifier or a guarantee about every SDK version.
[Poppler #11](https://github.com/miyako/4d-plugin-poppler/pull/11) fixed an
immediate dispose after text-array insertion. The original compiled plugin
failed an ownership-tracking host shim and the fix passed it; that evidence
does not reproduce the exact Windows 4D host crash.

## Classify each allocation and alias

Track the underlying allocation, not just the local `PA_Unistring` struct.
Classify each value as **owned**, **borrowed**, **copied** (an independent
allocation), or **transferred** (ownership passed to another owner).
Struct assignment alone does not copy the character buffer. For each path,
identify who disposes the allocation, when the last consumer finishes, and
whether an error, callback or abort changes the owner.

| API / operation in the baseline | Ownership consequence |
|---|---|
| Successful `PA_CreateUnistring` | Creates a caller-owned string requiring disposal or transfer. Check allocation/API errors. |
| `PA_GetStringInArray` (lines 4738-4755) | Returns a borrowed struct alias to the element. Do not modify or dispose its buffer; do not retain it across replacement, resize or clear. |
| `PA_SetStringInArray` (lines 4933-4947) | On accepted assignment, disposes the old element then shallow-assigns `*pt = *ustr`. Ownership of the supplied allocation transfers to the array; the caller's struct is not reset. |
| `PA_SetStringVariable` (lines 4254-4259) | Shallow-assigns the string into the variable. Analyze the variable's consumer, lifetime and cleanup; this is not an independent copy. |
| `PA_ReturnString` / `PA_SetUnistring` (lines 2600-2603 / 289-299) | The return helper calls the engine-backed content setter with a UTF-16 buffer, not the array's struct-transfer implementation. Verify its copy/lifetime contract for the compiled SDK and host; do not apply the array cleanup rule by name alone. |
| `PA_SetStringField` (lines 3741-3754) | Explicitly non-owning in this SDK: the caller remains responsible for disposing an owned input when no longer needed. |

### Transfer is conditional

The baseline array setter returns `void`. It only assigns for
`eVK_ArrayUnicode`, non-null array data, `0 <= i <= fNbElements`, and a
non-null string pointer. Rejected destinations do not consume the supplied
allocation. Do not infer success from the function returning or a stale SDK
error code. Check the actual SDK's accepted destination conditions and the
caller's allocation/resize results before deciding ownership changed.
Index zero is accepted by this implementation; preserve the intended 4D
array indexing behavior rather than inventing a different range.

After a confirmed transfer, do not call `PA_DisposeUnistring` on the local
alias or let an RAII destructor dispose it. Release/disarm the local owner
without freeing the transferred allocation. On rejection or any path before
transfer, retain normal caller cleanup and report errors through the
repository's established mechanism. Do not fix a use-after-free by leaking
failed insertions.

Never insert a borrowed getter result directly, reuse the same owned
allocation in multiple elements, or replace an element with an alias to
itself: disposing the old element can invalidate the incoming alias, and
multiple apparent owners can later double-free it. When another owner is
needed, make a verified independent copy using the SDK's supported content
creation/setter operations, preserving explicit lengths and embedded nulls
where required. Do not invent a copy with struct assignment.

### Scalar variables and callbacks

Follow `PA_SetStringVariable` aliases through method invocation, parameter
wrappers, callback retention, reassignment, and variable cleanup. An
independently allocated callback string may correctly be disposed after a
synchronous call if no consumer retains it and no other owner disposes it.
Do not share an array-owned allocation with an independently cleaned-up
callback variable. Delayed callbacks need a lifetime that extends through
their last use, including cancellation/abort cleanup. Do not remove scalar
or callback disposal merely because array insertion transfers ownership.

## Audit and regression procedure

Prioritize command manifests declaring text/string arrays, but do not use
them as an exclusion filter. Also scan scalar-only commands, internal arrays,
shared wrappers and callback helpers for string creation, getters, setters,
struct assignments and disposal. Trace success, rejection, early return,
exception, abort and final cleanup paths. Flag early disposal, borrowed
insertion, one allocation in multiple elements, stale aliases and double
cleanup. Patch the proven ownership error, not every nearby disposal or the
bundled SDK globally.

Use the repository's existing tests where possible. Regression coverage
should read text after allocator churn, replace existing elements,
resize/clear arrays, repeat conversion and final cleanup, and exercise
callback independence and abort paths. Include rejected type/index and
allocation/resize failure paths so cleanup remains correct without a
transfer.

### Faithful host-shim contracts

Derive shim behavior and expected results from the bundled SDK implementation,
comments and engine parameter forwarding, not convenient mock semantics.
Preserve byte lengths versus UTF-16 code-unit counts, buffer-capacity units
and whether capacity/returned length includes a terminator. Where conversion
returns bytes, convert to code units before passing a length to a UTF-16
string wrapper; do not make the shim return units to match a faulty caller.
Also preserve ownership transfers (including shallow assignment, old-element
disposal and rejection) and allocated versus null empty representations.

Assert exact source-derived content and lengths with ASCII, BMP and
supplementary-character fixtures (including surrogate pairs); check capacity
and terminator boundaries and empty results. When feasible, run ASan/UBSan
and show that the original fails because of the actual defect under the
faithful contract, then that the fix passes the same assertions. A passing
ownership shim is not evidence that buffer bounds are correct.

Report shim/sanitizer evidence separately from testing in the actual 4D
host, naming the host version/platform and any unreproduced crash.

## Non-release validation

Inspect project configurations, build phases, post-build scripts and CI
triggers before building. Prefer a non-release configuration or a narrow
test/compile target, and verify that it has no release side effects: even a
Debug build can run packaging scripts. Do not run signing, notarization,
packaging, upload, release-tag creation or binary publication without
explicit permission. Disable such phases only through an existing supported
validation option, or choose another validation path and report its limits.
Keep validation output separate from tracked binaries and do not broaden an
ownership fix into SDK upgrades or release automation changes.
