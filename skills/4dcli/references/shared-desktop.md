# Running 4D on a Shared Desktop

The agent often runs on the user's own Mac while the user keeps working.
Anything that takes focus, types or clicks can land in the user's window.
This file covers launching the full 4D app without disturbing the user,
capturing its window, and leaving no process behind.

## Never send keystrokes or clicks

The default for an unattended run. When the user explicitly asks for a live,
watched click-through, use the synthetic `CGEvent` procedure in
[`../SKILL.md`](../SKILL.md#driving-a-gui-form-with-synthetic-clicks) and keep
the rules below for everything else: target the window you started by PID,
never by owner name, and never `pkill` or `killall` a 4D app.

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

## Only touch the instance you started

The user may have their own 4D running, often the same build. Anything that
selects by app name or path (window owner `"4D"`, `tell application
"<path>/4D.app" to quit`, `killall 4D`) reaches their instance too. In a
real session a capture keyed on owner name `"4D"` grabbed the user's own
project window; after the quit-by-path that followed, no 4D was running,
so it may have closed the user's instance too. So:

1. Launch a new instance and record **its** PID.
2. Select windows by `kCGWindowOwnerPID`, never by owner name.
3. Let 4D quit itself from the startup method; otherwise `kill <literal PID>`.
4. Never `osascript ... quit`, `killall` or `pkill` a 4D app.

## Launching without stealing focus

```sh
open -g -n -a "/Applications/4D 21 R5 (100189)/4D.app" --args \
  --project "$PWD/Project/MyDemo.4DProject" --data "$PWD/Data/data.4DD" \
  --startup-method shotRun --skip-onstartup --user-param "ja|MyForm"
sleep 6
pgrep -n -f "$PWD/Project/MyDemo.4DProject"    # the PID of this instance
```

`-g` keeps it in the background, `-n` starts a new instance. Use absolute
paths; `pgrep -f` on the unique project path finds only the copy you just
started (use a scratch copy of the project if the user may have the same
one open).

## Capturing one window, even when occluded

`screencapture -x -o -l<windowID> out.png` captures one window by ID,
without sound or shadow, even behind other windows. Get the ID from
CoreGraphics by PID, not from Accessibility or the owner name:

```swift
// winid.swift -- usage: winid <pid>  ->  id width height title
import CoreGraphics
let pid = Int(CommandLine.arguments[1])!
let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as! [[String: Any]]
for w in list where (w[kCGWindowOwnerPID as String] as? Int) == pid {
  let b = w[kCGWindowBounds as String] as! [String: Any]
  print(w[kCGWindowNumber as String]!, b["Width"]!, b["Height"]!, w[kCGWindowName as String] ?? "")
}
```

Compile once (`swiftc winid.swift -o winid`) and pick the largest window
that is not the Explorer:

```sh
ID=$(./winid "$PID" | grep -v "Explorer\|エクスプローラー" | sort -k2 -n | tail -1 | cut -d' ' -f1)
screencapture -x -o -l"$ID" out.png
```

Window names and captures need the Screen Recording permission for the
terminal. Without it `kCGWindowName` is empty: match on PID and bounds,
and check the result (`../SKILL.md`, "Screenshot Sanity Check").

Prefer this real-window capture over `FORM SCREENSHOT` for review images:
it shows the real window background and text that `FORM SCREENSHOT` drops
(see `../../4dform/references/screenshot-rendering.md`).

## Preparing the window from inside 4D

The startup method opens the form and sets its state, then schedules the
quit, so the shell never has to address the app:

```4d
// shotRun -- --user-param "lang|form|..."
var $param : Text
var $unused : Real:=Get database parameter(User param value; $param)
var $p : Collection:=Split string($param; "|")
SET DATABASE LOCALIZATION($p[0])
var $window : Integer:=Open form window($p[1]; Plain form window; Horizontally centered; Vertically centered)
DIALOG($p[1]; {}; *)
CALL FORM($window; Formula(shotPrepare))  // runs after On Load
CALL WORKER("shotQuit"; Formula(DELAY PROCESS(Current process; 480)))  // ~8 s
CALL WORKER("shotQuit"; Formula(QUIT 4D))
```

Guard optional objects before using their geometry
(`If (OBJECT Get pointer(Object named; "panel")#Null)`): on a form without
the object, coordinates come back 0 and a window resized from them shrank
to 20 px.

After the capture, wait for the PID to exit (`kill -0 <pid>` in a loop);
if it is still there, `kill <literal PID>`. SIGTERM may leave the instance
running with the data file still locked: a `kill`ed 4D kept `Data.4DD` open
(visible with `lsof`) and the next launch failed with "You cannot open this
database because the data file (or one of its segments) is locked." Check
`lsof <data file>`, then `kill -9 <literal PID>` and wait for the lock to
release before relaunching.

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
  `kill <literal PIDs>`;
* any heredoc whose body contains the 4D command `KILL WORKER` (parsed as a
  `kill`): write `.4dm` files with the agent's file-editing tool, never
  with `cat <<EOF`.
