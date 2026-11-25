# 4D Language Pitfalls

Language constraints and rules that can compile cleanly but behave differently
from what an agent used to other languages expects. Look up exact signatures with the lookup tools
(`skills/4dlang/SKILL.md`); validate with `skills/4dlsp/SKILL.md`.

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Operators

| Pitfall | Rule |
|---|---|
| No arithmetic precedence | Expressions are evaluated strictly left to right: `3+4*5` is `35`. Write `3+(4*5)`. |
| `&&` / `\|\|` have no precedence over each other | `$a \|\| $b && $c` is `($a \|\| $b) && $c`. Parenthesise every operand of a mixed condition. |
| Negation | Use `Not($x)`. `!` delimits date literals (`!2026-01-21!`); `not` / `!` as negation exist only inside ORDA query strings. |
| Text `=` is not exact | `"a"="A"` is True (case ignored), and `@` in the right operand is a wildcard (`"abcd"="ab@"` is True). The same holds in `Case of` branches such as `:($x="abc")` and for `#`. |
| Exact text comparison | Compare `Character code` of each character; test a literal `@` with `Character code(At sign)`. |

Reference: https://developer.4d.com/docs/Concepts/operators,
https://developer.4d.com/docs/Concepts/string

## Objects and Literals

* Keys written in a `{}` literal must be valid identifiers (start with a
  letter, `_` or `$`; no spaces, dashes or dots). For other names use
  `New object("first name"; $v)` or `$o["first name"]:=$v`.
* Reading a property of an **undefined** property returns undefined;
  reading a property of a **Null** value raises an error. Guard with
  `#Null` (entity attributes: `skills/4dorda/SKILL.md`).
* Large inline literals (long text, big `{}` / `[]` blocks) can fail
  silently: observed as the expression evaluating to Null once the source
  exceeds roughly 32 KB in compiled mode. Keep data in a file under
  `Resources/` and load it: `JSON Parse(File("/RESOURCES/data.json").getText())`.
* Numeric object properties are always **Real**: `Value type($o.count)`
  is `Is real` even for `New object("count"; 42)` or an integer parsed
  from JSON. A guard such as `Value type($o.count)=Is longint` is never
  true and silently skips its branch. Accept `Is real` (add `Is longint`
  only for values that are not object properties) and check integrality
  separately if it matters.
* **Collections are 0-based**, while arrays are 1-based. `$c[0]` is the
  first element, `$c.length` is the count, so the array idiom
  `For ($i; 1; $c.length)` skips element 0 and then raises
  `Index in collection is out of range (-10713)` on the final pass.
  Iterate `For ($i; 0; $c.length-1)` or use `For each ($item; $c)`.
* `4D.File.name` is the **display name without the extension**: `cube.stl`
  reads as `cube`. Building a path back from a collected `.name` produces
  `.../cube` and a "file not found" from whatever consumes it. Use
  `.fullName` whenever the name must round-trip into a path, and
  `.extension` when only the suffix is wanted.

## Instance checks and inheritance boundaries

* `OB Instance of(object; class)` requires an **Object** as its first
  parameter, not an arbitrary Variant. Before checking a value that may
  be a collection or scalar, establish its Object type with `Value type`
  in a guard that prevents the instance check from executing otherwise.
  Checking only `#Null` does not exclude collections/scalars. Do not rely
  on an unchecked compound expression to protect the call.
* A user class cannot extend a user class from another project or
  component. Put a test subclass in the same project/component fixture
  as its parent, or use composition at the boundary. The official class
  reference warns that inheritance-rule violations are detected by the
  compiler / check syntax, not necessarily the editor or interpreter.
  Test doubles must respect the same boundary as production classes.

References: https://developer.4d.com/docs/commands/ob-instance-of,
https://developer.4d.com/docs/Concepts/classes#class-extends-classname

## Paths, file names and pictures

