---
name: native-artifact-provenance
description: >
  Build native binaries from upstream source across Linux, macOS and Windows,
  preserve legacy wrapper compatibility, assemble cross-platform packages,
  record provenance and checksums, and diagnose packaging CI failures.
  Use for deterministic release candidates, compiler harness isolation,
  macOS signing/notarization and verification of exact published bytes.
---

# Portable native artifact provenance

## Diagnose the complete pipeline

Inspect the exact failed run, commit, job, step and logs before changing code.
Distinguish tooling-test failures, compiler failures, runtime smoke failures,
package validation and publication. A successful native build does not prove its
artifact can be combined with artifacts produced on other operating systems.

After fixing an early failure, follow all targets through final packaging.
Download actual native CI artifacts when useful and validate their manifests on
the packaging host. This can reveal the next failure while a packaging runner is
still queued. Report local packaging verification separately from remote CI.

Before rerunning a workflow, inspect its jobs and reusable workflow callers.
Build/test-only runs are not interchangeable with workflows that bump versions,
push tags, sign, deploy or publish releases.

Exercise the actual reusable-workflow caller and same-run artifact handoff, not
only a parallel build-only approximation. A credential-free dry run must restore
the real candidate, pass it through native builds and component compilation, and
exercise postcompile source/candidate guards and downstream artifact validation.
A prebuild cleanliness check alone does not establish postbuild cleanliness.
Keep PR validation read-only and explicitly exclude PR events from production
jobs. An existing default-branch `workflow_dispatch` may support running a
feature ref without merging; check availability before assuming integration is
required.

Distinguish release blockers from missing conveniences. A patch/minor/major bump
workflow is useful but not required to release an already synchronized version.
Audit version selection, metadata synchronization, tag creation and publication
as separate operations; do not imply a release workflow performs all four.
Before publication, refresh actual repository visibility, merged revision, tags,
release assets and opt-in variables. Confirm public publication if it differs
from the user's authorized private scope; never change visibility implicitly.

When configuring release secrets, consult a user-referenced prior session or
setup script before asking for credential locations again. Prefer existing
Keychain reuse without a certificate-import override. Never print secret values,
assume GitHub can export existing secrets, or equate secret registration with
implemented signing. Keep human certificate confirmation in an interactive
terminal when the existing script requires it.

Test source initialization with a real temporary Git repository: fresh clone,
cached checkout and dirty-source rejection. `git clone --no-checkout` leaves
tracked files absent, so a clean-worktree guard can mistake initialization for
mass deletion. Populate a fresh checkout before applying the normal guard;
never reset an existing dirty cache to hide changes.

## Serialize portable paths

Manifest paths are a portable format, not host-native filesystem strings.
Use forward-slash relative paths:

```python
key = path.relative_to(output).as_posix()
```

Sort manifest inputs by their relative POSIX strings as well, not native `Path`
ordering: Windows ordering is case-insensitive and can change a source digest
even with identical LF bytes. Cover mixed-case names with `PureWindowsPath`
regressions and real native artifacts.

`str(path.relative_to(output))` emits backslashes on Windows. A strict validator
expecting `Windows/engine.exe` will reject `Windows\\engine.exe`, even when every
file exists.

Keep the validator strict. Add a regression that exercises `PureWindowsPath`
serialization on non-Windows hosts as well as native Windows CI. Simulate the
path representation at the manifest boundary, not the underlying filesystem.

## Stabilize bytes before hashing

Git checkout conversion can change LF to CRLF on Windows. Identical commits can
therefore yield different SHA-256 values for checked-out lockfiles and licenses.
Do not silently normalize arbitrary files inside the checksum function: the
checksum must continue to identify the exact bytes shipped or used.

For repository-owned text inputs that must hash identically, declare LF checkout
bytes explicitly in `.gitattributes`. Quote paths containing spaces:

```gitattributes
Cargo.lock text eol=lf
"component/third party/LICENSE.txt" text eol=lf
```

For an upstream license, export the bytes from the verified immutable Git object
instead of copying a potentially converted working tree file:

```python
license_bytes = subprocess.check_output(
    ["git", "show", f"{revision}:LICENSE"], cwd=source
)
destination.write_bytes(license_bytes)
```

Use binary subprocess output and binary writes; text-mode newline conversion
would reintroduce the problem.

Verify checkout behavior with `core.autocrlf=true` and `core.eol=crlf`, checking
that declared inputs remain byte-identical. An unconstrained control text file
should convert to CRLF, demonstrating that conversion was actually exercised.
When diagnosing a mismatch, compare the recorded hash with both LF and
CRLF-transformed input hashes before assuming corruption or a source mismatch.

