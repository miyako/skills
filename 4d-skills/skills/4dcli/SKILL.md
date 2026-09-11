---
name: 4dcli
description: >
  Run a 4D project from the command line with tool4d or the full 4D
  application: version requirements, binary paths, flags, startup-method
  patterns, automated testing, and the DIALOG + CALL FORM render cycle.
  Use when executing 4D code headlessly, capturing form output, or wiring
  4D into CI.
---

# 4D Command Line

## Scope

This skill covers **invoking** a 4D project from a shell -- the `tool4d`
and `4D` binaries, their flags, and the startup-method patterns that make
a headless run produce observable output.

It does not cover:

* the skillset's own helper binaries -- see `skills/4dtools/SKILL.md`
* syntax checking `.4dm` files -- use `check-syntax` in
  `skills/4dlsp/SKILL.md`, which does this without writing a startup
  method or running a CLI session by hand
* 4D command and class syntax -- see `skills/4dlang/SKILL.md`
* what a captured form image actually shows -- see
  `skills/4dform/references/screenshot-rendering.md`

Reference: https://developer.4d.com/docs/Admin/cli

## What is tool4d

`tool4d` is a CLI build of 4D intended for CI/CD and automated testing:

* No license activation required.
* Runs 4D methods headlessly, without a GUI.
* Must be compatible with the project's `compatibilityVersion` (owned by
  `skills/4dproject/SKILL.md`). A newer tool4d can run an older project;
  the reverse also works, but the project may use commands that do not
  exist in the older tool4d.

## Feature Releases vs LTS

Reference: https://blog.4d.com/4d-versioning-feature-releases-lts-releases-explained/

* **Feature releases** (21 R2, 21 R3, 21 R4) contain new features **and**
  bug fixes, and ship more frequently.
* **LTS releases** (21.1, 21.2) contain only bug fixes backported from
  feature releases, and are intended for production stability.

Fixes land in feature releases first and may be backported to LTS later.
This matters when choosing a binary: a fix you depend on may not yet be
in the LTS you have installed.

## Version Requirements

`FORM SCREENSHOT` works in both `tool4d` and the full 4D application
(`4D.app`), but requires **tool4d 21 R3 (build 100186) or later**.

Earlier builds, including 21.1 LTS, had a bug that caused
`FORM SCREENSHOT` to crash (segfault) or silently produce blank or
incorrect output for certain picture formats (SVG, WEBP), and failed to
apply conditional form behavior such as dark-mode picture substitution.
This was a bug, not a design limitation of `tool4d`. Until 21.1 LTS is
confirmed to have the fix, use tool4d 21 R3 or later.

### Workaround for Older Builds

If an older build is unavoidable, use the full 4D application in headless
mode instead of `tool4d`:

```
/Applications/4D\ 21.1/4D.app/Contents/MacOS/4D --headless ...
```

Treat this as a workaround, not a preference.

### Binary Paths

| Binary | Typical path |
|--------|-------------|
| `tool4d` (21 R3) | `/Applications/4D 21 R3/tool4d.app/Contents/MacOS/tool4d` |
| `4D` (21 R3) | `/Applications/4D 21 R3/4D.app/Contents/MacOS/4D` |
| `4D` (21.1 LTS) | `/Applications/4D 21.1/4D.app/Contents/MacOS/4D` |

## Obtaining tool4d

`tool4d` is a 4D product download, not one of the helper binaries that
`4dtools` provisions from this skillset's own releases. Do not look for it
there.

```
https://resources-download.4d.com/release/{branch}/{version}/latest/{platform}/tool4d_{suffix}.tar.xz
```

| Parameter | Examples |
|---|---|
| branch | `21.x`, `20.x` |
| version | `21.1`, `21 R2` |
| platform | `win`, `mac` |
| suffix | `win`, `x86_64`, `arm64` |

No authentication is required. Before downloading, check whether a usable
4D or tool4d installation already exists on the host -- the search order
that `tool4d-lsp-stdio` uses (documented under "Prerequisites" in
`skills/4dlsp/SKILL.md`) lists the conventional locations.

## Flags

| Flag | Description |
|---|---|
| `--project` | Path to the `.4DProject` file |
| `--startup-method` | 4D method to execute at startup |
| `--dataless` | No data file. Use whenever the project may be open elsewhere, to avoid lock conflicts |
| `--user-param` | A single text argument, read back with `Get database parameter(User param value; $text)` |
| `--headless` | Full `4D` only: run without a GUI. Requires a license |

## Choosing the Right Engine

| Engine | Mode | Use for |
|--------|------|---------|
| `tool4d` | Always headless | Work that needs no UI: string manipulation, file I/O, calculations, `FORM LOAD`-based screenshots |
| `4D` (no flags) | GUI | Work that needs windows: `Open form window`, `DIALOG`, `FORM SCREENSHOT` after runtime code |
| `4D --headless` | Headless, licensed | Server-like batch tasks that do not need `DIALOG` |

**Key limitation**: in headless mode (`tool4d` or `4D --headless`) every
call to a dialog box is intercepted and answered automatically. `DIALOG`
is therefore dismissed immediately -- the form loads but closes before
any deferred code (such as a `CALL FORM` that takes a screenshot) can
run, and the process may then hang. For `dialog_screenshot`-style
workflows, use `4D` **without** `--headless`.

## Automated Testing

```bash
/path/to/tool4d --dataless --startup-method=test_all --project=/path/to/{name}.4DProject
```

