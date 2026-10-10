# 4D Development Agent Instructions

## Purpose

This repository provides a collection of Agent Skills for 4D development.

The skills provide 4D-specific knowledge, validation rules, schemas, and
workflows for working with 4D source projects and their associated files.

When working on a 4D project, prefer the most specific 4D skill available
rather than treating a 4D artifact as a generic JSON or XML document.

All paths in this file and in the skills (`skills/...`, `schemas/...`) are
relative to the folder that contains this `AGENTS.md` -- the skillset root.
In a consumer repository the skillset is usually mounted as a git submodule
at `.agents/`, so `skills/4dform/SKILL.md` is
`.agents/skills/4dform/SKILL.md` there. Paths such as `Project/...` and
`tools/...` always refer to the repository being worked on.

## 4D Source Artifacts

Recognize the following 4D-specific artifacts:

* `.4DProject` — 4D project definition
* `.4DForm` — 4D form definition
* `.4DCatalog` — 4D catalog
* `.4DSettings` — 4D settings

Other `.json` and `.xml` files may also occur in a 4D project.

Do not assume that a JSON or XML file is a generic document merely because
of its file extension. Determine whether it is a known 4D artifact before
applying generic processing.

## 4D Tooling

This skillset provides the `4dtools` skill for provisioning platform-specific
command-line tools used by the other 4D skills.

Use `4dtools` when a required tool is not available on the host.

Tools provisioned by `4dtools` are installed under `tools/` at the root of
the repository being worked on -- never inside the skillset (e.g. not under
`.agents/`).

Every tool currently provisioned is used by exactly one 4D skill, so
each is installed into a subdirectory named after that skill (e.g.
`tools/4dcatalog/`, `tools/4dform/`, `tools/4dlsp/`, `tools/4dlang/`),
keeping each skill's tooling isolated. A future tool genuinely needed by
more than one skill would instead stay directly under `tools/`. See
`skills/4dtools/SKILL.md` for the exact destination of each tool.

Git-ignore only those per-skill directories, never the whole `tools/`
folder: repositories may commit their own scripts there. The canonical
`.gitignore` is in `skills/4dproject/SKILL.md`.

Do not install these tools globally or modify the user's PATH.

Prefer an existing compatible system installation of a tool when the
applicable skill permits it. Otherwise use `4dtools` to provision the
required tool.

Do not duplicate tool-download or installation logic in individual 4D
skills.

The `4dtools` skill currently provisions tools such as:

- `xmllint`
- `boon` (JSON Schema validator)
- `tool4d-lsp-stdio` (4D LSP bridge for validation and code intelligence)
- `4d-language-classic` (natural-language lookup service for 4D
  classic-language commands)
- `4d-language-oop` (natural-language lookup service for the 4D object
  (OOP) language class reference)

Individual skills specify which tools they require.

## Skill Selection

Use the most specific applicable skill. Each skill is a `SKILL.md` file
in the `skills/` directory relative to this file. Every topic has exactly
one owning skill; other skills link to it instead of restating it.

### 4D artifacts and tooling

| Task / artifact | Skill | File path |
|----------|-------|-----------|
| `.4DCatalog` (database schema) | 4dcatalog | `skills/4dcatalog/SKILL.md` |
| `.4DForm` (form design + validation, list box defaults, layout geometry, doc index) | 4dform | `skills/4dform/SKILL.md` |
| `.4DProject`, project layout, version detection, token suffixes, `.gitignore`, `menus.json` | 4dproject | `skills/4dproject/SKILL.md` |
| `.4DSettings` (settings) | 4dsettings | `skills/4dsettings/SKILL.md` |
| `.4dm` validation / syntax check / LSP / MCP | 4dlsp | `skills/4dlsp/SKILL.md` |
| 4D command / OOP class member lookup, doc and forum search | 4dlang | `skills/4dlang/SKILL.md` |
| Running tool4d / 4D from the command line (tests, compile, render) | 4dcli | `skills/4dcli/SKILL.md` |
| Tool provisioning | 4dtools | `skills/4dtools/SKILL.md` |

### 4D development topics

| Task | Skill | File path |
|----------|-------|-----------|
| Method attributes, `invisible`, Run Method dialog | 4dmethods | `skills/4dmethods/SKILL.md` |
| `C_*` → `var` / `#DECLARE`, deprecated `_o_` commands | 4dmodernise | `skills/4dmodernise/SKILL.md` |
| Stylesheets, dark mode, Liquid Glass / Fluent UI form themes | 4dcss | `skills/4dcss/SKILL.md` |
| XLIFF localisation, `Localized string`, language-following attributes | 4dlocalise | `skills/4dlocalise/SKILL.md` |
| Startup / first window, chaining forms, `DIALOG(...; *)` | 4dstartup | `skills/4dstartup/SKILL.md` |
| 4D AI Kit, async callbacks and streaming | 4daikit | `skills/4daikit/SKILL.md` |
| ORDA: queries, entity selections, null handling, saving and locking, `fromCollection`, vector queries | 4dorda | `skills/4dorda/SKILL.md` |