## Test permissions according to the host

Windows does not implement POSIX execute bits the same way as Unix. An extensionless
macOS executable fixture may not report `stat().st_mode & 0o111` on Windows even
after `chmod(0o755)`.

Assert that packaging requests the intended chmod on every host. Additionally
inspect POSIX execute bits on Unix, and run real executable smoke checks on each
native target. Do not disable the Windows test suite or relax provenance checks
to avoid Unix-specific permission assertions.

## Preserve the source-to-package chain

- Verify the actual upstream package, binary and server subcommand; a similarly
  named standalone server may expose different behavior.
- Resolve release tags to immutable commits and compare with default-branch HEAD.
  Existing binaries may already report the latest version without having any
  reproducible build provenance.
- Pin the source revision, Rust toolchain, dependency lock and explicit features.
  An upstream Rust minimum is not proof that newly resolved dependencies build
  on that compiler.
- Check runtime/tool installer availability for every runner architecture from
  authoritative manifests. Do not assume a Python version available on Windows
  x64 also has a native Windows ARM64 distribution.
- Record and validate target, features, compiler, source revision, lockfile,
  license and executable hashes. Reject mixed or incomplete target sets.
- Smoke-test each native executable before assembling universal/distribution
  artifacts, then validate the final resource layout and packaged component.
- State whether checksums describe pre-signing artifacts: signing changes bytes.
- Keep artifact staging after version-bump actions that require a clean Git
  working tree, and before component compilation. Otherwise tools such as
  `npm version` or `git pull --rebase` may fail on modified bundled executables.
- Keep a runner-queued job distinct from a failed job. Preserve the target and
  validation requirements rather than changing them merely to clear the queue.

## Resolve one source snapshot for the matrix

Define "latest" explicitly. If it means GitHub's latest published stable release,
query that API once in a source-resolution job, resolve the returned tag to a
full commit SHA, and pass the same metadata to every target. Do not let matrix
jobs resolve moving tags independently. Support exact tag/full-SHA overrides
without silently falling back to a branch or another release.

Inspect the pinned upstream Makefile, release configuration, module requirements,
generated-code prerequisites and embedded UI build. Historical commands, Go
build tags and linked inference libraries may no longer describe the current
server. Use dependency locks rather than dependency-updating commands where
possible, and record actual toolchain versions. Source-pinned rebuildability is
not the same as byte-for-byte reproducibility across different toolchains.

For version-changing releases, resolve default-branch HEAD once and prepare one
version-only candidate commit. Select one authoritative version and synchronize
package, CLI, component metadata and exact-version contracts before building.
Promotion removes a prerelease suffix without incrementing the numeric version:
`0.1.0-rc.2` -> `0.1.0` is distinct from a patch bump. Transport the exact
candidate commit in a checksum-verified source bundle (or equivalent immutable
snapshot) shared by the native matrix, compiler and signing jobs; do not rebuild
from a newly resolved branch HEAD.

Use an explicit reusable-workflow/publication handoff. Tags pushed using
`GITHUB_TOKEN` do not trigger another workflow; do not rely on an implicit tag
event to complete the release. Set prerelease and Latest flags deliberately for
the selected channel rather than renaming an existing RC release into stable.

## Separate new artifacts from legacy wrapper behavior

A new release matrix is not permission to remove existing wrapper platforms.
Keep three contracts distinct:

- Newly built and tested server artifacts.
- Unchanged legacy executables already bundled with an application/component.
- Independently managed servers accessed through HTTP.

Preserve legacy executable selection, managed-process reuse and platform-specific
quoting unless deprecation is explicitly requested. Probe actual bundled and new
CLI help for common arguments before changing wrapper defaults. Exit zero with
empty `--version` output is not version evidence; component versions, filenames
and Go compiler metadata do not establish the upstream server version.

Do not pass modern-only flags to legacy binaries by default. Scope such options
to a verified replacement, and document whether executable/resource/PATH lookup
checks architecture or version. If replacement is manual, require target,
checksum, provenance and nonempty version/help verification. Do not imply that
the new server workflow automatically refreshes component resources.

For process-manager integration, verify installation completes before server
startup, nonzero exits propagate failure, and shutdown does not construct an
object whose constructor starts a process. Include persistent compatibility
regressions; label static source/fixture checks separately from application
runtime validation.

## Distinguish server readiness from inference readiness

