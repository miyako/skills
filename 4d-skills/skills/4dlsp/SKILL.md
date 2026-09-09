---
name: 4dlsp
description: >
  Validate and explore 4D source code (.4dm files) using tool4d-lsp-stdio.
  One-shot validation via CLI, or persistent MCP server for completions,
  hover, goto-definition, and more. Look up correct 4D command and OOP
  class member syntax via the 4dlang skill before writing code.
---

# 4D LSP

## Scope

This skill validates 4D source code (`.4dm` files) using the 4D compiler
via `tool4d-lsp-stdio`.

Use this skill after generating or modifying `.4dm` files. The validation
gives compiler-grade feedback from the real 4D engine -- do not rely on
pattern matching or guesswork to verify 4D code.

## When to use

- Before writing an unfamiliar 4D command, to look up its correct syntax
  and a compiler-verified example (see "Command lookup" below)
- After generating a new `.4dm` method or class
- After modifying existing `.4dm` code

## When to skip

- Reading code for understanding (no writes)
- Trivial changes: renaming files, moving methods, updating comments only

## Tool location

Prefer `tools/4dlsp/tool4d-lsp-stdio` over any system-installed copy. If
`tools/4dlsp/tool4d-lsp-stdio` does not exist, provision it first by reading
`skills/4dtools/SKILL.md`.

```sh
test -x tools/4dlsp/tool4d-lsp-stdio
```

On Windows, check for `tools\4dlsp\tool4d-lsp-stdio.exe`.

## Prerequisites

`tool4d-lsp-stdio` requires **tool4d** (the headless 4D runtime). It
searches for tool4d automatically in this order:

1. `--tool` argument or `TOOL4D_PATH` environment variable
2. System PATH
3. VS Code 4D Analyzer extension storage
   - macOS: `~/Library/Application Support/Code/User/globalStorage/4d.4d-analyzer/tool4d/`
   - Windows: `%APPDATA%/Code/User/globalStorage/4d.4d-analyzer/tool4d/`
   - Linux: `~/.config/Code/User/globalStorage/4d.4d-analyzer/tool4d/`
4. Conventional application locations
   - macOS: `/Applications/4D*.app` and `~/Applications/4D*.app`
   - Windows: `%ProgramFiles%\4D\<version>\tool4d\`
   - Linux: `/opt/4d/`, `/opt/4D*/`, `/usr/local/bin/`

If tool4d is installed via the 4D Analyzer VS Code extension, no
configuration is needed. Otherwise pass `--tool <path-to-tool4d>` (or set
`TOOL4D_PATH`) explicitly -- e.g. on macOS a manually-installed 4D.app is
common and won't be found without this, since it isn't on PATH and isn't
in the VS Code extension storage or conventional locations list above.

## Command lookup (before writing code)

Before writing or fixing a call to an unfamiliar 4D command or OOP class
member, look it up with the `4dlang` skill (`skills/4dlang/SKILL.md`)
instead of guessing at its syntax from training data. It wraps
deterministic, offline references over compiler-verified 4D command and
class IRs and returns real overload signatures plus a `tool4d`-verified
example. This is a **lookup aid for getting syntax right the first time**
-- it is not a substitute for `validate`/`check-syntax` below. Always
still validate the code you write; do not treat a lookup result alone as
proof the code compiles.

## Validate command

Use the `validate` subcommand to check `.4dm` files in a single call:

```sh
tools/4dlsp/tool4d-lsp-stdio validate --workspace Project/ Sources/Methods/myMethod.4dm
```

Or point directly at the `.4DProject` file:

```sh
tools/4dlsp/tool4d-lsp-stdio validate \
  --project Project/MyApp.4DProject \
  Sources/Methods/myMethod.4dm
```

### Multiple files

Pass multiple file paths to validate them all in one session:

```sh
tools/4dlsp/tool4d-lsp-stdio validate --workspace Project/ \
  Sources/Methods/method1.4dm \
  Sources/Methods/method2.4dm \
  Sources/Classes/MyClass.4dm
