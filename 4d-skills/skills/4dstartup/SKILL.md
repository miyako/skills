---
name: 4dstartup
description: >
  The canonical non-blocking pattern for opening a 4D application's first
  window (startup / splash / main form) and chaining to the next form:
  #DECLARE($params : Object), window reuse with WINDOW LIST + CALL FORM,
  CALL WORKER(1; Current method name; {}), SET MENU BAR, Open form window
  with Plain form window, DIALOG(...; *), Accept-action buttons that open the
  next form, and INVOKE ACTION(ak return to design mode) instead of QUIT 4D.
  Use when writing or modernising On Startup / start methods or any method
  that opens a form window from a menu.
---

# 4D Startup Window Pattern

## Scope

This skill is the **single** pattern for opening a form window when the
application starts, from a menu item, or from another form. Every other
skill that opens a window (AI Kit demos, localisation, technote demos)
links here instead of restating it.

It replaces these legacy patterns:

* `New process` used only to get a fresh event cycle
* blocking `DIALOG(form)` followed by `CLOSE WINDOW`
* chains of blocking `DIALOG` calls from `On Startup` (the first modal
  window stays open behind the next one)
* `Pop up form window` for a window with interactive controls
* `QUIT 4D` when a demo cannot run
* version checks against releases older than v17 (any `.4DProject` runs on
  v17+, so they are dead code)

### Not in this skill

| Topic | Skill |
|---|---|
| Form JSON, `"method"` / `"events"` wiring, `"action"` | `4dform` |
| Localised window titles and labels | `4dlocalise` |
| `C_*` → `#DECLARE` in the rest of the project | `4dmodernise` |
| `menus.json` items that call the start method | `4dproject` (`references/menus.md`) |
| Running the project headlessly (tool4d) | `4dcli` |

References:
- `CALL WORKER`: https://developer.4d.com/docs/commands/call-worker
- `CALL FORM`: https://developer.4d.com/docs/commands/call-form
- `DIALOG`: https://developer.4d.com/docs/commands/dialog
- `Open form window`: https://developer.4d.com/docs/commands/open-form-window
- `INVOKE ACTION`: https://developer.4d.com/docs/commands/invoke-action
- Standard actions: https://developer.4d.com/docs/Desktop/standard-actions

## The Start Method

One project method (any name, e.g. `Start`), called **without parameters**
by the `On Startup` database method and/or a menu item, and **with** a
parameter by itself through `CALL WORKER`:

```4d
#DECLARE($params : Object)

var $title : Text
var $window : Integer
$title:=Localized string("Main_WindowTitle")  // or a fixed title

If (Count parameters=0)
	
	// already open? bring it to the front instead of opening a duplicate
	ARRAY LONGINT($windows; 0)
	WINDOW LIST($windows)
	var $i : Integer
	For ($i; 1; Size of array($windows))
		$window:=$windows{$i}
		If (Window process($window)=1) && (Get window title($window)=$title)
			var $left; $top; $right; $bottom : Integer
			GET WINDOW RECT($left; $top; $right; $bottom; $window)
			CALL FORM($window; Formula(SET WINDOW RECT($left; $top; $right; $bottom; $window)))
			return 
		End if 
	End for 
	
	CALL WORKER(1; Current method name; {})
	
Else 
	
	SET MENU BAR(1)
	$window:=Open form window("Main"; Plain form window; Horizontally centered; Vertically centered)
	SET WINDOW TITLE($title; $window)
	DIALOG("Main"; $params; *)
	
End if 
```

