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

## Code intelligence (MCP)

When you need more than validation — completions, documentation lookups,
or navigating to definitions — start the MCP server:

```sh
tools/tool4d-lsp-stdio mcp --workspace Project/
```

Use the MCP tools in these situations:

- **Before using a 4D command you are not certain about**, call `hover`
  on a similar command in existing code to check its signature and
  arguments.
- **When you encounter an unfamiliar 4D command** while reading code,
  call `hover` to read its documentation instead of guessing what it does.
- **When you need to understand what a project method does**, call
  `goto_definition` to find its source code.
- **When you need to see what a file contains** before editing it, call
  `document_symbols` to get a quick overview of its methods and variables.
- **When writing new code**, call `completion` at the cursor position to
  discover available 4D commands, methods, and variables.
- **After modifying code**, call `validate` to check for errors (same as
  the CLI command, but without restarting tool4d each time).

### MCP vs CLI validation

Use the **MCP server** when you plan to do multiple interactions with 4D
code in one session (write → validate → fix → re-validate, or exploring
code with hover/goto). The server starts tool4d once (~8 seconds) and
keeps it running.

Use the **CLI `validate` command** for quick one-shot checks when you
just need to verify a file is correct.

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