```

This starts tool4d once and validates all files before shutting down.

### Output format

Human-readable output (default):

```
Sources/Methods/myMethod.4dm:6:1: error: Unknown command: ALRT
Sources/Methods/myMethod.4dm:10:5: warning: Variable not declared
```

Format: `file:line:col: severity: message`

JSON output with `--json`:

```sh
tools/4dlsp/tool4d-lsp-stdio validate --json --workspace Project/ Sources/Methods/myMethod.4dm
```

### Exit codes

- `0` -- no errors (warnings are allowed)
- `1` -- one or more errors (severity: error)

### Interpreting results

- **error** -- code will not compile. Must fix before reporting success.
- **warning** -- code compiles but may have issues. Report to user but
  do not block on warnings.
- **info** / **hint** -- informational. Ignore unless relevant to the task.

## Check-syntax command (project-wide)

`validate` requires a specific list of files. Use the `check-syntax`
subcommand instead when you want a project-wide compile-check pass
without knowing or listing every `.4dm` file yourself -- e.g. after a
refactor that may have touched files you didn't explicitly edit, or when
asked "does the whole project still compile?".

`check-syntax` wraps the LSP's `experimental/checkSyntax` request (a
project-wide check), as opposed to `validate`, which pulls diagnostics
per file via `textDocument/diagnostic`. It accepts the same
`--tool`/`--project`/`--workspace`/`--port`/`--startup-timeout`/
`--shutdown-timeout`/`--skip-onstartup`/`--dataless`/`--log-level`/
`--json` flags as `validate`.

`[FILES]...` is **optional** for `check-syntax` (unlike `validate`,
where it's required):

```sh
# Project-wide check, no files needed:
tools/4dlsp/tool4d-lsp-stdio check-syntax --workspace Project/

# Anchor on specific file(s) you just edited:
tools/4dlsp/tool4d-lsp-stdio check-syntax --workspace Project/ \
  Sources/Methods/myMethod.4dm
