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
* A started process is not a ready service. For a server, poll its own
  documented readiness endpoint with a deadline; an open port or the first
  `onData` proves only that something launched.
* `commandLine` is not run through a shell: shell builtins and pipes do
  not work (use `cmd /c` or `/bin/sh -c` explicitly), and quoting must be
  tested with paths containing spaces and quotes.

Reference: https://developer.4d.com/docs/API/SystemWorkerClass

## Command Signatures Often Guessed Wrong

| Command | Correct use |
|---|---|
| `OBJECT SET VALUE(name; value)` | Object name only -- no `*` parameter |
| `OBJECT SET TITLE(*; name; title)` | Static text and button labels (not `OBJECT SET VALUE`) |
| `OBJECT SET COORDINATES(*; name; left; top {; right; bottom})` | Absolute coordinates, not width / height (`skills/4dform/references/layout.md`) |
| `OBJECT SET CSS CLASS` | Does not exist: use `OBJECT SET RGB COLORS`, `OBJECT SET FONT STYLE`, ... (`skills/4dcss/SKILL.md`) |
| `BLOB TO PICTURE(blob; picture {; codec})` | Codec is optional |
