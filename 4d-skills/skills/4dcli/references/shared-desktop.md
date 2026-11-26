# Running 4D on a Shared Desktop

The agent often runs on the user's own Mac while the user keeps working.
Anything that takes focus, types or clicks can land in the user's window.
This file covers launching the full 4D app without disturbing the user,
capturing its window, and leaving no process behind.

## Never send keystrokes or clicks

4D form objects are not exposed to Accessibility: System Events sees the
window but no text fields or buttons. `activate` followed by `keystroke`
raced with the user's browser in a real session: the screenshot showed the
user's Chrome window, and the pasted text plus Return may have gone to the
user's app.

* Do not drive 4D forms with `osascript ... keystroke`, `cliclick` or
  similar. Verify interactive behaviour headlessly instead: call the methods
  the buttons call from a `tool4d` startup method (`../SKILL.md`,
  "Startup-Method Patterns") and assert on `Form` or the data.
* For a form that must be seen after `On Load`, use the
  `dialog_screenshot` chain (`../SKILL.md`), which captures from inside 4D.

## Launching without stealing focus

```sh
open -g -n -a "/Applications/4D v21 R5/4D.app" --args \
  --project "$PWD/Project/MyDemo.4DProject" --data "$PWD/Data/data.4DD"
```

`-g` keeps it in the background, `-n` starts a new instance. Use absolute
paths.

## Capturing one window, even when occluded

`screencapture -x -o -l<windowID> out.png` captures one window by ID,
without sound or shadow, even behind other windows. Get the ID from
CoreGraphics, not from Accessibility:

```swift
// winid.swift -- usage: swift winid.swift 4D "Window title"
import CoreGraphics
let a = CommandLine.arguments
let list = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
for w in list where (w[kCGWindowOwnerName as String] as? String) == a[1]
    && (w[kCGWindowName as String] as? String ?? "").contains(a[2]) {
  print(w[kCGWindowNumber as String]!); break
}
```

Window names and captures need the Screen Recording permission for the
terminal. Without it `kCGWindowName` is empty: match on owner and bounds,
and check the result (`../SKILL.md`, "Screenshot Sanity Check").

## Quitting

```sh
osascript -e 'tell application "/Applications/4D v21 R5/4D.app" to quit'
```

An Apple Event addressed by path quits that copy without keystrokes.

## Background servers started by the project

Components such as `miyako/llama-cpp` start helper servers (llama-server)
that can outlive the 4D process that started them:

* An orphan left by the component ignored `SIGTERM` (a llama-server
  started by hand from the shell does exit on `SIGTERM`, so test the
  orphan, not a stand-in). The component's `terminate()` only stops a
  server owned by the **current** process's worker.
* A headless build that quit without stopping its server left an orphan
  on the port. Later GUI sessions silently reused it and could never stop
  it.

Rules for any startup method that may start such a server:

1. Remember whether **this run** started it
   (`var $startedHere:=Not($model.isReady())`).
2. When `$startedHere`, stop it before `QUIT 4D`; in GUI runs stop it in
   `On Exit`.
3. After the run, check the port: `lsof -ti tcp:PORT -sTCP:LISTEN`. For an
   orphan, `kill -9 <pid>` with the literal PID.

## Agent shell constraints

Some agent hosts reject shell forms they cannot attribute:

* a compound `cd dir && cat <<EOF ...` heredoc ("shell path attribution
  could not be completed") -- use absolute paths, or write a script file and
  run it;
* `kill $(...)` / `kill $pid` -- list the PIDs first, then
  `kill <literal PIDs>`.