A source-built server and embedded web UI may have no inference backends, model
weights, Python environments, GPU drivers or backend shared libraries. Document
these separately rather than implying offline inference out of the box. Backend
galleries can move independently of the pinned server. Empty configuration
collections may select downloadable defaults, not disable downloads.

Audit runtime dependencies on each actual native target. A CGO-disabled Go
server does not prove that inference backends are static or dependency-free.
Fail packaging for unbundled required libraries instead of silently publishing
an incomplete distribution.

Smoke-test the extracted archive with isolated writable directories and explicit
loopback binding. Verify expected version/full SHA, CLI help, liveness, readiness,
an empty model listing and the embedded UI without downloading models/backends.
Use explicit installed model IDs in inference examples. A healthy empty server
does not validate inference or wrapper runtime behavior.

Keep server and component publication separate when needed. Make publication
explicitly opt-in, avoid unintentionally replacing the component's latest
release, and distinguish ad-hoc signing from Developer ID signing/notarization.
Report local build evidence separately from unrun hosted targets and unavailable
application runtimes.

## Distinguish tool4d checks from real 4D component loading

tool4d does not load components. Do not describe a tool4d fixture, successful
compilation, namespaced call or Smoke report as proof that an external component
loads in the normal 4D application. Inspect how the fixture makes its classes
available and report only what that execution actually establishes.

Validate component installation and loading with the actual 4D application and
the exact packaged artifact. Record user-reported manual acceptance separately
from automated evidence, including only the platform and operations actually
reported; do not infer Windows/Intel support or successful shutdown.

A tool4d shutdown crash remains a failed tool4d process even if its Smoke report
says success. Keep that tooling/harness failure distinct from a demonstrated
component failure in real 4D. If the user confirms the same signed package works
in real 4D, do not continue treating the tool4d-only crash as a component release
blocker. Preserve the diagnostics without weakening checks or claiming the
tool4d run passed.

## Verify the published macOS distribution

Treat signing and notarization as fail-closed gates. Inspect external actions for
`continue-on-error` and success-shaped outputs; process completion alone is not
acceptance. Require explicit notarization `Accepted` status, expected Developer
ID team, secure timestamps and appropriate hardened runtime settings. Sign real
code objects rather than arbitrary resource files, then regenerate final-byte
inventories after all byte-changing operations.

Signing contents, signing the DMG container, notarizing and stapling are separate
operations. A valid stapled ticket does not prove that the DMG container has a
valid signature or passes Gatekeeper. Inspect reusable signing actions rather
than assuming they sign both payload and image. Validate the downloaded release
with `codesign --verify --strict`, `xcrun stapler validate` and the appropriate
`spctl` assessment for each artifact. Report container and payload results
separately.

Choose assessment policy by artifact type and proven evidence, not exit code
alone. A notarized bare CLI can fail `spctl` with exit 3 and the exact diagnostic
`the code is valid but does not seem to be an app`. Only classify that known
diagnostic as a failed, non-applicable app probe when every payload code object
independently passes
`codesign --verify --strict --all-architectures --check-notarization -R=notarized`.
Retain the failed probe and `applicable: false`; never relabel it accepted.
Any other rejection or absent notarization remains fatal, and the DMG must
still pass its own signature, staple and Gatekeeper checks.

Apple `Accepted` is not successful stapling or staple validation. Preserve
stapler failures (including exit 68) as failures; investigate submission and
ticket evidence and use only bounded, evidence-based retries, not endless
rebuilds or ignored errors.

Component packaging can re-sign an embedded CLI with different entitlements.
Its bytes may legitimately differ from the standalone signed CLI. Verify each
distribution's own final-byte checksums and signatures; compare source
provenance and Mach-O UUIDs as supporting evidence of build identity rather than
requiring cross-distribution byte equality or treating UUIDs as integrity proof.

When publication is authorized, follow the workflow through public release
assets, not merely dispatch or successful compilation. Download the actual
published archives, verify checksums, extract and smoke-test the shipped binary.
Keep standalone native and normal component releases distinct, and verify that
the intended component remains GitHub's Latest release.

Delay pushing a version commit/tag until signing and package gates pass. Target
the actual version commit rather than implicitly tagging default-branch HEAD.
Before creating release refs, reject a moved default branch or an existing
target tag. Where applicable, push branch and tag atomically with fast-forward
protection, never overwrite an existing release/tag, and verify downloaded
draft-upload bytes before making the release public. Separately authorized
publication against an existing immutable tag must verify that exact tag,
not recreate it.