### Technote-localisation repositories only

These skills apply **only** in a repository created from
`miyako/4d-technote-localisation-template` (a `technote.json` at the
repository root). Ignore them everywhere else.

| Task | Skill | File path |
|----------|-------|-----------|
| Localise the 4D demo under `demo/` (wrapper over the 4D skills) | technote-localise-4d-project | `skills/technote-localise-4d-project/SKILL.md` |
| Change a term across glossary, text and figures | technote-apply-glossary | `skills/technote-apply-glossary/SKILL.md` |
| Review and fix localised figures | technote-review-figures | `skills/technote-review-figures/SKILL.md` |
| Replace the demo's sample data and recompute examples | technote-localise-demo-data | `skills/technote-localise-demo-data/SKILL.md` |
| Publish the PDF and demo zip as a GitHub release | technote-release | `skills/technote-release/SKILL.md` |

Read the applicable `SKILL.md` before making structural changes to a
proprietary 4D artifact.

Several skills carry longer material under `references/` (and `4dform`
a calculator under `scripts/`). Do not read those files directly -- route
to them through the route table in the owning `SKILL.md`; `4dform`'s table
also states how many of its files a task may open.

`4dcli` is the only skill that runs the 4D or `tool4d` binary itself. It
is separate from `4dtools`, which provisions this skillset's own helper
binaries and does not provision 4D.

Schemas referenced by skills are in the `schemas/` directory relative to
this file:

- `schemas/4dcatalog/base.dtd` -- 4D Catalog DTD
- `schemas/4dform/formsSchema.json` -- 4D Form JSON Schema

A skill may also ship 4D source templates in an `assets/` subdirectory
next to its `SKILL.md`. These are distinct from `tools/` (executables
provisioned by `4dtools`) and from `schemas/` (validation inputs): they
are `.4dm` source intended to be copied into a user's project. Currently
only `skills/4dcli/assets/` does this, providing the startup methods that
drive a project from the command line.

Copying a source asset into a project adds code the user will maintain,
so treat it as a change to their project, not as tool provisioning:
install only what the current task needs, never overwrite an existing
file that differs, and validate the result. The owning `SKILL.md` states
the exact procedure.

Do not duplicate detailed artifact-specific instructions here. Those belong
in the corresponding `SKILL.md`.

## Validation

4D-specific validation takes precedence over generic file-format validation.

For example:

* Valid JSON does not necessarily mean a `.4DProject` or `.4DForm` is valid.
* Well-formed XML does not necessarily mean a `.4DCatalog` or `.4DSettings`
  file is valid.

When a 4D schema or validator is available, use it.

Validation should normally include:

1. File-format syntax validation
2. Applicable 4D schema validation
3. Additional 4D-specific validation where available

After modifying a 4D artifact, validate it before considering the change
complete.

### .4dm source code validation and code intelligence

If the workspace contains a `.4DProject` file and you create or modify
`.4dm` files under `Project/Sources/`, use the `4dlsp` skill to validate
them via the 4D LSP server. Read `skills/4dlsp/SKILL.md` -- in
particular "When to use code intelligence" and "Syntax checking vs
running code" -- for the workflow.

For a project-wide compile-check pass without listing every file, use
`check-syntax` instead of `validate` -- see `skills/4dlsp/SKILL.md` for
its optional-files behavior and current limitations.

For multi-step 4D coding sessions (writing, validating, fixing, exploring
code), use the one-shot subcommands (`hover`, `completion`,
`goto-definition`, `document-symbols`) for a handful of calls, or start a
self-managed persistent server (`tool4d-lsp-stdio mcp --project ...`,
which prints a PID and returns) and reuse it across many calls, stopping
it (`mcp --stop`) at the end of the task -- no host configuration
required. See `skills/4dlsp/SKILL.md` for details; older provisioned
builds may lack these one-shot subcommands, in which case fall back to
its "No MCP client available" section or the host-level suggestion below.

### Suggesting a persistent MCP server to the user

`validate` alone can miss obsolete or renamed 4D commands (see
`skills/4dlsp/SKILL.md`). The one-shot `hover` subcommand (or a
self-managed `mcp --project ...` server, both described above) already
closes this gap without any host configuration -- **prefer that first**.

Only suggest a **host-registered** MCP server as a secondary option, and
only when it would add value beyond what you can already do yourself --
either your provisioned `tool4d-lsp-stdio` build predates the one-shot
subcommands and self-managed server mode (check `--help`), or the user
is working on this same `.4DProject` across a long session (e.g. a full
day) and would rather the host keep one `tool4d-lsp-stdio mcp
--foreground` process alive and attached for the whole time, instead of
you starting/stopping a self-managed server per task.