| Element | Why |
|---|---|
| `#DECLARE($params : Object)` | One optional parameter: `Count parameters` tells the two roles apart. The method stays **visible** (it is an entry point -- see the `4dmethods` skill). |
| `WINDOW LIST` + title match + `CALL FORM` / `SET WINDOW RECT` | Re-running the method (menu, second startup) brings the existing window to the front instead of opening a duplicate. `CALL FORM` runs the call in the window's own process. |
| `CALL WORKER(1; Current method name; {})` | Runs the `Else` branch in the application process (worker 1). `{}` (an empty object) is the parameter that selects the `Else` branch. Replaces `New process`. |
| `SET MENU BAR(1)` | Keeps the menu bar installed after the window closes. |
| `Plain form window` | A normal movable window. Never `Pop up form window` for a window with controls: pop-ups close when the user clicks outside and are not movable. It is also the default when the type is omitted. |
| `SET WINDOW TITLE` | The title is what the reuse loop matches on. |
| `DIALOG(form; data; *)` | `*` makes the dialog non-blocking in the worker; the window lives as long as the form. No `CLOSE WINDOW`. |

Rules:

* **Declare each local once, above the `If`.** `var` is method-scoped, not
  block-scoped: declaring `$window` in both branches triggers "Redefinition
  of variable".
* `GET WINDOW RECT` / `SET WINDOW RECT` take `left; top; right; bottom`
  in that order -- name the variables accordingly.
* Arrays are still declared with `ARRAY LONGINT`, not `var`.
* Write commands without token suffixes unless the exact token already
  appears in the project (token rules in `skills/4dproject/SKILL.md`).

The `On Startup` database method
(`Project/Sources/DatabaseMethods/onStartup.4dm`) just calls the start
method with no argument.

## Moving to the Next Form

A button that leaves the current form for the next one has the **Accept**
standard action (`"action": "accept"` in the form JSON) and an object method
that opens the next form in its own window on `On Clicked`:

```4d
// the button has the "accept" standard action
If (FORM Event.code=On Clicked)
	var $window : Integer
	$window:=Open form window("Next"; Plain form window; Horizontally centered; Vertically centered)
	SET WINDOW TITLE(Get window title(Current form window); $window)
	DIALOG("Next"; Form; *)
End if 
```

* Accepting closes the current form; the new window replaces it.
* Passing `Form` hands the current form data to the next form.
* Copying the window title keeps the start method's reuse loop working.
* The object method only runs if the object in `form.4DForm` has
  `"method": "ObjectMethods/<name>.4dm"` and `"events": ["onClick"]`.

## Leaving Instead of Quitting

When the application cannot continue (missing license, unsupported
feature), do not call `QUIT 4D` -- it is hostile during development.
Return to the IDE gracefully:

```4d
INVOKE ACTION(ak return to design mode)
```

Label the corresponding button "Close" (localised), not "Quit 4D".

## Anti-Patterns

| Do not | Do |
|---|---|
| `$p:=New process(Current method name; 0; Current method name; 0)` | `CALL WORKER(1; Current method name; {})` |
| `DIALOG("Main"; $data)` + `CLOSE WINDOW` | `DIALOG("Main"; $data; *)` |
| `Open form window("Main"; Pop up form window; ...)` | `Plain form window` |
| `QUIT 4D` on failure | `INVOKE ACTION(ak return to design mode)` |
| `If (Application version<"1650")` | nothing -- dead code in a `.4DProject` |
| `C_TEXT($cr)`, `If (Shift down)` debug scaffolding | remove dead code |
| `var $window` in both branches | declare once above the `If` |
| Missing `SET MENU BAR(1)` | install the menu bar before opening the window |

## Checklist

- [ ] Start method uses `#DECLARE($params : Object)` and `Count parameters=0` to choose the role
- [ ] Existing window found by title and brought to front with `CALL FORM` + `SET WINDOW RECT`
- [ ] `CALL WORKER(1; Current method name; {})`, no `New process`
- [ ] `SET MENU BAR(1)` before opening the window
- [ ] `Plain form window` and `DIALOG(...; *)`; no `CLOSE WINDOW`
- [ ] Next-form buttons: Accept action + `On Clicked` opening the next form with `DIALOG(...; *)` and the same title
- [ ] Object methods referenced by `"method"` in `form.4DForm`
- [ ] No `QUIT 4D`, no obsolete version checks, no dead code
- [ ] Locals declared once; changed `.4dm` validated with `4dlsp`
- [ ] User-visible strings localised (`4dlocalise`)
