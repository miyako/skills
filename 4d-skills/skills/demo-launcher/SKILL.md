---
name: demo-launcher
description: >
  A launcher form for a 4D demo that shows several forms or variants: one
  button per demo form, a "side by side" button that places windows from
  Screen width, an in-app language toggle that closes and reopens every
  demo window at the same place in the new language (SET DATABASE
  LOCALIZATION, SET MENU BAR rebuild), a single launcher window even when
  the start method runs twice, a pinned colorScheme, and a CALL FORM smoke
  test. Use when a webinar or seminar demo needs a start screen, a
  language switch for the presenter, or two forms compared on one screen.
---

# Demo Launcher

A small form that opens first and lets the presenter reach each part of
the demo in one click, in either UI language (e.g. en/ja). The names
below (`Demo_*`, `Launcher`, `FormA`/`FormB`) are examples.

## Related

| Topic | Skill |
|---|---|
| Start method, worker 1, window reuse, `DIALOG(...; *)` | `4dstartup` |
| XLIFF, `SET DATABASE LOCALIZATION`, why not `Common*` IDs | `4dlocalise` |
| Comparing an old and a new technique | `demo-feature-comparison` |
| Live presentation, Japanese wording, pinned `colorScheme` | `demo-presentation` |
| Shareable repository, README | `demo-shareable-repo` |
| Runtime captures, smoke tests | `4dcli` |

## Layout

| Object | Notes |
|---|---|
| Title and one-line subtitle | localised (`:xliff:`) |
| Language toggle | a dropdown or segmented control with an object data source `{values; index}`; the language names are endonyms ("English", "日本語"), the same in every XLIFF file |
| One button per demo form | label = what the audience sees, not the form name |
| "Side by side" button | when two forms are compared |

Pin `"colorScheme"` on the launcher as on every demo form
(`demo-presentation`, "Appearance").

## Methods

All windows live in **worker 1**: the start method hops there
(`4dstartup`), and the launcher's buttons run in its form method, so the
demo windows open in the same process with `DIALOG(...; *)`.

| Method | Role |
|---|---|
| `Start` | the `4dstartup` start method; passes its parameter object to the launcher as `Form` (`{reopen: [...]}` after a language switch) |
| `Demo_windowTitle(form)` | the localised title of a demo window; the single place that maps a form to its title |
| `Demo_openForm(form; position)` | finds the window by title and moves it to the front (and to `position`), or opens it with `Open form window(form; Plain form window; left; top)` + `DIALOG(form; {}; *)` |
| `Demo_sideBySide` | computes two positions and calls `Demo_openForm` twice |
| `Demo_switchLanguage(lang)` | the switch below |

Mark the helpers invisible (`4dmethods`); only `Start` is an entry point.

### Side by side

```4d
var $width; $height; $top; $gap; $left1; $left2 : Integer
FORM GET PROPERTIES("FormA"; $width; $height)
$gap:=12
$top:=Menu bar height+40
If (Screen width>=((2*$width)+(3*$gap)))
	$left1:=(Screen width-((2*$width)+$gap))\2
	$left2:=$left1+$width+$gap
Else   // narrow screen (projector): overlap, staggered
	$left1:=$gap
	$left2:=Screen width-$width-$gap
End if 
Demo_openForm("FormA"; {left: $left1; top: $top})
Demo_openForm("FormB"; {left: $left2; top: $top+24})
```

Parenthesise every sub-expression: 4D has no operator precedence
(`skills/4dlang/references/pitfalls.md`). Check the result at the
projector's resolution (1280×800 is a safe assumption).

### Language switch

`SET DATABASE LOCALIZATION` changes only what is displayed afterwards, and
menus built from `:xliff:` keep their language until the menu bar is
installed again. So the switch rebuilds everything:

1. In the launcher's form method, collect each open demo window (form
   name and rect, found by its localised title) and close it with
   `CALL FORM($window; Formula(CANCEL))`.
2. `SET DATABASE LOCALIZATION($lang)`.
3. `CANCEL` the launcher itself.
4. `CALL WORKER(1; "Start"; {reopen: $reopen})`. `Start` runs
   `SET MENU BAR(1)` again (menus rebuild in the new language) and opens
   a new launcher with `Form.reopen`.
5. The launcher's `On Load` reopens each window at its saved place with
   `Demo_openForm`.

The toggle's current index comes from
`Get database localization(Current localization)="ja@"` (pass the
constant explicitly). Every string on the launcher, the demo forms and the
menus must use **project** XLIFF IDs: built-in `Common*` IDs do not follow
the switch (`4dlocalise`).

### Only one launcher

`--startup-method` does not replace `On Startup`, and a presenter may
press the menu shortcut twice. The start method must check for an open
launcher **inside worker 1**, after its `CALL WORKER` hop, or two
launchers open (`4dstartup`, "Why the check runs in the worker"). A
`File` menu item ("Demo Launcher…", with a shortcut) that calls `Start`
brings it back after it is closed.

## Smoke Test

Test the flows without clicking: a scratch startup method calls `Start`,
then a worker sends `CALL FORM(<launcher window>; "Demo_sideBySide")` and
`CALL FORM(<launcher window>; "Demo_switchLanguage"; "ja")`, logging the
window list after each step (`4dcli`, "Smoke-testing a running app without
UI automation"). Assert: one launcher, both demo windows at the same rects
after the switch, titles and menu titles in the new language. Keep the
harness in a scratch copy of the project.

## Checklist

- [ ] Launcher opens first; one button per demo form; side by side when forms are compared
- [ ] Every demo window title comes from one function; reuse finds windows by that title
- [ ] Language switch closes and reopens demo windows at the same rects, rebuilds the menu bar
- [ ] No `Common*` XLIFF IDs on the launcher, demo forms or menus
- [ ] One launcher after `On Startup` + `--startup-method`, and after a double shortcut
- [ ] `colorScheme` pinned; side-by-side checked at projector resolution
- [ ] Smoke test log checked; captures in each language (`4dcli`)
