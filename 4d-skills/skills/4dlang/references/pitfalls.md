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
| A comparison mixed with arithmetic | `This.selected=$i-1` is `(This.selected=$i)-1`: a Boolean minus a number, which raises error 15 *This operation is not compatible with the two arguments* **at runtime only**. `validate`, `check-syntax` and `Compile project` (`success:true`) all pass. Write `This.selected=($i-1)`. The same applies inside a ternary condition: `(a=$i-1) ? x : y`. |
| Silent layout errors from the same rule | Where no type error results, the value is just wrong: `$x+$w/2` is `($x+$w)/2` and `$off+($a-$b)*$k` is `($off+($a-$b))*$k`. Geometry, centring and scale code (SVG, form coordinates) draws plausibly but in the wrong place. Parenthesise each sub-expression, and compute a repeated test once (`$sel:=(…=($i-1))`). |
| `&&` / `\|\|` have no precedence over each other | `$a \|\| $b && $c` is `($a \|\| $b) && $c`. Parenthesise every operand of a mixed condition. |
| Negation | Use `Not($x)`. `!` delimits date literals (`!2026-01-21!`); `not` / `!` as negation exist only inside ORDA query strings. |
| Text `=` is not exact | `"a"="A"` is True (case ignored), and `@` in the right operand is a wildcard (`"abcd"="ab@"` is True). The same holds in `Case of` branches such as `:($x="abc")` and for `#`. |
| Exact text comparison | Compare `Character code` of each character; test a literal `@` with `Character code(At sign)`. |
| No implicit number-to-text conversion | `"count: "+$count` fails (*These operators cannot be used together*, or a compile error on the analyzer): wrap every number, `"count: "+String($count)`. The same applies to `Real`, `Integer` and object/collection `.length` values. |
| `~=` is not a regex or "matches" operator | Use `Match regex("^/"; $path)`; `$path~=^/` raises *These operators cannot be used together* [50]. 4D has no bare regex comparison operator. |
| Ternary in an inferred declaration | `var $label:=$ok ? "Ready" : String($n)+" left"` was inferred as Variant (`check-syntax` 550.11). When the branches are expressions rather than literals, declare the type: `var $label : Text:=...`. |

Reference: https://developer.4d.com/docs/Concepts/operators,
https://developer.4d.com/docs/Concepts/string

## Paths, File and Folder

Three path conventions meet in one call chain and 4D converts none of them:

| Value | Convention | Construct with |
|---|---|---|
| `Get 4D folder(...)` (e.g. `Database folder`) | HFS system path, **volume-qualified** on macOS (`Macintosh HD:Users:...:`), `:`-separated | `Folder(...; fk platform path)`, then colon-join children |
| `.platformPath` of a 4D object | HFS on macOS | `File(x; fk platform path)` |
| path produced by Python, a shell or a CLI | POSIX (`/Users/...`) | `File(x; fk posix path)` |

A system path passed to `File()` / `Folder()` without a kind raises
`[3] A valid posix path was expected`; the constructor then yields Null and
later accesses cascade into `[-10716] Object or Collection Expected` /
`[55] A Boolean argument was expected` (the first error is the real one).

* Pass `fk platform path` when the string came from `Get 4D folder`,
  `.platformPath`, `Select folder` or `Select document` (both its return
  value and every element of the selected-documents array); or convert first:
  `File(Convert path system to POSIX($systemPath))`. On Windows the value is
  already a platform path, so branch on `Is Windows` rather than converting
  unconditionally.
* `File("/tmp/x.png")` (POSIX) works as-is, and `Folder("/RESOURCES/...")`
  is a 4D relative path that also works. The failure is easy to miss because
  the POSIX branch succeeds and the system path shows up only on the
  machine-specific branch.
* `Folder(<HFS path>; fk platform path).posixPath` returns **empty**: a Folder
  configured from an HFS path has no POSIX form. Convert explicitly with
  `Convert path system to POSIX($folder.platformPath)`.
* The reverse also fails: a `.platformPath` (HFS) given to
  `File(x; fk posix path)` raises the same error at runtime, which in a
  headless run looks like a dead method with no output. Give each consumer the
  convention it names, and convert at the boundary rather than once for the
  whole call chain.
