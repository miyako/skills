# 4D Source Code Validation

When you create or modify `.4dm` files under `Project/Sources/`, validate
them before reporting the task as complete.

## Validation workflow

1. Provision `tool4d-lsp-stdio` if not already available (see
   `skills/4dtools/SKILL.md`).
2. Start one LSP session for the project:

   ```sh
   tools/tool4d-lsp-stdio start --project Project/*.4DProject &
   LSP_PID=$!
   ```

3. For each `.4dm` file you created or modified, send `textDocument/didOpen`
   (or `textDocument/didChange` for updates) and read the
   `publishDiagnostics` response.
4. If diagnostics contain errors (severity 1), fix the code and re-check.
5. After all files validate cleanly, shut down the LSP session.

See `skills/4dlsp/SKILL.md` for the full LSP protocol reference
(initialize, didOpen, diagnostics format, shutdown sequence).

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