```

- If files are given, each is opened via `didOpen` first (so the server
  has at least one known/open document as a valid anchor URI).
- If omitted, the tool automatically picks the first `.4dm` file found
  under `Sources/` (falling back to the project root if no `Sources/`
  directory exists) and opens that as the anchor document.
- Exactly **one** `experimental/checkSyntax` request is sent (not one
  per file), anchored at the first opened document. Per the 4D Analyzer
  VS Code extension's own usage of this request, the anchor document is
  arbitrary -- the response is project-wide regardless of which
  document was passed.

### Output format

Non-JSON output mirrors `validate`'s per-file `got N diagnostic(s) for
<path>` logging style, plus a `previously opened: true/false` note per
file in the report -- useful because the response may include
diagnostics for files that were never explicitly `didOpen`'d by this
process.

`--json` output normalizes the upstream `WorkspaceDiagnosticReport`
shape to match `validate --json`'s contract exactly:

```json
[{"uri": "...", "diagnostics": [...]}]
```

(Upstream nests entries as `{ items: [{ uri, version, kind: "full",
items: Diagnostic[] }, ...] }` -- note the inner per-file diagnostics
field is itself named `items` upstream; this CLI renames it to
`diagnostics` in its own JSON output, matching `validate`.)

Exit codes follow the same convention as `validate`: `0` whether or not
diagnostics were found (as long as the session ran cleanly), nonzero
only for real transport/protocol failures.

> **Not yet empirically verified against a live tool4d binary:** it is
> not yet confirmed whether the response reliably includes diagnostics
> for files that were never opened by this process. `check-syntax`
> *should* report project-wide diagnostics regardless of the anchor
> file, but treat that as unconfirmed until tested in practice. Do not
> drop `validate`'s per-file chunking in favor of `check-syntax` based
> on this alone.

### `validate` vs `check-syntax`

- **`validate`** -- check specific files you just wrote or modified;
  files are required.
- **`check-syntax`** -- check the whole project's syntax in one pass
  without listing every file; files are optional and only serve as an
  anchor document.

## Diagnostics scope

`--diagnostics-scope <document|workspace>` controls how much of the
project the LSP `initialize` request asks tool4d to diagnose. It
defaults to `workspace` (the prior, unconditional behavior), so existing
commands and examples above are unaffected unless you pass it
explicitly.

- `workspace` (default) -- diagnostics/checks apply project-wide.
- `document` -- diagnostics/checks are scoped to documents this session
  explicitly opens (via `didOpen`), narrower than workspace scope.

```sh
tools/4dlsp/tool4d-lsp-stdio check-syntax --workspace Project/ --diagnostics-scope document
```

This flag is available on `validate`, `check-syntax`, `mcp`, `hover`,
`completion`, `goto-definition`, `document-symbols`, and
`install-components` -- i.e. every subcommand that builds its own
`initialize` request. It mirrors the non-standard
`initializationOptions.diagnostics.scope` option the 4D Analyzer VS Code
extension sends to the LSP server.

> **Runtime effect not independently verified:** it is confirmed that
> this flag correctly threads the option through to the LSP
> `initialize` request, matching what the real VS Code extension sends.
> Whether `document` scope actually narrows diagnostics further (or
> affects performance) against a live tool4d server has not been
> empirically verified in this environment -- treat the behavioral
> description above as the LSP option's intent, not a confirmed
> guarantee.

## Install-components command

`install-components` wraps the custom `dependency/installComponents`
LSP notification -- the same one the 4D Analyzer VS Code extension's
`DependencyManager` sends after downloading a project's dependencies
via `dependencies.json`.

> **This is not a full dependency manager.** `install-components` does
> **not** fetch or download anything itself. It assumes the project's
> components are already present on disk -- fetched out-of-band, or by
> a prior IDE/VS Code session -- and just tells tool4d to (re)load them.
> Parsing `dependencies.json`, GitHub/GitLab auth, and actually
> downloading components are out of scope here and deferred to a future
> change.

```sh
tools/4dlsp/tool4d-lsp-stdio install-components --workspace Project/
```

Unlike `validate`/`check-syntax`, `install-components` takes **no
`[FILES]...` argument** -- it always targets the resolved project
(`.4DProject` file) as a whole, not individual source files.

### Behavior

- Sends `dependency/installComponents` with `{"uri": <project's
  .4DProject file URI>}` -- the project file itself, not a source file,
  matching what the VS Code extension's `commands.ts`
  (`fetchProjectForCommand`) sends.
- Waits for the matching `dependency/installComponents/done`
  notification before exiting successfully.
- If tool4d asks the client to re-send via
  `dependency/installComponents/before` (a real protocol behavior
  confirmed in `DependencyManager.ts`'s own notification handler), the
  subcommand automatically re-sends `installComponents` and keeps
  waiting -- no action needed on your part.

### Flags

Accepts the same `--tool`/`--project`/`--workspace`/`--port`/
`--startup-timeout`/`--shutdown-timeout`/`--skip-onstartup`/
`--dataless`/`--log-level`/`--diagnostics-scope`/`--json` flags as
`check-syntax`/`validate`, plus one flag specific to this command:

- `--install-timeout <seconds>` (default `300`) -- how long to wait for
  `installComponents/done`. Installs can take much longer than a
  compile check, hence the separate, longer default from
  `--startup-timeout`/`--shutdown-timeout`.

### Output format

Non-JSON output prints a single line on success:

```
Project/MyApp.4DProject: components installed
```

`--json` output is a single JSON **object**, not an array like
`validate --json`/`check-syntax --json` -- there's only one project per
invocation, no per-file breakdown:

```json
{"uri": "file:///.../MyApp.4DProject", "installed": true}
```

### Exit codes

- `0` -- `installComponents/done` received within `--install-timeout`.
- nonzero -- any transport/protocol failure, or a timeout waiting for
  `done`.

Unlike `validate`/`check-syntax`, there is no diagnostics-found/
diagnostics-not-found duality here -- `install-components` either
confirms the install completed or fails outright.

## Workflow

1. Before writing unfamiliar 4D code, look up correct command or class
   member syntax with the `4dlang` skill (see "Command lookup" above)
2. Write or modify `.4dm` files
3. Run `validate` on all modified files (or `check-syntax` for a
   project-wide pass -- see above)
4. If errors: fix the code based on error messages, re-validate
5. Repeat until exit code 0
6. Report success to user

## Windows

On Windows, use `tools\4dlsp\tool4d-lsp-stdio.exe`:

```powershell
tools\4dlsp\tool4d-lsp-stdio.exe validate --workspace Project\ Sources\Methods\myMethod.4dm
```

## Linux

On Linux, tool4d is available for CI and GitHub Codespaces. Use the same
syntax as macOS:

```sh
tools/4dlsp/tool4d-lsp-stdio validate --workspace Project/ Sources/Methods/myMethod.4dm
```

## Important notes

- The validator uses the real 4D compiler. Its diagnostics are authoritative.
  Do not second-guess them.
- tool4d may take a few seconds to start (it loads the project). The default
  startup timeout is 30 seconds.
- Validate only the files you created or modified, not the entire project.
- **`validate` reporting 0 errors does not guarantee every command is
  current.** Some obsolete/renamed commands (e.g. old commands replaced by
  a newer equivalent) may not surface as a compile error. If you are
  unsure whether a specific command is real or current -- especially one
  from training data, an older 4D version, or unfamiliar code -- confirm
  it with the MCP `hover` tool (see below) rather than relying on
  `validate` alone. `hover` returning "No hover information available"
  for a command-shaped token is a strong signal it is not recognized.
- For unfamiliar commands or class members, prefer looking them up with
  the `4dlang` skill (see "Command lookup" above) before writing code
  at all -- it returns the authoritative overload signature and a
  compiler-verified example, which is more useful upfront than
  discovering a syntax mistake after the fact via `validate`/`hover`.

## MCP server

The `mcp` subcommand starts a persistent server that keeps a tool4d LSP
session alive so agents can make repeated calls without the ~8-second
startup cost each time. It also exposes the LSP capabilities directly as
one-shot CLI subcommands (see "One-shot commands" below) -- most agent
tasks should prefer those over talking MCP/JSON-RPC directly.

> **Note:** this section describes the design agreed in
> https://github.com/miyako/skills/issues/27 -- check
> `tools/4dlsp/tool4d-lsp-stdio --version` and `--help` to confirm which of
> these subcommands/flags are present in your provisioned build before
> relying on them. Older builds only have `mcp` (stdio, foreground) and
> `validate`; fall back to "No MCP client available" below if `hover`
> etc. are not recognized subcommands.

### One-shot commands

`hover`, `completion`, `goto-definition`, and `document-symbols` work
exactly like `validate` -- no persistent process, no MCP/JSON-RPC
knowledge required:

```sh
tools/4dlsp/tool4d-lsp-stdio hover --project Project/MyApp.4DProject \
  Sources/Methods/myMethod.4dm --line 6 --character 21