Reuse fully accepted signed/notarized preflight bytes when they are already the
intended release payload; tagging alone does not require rebuilding the DMG.
Revalidate the immutable tag's exact source commit, producing workflow/run
identity, native/compiler/harness evidence, signing/notarization gates and
complete final-byte inventory before draft upload and download comparison.
This is promotion of an accepted artifact, not fallback to artifacts from a
failed run or a different revision. A failed fresh build never makes its own
partial output eligible, nor does an earlier success waive any publication gate.

## Package Swift and Metal runtime closure

A successful Swift release build can still depend on the build machine's Xcode.
Inspect Mach-O imports and rpaths, including compatibility libraries such as
`libswiftCompatibilitySpan.dylib`. Use Apple's `swift-stdlib-tool` to copy required
redistributable runtimes unmodified, preserve their vendor signatures, include
the corresponding license, and remove build-machine-specific rpaths. Re-sign
modified executables before final signature checks and hashing. Audit the
dependency closure, architecture and minimum OS for every shipped code object.

Stage all required SwiftPM resource bundles and source-compiled Metal libraries;
the executable alone is not a complete installation. Smoke-test from an unrelated
directory with the upstream build tree temporarily unavailable, restoring it
afterward. Confirm delivered runtime/resource loading separately from inference;
successful Metal kernel loading is not model acceptance.

## Require actual 4D compilation success

External component-packaging actions may return success and produce an archive
despite missing dependency classes or compiler diagnostics. Install explicitly
pinned, checksum-verified component dependencies and independently require a
structured `Compile project` report with `success: true` and no diagnostics before
packaging. Apply the same guard to validation and every production build path.
Handle `.4DZ` filename casing explicitly rather than assuming `.4dz`.

Run compiler/tool harnesses from isolated copies under an ignored build
directory, not the tracked tooling project. Opening a project can generate
`Project/DerivedData/`, `Project/Sources/catalog.4DCatalog` and settings changes
even when compilation succeeds. Check staging paths for symlink escapes before
launch; preserve the real component target and its input/output digests.
Keep strict source/candidate guards after compilation in the same production
caller exercised by the dry run. Test representative generated outputs and
unchanged tracked harness bytes; do not broadly ignore source/catalog paths or
reset the checkout to make the guard pass.

Verify the actual compiled component archive and its packaged native executable,
not merely archive existence. Preserve source-build hashes as explicitly
pre-sign provenance when component signing changes embedded bytes; maintain a
separate final signed-byte inventory.

## Diagnose cache-sensitive model failures

A server can compile and pass CLI checks yet fail inference because a persistent
model cache contains incomplete downloads. Reproduce once with a fresh isolated
cache using the runtime's actual cache mechanism; an unrelated environment
variable such as `HF_HUB_CACHE` may not control a native Foundation downloader.
Do not delete the user's cache or silently redirect normal operation to hide
the problem.

Check downloader terminal states explicitly: a stream ending or leaving a
progress phase does not establish a completed download. Error and paused states
must not be treated as loaded. Separate cache/downloader failures from missing
packaged runtime assets, and verify inference with the actual published signed
binary when feasible.

For Metal-backed engines, derive supported GPU architecture and minimum OS from
the pinned source, shader language/compiler requirements and final Mach-O load
commands, not historical platform claims. Record the OS actually exercised;
passing on a newer macOS does not validate the minimum deployment version.

## Deliver the distribution's Pages site

When matching a reference site, inspect rendered HTML, layout overrides and CSS;
Markdown extraction hides the design. A stock Jekyll theme can retain a narrow
column and obsolete sidebar even when the guide text is correct. Put supported
platforms, actual release downloads and a working quickstart first; link deeper
integration and build/provenance guides separately. Do not copy the reference
product's platform or API claims.

Distinguish a green PR Pages build from a live deployment. Inspect Pages
environment branch restrictions; do not weaken them to deploy a feature branch.
Obtain merge authorization when needed, isolate site-only changes, then follow
the default-branch deployment and verify the actual public site. A docs update
should not republish a component or change release assets.

Check all pages at desktop and narrow mobile widths, including overflow,
base-path-prefixed links/assets, anchors, clipboard text, keyboard skip links
and browser errors. Validate the deployed pages as well as a local preview.
For resource-logo reuse, preserve the original artwork and unrelated untracked
files; copy the selected image into published assets, update every logo consumer
and compare public asset bytes with the source. A new asset URL can avoid stale
old-logo caches.