### Exit Behavior

* **PASS**: stdout contains `PASS`, exit code 0.
* **FAIL**: `ASSERT` triggers a dialog, headless mode auto-aborts, exit
  code is non-zero and no `PASS` is printed.

## Startup-Method Patterns

### Pattern 1: Direct Test (no UI needed)

Run commands against variables and write the result to a file:

```4d
//%attributes = {"invisible":true}
var $st : Text
$st:="Hello World"
ST SET ATTRIBUTES($st; 1; 6; Attribute bold style; 1)

var $result : Object
$result:={}
$result.styled:=$st
$result.plain:=ST Get plain text($st)
$result.length:=Length($st)

var $file : 4D.File
$file:=File("/RESOURCES/tests/result.json")
$file.parent.create()
$file.setText(JSON Stringify($result; *))

QUIT 4D
```

```bash
tool4d --project path/to/project.4DProject --startup-method test_method --dataless
```

### Pattern 2: Form + DIALOG (UI needed)

To observe form-level behavior -- `On Load`, object methods, `Form`
population -- open the form and serialize the `Form` object afterwards:

```4d
//%attributes = {"invisible":true}
var $formName : Text
$formName:="MyForm"

var $form : Object
$form:={}

var $window : Integer
$window:=Open form window($formName)
DIALOG($formName; $form; *)
CALL FORM($window; Formula(ACCEPT))

// $form now contains all Form.xxx values set during On Load
var $file : 4D.File
$file:=File("/RESOURCES/tests/form_result.json")
$file.parent.create()
$file.setText(JSON Stringify($form; *))

QUIT 4D
```

This pattern requires `4D`, not `tool4d`, because it uses `DIALOG`:

```bash
/Applications/4D\ 21\ R3/4D.app/Contents/MacOS/4D \
  --project path/to/project.4DProject \
  --startup-method run_project_form \
  --user-param "FormName:1:/RESOURCES/tests/output.json" \
  --dataless
```

### Pattern 3: Parameterized with `--user-param`

```4d
var $userParamValue : Text
Get database parameter(User param value; $userParamValue)
var $params : Collection
$params:=Split string($userParamValue; ":")
// $params[0] = form name, $params[1] = page, $params[2] = output path
```

One generic method can then drive any form/page combination.

### Pattern 4: Runtime Screenshot with `dialog_screenshot`

Combines `DIALOG` (which runs `On Load` code) with `FORM SCREENSHOT`
(which captures the rendered state) in a single CLI call:

```bash
/path/to/4D --project path/to/project.4DProject \
  --startup-method dialog_screenshot \
  --user-param "FormName:Page:/RESOURCES/output.png" \
  --dataless
```

Architecture: `dialog_screenshot` opens `DIALOG` with `*`
(non-blocking), then `CALL FORM(goto_page_then_screenshot)`, then
`CALL FORM(screenshot_and_accept)`.

#### Form Rendering Cycle

4D defers form rendering to the end of each execution cycle (a form event
or a `CALL FORM` execution). `FORM GOTO PAGE` and `FORM SCREENSHOT` in
the **same** cycle therefore capture the **old** page.

Chain `CALL FORM` calls instead; each one is a separate cycle:

1. **Cycle 1** (`goto_page_then_screenshot`): call `FORM GOTO PAGE($page)`,
   then issue `CALL FORM(screenshot_and_accept)`. Rendering happens at the
   end of this cycle.
2. **Cycle 2** (`screenshot_and_accept`): call `FORM SCREENSHOT` -- now the
   page is correctly rendered. Then `ACCEPT` and `QUIT 4D`.

```4d
// goto_page_then_screenshot -- called via CALL FORM
FORM GOTO PAGE(Form.__page)
// Chain: screenshot runs in the NEXT cycle, after this cycle renders
CALL FORM(Current form window; Formula(screenshot_and_accept))
```

The same rule applies anywhere state is changed and then observed: the
change and the observation must be in separate execution cycles.

#### Where to Place `QUIT 4D`

With `DIALOG($form; *)` (non-blocking) the process stays alive while the
dialog is open. Put `QUIT 4D` inside the **last chained method**, after
`ACCEPT` -- not in the startup method, or the process may exit before the
chained `CALL FORM` runs.

## Writing Output Files

`tool4d` can write within the project scope, for example under
`Get 4D folder(Database folder)`. Writing to arbitrary locations such as
`/tmp/` may fail **silently** on macOS due to sandboxing, so do not read a
missing output file as proof that the code did not run.

```4d
// Safe output path within project scope
var $path : Text
$path:=Get 4D folder(Database folder)+"output.json"
BLOB TO DOCUMENT($path; $blob)
```

Write output next to the project, then read it back from the shell.

The path APIs themselves (`File`, `4D.File`, `Convert path system to POSIX`,
`Convert path POSIX to system`) are language-level -- look them up via
`skills/4dlang/SKILL.md`.

## Tips

* `--dataless`: always pass when the project may be open elsewhere.
* `QUIT 4D`: always include, or 4D stays open indefinitely in GUI mode.
* `Application info.headless`: branch behavior on it, for example logging
  to stdout when headless and showing UI otherwise.
* Output format: JSON is easiest to parse; use `JSON Stringify($obj; *)`
  for pretty-printing.

## Tool Dependencies

This skill needs a `tool4d` or `4D` installation on the host, obtained as
described under "Obtaining tool4d" above. Report the detected version
before relying on any behavior that is version-dependent.
