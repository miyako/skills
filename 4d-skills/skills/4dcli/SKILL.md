---
name: 4dcli
description: >
  Run a 4D project from the command line with tool4d or the full 4D
  application: version requirements, binary paths, flags, startup-method
  patterns, automated testing, and the DIALOG + CALL FORM render cycle.
  Ships installable source for six ready-made startup methods that
  capture or execute a form. Use when executing 4D code headlessly,
  capturing form output, or wiring 4D into CI.
---

# 4D Command Line

## Scope

This skill covers **invoking** a 4D project from a shell -- the `tool4d`
and `4D` binaries, their flags, and the startup-method patterns that make
a headless run produce observable output.

It also ships the source of six ready-made startup methods in `assets/`,
which a project must contain before it can be driven this way. See
"Bundled Startup Methods".

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

## Bundled Startup Methods

A startup method is the only way to make a headless 4D run do anything:
`--startup-method` names a project method, and everything else arrives
through `--user-param`. The six methods below cover form capture and form
execution, and this skill ships their source in `assets/`:

```
skills/4dcli/assets/
  project_form_to_image.4dm
  print_form_to_file.4dm
  run_project_form.4dm
  dialog_screenshot.4dm
  goto_page_then_screenshot.4dm
  screenshot_and_accept.4dm
```

They are ordinary project methods, not 4D built-ins. A project that does
not have them cannot be driven this way until they are installed -- see
"Installing a Bundled Method" below.

All six are generic: no table references, no project classes, no
hardcoded paths. They are written untokenized and are verified to compile
both in a project with `"tokenizedText": false` and in one that omits the
key (tokenized default).

### Contracts

You do not need to read the asset files to use these. Each contract below
is complete.

| Method | `--user-param` | Binary | Effect |
|---|---|---|---|
| `project_form_to_image` | `FormName:Page:/out.png` | `tool4d` | Static-template screenshot to PNG. No CSS |
| `print_form_to_file` | `FormName:Page:/out.pdf` | `tool4d` | Prints the form to PDF. CSS applied |
| `run_project_form` | `FormName:Page:/out.json` | `4D`, no `--headless` | Opens the form, accepts it, writes the `Form` object as JSON |
| `dialog_screenshot` | `FormName:Page:/out.png` | `4D`, no `--headless` | Runtime screenshot after `On Load`. Entry point of a three-method chain |
| `goto_page_then_screenshot` | -- | -- | Chain link. Never invoked as a startup method |
| `screenshot_and_accept` | -- | -- | Chain link. Never invoked as a startup method |

All four entry points that take a path share the same `--user-param`
shape, `FormName:Page:Path`:

* The value is split on `:`, and fewer than three segments is a silent
  no-op return. The **path may itself contain colons**: everything from
  the third segment onward is rejoined, so a Windows drive-letter path
  such as `MyForm:1:C:\out.png` resolves correctly to `C:\out.png`. The
  form name and the page number must not contain a colon.
* A 4D filesystem path such as `/PACKAGE/out.png` is still the better
  choice where it works -- it is platform independent and sandboxed.
* A page number below 1 is clamped to 1.
* The parent directory of the output path is created if missing.

The three tool4d entry points -- `project_form_to_image`,
`print_form_to_file` and `run_project_form` -- additionally:

* return without doing anything if the path is empty;
* clamp a page beyond the form's page count to the last page, via
  `FORM GET PROPERTIES`;
* log the output path to standard output and quit when
  `Application info.headless` is true.

`dialog_screenshot` does none of those three: it cannot call
`FORM GET PROPERTIES` before the form is open, and an empty path makes
the chain accept the dialog without writing a file.

`project_form_to_image` renders the **static template**, so it never
reflects `On Load` or any `Form.xxx` value. That is a property of
`FORM SCREENSHOT`, not a limitation of the method -- see
`skills/4dform/references/screenshot-rendering.md` for what the static
template shows per object type. Use `dialog_screenshot` when you need the
runtime appearance.

### The `dialog_screenshot` Chain

`dialog_screenshot` is one CLI entry point implemented as three methods,
because of the rendering-cycle rule described under Pattern 4 below.
Installing it means installing all three.

State is handed between them on the form object:

| Property | Set by | Read by |
|---|---|---|
| `Form.__page` | `dialog_screenshot` | `goto_page_then_screenshot` |
| `Form.__screenshotPath` | `dialog_screenshot` | `screenshot_and_accept` |

`dialog_screenshot` builds `$form`, assigns both properties, opens the
form with `DIALOG($formName; $form; *)`, and issues
`CALL FORM(goto_page_then_screenshot)`. That method navigates and chains
`CALL FORM(screenshot_and_accept)`, which captures, writes the file,
calls `ACCEPT`, and quits.

**Caveat -- `formClass` and undeclared properties.** `__page` and
`__screenshotPath` are assigned to the form object from outside the form.
If the target form declares a `formClass`, the compiler checks
`Form.xxx` accesses against the class and will emit **"Undeclared
property 'xxx' used"** warnings for both. Fix it by declaring them in the
form class:

```4d
property __page : Integer
property __screenshotPath : Text
```

See the Form Class section of
`skills/4dform/references/form-concepts.md`. These are warnings, not
errors, so the capture still works -- but they will show up in `4dlsp`
output and should not be mistaken for a defect in the form.

**Caveat -- binary.** `dialog_screenshot` requires `4D` **without**
`--headless`, and does not work under `tool4d` at all. Headless mode
auto-answers dialog boxes, so `DIALOG` is dismissed before the chained
`CALL FORM` can run, and the process may then hang. The same applies to
`run_project_form`.

### Installing a Bundled Method

Copy the asset to the project's methods directory, keeping the filename:

```
<project>/Project/Sources/Methods/<name>.4dm
```

Install only the methods the current task needs. Do not install all six
by reflex -- a screenshot task needs `project_form_to_image` alone.
Installing `dialog_screenshot` means installing its two chain links as
well.

Before writing each file, check whether it already exists:

| State | Action |
|---|---|
| Absent | Write it. Report that you added it |
| Present, byte-identical | Do nothing. Report that it was already installed |
| Present, different | **Stop. Never overwrite.** Report the difference and let the user decide |

The third case is not a formality. The method may be the user's own code
that happens to share a name, or a modified copy whose behavior the
project depends on. Overwriting it silently changes program behavior.

Create files only under `Project/Sources/Methods/`. Do not modify the
`.4DProject` file, forms, classes, or anything else in the project as
part of installing a method.

After installing, validate with the `4dlsp` skill:

```sh
tools/4dlsp/tool4d-lsp-stdio validate --workspace Project/ Sources/Methods/<name>.4dm
```

**Caveat -- name collisions.** 4D method names are global, so
`run_project_form` or `test`-like names can collide with an existing user
method. If a name is taken and the existing method is unrelated, install
under a different name -- and remember that `--startup-method` must then
be given the new name. Renaming an entry point does not require editing
the chain links, but renaming a chain link does require editing the
`Formula(...)` reference that calls it.

If the user declines the install, the contracts above are complete enough
to hand-author an equivalent method, or to drive the project through a
startup method it already has.

## Startup-Method Patterns

The patterns below are for writing your own startup method when the
bundled ones do not fit. They are the same techniques the bundled methods
use.

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
