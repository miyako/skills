---
name: 4dlsp
description: >
  Validate 4D source code (.4dm files) using tool4d-lsp-stdio. Run a single
  command to get compiler-grade diagnostics from the real 4D engine.
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
- `tool4d-lsp-stdio` is available on macOS and Windows only (no Linux).
