# 4D Source Code Validation

When you create or modify `.4dm` files under `Project/Sources/`, validate
them before reporting the task as complete.

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

See `skills/4dlsp/SKILL.md` for the full reference (output formats,
flags, prerequisites).

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
