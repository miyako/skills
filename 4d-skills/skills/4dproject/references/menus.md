# menus.json: Standard Actions vs Method Wrappers

Reference: https://developer.4d.com/docs/Menus/properties
Also: https://developer.4d.com/docs/Menus/bars

A common legacy pattern creates a project method (e.g. `m_Quit`) that wraps a
single built-in command (e.g. `QUIT 4D`) and assigns it to a menu item with
the `"method"` property. Replace it with a standard `"action"`.

## Why the wrapper is wrong

1. **Unnecessary indirection.** A one-line wrapper method serves no purpose.
2. **Bypasses platform integration.** Standard actions integrate with native
   behaviour. On macOS the Quit item is moved to the application menu per the
   Human Interface Guidelines; a method-based item loses this.
3. **No automatic enable/disable.** 4D enables/disables standard actions by
   context. A method-based item is always enabled.
4. **Pollutes the method namespace** and the Run > Method... dialog.

## The fix

1. Replace `"method"` with `"action"` on the menu item, using the matching
   standard action string.
2. Delete the wrapper `.4dm` file.
3. Remove every remaining reference to the deleted method, including its
   entry in `Project/Sources/folders.json` (grep the whole project for the
   name).
4. Preserve all other properties (`"title"`, `"shortcutAccel"`,
   `"shortcutKey"`, ...).

Before:

```json
{ "title": ":xliff:CommonMenuItemQuit", "method": "m_Quit", "shortcutAccel": true, "shortcutKey": "Q" }
```

After (and `m_Quit.4dm` deleted):

```json
{ "title": ":xliff:CommonMenuItemQuit", "action": "quit", "shortcutAccel": true, "shortcutKey": "Q" }
```

## Common standard actions

| Standard action | Replaces a method wrapping | Notes |
|---|---|---|
| `quit` | `QUIT 4D` | Graceful quit with platform integration |
| `cut` / `copy` / `paste` | clipboard code | |
| `clear` | clear code | |
| `selectAll` | select-all code | |
| `undo` / `redo` | undo/redo code | |
| `showClipboard` | show-clipboard code | |
| `design` | return to Design mode | |

Full list: https://developer.4d.com/docs/Desktop/standard-actions

## `"action"` vs `"method"`

| Use case | Approach |
|---|---|
| Item performs a single built-in operation | `"action"`; delete the wrapper method |
| Item performs project-specific logic | `"method"` |
| Item needs standard enable/disable **and** custom code | both `"action"` and `"method"` |

When both are set, 4D never executes the action; it uses it to enable or
disable the item and to place it per platform. When the item is disabled,
the method cannot run.

> **Do not invent `action` values.** A method-only item exports from 4D as
> `{"title": "...", "method": "..."}` with no `action` key at all. Strings such
> as `"action": "action-none"` are not standard actions, and an unrecognized
> action can make 4D drop the item or disable the menu. If you need only custom
> code, omit `action` entirely.

Menu titles should use `:xliff:` references; reuse 4D's built-in `Common*`
IDs for standard items (see the `4dlocalise` skill).

## Audit procedure

1. Scan `menus.json` for items with a `"method"` property.
2. Read each referenced `Project/Sources/Methods/{name}.4dm`.
3. Body is a single command matching a standard action → replace with
   `"action"`, delete the `.4dm`, remove the name from `folders.json` and any
   other reference.
4. Body has custom logic → keep `"method"`; optionally add `"action"` for
   enable/disable management.

## 4D crashes at open inside `VMenu::Rebuild`

A crash while a project opens, before any project code runs, can come from
AppKit rather than from `menus.json`. The signature in the `.ips` report:

* `lastExceptionBacktrace`: `-[NSMenu removeAllItems]` <-
  `xbox::XMacTextMenu::Clear()` <- `xbox::VMenuItem::~VMenuItem()`
  (AppKit's own `_menuDidRemoveAllItems` handler throws an Objective-C
  exception).
* crashed thread: `std::terminate` <- `xbox::VMenuItem::~VMenuItem()` <-
  `xbox::VMenu::Rebuild()` <- `V4DApplication::ResetMenuBar` <-
  `V4DDatabase_application_impl::_Init_Menus` <- `_Open`. The exception
  escapes a C++ destructor, so the process terminates.

Seen three times on macOS 27.2.1 (4D 21.2 build 100691 twice, 21 R5 build
100175 once). A scratch copy of the same project, with a `menus.json` that
was the default bar plus a method menu, opened on 100691 without crashing, so
the trigger is not established. Do not rewrite `menus.json` or drop the
method items to chase it. Grep the report for `_menuDidRemoveAllItems`, record
the macOS and 4D build, and reduce `menus.json` in a scratch copy only if the
crash reproduces there.

## Checklist

- [ ] Every `"method"` item in `menus.json` audited
- [ ] Single-command wrappers replaced with `"action"`
- [ ] Wrapper `.4dm` files deleted
- [ ] Deleted method names appear nowhere in the project, including `folders.json`
- [ ] Remaining `"method"` references point to methods with real logic
- [ ] All other item properties (title, shortcuts) preserved
- [ ] Menu methods that remain stay **visible** (see the `4dmethods` skill)
