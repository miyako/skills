---
object: "form"
json_type: null
keywords: ["async", "non-blocking", "long operation", "SET TIMER", "On Timer", "CALL FORM", "CALL WORKER", "HTTPRequest callback", "spinner", "progress", "freeze"]
summary: "Keeping a form responsive during long work: why handlers freeze the form, and three patterns (async callbacks, SET TIMER chunking, worker + CALL FORM) with their form-side requirements."
---

# Async UI Patterns

A form only redraws between event cycles, so a long `On Clicked` handler
freezes it, spinners included (`references/form-concepts.md`, "Event
Cycle Architecture"). Work that takes more than a moment must return
control to the form and come back later.

The window itself (`CALL WORKER(1; ...)`, `Open form window`,
`DIALOG(form; data; *)`) is owned by `skills/4dstartup/SKILL.md`; this file
covers what happens inside an open form.

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Choosing a Pattern

| Work | Pattern | Form requirement |
|---|---|---|
| Network call (`4D.HTTPRequest`, AI Kit) | Asynchronous request with callbacks, no `.wait()` | Form runs in a worker (4dstartup pattern); see `skills/4dlang/references/pitfalls.md` / `skills/4daikit/SKILL.md` |
| Many small steps in the form's process (import rows, build a list) | `SET TIMER` chunking | `"onTimer"` in the form `events` |
| Heavy work that can run elsewhere | `CALL WORKER("name"; ...)`, then `CALL FORM` back | Window reference kept in the form object |

In all cases, show progress with a spinner or progress indicator bound to a
form property, and set it back when done (a spinner set to 0 stops but
stays in place -- hide it with `OBJECT SET VISIBLE`).

## `SET TIMER` Chunking

```4d
// start (e.g. On Clicked)
Form.todo:=$items
Form.busy:=1
SET TIMER(-1)  // On Timer at the next event cycle

// form method, On Timer
var $n:=0
While (Form.todo.length>0) && ($n<100)
	Form.process(Form.todo.shift())
	$n+=1
End while
If (Form.todo.length=0)
	SET TIMER(0)  // stop
	Form.busy:=0
End if
```

Keep each tick short (a fixed count or a time budget); the form redraws
between ticks. `SET TIMER(0)` stops the timer.

## Worker + `CALL FORM`

```4d
// form: start
Form.window:=Current form window
CALL WORKER("importer"; Formula(runImport); Form.window; $path)

// project method runImport, in the worker
#DECLARE($window : Integer; $path : Text)
var $result:=...  // heavy work
CALL FORM($window; Formula(Form.onImportDone($1)); $result)
```

* `CALL FORM` runs the formula in the form's process at its next event
  cycle, with `Form` being that form's object.
* Pass data as parameters; a `Formula` copies local values but not `This`
  (`skills/4dlang/references/pitfalls.md`).
* Standard objects and collections passed to another process are copied;
  pass plain values (window number, path text) rather than references.