At the start of a session involving `.4dm` work, if **all** of the
following hold, suggest the user add this as a host-level MCP server
(most agent hosts expose an "Add MCP Server" setting: name, command,
arguments, environment variables, timeout):

* No MCP tool backed by `tool4d-lsp-stdio` already appears in your own
  available tool list (do not suggest this if one is already configured).
* Your provisioned `tool4d-lsp-stdio` lacks the one-shot subcommands
  (`hover`, etc.) and self-managed `mcp --project ...` server mode --
  check `tool4d-lsp-stdio --help`. If those are present, use them
  directly instead of suggesting host configuration.
* The workspace contains a resolvable `.4DProject` file.
* `tool4d-lsp-stdio` is available (in `tools/4dlsp/` or on the system) and
  runnable.
* The session is not running unattended/autonomously (e.g. an autopilot
  or background-agent mode with no user expected to read suggestions or
  act on them). Adopting this suggestion requires a user to edit host
  settings and restart the session -- skip it when no user is available
  to do that, and continue using `validate` (and `hover` directly against
  the MCP server, per `skills/4dlsp/SKILL.md`, if already configured)
  without prompting.

Suggest it once per session, phrased approximately as:

> Adding an MCP server for 4D code intelligence would let me verify
> commands more reliably (catching obsolete/renamed commands that
> `validate` alone can miss) and keep one tool4d session alive across
> this whole task or session instead of restarting it per check. If your
> agent host supports adding MCP servers, use:
> - **Command**: `<absolute path to tool4d-lsp-stdio>`
> - **Arguments**: `["mcp", "--foreground", "--project", "<absolute path to the .4DProject file>"]`
> - **Environment variables**: none, unless tool4d isn't auto-discoverable
>   (then set `TOOL4D_PATH=<absolute path to tool4d>`)
> - **Timeout**: 30–60 seconds
>
> After adding it, restart this session to pick up the new tool.

`--foreground` is required in the arguments above: the host spawns this
command and attaches to its stdio directly as the MCP transport, so it
must not daemonize/fork (the default `mcp` behavior without
`--foreground`) or the host will have nothing to talk to.

Resolve `<absolute path to tool4d-lsp-stdio>` and
`<absolute path to the .4DProject file>` to real, absolute paths before
presenting this suggestion -- do not leave placeholders in the message
shown to the user. This is advisory only: continue using the CLI
`validate` command regardless of whether the user acts on the suggestion.

## Tool Usage

Prefer mature, established command-line tools for generic processing.

Examples include:

* `jq` for JSON processing
* `xmllint` for XML validation and XPath
* `xsltproc` for XSLT processing
* other established tools where appropriate

Do not create a new abstraction over an existing mature CLI unless there is
a concrete requirement for one.

Use small shell scripts when they provide useful routing, portability,
environment detection, or consistent invocation.

Do not compile or install third-party tools automatically unless the
applicable skill explicitly requires it.

When a tool may not be available on the host, follow the fallback mechanism
defined by the applicable skill.

## Schemas

Schemas in this repository are used to validate 4D-specific file formats.

Do not modify a schema merely to make an invalid source file pass validation.

If a file fails validation, first determine whether:

* the source file is invalid;
* the wrong schema or 4D version is being used;
* the schema does not cover the artifact correctly; or
* the validator invocation is incorrect.

Where 4D versions have different schemas or rules, use the schema applicable
to the artifact's version.

## Modification Discipline

When modifying 4D source files:

* Make the smallest necessary change.
* Preserve existing structure and conventions.
* Preserve unknown properties or elements unless there is a clear reason
  to remove them.
* Avoid unrelated formatting or normalization.
* Do not rewrite generated metadata without understanding its purpose.
* Review the resulting diff.
* Validate the modified artifact.

Do not rely solely on a generic JSON/XML parser to determine whether a
modified 4D artifact is safe.

## Error Reporting

When reporting validation failures, provide:

* the artifact type;
* the file;
* the validation stage;
* the location of the problem when available;
* the relevant error;
* a concise explanation of the likely cause.

Do not conceal a 4D validation failure behind a generic parser error.

## Repository Organization

Keep artifact-specific knowledge in the corresponding skill.

Keep machine-readable schemas in `schemas/`.

Keep small helper scripts that run in place inside the owning skill
(`skills/<name>/scripts/`); executables provisioned by `4dtools` go to the
consumer repository's `tools/<skill>/`.

Keep repository-specific rules (a template's README structure, branch
conventions, a project's splash form) in that repository's own
`AGENTS.md` or `.github/instructions/`, not in these skills.
`MIGRATION.json` maps the old `.github/instructions/*.instructions.md`
files to their new homes.

Avoid duplicating the same 4D rules across multiple skills.

## General Principle

Treat this repository as a 4D development knowledge and tooling layer.

Prefer:

```
4D artifact
	↓
specific 4D skill
	↓
established validator/tool
	↓
4D-specific validation
```

over:

```
4D artifact
	↓
generic JSON/XML processing
```
