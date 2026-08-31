---
name: 4dlsp
description: >
  Validate and explore 4D source code (.4dm files) using tool4d-lsp-stdio.
  One-shot validation via CLI, or persistent MCP server for completions,
  hover, goto-definition, and more.
---

# 4D LSP

## Scope

This skill validates 4D source code (`.4dm` files) using the 4D compiler
via `tool4d-lsp-stdio`.

Use this skill after generating or modifying `.4dm` files. The validation
gives compiler-grade feedback from the real 4D engine -- do not rely on
pattern matching or guesswork to verify 4D code.

## When to use

- After generating a new `.4dm` method or class
- After modifying existing `.4dm` code

## When to skip

- Reading code for understanding (no writes)
- Trivial changes: renaming files, moving methods, updating comments only

## Tool location

Prefer `tools/tool4d-lsp-stdio` over any system-installed copy. If
`tools/tool4d-lsp-stdio` does not exist, provision it first by reading
`skills/4dtools/SKILL.md`.

```sh
test -x tools/tool4d-lsp-stdio
```

On Windows, check for `tools\tool4d-lsp-stdio.exe`.

## Prerequisites

`tool4d-lsp-stdio` requires **tool4d** (the headless 4D runtime). It
searches for tool4d automatically in this order:

1. `--tool4d-path` argument or `TOOL4D_PATH` environment variable
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
configuration is needed. Otherwise set `TOOL4D_PATH` explicitly.

## Validate command

Use the `validate` subcommand to check `.4dm` files in a single call:

```sh
tools/tool4d-lsp-stdio validate --workspace Project/ Sources/Methods/myMethod.4dm
```

Or point directly at the `.4DProject` file:

```sh
tools/tool4d-lsp-stdio validate \
  --project Project/MyApp.4DProject \
  Sources/Methods/myMethod.4dm
```

### Multiple files

Pass multiple file paths to validate them all in one session:

```sh
tools/tool4d-lsp-stdio validate --workspace Project/ \
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
tools/tool4d-lsp-stdio validate --json --workspace Project/ Sources/Methods/myMethod.4dm
```

### Exit codes

- `0` -- no errors (warnings are allowed)
- `1` -- one or more errors (severity: error)

### Interpreting results

- **error** -- code will not compile. Must fix before reporting success.
- **warning** -- code compiles but may have issues. Report to user but
  do not block on warnings.
- **info** / **hint** -- informational. Ignore unless relevant to the task.

## Workflow

1. Write or modify `.4dm` files
2. Run `validate` on all modified files
3. If errors: fix the code based on error messages, re-validate
4. Repeat until exit code 0
5. Report success to user

## Windows

On Windows, use `tools\tool4d-lsp-stdio.exe`:

```powershell
tools\tool4d-lsp-stdio.exe validate --workspace Project\ Sources\Methods\myMethod.4dm
```

## Linux

On Linux, tool4d is available for CI and GitHub Codespaces. Use the same
syntax as macOS:

```sh
tools/tool4d-lsp-stdio validate --workspace Project/ Sources/Methods/myMethod.4dm
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

## MCP server

The `mcp` subcommand starts a persistent server that keeps a tool4d LSP
session alive so agents can make repeated calls without the ~8-second
startup cost each time. It also exposes the LSP capabilities directly as
one-shot CLI subcommands (see "One-shot commands" below) -- most agent
tasks should prefer those over talking MCP/JSON-RPC directly.

> **Note:** this section describes the design agreed in
> https://github.com/miyako/skills/issues/27 -- check
> `tools/tool4d-lsp-stdio --version` and `--help` to confirm which of
> these subcommands/flags are present in your provisioned build before
> relying on them. Older builds only have `mcp` (stdio, foreground) and
> `validate`; fall back to "No MCP client available" below if `hover`
> etc. are not recognized subcommands.

### One-shot commands

`hover`, `completion`, `goto-definition`, and `document-symbols` work
exactly like `validate` -- no persistent process, no MCP/JSON-RPC
knowledge required:

```sh
tools/tool4d-lsp-stdio hover --project Project/MyApp.4DProject \
  Sources/Methods/myMethod.4dm --line 6 --character 21
tools/tool4d-lsp-stdio completion --workspace Project/ \
  Sources/Methods/myMethod.4dm --line 5 --character 10
tools/tool4d-lsp-stdio goto-definition --workspace Project/ \
  Sources/Methods/myMethod.4dm --line 5 --character 10
tools/tool4d-lsp-stdio document-symbols --workspace Project/ \
  Sources/Methods/myMethod.4dm
```

`--line`/`--character` are zero-based, same as the MCP tool parameters
below. Add `--json` for structured output. These accept the same
`--tool`/`--project`/`--workspace`/`--startup-timeout`/etc. flags as
`validate`.

**Prefer these one-shot commands over hand-rolling MCP/JSON-RPC.** Use
`hover` on any command you're not fully certain is current -- `validate`
alone can miss obsolete/renamed commands (see Important notes above).

### Reusing a running server (faster repeated calls)

Omit **both** `--project` and `--workspace` on any one-shot subcommand
(including `validate`) to attach to an already-running persistent server
for the current project instead of starting a new tool4d process:

```sh
tools/tool4d-lsp-stdio hover Sources/Methods/myMethod.4dm --line 6 --character 21
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
tools/tool4d-lsp-stdio mcp --project Project/MyApp.4DProject
# -> pid=12345 socket=/tmp/tool4d-lsp-<hash>.sock
```

> **Note on `tool4d-lsp-stdio` 0.3.0:** the originally-shipped 0.3.0
> build of this daemonize/attach workflow was broken (tracked in
> https://github.com/miyako/language-4dm-nova/issues/42 -- daemonize
> always failed to start, and attached one-shot calls returned no
> hover/completion/etc info even for valid commands). A fix has been
> merged upstream (PR #43) and `tools/tool4d-lsp-stdio` in this
> workspace has been rebuilt from that fix, so the daemonize/attach
> pattern below now works reliably here. If you're working from a
> `tool4d-lsp-stdio` build that predates that fix, fall back to running
> one-shot subcommands directly with `--project`/`--workspace` on every
> call, or `mcp --foreground`.

Use this at the start of a multi-step `.4dm` task, then call one-shot
subcommands without `--project`/`--workspace` for the rest of the task.
Stop it when done:

```sh
tools/tool4d-lsp-stdio mcp --stop --project Project/MyApp.4DProject
# or: kill <pid>
```

A daemonized server also self-terminates after an idle timeout as a
safety net if you forget to stop it.

**For hosts with a native MCP client** that want to attach to this
server's stdio directly (JSON-RPC over stdin/stdout) instead of a
detached background process, pass `--foreground` to keep the original
(pre-daemonizing) behavior:

```sh
tools/tool4d-lsp-stdio mcp --foreground --workspace Project/
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
  above; do not spawn a duplicate `tools/tool4d-lsp-stdio mcp` process
  yourself in that case.

### MCP protocol details (for `--foreground` / native MCP clients only)

The server runs on stdio using the MCP protocol (JSON-RPC 2.0), framed as
**newline-delimited JSON** (one JSON object per line) -- not the
`Content-Length:` header framing used by the LSP protocol itself.

It exposes these tools:

| Tool | Description |
|------|-------------|
| `validate` | Check `.4dm` files for syntax errors |
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
