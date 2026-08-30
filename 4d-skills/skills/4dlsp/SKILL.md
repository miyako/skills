---
name: 4dlsp
description: >
  Use tool4d-lsp-stdio to validate and inspect 4D source code via the
  Language Server Protocol. Start an LSP session, send diagnostics
  requests, and interpret results to verify generated .4dm files.
---

# 4D LSP

## Scope

This skill covers using `tool4d-lsp-stdio` to validate and understand 4D
source code (`.4dm` files) through the Language Server Protocol.

Use this skill after generating or modifying `.4dm` files. The LSP gives
you compiler-grade feedback from the real 4D engine -- do not rely on
pattern matching or guesswork to verify 4D code.

## When to use

- After generating a new `.4dm` method or class
- After modifying existing `.4dm` code
- When you need to discover available commands, methods, or class members
- When refactoring and you need to find all references to a symbol

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
4. Conventional application locations
   - macOS: `/Applications/4D*.app` and `~/Applications/4D*.app`

If tool4d is installed via the 4D Analyzer VS Code extension, no
configuration is needed. Otherwise set `TOOL4D_PATH` explicitly.

## Starting an LSP session

```sh
tools/tool4d-lsp-stdio start --workspace /path/to/project/root
```

The `--workspace` flag points to the directory containing (or a parent of)
the `.4DProject` file. The tool searches up to 6 levels deep for a
`.4DProject` file. Alternatively, use `--project` to point directly at the
`.4DProject` file:

```sh
tools/tool4d-lsp-stdio start --project /path/to/Project/Sources/project.4DProject
```

### Default flags

By default, tool4d starts with `--dataless` (no data file) and
`--skip-onstartup` (skip the On Startup method). These are correct for
code validation. Do not change them unless you have a specific reason.

### What happens at startup

1. `tool4d-lsp-stdio` binds a local TCP port
2. It launches tool4d with `--lsp=<port>`
3. tool4d connects back over TCP
4. The bridge relays LSP JSON-RPC between stdin/stdout and the TCP
   connection

The process runs until you send an LSP `shutdown` request followed by
`exit`, or until you terminate it (e.g., close stdin, send SIGTERM).

## LSP protocol over stdio

Communication uses the standard LSP wire format on stdin/stdout:

```
Content-Length: <length>\r\n
\r\n
<JSON-RPC body>
```

Every message must have the `Content-Length` header. The body is a JSON-RPC
2.0 message.

## Workflow: validate generated code

This is the primary use case for agents.

### 1. Start the LSP server

```sh
tools/tool4d-lsp-stdio start --workspace . &
LSP_PID=$!
```

Or run it as a subprocess whose stdin/stdout you control.

### 2. Send `initialize`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "processId": null,
    "capabilities": {
      "textDocument": {
        "publishDiagnostics": {
          "relatedInformation": true
        }
      }
    },
    "rootUri": "file:///path/to/project/root"
  }
}
```

Wait for the `initialize` response, then send `initialized`:

```json
{
  "jsonrpc": "2.0",
  "method": "initialized",
  "params": {}
}
```

### 3. Open a document

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didOpen",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/Project/Sources/Methods/myMethod.4dm",
      "languageId": "4d",
      "version": 1,
      "text": "// contents of the file"
    }
  }
}
```

### 4. Read diagnostics

The server sends `textDocument/publishDiagnostics` notifications
asynchronously after `didOpen`. Read from stdout and look for:

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/publishDiagnostics",
  "params": {
    "uri": "file:///path/to/Project/Sources/Methods/myMethod.4dm",
    "diagnostics": [
      {
        "range": {
          "start": { "line": 5, "character": 0 },
          "end": { "line": 5, "character": 10 }
        },
        "severity": 1,
        "message": "Unknown command: ALRT"
      }
    ]
  }
}
```

Diagnostic severity levels:
- `1` = Error -- code will not compile
- `2` = Warning -- code compiles but may have issues
- `3` = Information
- `4` = Hint

**An empty `diagnostics` array means the code is clean.**

### 5. Fix and re-check

If diagnostics report errors:

1. Fix the code based on the error messages
2. Send `textDocument/didChange` with the updated text:

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didChange",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/Project/Sources/Methods/myMethod.4dm",
      "version": 2
    },
    "contentChanges": [
      { "text": "// entire updated file contents" }
    ]
  }
}
```

3. Read the new `publishDiagnostics` notification
4. Repeat until no errors remain

### 6. Shut down

```json
{
  "jsonrpc": "2.0",
  "id": 99,
  "method": "shutdown",
  "params": null
}
```

Wait for the response, then:

```json
{
  "jsonrpc": "2.0",
  "method": "exit",
  "params": null
}
```

## Other useful LSP requests

### Completion

Query available commands, methods, and class members at a cursor position:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "textDocument/completion",
  "params": {
    "textDocument": { "uri": "file:///..." },
    "position": { "line": 10, "character": 5 }
  }
}
```

Use this to discover valid 4D command names instead of guessing.

### Hover

Get type information and documentation for a symbol:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "textDocument/hover",
  "params": {
    "textDocument": { "uri": "file:///..." },
    "position": { "line": 10, "character": 5 }
  }
}
```

### Goto Definition

Find where a method or variable is defined:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "textDocument/definition",
  "params": {
    "textDocument": { "uri": "file:///..." },
    "position": { "line": 10, "character": 5 }
  }
}
```

### Find References

Find all usages of a symbol (useful before refactoring):

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "textDocument/references",
  "params": {
    "textDocument": { "uri": "file:///..." },
    "position": { "line": 10, "character": 5 },
    "context": { "includeDeclaration": true }
  }
}
```

## Important notes

- The LSP server is the real 4D compiler. Its diagnostics are authoritative.
  Do not second-guess them.
- `tool4d-lsp-stdio` writes diagnostic messages to stderr. Only stdout
  carries the LSP protocol. Do not mix them.
- The server may take a few seconds to start (tool4d needs to load the
  project). The default startup timeout is 30 seconds.
- One LSP session per project. Do not start multiple sessions for the same
  project.
- Always shut down the LSP session when done. Leaving tool4d running
  wastes resources.
