# Hosted CI release-pipeline failures for 4D component repositories

## Scope and ownership

Use this reference when a GitHub Actions release/acceptance pipeline in a
4D component repository fails in a way that produces no normal error
message. It covers failure modes observed live in a production component
release (2026-11-21, a repository derived from
[4d-component-template](https://github.com/miyako/4d-component-template)).
The template's own validation rules and
[its repo skill](https://github.com/miyako/4d-component-template/blob/main/.github/skills/4d-cli-component/SKILL.md)
own the canonical workflow contract; this page is the triage knowledge.
Component tag/version rules live in
[component-releases.md](component-releases.md); tool4d download URLs and
digest pinning live in `4dcli`, "Obtaining tool4d".

## Job identifiers that start with a digit invalidate the whole file

GitHub Actions job IDs under `jobs:` **must start with a letter or an
underscore**. A job id like `4d-acceptance` does not produce one failed
job -- it renders the **entire workflow file invalid**:

- the run is created and concludes `failure`,
- it has **zero jobs and zero check-run annotations**,
- its display name is the file path (`.github/workflows/ci.yml`) instead
  of the workflow's `name:` field,
- every future push keeps failing silently until the file is fixed.

The workflow name signature is the fastest tell: when a run's title is a
file path, suspect the workflow text itself, not the code under test.

Verified live (2026-11-21): renaming the job to `acceptance-4d` in an
otherwise identical file let the same push create all four jobs (one
concurrency-cancelled but each job enumerated); the digit-first file at
the neighboring commit had created none.

`4d-component-template`'s `workflow_contract.py` rejects such
identifiers proactively; do not bypass that rule when adding jobs.

## Retired hosted runner labels

GitHub periodically retires hosted runner images. A retired label
(`macos-14`, `macos-13`) cancels the affected job **within a second of
start** with a check-run annotation like:

```
The configuration 'macos-14-arm64-us-default' is not supported
```

Because sibling jobs (e.g. preflight) finish `success` first, this reads
like an acceptance failure. It is not: no code under test ran.

Rules:

- pin concrete images (`macos-15`, `ubuntu-24.04`), never
  `*-latest`, in release pipelines that must reproduce;
- keep the labels aligned with the audited gold-standard component
  repositories (e.g. the mirror repository of the same release process);
- on the annotation above, bump the label only; do not add mitigations
  around jobs that never started.

## Evidence that travels between jobs must use root-relative paths

A release pipeline commonly runs acceptance on one runner OS (macOS) and
verification/publication on another (Linux). Any artifact recorded by
the first job -- acceptance evidence, signing proofs, locks, manifests --
must therefore store **root-relative POSIX paths** (`dist/<component>.zip`),
never absolute ones: the verifying job re-derives paths under its own
`/home/runner/...` root, and two absolute paths from different runner
operating systems can never be equal. Failure signature:

```
release asset verification/publication failed: acceptance evidence does
not identify the final archive
```

The template's release scripts enforce the relative form; extensions and
ports must not regress it.

## Expect gitignored cache directories to be absent on the runner

Directories that hold downloaded pinned assets (e.g. the CLI asset cache
under `cli/assets/`) are gitignored, so a hosted runner starts without
them even though the local machine always has them. Any staged download
must create the destination parent first --
`mkdir(parents=True, exist_ok=True)` before opening
`<file>.downloading` -- or it fails with `FileNotFoundError` only in
CI. Test download paths from a clean state (delete the cache locally,
run the downloader) before pushing.

## Artifacts flatten their common path prefix

`actions/upload-artifact@v4` strips the common ancestor of all `path:`
entries. An upload declared as a single `4d/dist/webp.zip` entry stores
a top-level `webp.zip`; a later `actions/download-artifact` must set
`path:` to the directory that reconstructs the layout the verifying
script expects (e.g. `path: 4d/dist`), or verification fails with
"file not found" instead of a hash mismatch -- pointing at the wrong
failure class. Multi-entry uploads keep their real structure
relative to the shared prefix; know which shape each upload produces.

## Triage order for a failed release run

1. Run labeled by file path, zero jobs → workflow-file problem (job id
   / YAML), not code.
2. Job `cancelled` instantly after a successful dependency job →
   retired runner label (annotation on the check run).
3. Verification rejects "evidence does not identify ..." → path or
   digest portability (root-relative rule).
4. `FileNotFoundError` under a repo path that exists locally →
   gitignored cache directory not created in CI.
5. Actual script error inside a job → read the job log and the
   acceptance `build/*.json` diagnostics artifact before changing code.