* A worker, callback or `--user-param` payload does not inherit your
  convention: decide one spelling for the boundary and convert on the sending
  side (see `skills/4dcli/SKILL.md`, "Path Arguments").
* `4D.SystemWorker.new` takes a POSIX `commandLine` on macOS, so build it from
  `File(...; fk posix path).platformPath`, never by concatenating an HFS
  folder path with a name.
* Writes through a POSIX path are reliable on macOS; the "silent write
  failure" noted for `tool4d` applies to arbitrary locations, so prefer the
  database folder for evidence.

## Shared objects: `Storage`

Assigning a property on the shared `Storage` object without entering `Use`
raises `-10719 Shared Object needs a "Use" before altering a property` at
runtime (the analyzer does not catch it). Wrap every first write:

```4d
Use (Storage)
	Storage.captureWindow:=0
End use
```

The same `Use` rule applies to shared objects returned by `New shared object`
and to reading properties inside a preemptive process.

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
* Not every member returns `This`: `$e.fromObject($o)` returns nothing,
  so `$e.fromObject($o).save()` fails. Check the return type with
  `4dlang` before chaining.
* `4D.File.name` is the **display name without the extension**: `cube.stl`
  reads as `cube`. Building a path back from a collected `.name` produces
  `.../cube` and a "file not found" from whatever consumes it. Use
  `.fullName` whenever the name must round-trip into a path, and
  `.extension` when only the suffix is wanted.

## Value Types, Null and Guards

* `String($o.key)` on a property that holds **Null** (for example a JSON
  `null` from a CLI envelope: `{"stage": null}`) returns the text `"null"`,
  not `""`. A guard such as `If (String($e.stage)#"")` is always true and
  prints `stage: null`. Test `$e.stage#Null` first. Observed on 21 R5.
* `Is number` is **not** a `Value type` constant. `Value type($x)#Is number`
  compiles, runs and is **always true** (the undefined constant evaluates to
  0 and no type equals 0), so the guard never skips anything. The numeric
  constants are `Is real`, `Is integer` and `Is longint`; test all three when
  the value may come from an object property or from `JSON Parse`.
* `Value type` returns an Integer, not a type name. `"type="+Value type($x)`
  raises a runtime type error instead of concatenating; wrap it:
  `"type="+String(Value type($x))`.
* `Error description` and `Error code` do not exist. Both compile (read as
  undeclared variables, so `validate` and `check-syntax` stay silent) and
  evaluate to empty, which turns a handler built on them into a no-op. Read
  the failure from `Last errors` (a collection; `[0].errCode`,
  `[0].message`) plus `Error method`, `Error line` and `Error formula`.
  Measured on tool4d 21R4 with `ON ERR CALL(...; ek local)`.
* An error handler is called with **no parameters** (`Count parameters`
  is 0 there, measured on tool4d 21R4). `#DECLARE($type : Integer)` plus
  `If ($type=2)` is never true, so the handler never reports. If the
  handler itself raises an error it is called again until 4D reports
  `-9996 Stack is full`: start it with `ON ERR CALL(""; ek local)`. Do not
  write `Form` from a handler that may run outside a window: there `Form`
  is an empty object (`Value type(Form)=Is object`), not Null.
* A process-scoped `var X : Type` declared inside a method persists between
  `CALL WORKER` messages **and starts as Null** in a fresh process, not as 0
  or empty. `If ($counter<$limit)` is then never true, and the loop silently
  runs zero times: seed it (`If (Not(IsNumeric($counter))) $counter:=0`).
* Comparing anything with Null is False, including `$x>=0` and `$x#0`.
  Null is only caught by an explicit `#Null` / `Value type($x)=Is Null` test.

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

## File names and pictures

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
* The child process does not die with the 4D process that started it:
  `QUIT 4D` from a startup method or harness leaves it running, re-parented
  to PID 1, and it keeps whatever it holds (a PTY, a port, a lock). Call
  `.terminate()` before quitting; do not rely on the form's `On Unload`.
* In `onTerminate`, compare `$worker.pid` with the pid of the worker the
  object currently holds before resetting state. After `stop()` and a
  restart, a late `onTerminate` of the *old* process would otherwise mark
  the new one stopped.
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

