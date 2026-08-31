# 4D Source Code — Validation and Code Intelligence

When you work with `.4dm` files under `Project/Sources/`, use
`tool4d-lsp-stdio` for validation and code intelligence.

## Validation workflow

1. Provision `tool4d-lsp-stdio` if not already available (see
   `skills/4dtools/SKILL.md`).
2. Validate all modified files in one call:

   ```sh
   tools/tool4d-lsp-stdio validate --workspace Project/ \
     Sources/Methods/method1.4dm \
     Sources/Classes/MyClass.4dm
   ```

3. If the exit code is 1, read the error messages, fix the code, and
   re-validate until exit code 0.

## Code intelligence (hover, completion, goto-definition)

When you need more than validation — completions, documentation lookups,
or navigating to definitions — prefer the one-shot subcommands (no
persistent process needed for a handful of calls):

```sh
tools/tool4d-lsp-stdio hover --workspace Project/ \
  Sources/Methods/myMethod.4dm --line 5 --character 10
```

For many such calls in one task, start a persistent server once and omit
`--project`/`--workspace` on subsequent calls to reuse it (avoids paying
the tool4d startup cost per call):

```sh
tools/tool4d-lsp-stdio mcp --project Project/MyApp.4DProject   # prints pid + socket, returns
tools/tool4d-lsp-stdio hover Sources/Methods/myMethod.4dm --line 5 --character 10
# ... more one-shot calls without --project/--workspace ...
tools/tool4d-lsp-stdio mcp --stop --project Project/MyApp.4DProject   # clean up when the task ends
```

**Note:** the originally-shipped `tool4d-lsp-stdio` 0.3.0 build had this
daemonize/reuse pattern broken (see
https://github.com/miyako/language-4dm-nova/issues/42). That fix has
been merged upstream and `tools/tool4d-lsp-stdio` in this workspace has
been rebuilt from it, so the pattern above works reliably here. If your
provisioned build predates the fix, fall back to calling one-shot
subcommands directly with `--project`/`--workspace` on every call, or
use `mcp --foreground`.

If your provisioned `tool4d-lsp-stdio` build predates these one-shot
subcommands (check `--help`), fall back to the raw MCP protocol per
`skills/4dlsp/SKILL.md`'s "No MCP client available" section, or prefer
provisioning a newer build via `skills/4dtools/SKILL.md`.

Use `hover`/`completion`/`goto-definition`/`document-symbols` in these
situations:

- **Before using a 4D command you are not certain about**, call `hover`
  on a similar command in existing code to check its signature and
  arguments.
- **When you encounter an unfamiliar 4D command** while reading code,
  call `hover` to read its documentation instead of guessing what it does.
- **When reviewing existing code for correctness** (e.g. asked "is this
  code correct?" or "are these commands valid?"), do not rely on
  `validate` alone -- it can report 0 errors even when a command is
  obsolete or has been renamed in a later 4D version. Call `hover` on
  every command you're asked to vouch for; a result of "No hover
  information available at this position" means the token is not a
  recognized command, even if `validate` passed.
- **When you need to understand what a project method does**, call
  `goto-definition` to find its source code.
- **When you need to see what a file contains** before editing it, call
  `document-symbols` to get a quick overview of its methods and variables.
- **When writing new code**, call `completion` at the cursor position to
  discover available 4D commands, methods, and variables.

### One-shot vs persistent server vs `validate`

Use `validate` alone when you don't need command verification. Use the
one-shot subcommands directly (with `--project`/`--workspace`) for a
handful of hover/completion/goto-definition checks. Start a persistent
server (`mcp --project ...`, then omit `--project`/`--workspace` on
later calls, then `mcp --stop` when done) only when a task needs many
such checks -- e.g. reviewing every command in a file. If a native MCP
client for this server is already available in your own tool list, use
its tools directly instead of shelling out to any of the above.

See `skills/4dlsp/SKILL.md` for the full reference (tool parameters,
output formats, prerequisites).

## When to skip validation

- Trivial changes: renaming files, moving methods, updating comments only
- Reading code for understanding (no writes)

## Subdirectory layout

`.4dm` files live in subdirectories under `Sources/`:

```
Project/Sources/
  Methods/           project methods
  Classes/           class definitions
  DatabaseMethods/   On Startup, On Exit, etc.
  Triggers/          table triggers
```

Each `.4dm` file maps to a method or class. The file name is the method or
class name.
