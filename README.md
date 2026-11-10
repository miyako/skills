# skills

[Agent Skills](https://agentskills.io/home) for 4D development.

The skillset lives in [`4d-skills/`](.): a root
[`AGENTS.md`](AGENTS.md) that routes tasks to skills, one folder
per skill under [`4d-skills/skills/`](skills) (each with a
`SKILL.md`), and the validation schemas under
[`4d-skills/schemas/`](schemas). Every topic has exactly one
owning skill; the others link to it.

## Skills

### 4D artifacts and tooling

| Skill | Scope |
|---|---|
| [`4dproject`](skills/4dproject/SKILL.md) | The project as a whole: `.4DProject`, version detection, token suffixes, folder layout, `menus.json`, the canonical `.gitignore`, component release tags and Dependency manager version rules |
| [`4dcatalog`](skills/4dcatalog/SKILL.md) | `.4DCatalog` database schema: structure, DTD validation, diagrams |
| [`4dform`](skills/4dform/SKILL.md) | `.4DForm` JSON: objects, list box defaults, layout geometry and overlap checks, form documentation index, schema validation, quick PNG assessment with `fourdform` (macOS/Windows), then 4D/tool4d captures for a second opinion when needed |
| [`4dsettings`](skills/4dsettings/SKILL.md) | `.4DSettings` (placeholder) |
| [`4dlsp`](skills/4dlsp/SKILL.md) | `.4dm` validation, syntax check and code intelligence with `tool4d-lsp-stdio` |
| [`4dlang`](skills/4dlang/SKILL.md) | Classic command and OOP class member lookup; documentation and forum search |
| [`4dcli`](skills/4dcli/SKILL.md) | Running tool4d / 4D from the command line: tests, compile, form rendering |
| [`4dtools`](skills/4dtools/SKILL.md) | Provisioning the helper binaries the other skills use |

### 4D development topics

| Skill | Scope |
|---|---|
| [`4dplugin`](skills/4dplugin/SKILL.md) | Native C/C++ plugin string ownership, text-array lifetimes, callbacks and non-release validation |
| [`4dmethods`](skills/4dmethods/SKILL.md) | Method attributes and which methods to hide from the Run Method dialog |
| [`4dmodernise`](skills/4dmodernise/SKILL.md) | `C_*` → `var` / `#DECLARE`, deprecated `_o_` commands and their replacements |
| [`4dcss`](skills/4dcss/SKILL.md) | Form stylesheets, dark mode, Liquid Glass / Fluent UI form themes |
| [`4dlocalise`](skills/4dlocalise/SKILL.md) | XLIFF localisation, `Localized string`, attributes that follow the UI language |
| [`4dstartup`](skills/4dstartup/SKILL.md) | The non-blocking startup window pattern and chaining forms |
| [`4daikit`](skills/4daikit/SKILL.md) | 4D AI Kit: chat, vision, async callbacks and streaming |
| [`4dorda`](skills/4dorda/SKILL.md) | ORDA queries and placeholders, null handling, saving and locking, `fromCollection`, vector similarity |

### Technote-localisation repositories only

Used only in repositories created from
[4d-technote-localisation-template](https://github.com/miyako/4d-technote-localisation-template)
(a `technote.json` at the root).

| Skill | Scope |
|---|---|
| [`technote-localise-4d-project`](skills/technote-localise-4d-project/SKILL.md) | Localising the 4D demo under `demo/` |
| [`technote-apply-glossary`](skills/technote-apply-glossary/SKILL.md) | Changing a term across glossary, text and figures |
| [`technote-review-figures`](skills/technote-review-figures/SKILL.md) | Reviewing and fixing localised figures |
| [`technote-localise-screenshots`](skills/technote-localise-screenshots/SKILL.md) | Mechanical screenshot text replacement with authoritative UI strings, context-correct fonts and rendering verification |
| [`technote-localise-demo-data`](skills/technote-localise-demo-data/SKILL.md) | Replacing the demo's sample data and recomputing the examples |
| [`technote-release`](skills/technote-release/SKILL.md) | Publishing the PDF and demo zip as a GitHub release |

## Using the skills in a 4D repository

The [`dist`](https://github.com/miyako/skills/tree/dist) branch contains
only the skillset: the content of `4d-skills/` at its root (`AGENTS.md`,
`skills/`, `schemas/`, `MIGRATION.json`) plus this README and `VERSION`.
It is published automatically from `main` by
[`publish-dist.yml`](https://github.com/miyako/skills/blob/main/.github/workflows/publish-dist.yml).
Add it as a submodule at `.agents`:

```sh
git submodule add -b dist https://github.com/miyako/skills.git .agents
```

After cloning a repository that already has it:

```sh
git submodule update --init .agents
```

(`--recursive` is not needed: the `dist` branch has no submodules.) To pick
up a newer skillset, run `git submodule update --remote .agents` and commit
the new submodule commit.

Once mounted:

* skills live at `.agents/skills/<name>/SKILL.md`, where agent hosts that
  scan `.agents/skills/` discover them;
* schemas live at `.agents/schemas/`;
* `.agents/AGENTS.md` holds the skill-selection table. Point to it from the
  repository's own root `AGENTS.md` (e.g. "For 4D work, read
  `.agents/AGENTS.md` and the skills under `.agents/skills/`"), since a
  nested `AGENTS.md` is not read automatically;
* tools provisioned by `4dtools` still go under the **consumer** repository's
  `tools/<skill>/` (e.g. `tools/4dlsp/`), never inside `.agents/`. Git-ignore
  only those directories, not the whole `tools/` folder -- see
  [`4dproject`](skills/4dproject/SKILL.md) for the canonical
  `.gitignore`.

## Helper tool releases

Helper binaries are built from pinned sources by the **Build and Release**
workflow and published as assets of
[`miyako/skills` releases](https://github.com/miyako/skills/releases).
The `dist` branch carries skills and installers, not the binaries.
Updating the skillset does not build or replace installed tools.

All macOS release targets use `.github/scripts/notarize.py`: submit once,
then poll the same submission ID for up to 20 minutes. Failed status
requests are retried every 15 seconds (each request is capped at two
minutes); only `Accepted` allows packaging to continue. Rejected/invalid
submissions fail immediately with Apple's diagnostic log. Submission
requests have a separate five-minute limit and are not retried automatically
because a failed upload request can have an unknown outcome.

The submission ID is printed before polling. To resume an existing submission
without uploading again, set `APPLE_ID`, `APPLE_PASSWORD`, and `TEAM_ID`
securely in the environment, then run:

```sh
python3 .github/scripts/notarize.py --submission-id <submission-uuid>
```

Resuming only checks notarization; it does not resume a GitHub Actions job.
Rerunning an old workflow uses that run's original code and submits again,
so it does not validate this retry helper.

`fourdform` follows this model: the pinned `vendor/4d-form` source uses
the merged Windows-support revision from
[`miyako/4d-form#2`](https://github.com/miyako/4d-form/pull/2), while the
CLI version remains `0.1.0`. `_fourdform-macos` builds
`fourdform-macos-arm64.tar.xz` and `fourdform-macos-x64.tar.xz`; these
macOS 12+ builds remain Developer ID signed and notarized. Windows
builds use upstream `scripts/build-windows.ps1` to produce unsigned
`fourdform-windows-x64.zip` and `fourdform-windows-arm64.zip`.
Windows 10+ and the Evergreen Microsoft Edge WebView2 Runtime are required.
Linux is unavailable.

After merging the release integration, dispatch **Build and Release**
with a release tag before provisioning the new assets. The installer
uses the latest stable skills release, verifies `SHA256SUMS` and available
GitHub asset digests, checks `--version` and `--help`, and installs the
staged, verified files into `tools/4dform/` with rollback on write failure.
The multi-file installation is not concurrently atomic.
The executable is `fourdform` on macOS or
`fourdform.exe` on Windows; Windows packages include companion Swift/MSVC
DLLs and the WebView2 license notice, all installed side by side.
It does not fall back to the older upstream release.

From a **consumer 4D repository** with the skillset mounted at `.agents`:

```sh
python3 .agents/skills/4dtools/scripts/provision_fourdform.py --repo-root "$PWD"
```

The `miyako/skills` **source checkout** has no `.agents` submodule.
To use its installer, pass the actual consumer repository path:

```sh
python3 4d-skills/skills/4dtools/scripts/provision_fourdform.py \
  --repo-root /path/to/4d-project
```

On Windows, use `python` with the same script and `--repo-root` arguments
(for example, `--repo-root (Get-Location).Path` in PowerShell).
Compatible existing installations are reused; incompatible installations
require `--replace`. Use it also to explicitly reprovision, including
migration from an older universal binary. See
[`4dtools`](skills/4dtools/SKILL.md) for the complete installation
and platform checks, and [`4dform`](skills/4dform/SKILL.md) for
platform-specific themes. These are static reference previews, not real
4D runtime captures or native screenshots.

## Updating language lookup data

The CLI submodule pins use a **21 R5 BETA** snapshot from
`miyako/4d-static-docs` commit
`1dfd4e7eb832d19361f8ec1f4801603899087ca3`, containing 1,460 classic commands
and 528 OOP members. Source documentation, syntax/constants captures,
reviewed conflicts and fixture `checkSyntax` evidence are hash-bound upstream.
This is not a runtime or full-application compilation guarantee.

For a new 4D release, update and review both corpora in `4d-static-docs`
first. In each CLI repository, import the same explicit upstream commit:

```sh
scripts/refresh-vendor.sh <source-commit> <local-4d-static-docs-clone>
cargo test
cargo build --release
```

Review lookup changes and beta/version provenance, commit and publish the
two CLI revisions, then update their `vendor/` submodule pins here. Dispatch
the **Build and Release** workflow with a release tag to publish new helper
binaries. Updating `.agents` in a consumer repository does not replace its
installed tools; reprovision both `tools/4dlang/` binaries using `4dtools`
after the updated release is available. See
[`4dlang`](skills/4dlang/SKILL.md#corpus-version-and-verification-scope)
for verification limits and conflict inventory locations.

## Migration from `.github/instructions`

Many 4D repositories used to carry copies of the same
`.github/instructions/*.instructions.md` files and `.github/skills/`
folders. Their generic 4D content now lives in the skills above;
repository-specific rules stay in each repository.
[`4d-skills/MIGRATION.json`](MIGRATION.json) maps every old file to
its new home (`instructions.<file>.status`: `skill`, `instruction` or
`deleted`; legacy `.github/skills/` folders are under `skills`).

| Old file | New home |
|---|---|
| `variable.declarations`, `deprecated.commands` | `4dmodernise` |
| `method.visibility` | `4dmethods` |
| `menu` | `4dproject` |
| `listbox` | `4dform` |
| `css`, `tahoe.css` | `4dcss` |
| `localisation` | `4dlocalise` |
| `aikit.async` | `4daikit` |
| `startup` | `4dstartup` (generic pattern); HDI splash specifics stay as `.github/instructions/hdi.startup.instructions.md` |
| `4d-docs`, `4d-form-layout` skills | `4dform` (doc index, layout, `form_layout_calc.py`); search fallback in `4dlang` |
| `apply-glossary`, `review-figures`, `localise-demo-data`, `release-technote`, `localise-4d-project` skills | `technote-*` skills (generic 4D parts of `localise-4d-project` → `4dlocalise` and the other 4D skills) |
| `readme.structure`, `readme.branches`, `technote-translation` | Stay in their repositories under `.github/instructions/` |
| `copilot-instructions.md` | The repository's root `AGENTS.md` |
| `readme.usage.guidance`, `readme.hdi` | Deleted |