## Timers, Ticks and Background Windows

* macOS App Nap stretches timers in an unattended application: a
  `SET TIMER(1000)` window was measured updating roughly every 16 s, and
  `DELAY PROCESS` ticks stretch the same way. Never derive correctness from a
  tick count; make each tick idempotent and let the work re-check state.
* `CALL FORM($window; Formula(...))` from a **different** process into a
  window that nobody is clicking is unreliable: the formula frequently does
  not execute and there is no error to observe. Publish state to a document
  (or a shared object reached through the worker) and let the window pull it
  on its own timer, applying only entries newer than a cursor it owns.
* `DELAY PROCESS(Current process; n)` does not deliver SystemWorker callbacks
  while it runs, so a wait loop cannot keep a session alive by sleeping: pump
  the form (`CALL FORM($window; Formula(Pump))`) or read published state.
* A GUI application writes nothing to stdout. `LOG EVENT(Into system standard
  outputs; ...)` is a tool4d-only diagnostic; in an application the harness
  can only observe files the code writes itself, so design the run to publish
  a machine-readable report.

## Number Formatting, File API and Commands That Look Like Procedures

| Pitfall | Rule |
|---|---|
| `String(value; "0.#####")` | Not a safe general formatter: values with two or more integer digits come back as `<<<<<<<` (`41.313` -> `<<<<<<<`, `5618.49` -> `<<<<`, while `0.4` stays `0.4`). `String(value; "##.#####")` works. For machine-readable text (JSON, SVG attributes) use plain `String(value)` or format by hand. |
| `String(value)` and the locale | Single-argument `String` uses the host decimal separator, so a comma-decimal system emits `41,313` — fatal in a JSON number or an SVG coordinate. Normalise the separator before writing structured text. |
| `String(value; format; separator)` | Not an overload: the third argument is not a decimal-separator argument, and this call fails compilation with `At least one parameter type does not match the prototype(s) of the function "String"` plus `Invalid constant type : Alphanumeric`. |
| `Min(a; b)` / `Max(a; b)` | Array commands. With two scalars, compilation fails as `Impossible to cast Real to Array<Variant>.` / `Invalid constant type : Real` — the diagnostics never mention `Min`. Compare with `math` operators or a user helper. |
| `4D.Folder.delete()` | Refuses a non-empty folder: `[651] Folder  not empty`. Use `DELETE FOLDER($folder.path; Delete with contents)` for scratch directories. The failure is catchable by `Try`, but `Last errors` is empty in that `Catch`. |
| `Open document(path)` as a statement | It is a function: `This function has been called as a procedure.` Assign or discard the result (`$opened:=String(Open document($path))`). |
| `CONFIRM(message {; okTitle {; cancelTitle}})` as a function | It is a procedure: it returns nothing and reports the choice in the `OK` system variable (`1` = OK button). Write `CONFIRM(...)` then `If (OK#1)`. The title order is OK first, then Cancel, so `CONFIRM($msg; "Cancel"; "Title")` labels the OK button "Cancel". `tool4d-lsp-stdio validate` returned 0 diagnostics for `If (Not(CONFIRM(...)))`, so the analyzer does not catch it; the dialog needs a person, so check the path by reading it, not by a headless run. |
| Restoring an error handler | `ON ERR CALL($previous; ek local)` restores nothing if `$previous` was never assigned: an empty text removes the handler. Capture it first, `$previous:=Method called on error(ek local)`, then install yours. The analyzer reports no diagnostic for an unassigned `$previous`. Found by code review, not a measured run. |
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
| `Current date` / `Current time` | **Local** date and time. A field labelled UTC (an RFC 3339 `...Z` stamp) built from `Current date` is a day off near local midnight. `Timestamp` is always UTC (`2026-11-26T05:13:17.085Z`): use `Date(Substring(Timestamp; 1; 10))` for the UTC date. Measured on 4D 21 R5 / tool4d. |

The `ISO` format constants produce full date+time strings, so a value destined
for an API that wants `YYYY-MM-DD` or `HH:MM:SS` needs a slice
(`Substring(String($d; ISO date); 1; 10)`) or the three-argument combined form.
Measured on 21 R5 (100176).