tools/4dlsp/tool4d-lsp-stdio completion --workspace Project/ \
  Sources/Methods/myMethod.4dm --line 5 --character 10
tools/4dlsp/tool4d-lsp-stdio goto-definition --workspace Project/ \
  Sources/Methods/myMethod.4dm --line 5 --character 10
tools/4dlsp/tool4d-lsp-stdio document-symbols --workspace Project/ \
  Sources/Methods/myMethod.4dm
```

`--line`/`--character` are zero-based, same as the MCP tool parameters
below. Add `--json` for structured output. These accept the same
`--tool`/`--project`/`--workspace`/`--startup-timeout`/etc. flags as
`validate`.

**File path resolution differs by mode.** With `--project`/`--workspace`
given explicitly (standalone mode), the file argument resolves the same
way as `validate`'s file list -- relative to the workspace/repo root.
Once you attach to a running server by omitting both flags (see below),
the file argument instead resolves relative to **your current working
directory**, since there is no workspace context on that call. A
relative path that doesn't match your cwd fails fast (in well under a
second) with a generic read/parse error that looks like "file not
found" rather than "wrong path base" -- if an attached call fails
quickly and confusingly, pass an **absolute** file path instead of
debugging the relative one.

A relative **`--workspace`** (or `--project`) value can hit the same
kind of confusing failure in standalone mode too, not just the
attached-mode case above -- if a one-shot command fails to locate a file
that demonstrably exists, retry with an absolute `--workspace`/`--project`
path before assuming the command itself is broken.

**Prefer these one-shot commands over hand-rolling MCP/JSON-RPC.** Use
`hover` on any command you're not fully certain is current -- `validate`
alone can miss obsolete/renamed commands (see Important notes above).

#### Locating a character position

`--line`/`--character` must point at the exact token you want to check.
**Do not find this by trial and error** (e.g. calling `hover` repeatedly
across a range of `--character` values until one returns real info) --
each call is a full request and, in standalone mode, an ~8-second tool4d
startup; scanning a dozen columns one call at a time multiplies both the
call count and the wall-clock time for no reason. Compute the offset
once from the file text instead, then call `hover` exactly once:

```sh
# 0-based line number of the line containing the token (grep -n is 1-based, subtract 1):
grep -n "Count tables" Sources/Methods/myMethod.4dm
# 0-based character offset of the token's first character on that line:
python3 -c "print(open('Sources/Methods/myMethod.4dm').readlines()[LINE].index('Count tables'))"
```

Then call `hover`/`completion`/`goto-definition` once with the resulting
`--line`/`--character`. If you're unsure of the exact spelling of a
command (e.g. it might be a substring of a longer identifier), narrow
with `grep -bo` on that one line, or use `document-symbols` first to see
what tokens 4D itself recognizes on the line, rather than sweeping
character positions with `hover`.

### Reusing a running server (faster repeated calls)

Omit **both** `--project` and `--workspace` on any one-shot subcommand
(including `validate`) to attach to an already-running persistent server
for the current project instead of starting a new tool4d process:

```sh
tools/4dlsp/tool4d-lsp-stdio hover Sources/Methods/myMethod.4dm --line 6 --character 21
```

If no server is running, this fails with a clear error telling you to
start one with `mcp` or pass `--project`/`--workspace` to run standalone.
Use this pattern in a multi-step task (many hover/completion calls across
one session) to pay the tool4d startup cost once instead of per call.

### Starting a persistent server for a task

Running `mcp --project ...` (or `--workspace ...`) directly daemonizes:
it forks into the background, binds the discoverable socket used by (2),
and prints the PID (and socket path) to stdout, then returns control.

```sh
tools/4dlsp/tool4d-lsp-stdio mcp --project Project/MyApp.4DProject
# -> pid=12345 socket=/tmp/tool4d-lsp-<hash>.sock
```

> **Note on `tool4d-lsp-stdio` 0.3.0:** the originally-shipped 0.3.0
> build of this daemonize/attach workflow was broken (tracked in
> https://github.com/miyako/language-4dm-nova/issues/42 -- daemonize
> always failed to start, and attached one-shot calls returned no
> hover/completion/etc info even for valid commands). A fix has been
> merged upstream (PR #43) and `tools/4dlsp/tool4d-lsp-stdio` in this
> workspace has been rebuilt from that fix, so the daemonize/attach
> pattern below now works reliably here. If you're working from a
> `tool4d-lsp-stdio` build that predates that fix, fall back to running
> one-shot subcommands directly with `--project`/`--workspace` on every
> call, or `mcp --foreground`.

Use this at the start of a multi-step `.4dm` task, then call one-shot
subcommands without `--project`/`--workspace` for the rest of the task.
Stop it when done:

```sh
tools/4dlsp/tool4d-lsp-stdio mcp --stop --project Project/MyApp.4DProject
# or: kill <pid>
```

A daemonized server also self-terminates after an idle timeout as a
safety net if you forget to stop it.

**`mcp --stop` returns before shutdown is guaranteed complete.** The
worker and its tool4d child process may still be alive for a few
seconds after `--stop` prints its confirmation -- shutdown happens
asynchronously. If you need to verify no leftover process remains
(e.g. before starting a fresh server, or at the end of a task), poll
`ps` a couple of times with a short delay rather than checking
immediately once and concluding cleanup failed.

**Start it once per task, and pick one flag consistently.** Use either
`--project` or `--workspace` to start it (whichever you prefer), but do
not call `mcp` again mid-task to "restart" or switch flags -- if a
server is already running for this project, starting another is
redundant (and any in-flight attached calls may momentarily target the
wrong instance). If you're unsure whether one is already running,
either just try an attached one-shot call first (it fails clearly if
none exists, see above) or call `mcp --stop` before starting a fresh
one -- don't leave multiple starts/stops interleaved with your actual
work.

**For hosts with a native MCP client** that want to attach to this
server's stdio directly (JSON-RPC over stdin/stdout) instead of a
detached background process, pass `--foreground` to keep the original
(pre-daemonizing) behavior:

```sh
tools/4dlsp/tool4d-lsp-stdio mcp --foreground --workspace Project/
```

### When to use one-shot vs a persistent server vs validate

- **No `.4dm` command verification needed** -- use `validate` alone.
- **A few `hover`/`completion`/`goto-definition` checks in one task** --
  use the one-shot subcommands directly with `--project`/`--workspace`;
  the per-call startup cost is fine for a handful of calls.
- **Many LSP checks across one task** (e.g. reviewing every command in a
  file) -- use the one-shot subcommands directly with
  `--project`/`--workspace` for now (see known issue above); once fixed,
  start a persistent server once (`mcp --project ...`), then call
  one-shot subcommands without `--project`/`--workspace` for the rest of
  the task, and stop the server (`mcp --stop`) when done.
- **Host has a native MCP client already configured** for this server --
  use its MCP tools directly instead of shelling out to any of the
  above; do not spawn a duplicate `tools/4dlsp/tool4d-lsp-stdio mcp` process
  yourself in that case.

### MCP protocol details (for `--foreground` / native MCP clients only)

The server runs on stdio using the MCP protocol (JSON-RPC 2.0), framed as
**newline-delimited JSON** (one JSON object per line) -- not the
`Content-Length:` header framing used by the LSP protocol itself.

It exposes these tools:

| Tool | Description |
|------|-------------|
| `validate` | Check `.4dm` files for syntax errors |
| `check-syntax` | Project-wide compile-check (see "Check-syntax command" above) |
| `completion` | Code completion at a position |
| `hover` | Documentation / type signature at a position |
| `goto_definition` | Find where a symbol is defined |
| `document_symbols` | List all symbols in a file |
| `open_file` | Open a file in the LSP session |
| `close_file` | Close a file from the LSP session |

### Tool parameters

**validate**
```json
{ "files": ["Sources/Methods/myMethod.4dm"] }
```

**completion / hover / goto_definition**
```json
{ "file": "Sources/Methods/myMethod.4dm", "line": 5, "character": 10 }
```
Line and character are zero-based.

**document_symbols / open_file / close_file**
```json
{ "file": "Sources/Methods/myMethod.4dm" }
```

### No MCP client available (older builds only)

If your provisioned build doesn't have the one-shot subcommands above
(`hover`, `completion`, etc. as top-level subcommands) and your host has
no native MCP client either, drive the newline-delimited JSON-RPC
protocol directly over the `mcp --foreground` subprocess's stdin/stdout
(write one JSON object per line, read one JSON object per line back).
Any language works; example in Python:

```python
proc.stdin.write(json.dumps(request) + "\n"); proc.stdin.flush()
response = json.loads(proc.stdout.readline())
```

Handshake before any tool call: send `initialize` (id +
`protocolVersion`, `capabilities`, `clientInfo`) → read the response →
send `notifications/initialized` (no id) → send `tools/call` requests
(e.g. `{"name":"hover","arguments":{...}}`).

Prefer provisioning a newer `tool4d-lsp-stdio` build with the one-shot
subcommands over this fallback -- see `skills/4dtools/SKILL.md`.

### Notes

- Files must be opened (`open_file` or `validate`) before `completion`,
  `hover`, or `goto_definition` will return results, when using the MCP
  tools directly. The one-shot CLI subcommands handle this automatically.
- All file paths are relative to the workspace (the `Project/` directory)
  unless an absolute path is given.