* `File("chart.tif")` / `File("sub/x.png")` and `Folder("sub")` raise
  `FiFo [3] A valid posix path was expected.` -- a bare or relative name is
  not a path. Resolve it first
  (`Folder(fk database folder).folder("Out").file($name).path`) or pass the
  path kind explicitly. Nested inside another member call's argument list the
  same failure was reported as `-10729 Unknown member method` naming an
  **empty** method, which reads as a missing class function; split the chain
  into locals before concluding the function does not exist.
* `File.extension` includes the leading dot (`.tif`), so `"."+$ext` yields
  `name-2..tif`.
* A typed `Picture` property that was never assigned is not an empty picture:
  `Picture size($object.picture)` raises `[59] 4D was expecting a picture.`
  Assign a real picture when the object is constructed (a 4x4 transparent
  PNG read with `READ PICTURE FILE` is enough); do not leave it unassigned
  and do not assign `Null`.
* `Picture size` returns **bytes**, not dimensions; use `PICTURE PROPERTIES`
  when the width/height matter.

## Formula, `This` and `.call()`

* `Formula(...)` copies the **values** of local variables when the formula
  object is created; `This` is resolved when it is **called**. Inside a
  formula handed to `CALL FORM`, a timer, a callback or a subform, `This`
  is not the object that created it. Capture it first:

  ```4d
  var $self:=This
  CALL FORM(Current form window; Formula($self.refresh()))
  ```

* The first argument of `$f.call()` and `$f.apply()` is always the object
  used as `This`. Pass `Null` when there is none:
  `$f.call(Null; $param1; $param2)`.

Reference: https://developer.4d.com/docs/API/FunctionClass

## 4D.HTTPRequest

* `response.body` type follows `dataType`. With the default `"auto"`, JSON
  responses are already an **Object**, text/JavaScript/XML/form responses
  are Text, anything else is a Blob. Do not `JSON Parse` blindly: check
  `Value type($request.response.body)` or set `dataType: "text"` /
  `"object"` explicitly.
* Callbacks (`onResponse`, `onError`, ...) without `.wait()` fire only if
  the calling process is a **worker** (`CALL WORKER`, not `New process`).
  The window pattern in `skills/4dstartup/SKILL.md` runs forms in worker 1,
  so callbacks reach the form.
* Callback order: `onHeaders` once → `onData` zero or more times →
  `onResponse` or `onError` once → `onTerminate` once.
* `.wait()` blocks the process (and its form) until the response arrives.

Reference: https://developer.4d.com/docs/API/HTTPRequestClass

## 4D.SystemWorker

* Callback order: `onData` / `onDataError` zero or more times → `onError`
  at most once (stops processing) → `onResponse` **only if no error** →
  `onTerminate` always. Code that releases a worker, advances a queue or
  marks completion only in `onResponse` leaks state after an error; do
  cleanup in `onTerminate`.
* `onDataError` is the process's stderr, not a failure signal. Many tools
  log progress there. `onError` is a system/runtime error.
* If the process cannot start, `4D.SystemWorker.new()` throws and returns
  `Null` -- no callback fires. Handle that path separately.
* An error from `postMessage()` (for example POSIX 32, broken pipe) means
  the process has already exited and closed its stdin. It is a symptom,
  not the cause: keep the stderr collected in `onDataError` and report
  it with the exit code from `onTerminate`. Those callbacks can run after
  the failed write, so do not let the write error replace the diagnostic.
* A started process is not a ready service. For a server, poll its own
  documented readiness endpoint with a deadline; an open port or the first
  `onData` proves only that something launched.
* `commandLine` is not run through a shell: shell builtins and pipes do
  not work (use `cmd /c` or `/bin/sh -c` explicitly), and quoting must be
  tested with paths containing spaces and quotes.

Reference: https://developer.4d.com/docs/API/SystemWorkerClass

## Workers and `Signal.wait()`

* A worker runs its `CALL WORKER` messages one at a time, in order. A
  message waits behind every earlier one, including a slow callback or a
  first-use initialisation queued on the same worker.
* `$signal.wait(n)` in the caller counts from the call to `wait()`, not
  from the moment the worker starts the message. The timeout therefore covers the
  queue as well as the work, and can expire before the work begins.
* Keep user callbacks and one-time setup off a worker whose messages are
  timed, or run the setup once under its own, longer deadline before the
  timed calls start.
* A cooperative worker only advances when other cooperative processes
  yield; the debugger, a modal dialog or a long loop without
  `DELAY PROCESS` holds it while the caller's timeout keeps running.

References: https://developer.4d.com/docs/API/SignalClass,
https://developer.4d.com/docs/Develop/processes

## Number Formatting, File API and Commands That Look Like Procedures

| Pitfall | Rule |
|---|---|
| `String(value; "0.#####")` | Not a safe general formatter: values with two or more integer digits come back as `<<<<<<<` (`41.313` -> `<<<<<<<`, `5618.49` -> `<<<<`, while `0.4` stays `0.4`). `String(value; "##.#####")` works. For machine-readable text (JSON, SVG attributes) use plain `String(value)` or format by hand. |
| `String(value)` and the locale | Single-argument `String` uses the host decimal separator, so a comma-decimal system emits `41,313` — fatal in a JSON number or an SVG coordinate. Normalise the separator before writing structured text. |
| `String(value; format; separator)` | Not an overload: the third argument is not a decimal-separator argument, and this call fails compilation with `At least one parameter type does not match the prototype(s) of the function "String"` plus `Invalid constant type : Alphanumeric`. |
| `Min(a; b)` / `Max(a; b)` | Array commands. With two scalars, compilation fails as `Impossible to cast Real to Array<Variant>.` / `Invalid constant type : Real` — the diagnostics never mention `Min`. Compare with `math` operators or a user helper. |
| `4D.Folder.delete()` | Refuses a non-empty folder: `[651] Folder  not empty`. Use `DELETE FOLDER($folder.path; Delete with contents)` for scratch directories. The failure is catchable by `Try`, but `Last errors` is empty in that `Catch`. |
| `Open document(path)` as a statement | It is a function: `This function has been called as a procedure.` Assign or discard the result (`$opened:=String(Open document($path))`). |
| `var` placement | A `var` inside an `If` or `For each` block compiles and is block-scoped; the "declarations must be at the top" rule forbids a redeclaration, not a block-local declaration. Keep declarations at the top by convention, and do not diagnose block-local `var` as a syntax error. |

## Command Signatures Often Guessed Wrong

| Command | Correct use |
|---|---|
| `OBJECT SET VALUE(name; value)` | Object name only -- no `*` parameter |
| `OBJECT SET TITLE(*; name; title)` | Static text and button labels (not `OBJECT SET VALUE`) |
| `OBJECT SET COORDINATES(*; name; left; top {; right; bottom})` | Absolute coordinates, not width / height (`skills/4dform/references/layout.md`) |
| `OBJECT SET CSS CLASS` | Does not exist: use `OBJECT SET RGB COLORS`, `OBJECT SET FONT STYLE`, ... (`skills/4dcss/SKILL.md`) |
| `BLOB TO PICTURE(blob; picture {; codec})` | Codec is optional |
| `Time string(time; format)` | One argument only. A format argument is not rejected until run time: `Time string($t; ISO time)` aborts with `[58] A ")" was expected.` |
| `String(date; ISO date)` | `2026-11-26T00:00:00`, **not** `2026-11-26` -- the string carries a zero time as well |
| `String(time; ISO time)` | `0000-00-00T05:44:44` -- a zero date as well |
| `String(date; ISO date; time)` | `2026-11-26T05:44:44`: the three-argument form is the one that yields an ISO timestamp |

The `ISO` format constants produce full date+time strings, so a value destined
for an API that wants `YYYY-MM-DD` or `HH:MM:SS` needs a slice
(`Substring(String($d; ISO date); 1; 10)`) or the three-argument combined form.
Measured on 21 R5 (100176).
