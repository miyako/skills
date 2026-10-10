---
object: "list"
json_type: "list"
keywords: ["list", "hierarchical list", "ListRef", "New list", "APPEND TO LIST", "EDIT ITEM", "sublist", "choice list", "expand", "collapse", "itemRef"]
summary: "Hierarchical list form object — displays data as expandable/collapsible tree. Managed via ListRef (language object in memory). Supports unlimited nesting, single/multiple selection, enterable items, drag-and-drop, and choice list initialization. Dual identity: language object (ListRef) vs. form object (object name)."
---

# Hierarchical List

Reference: https://developer.4d.com/docs/FormObjects/listOverview

## Purpose

A hierarchical list displays data as a tree with one or more levels that can be
expanded or collapsed. Each item can have child items (sublists) to an unlimited
depth. The expand/collapse icon appears automatically to the left of items that
have children.

Hierarchical lists are used for:
- Tree navigation (file systems, categories, org charts)
- Multi-level selection (pick from a structured taxonomy)
- Outline views (table of contents, configuration panels)
- Choice list display (design-time lists rendered at runtime)

## Dual Identity: Language Object vs. Form Object

This is a key concept unique to hierarchical lists.

### Language Object (ListRef)

A hierarchical list exists **in memory** as a language object, identified by a
unique `ListRef` (Integer). This reference is returned by:

| Command | Purpose |
|---------|---------|
| `New list` | Create a new, empty list in memory |
| `Copy list` | Duplicate an existing list |
| `Load list` | Load a choice list defined in the Design-mode List editor |
| `BLOB to list` | Recreate a list from a BLOB |

**Important**: lists are held in memory. When finished, you **must** dispose of
them with `CLEAR LIST` to free memory. Forgetting this causes memory leaks.

There is only **one instance** of the language object in memory. Any modification
is immediately reflected in all places where it is used.

### Form Object (Object Name)

The same list can have **multiple representations** as form objects in the same
form or across different forms. Each representation has its own:
- Selection state
- Expanded/collapsed state
- Scroll position

Properties like font, color, and list contents are **shared** across all
representations — modifying them via any representation affects all.

### Connecting the Two

You connect them by assigning the `ListRef` to the variable associated with the
form object:

```4d
// mylist is the variable associated with the form object
mylist:=New list
```

### Targeting in Commands

- Use `ListRef` (Integer) when you want to address the **language object** in memory
- Use `(*; "objectName")` when you want to address a specific **form representation**

Commands based on expanded/collapsed state or current item must specify which
representation to use — different form objects showing the same list can have
different selections and expand states.

## Basic Definition (JSON Schema)

```json
{
  "myHierList": {
    "type": "list",
    "left": 20,
    "top": 20,
    "width": 250,
    "height": 300,
    "dataSource": "Form.listRef",
    "dataSourceTypeHint": "integer",
    "focusable": true,
    "enterable": false,
    "selectionMode": "single",
    "scrollbarVertical": "automatic",
    "borderStyle": "system",
    "events": ["onLoad", "onUnload", "onClick", "onDoubleClick",
               "onExpand", "onCollapse", "onSelectionChange"]
  }
}
```

The `dataSource` holds a variable/expression that receives/provides the `ListRef`.
`dataSourceTypeHint: "integer"` reflects that `ListRef` is an Integer.

## Supported Properties (per JSON Schema)

### Direct Properties

| JSON Key | Type / Enum | Notes |
|----------|-------------|-------|
| `type` | `"list"` | Required |
| `dataSource` | string | Variable/expression for the ListRef |
| `dataSourceTypeHint` | `"integer"` | Type hint for the data source |
| `method` | string | Object method path |
| `tooltip` | string | Help tip text |
| `focusable` | boolean | Whether the list can receive focus |
| `hideFocusRing` | boolean | Hide focus rectangle |
| `enterable` | boolean | Whether items can be edited in-place |
| `selectionMode` | `"single"`, `"multiple"` | Selection behavior |
| `entryFilter` | string | Filter for in-place editing |
| `list` | object | Choice list reference (design-time list) |
| `scrollbarHorizontal` | `"visible"`, `"hidden"`, `"automatic"` | Horizontal scrollbar |
| `scrollbarVertical` | `"visible"`, `"hidden"`, `"automatic"` | Vertical scrollbar |
| `dragging` | `"none"`, `"custom"` | Drag source behavior |
| `dropping` | `"none"`, `"custom"` | Drop target behavior |

### From Shared Types

Inherits from: `objectCommon` (position, size, sizing, visibility, class),
`events`, `borderStyle`, `drawingSpec` (fill, stroke), `fontSpec` (fontFamily,
fontSize, fontStyle, fontWeight, textDecoration).

## Data Source Initialization: Three Approaches

There are three ways to associate list content with a hierarchical list form object:

### Approach 1: Static `list` Property (Design-Time)

Set the `"list"` property directly in the form JSON. 4D manages the list lifecycle
automatically — no code needed, no cleanup required.

```json
{
  "type": "list",
  "list": {
    "items": ["Fruits", "Vegetables", "Grains", "Dairy"]
  }
}
```

The `list` value follows the `tree` schema: an object with optional `lineHeight`,
`editable`, and `items` array. Items can be strings, numbers, or objects with
`text`, `ref`, `subTree`, etc.

**Limitations**: flat or simple hierarchies only. No runtime customization (icons,
fonts, parameters). Good for fixed lists whose content is known at design time.

### Approach 2: `OBJECT SET LIST BY NAME` (Runtime, Named Reference)

Load a list from `lists.json` (defined in the Design List Editor) by name at runtime.
4D manages the list lifecycle — no manual cleanup needed.

```4d
// In On Load
OBJECT SET LIST BY NAME(*; "MyListObject"; "FoodTaxonomy")
```

The named list must exist in `lists.json`. The full hierarchy (sublists, styles,
icons specified with `path:`) is loaded. Each form object gets its own copy
in memory.

**Use when**: you want the rich structure of a saved list (hierarchy, per-item
styles) but need to decide which list to show at runtime.

### Approach 3: `OBJECT SET LIST BY REFERENCE` (Runtime, Programmatic)

Build a ListRef in memory and assign it to the form object. You own the lifecycle
and **must** clear it manually.

```4d
// In On Load
var $list : Integer
$list:=New list
APPEND TO LIST($list; "Mercury"; 1)
APPEND TO LIST($list; "Venus"; 2)
APPEND TO LIST($list; "Earth"; 3)

// Add sublists for hierarchy
var $sublist : Integer
$sublist:=New list
APPEND TO LIST($sublist; "Jupiter"; 5)
APPEND TO LIST($sublist; "Saturn"; 6)
APPEND TO LIST($list; "Outer Planets"; 9; $sublist; True)

OBJECT SET LIST BY REFERENCE(*; "MyListObject"; $list)
Form.listRef:=$list  // keep for cleanup
```

**Memory management**: always `CLEAR LIST` when done (typically in `On Unload`):

```4d
// In On Unload
If (Is a list(Form.listRef))
  CLEAR LIST(Form.listRef; *)  // * clears sublists too
End if
```

**Use when**: maximum flexibility — dynamic content, runtime icons via
`SET LIST ITEM ICON`, per-item fonts, custom parameters, user-editable lists.

### Comparison

| Aspect | Static `list` | By Name | By Reference |
|--------|---------------|---------|--------------|
| Where defined | form.4DForm JSON | lists.json | Code (New list) |
| Hierarchy support | Yes (subTree) | Yes (full) | Yes (full) |
| Runtime styling | No | Limited (what's in lists.json) | Full (all commands) |
| Lifecycle | Automatic | Automatic | Manual (CLEAR LIST) |
| Compiled mode | Always works | Always works (read-only) | Always works |
| Dynamic content | No | Switch between named lists | Fully dynamic |

## Item Reference Numbers (itemRef)

Each item has an `itemRef` (Integer) passed when creating items. This is a
user-defined identifier — 4D simply maintains it. Rules:

- **0 is reserved**: means "last item added" in most commands. Never use 0 as
  a real reference.
- **Uniqueness is optional** but recommended for direct access to any item.

### Strategies for itemRef

| Level | Strategy | When to use |
|-------|----------|-------------|
| Beginner | Pass any non-zero value | Only need selected item (position-based access) |
| Intermediate | Use record numbers | Map items to database records |
| Advanced | Maintain a global counter (never decrement) | Need unique identification of every item |

### Position vs. Reference Access

- **By position**: relative to visible/expanded items on screen. Position changes
  when items are expanded/collapsed. Each form representation has its own positions.
- **By reference**: uses `itemRef`, independent of display state. Consistent across
  representations.

## Supported Events

| Event | When |
|-------|------|
| `onLoad` | Form loads |
| `onUnload` | Form unloads — **clean up lists here** |
| `onClick` | Item clicked |
| `onDoubleClick` | Item double-clicked |
| `onExpand` | Item expanded (disclosure triangle) |
| `onCollapse` | Item collapsed |
| `onSelectionChange` | Selected item changes |
| `onAfterEdit` | During in-place editing: keystroke, copy, cut, paste (**not** delete/backspace — possible bug). Use `Get edited text` to read current text |
| `onDataChange` | After in-place editing ends (focus leaves the item). `$itemText` has the final value |
| `onDeleteAction` | Delete key pressed **when item is NOT in edit mode** (i.e. item selected but not being edited) |
| `onGettingFocus` / `onLosingFocus` | Focus enters/leaves the list |
| `onBeginDragOver` / `onDragOver` / `onDrop` | Drag-and-drop events |
| `onMouseEnter` / `onMouseLeave` / `onMouseMove` | Mouse tracking |
| `onHeader` / `onPrintingDetail` / `onPrintingBreak` / `onPrintingFooter` | Printing events |
| `onValidate` | Form validation |

### Event Ordering (Empirical Findings)

Events are fired in sequence for a single user action. The order varies:

| User Action | Event Sequence (first → last) |
|-------------|-------------------------------|
| Click on collapsed node | `On Clicked` → `On Selection Change` → `On Expand` |
| Click arrow to collapse | `On Collapse` → `On Clicked` |
| Click on already-selected item | `On Clicked` only |
| Click on unselected item | `On Clicked` → `On Selection Change` |
| Double-click unselected item | `On Selection Change` → `On Clicked` → `On Double Clicked` |
| Double-click selected item | `On Clicked` → `On Double Clicked` |
| Cmd+click to deselect | `On Selection Change` → `On Clicked` (ref=0, no selection) |
| Click on empty area | `On Clicked` only (ref=0) |
| Arrow key navigation | `On Clicked` → `On Selection Change` |

**Key observations**:
- `On Clicked` is **not** consistently first or last — its position varies by action
- `On Selection Change` largely covers click events; use `On Clicked` for:
  - Detecting clicks on empty areas (ref=0)
  - Cmd+click deselection (ref=0)
  - Re-clicks on already-selected items (no Selection Change fires)
- `On Double Clicked` is always preceded by `On Clicked`
- Expand/collapse via disclosure triangle includes `On Clicked`; via arrow key only fires `On Collapse`/`On Expand`

### Type-Ahead Selection (Built-In)

When a hierarchical list has focus, typing characters performs incremental search
on **visible** items (only expanded items are searchable):

- **Collapsed**: typing "F" selects "Fruits", "D" selects "Dairy"
- **Expanded**: typing "C" selects "Cherry", typing "CHEE" selects "Cheese"

The search matches from the beginning of item text and accumulates characters
(with a brief timeout between keystrokes). Only currently visible items
(not hidden inside collapsed nodes) participate.

**Note**: The front-end processor (IME) is disabled while the list has focus —
type-ahead works with direct key input only. This means Japanese/Chinese input
methods will not activate while the list is focused.

## Key Commands

Reference: https://developer.4d.com/docs/commands/theme/Hierarchical-Lists

### Creating and Destroying

| Command | Purpose |
|---------|---------|
| `New list` | Create empty list; returns `ListRef` |
| `Copy list` | Duplicate a list |
| `Load list` | Load a design-time choice list |
| `CLEAR LIST` | Free memory. Pass `*` to also clear sublists |
| `Is a list` | Returns `True` if the value is a valid `ListRef`. Use before `CLEAR LIST` (ref: https://developer.4d.com/docs/commands/is-a-list) |
| `SAVE LIST` | Save list back to List editor |
| `BLOB to list` / `LIST TO BLOB` | Serialize/deserialize to BLOB |

### List-Level Properties

| Command | Purpose |
|---------|---------|
| `SET LIST PROPERTIES` | Set list-level properties (ref: https://developer.4d.com/docs/commands/set-list-properties) |
| `GET LIST PROPERTIES` | Read list-level properties back |

`SET LIST PROPERTIES(list; appearance; icon {; lineHeight {; doubleClick {; multiSelections {; editable}}}})`

- `appearance` and `icon`: **deprecated**, always pass `0`
- `lineHeight`: minimum row height in pixels (0 = default from font)
- `doubleClick`: `0` = expand/collapse on double-click (default), `1` = disable
  (users can still click the disclosure triangle)
- `multiSelections`: `0` = single selection (default), `1` = enable multi-select
  (Shift+click for continuous, Ctrl/Cmd+click for discontinuous)
- `editable`: `1` = list is editable as a choice list (default — shows "Modify"
  button), `0` = not editable as a choice list

**Note**: `editable` here is a **list-level** property that controls whether the
list shows a "Modify" button when used as a choice list in data entry. This is
distinct from the per-item `enterable` in `SET LIST ITEM PROPERTIES` which
controls in-place text editing.

**Persistence**: only `lineHeight` and `editable` are saved to `lists.json`
(at the list level, outside `items`). `doubleClick` and `multiSelections` are
**runtime-only** — set them after `Load list`.

### Adding and Removing Items

| Command | Purpose |
|---------|---------|
| `APPEND TO LIST` | Add item at end. Optional sublist + expanded params |
| `INSERT IN LIST` | Insert item **before** a given itemRef (not position!) |
| `DELETE FROM LIST` | Remove item by position or reference |

`APPEND TO LIST` signature:
```
APPEND TO LIST(list; itemText; itemRef {; sublist; expanded})
```

`INSERT IN LIST` signature:
```
INSERT IN LIST(list; beforeItemRef; itemText; itemRef {; sublist; expanded})
```
**Important**: the second parameter is an **item reference number**, not a position.
The new item is inserted before the item with that reference.

`DELETE FROM LIST` signature:
```
DELETE FROM LIST(list; itemRef {; *})
```
- Without trailing `*`: sublists are **detached but kept in memory** (save the
  sublist reference beforehand to re-use it)
- With trailing `*`: sublists are **deleted from memory** permanently

### Getting and Setting Items

| Command | Purpose |
|---------|---------|
| `GET LIST ITEM` | Get ref, text, sublist, expanded state of an item |
| `SET LIST ITEM` | Change text, ref, sublist, expanded state |
| `GET LIST ITEM PROPERTIES` | Get enterable, style, icon, color |
| `SET LIST ITEM PROPERTIES` | Set enterable, style, icon, color |
| `SET LIST ITEM FONT` | Set font for a specific item |

`GET LIST ITEM` signature — **note ref comes before text**:
```
GET LIST ITEM(list; itemPos; var itemRef; var itemText {; var sublist; var expanded})
```
| `SET LIST ITEM ICON` | Set icon for a specific item |
| `Count list items` | Count items (optionally only visible/expanded) |
| `List item position` | Get position of item by reference |
| `List item parent` | Get parent reference of an item |

### Item Parameters

| Command | Purpose |
|---------|---------|
| `SET LIST ITEM PARAMETER` | Set a named parameter on an item (ref: https://developer.4d.com/docs/commands/set-list-item-parameter) |
| `GET LIST ITEM PARAMETER` | Read a named parameter back |
| `GET LIST ITEM PARAMETER ARRAYS` | Get all parameter names and values for an item |

**Built-in selectors** (constants in `Hierarchical Lists` theme):

| Constant | Selector string | Value type | Purpose |
|----------|----------------|------------|---------|
| `Additional text` | `"4D_additional_text"` | Text | Displays secondary text right-aligned in the list row |
| `Associated standard action` | `"4D_standard_action_name"` | Text | Associates a standard action (e.g. `"fontSize?value=12pt"`) |

**Custom selectors**: pass any text string as selector with a Text, Number, or
Boolean value. Retrieved via `GET LIST ITEM PARAMETER`. Useful for attaching
metadata (record IDs, categories, flags) to items without subclassing.

## lists.json Structure and Persistence

`SAVE LIST` writes to `Project/Sources/lists.json`. Each named list is a top-level
key containing an `items` array. Each item can have:

### Compiled Mode and Read-Only Structures

**Important**: when a 4D project is compiled, the entire `Project/Sources/` folder
(including `lists.json`) is packaged inside a `.4DZ` file as **read-only**. This
means `SAVE LIST` **cannot be used in compiled mode**.

**Rule of thumb**:
- Use `lists.json` (and the List editor) for **static or default lists** — lists
  whose structure is known at design time and does not change at runtime
- Use `New list` + `APPEND TO LIST` (programmatic) for **mutable lists** — lists
  built from data, user input, or any source that changes at runtime
- `Load list` creates a **copy in memory** — you can modify the copy freely at
  runtime, but you cannot save it back in compiled mode

### List-level properties stored in lists.json

These appear at the top level of each named list, outside the `items` array:

| JSON Key | Source | Persisted? | Notes |
|----------|--------|------------|-------|
| `lineHeight` | `SET LIST PROPERTIES` lineHeight param | ✅ Yes | Minimum row height in pixels; omitted when 0 (default) |
| `editable` | `SET LIST PROPERTIES` editable param | ✅ Yes | `false` = list not editable as choice list; omitted when `true` (default) |
| `doubleClick` | `SET LIST PROPERTIES` doubleClick param | ❌ No | Runtime-only — set after `Load list` |
| `multiSelections` | `SET LIST PROPERTIES` multiSelections param | ❌ No | Runtime-only — set after `Load list` |

### Properties stored per item

| JSON Key | Source | Type | Notes |
|----------|--------|------|-------|
| `text` | item text | string | Display text |
| `ref` | itemRef | integer | Reference number |
| `editable` | `SET LIST ITEM PROPERTIES` enterable param | boolean | Per-item editability |
| `collapsed` | expand/collapse state | boolean | `true` = collapsed |
| `fontWeight` | styles bitmask bit 0 (Bold=1) | `"bold"` | Only present when bold |
| `fontStyle` | styles bitmask bit 1 (Italic=2) | `"italic"` | Only present when italic |
| `textDecoration` | styles bitmask bit 2 (Underline=4) | `"underline"` | Only present when underline |
| `stroke` | color param (0x00RRGGBB) | `"#RRGGBB"` | CSS hex string — note the format conversion from integer! |
| `action` | `SET LIST ITEM PARAMETER` with `Associated standard action` | string | Standard action name |
| `subTree` | attached sublist | object with `items` | Nested hierarchy |

### What is NOT persisted to lists.json

**Important**: most `SET LIST ITEM PARAMETER` values are **runtime-only** (in memory).
They are **not saved** by `SAVE LIST`:

- `"4D_additional_text"` — ❌ not saved
- Custom parameters (any user-defined selector) — ❌ not saved
- `SET LIST ITEM FONT` — ❌ not saved (the font set via this command is not persisted)
- `SET LIST ITEM ICON` (Picture-based icons) — ❌ not saved (only `path:`-based icons
  via `SET LIST ITEM PROPERTIES` are saved as the `"icon"` key)

### Icon persistence: two approaches

| Method | `icon` param | Persisted to lists.json? |
|--------|-------------|--------------------------|
| `SET LIST ITEM PROPERTIES($l; ref; True; 0; "path:/RESOURCES/icon.svg")` | File path string | ✅ Yes → `"icon": "/RESOURCES/icon.svg"` (prefix stripped) |
| `SET LIST ITEM ICON($l; ref; $pictureVariable)` | In-memory Picture | ❌ No |

Use `path:` references for design-time icons; use `SET LIST ITEM ICON` for
runtime-generated icons (SVG, loaded images, etc.).

Only `"4D_standard_action_name"` persists as the `"action"` key.

This means: if you need additional text, custom parameters, or per-item fonts/icons,
you must set them **programmatically after `Load list`** — they cannot be defined
in the List editor or `lists.json` alone.

### Style integer → JSON decomposition

The `styles` parameter in `SET LIST ITEM PROPERTIES` is an integer bitmask:

| Value | Constant | JSON keys added |
|-------|----------|-----------------|
| 0 | Plain | (none) |
| 1 | Bold | `"fontWeight": "bold"` |
| 2 | Italic | `"fontStyle": "italic"` |
| 4 | Underline | `"textDecoration": "underline"` |
| 3 | Bold+Italic | both `fontWeight` + `fontStyle` |
| 5 | Bold+Underline | both `fontWeight` + `textDecoration` |
| 7 | All three | all three keys |

### Color integer → CSS hex conversion

The color param (integer `0x00RRGGBB`) is stored as CSS hex `"#RRGGBB"` in the
`stroke` key. This is the **opposite** of `ST SET ATTRIBUTES` which does NOT
accept CSS strings — in `lists.json`, 4D converts for you.

### Selection

| Command | Purpose |
|---------|---------|
| `Selected list items` | Get selected item(s) — returns position of first selected |
| `SELECT LIST ITEMS BY POSITION` | Select by position |
| `SELECT LIST ITEMS BY REFERENCE` | Select by reference |

`Selected list items` signature:
```
Selected list items({*;} list {; itemsArray {; *}}) → Integer
```
- Returns position of the **first** selected item (0 if none)
- With `itemsArray`: fills array with all selected positions
- With trailing `*`: fills array with **item references** instead of positions
- Use the `{*; objectName}` form to read selection from the form object representation

### Drag-and-Drop Reordering

Hierarchical lists support drag-and-drop for item reordering. The key events:

| Event | Role |
|-------|------|
| `On Begin Drag Over` | Serialize dragged item to pasteboard |
| `On Drag Over` | Accept/reject drop (`$0:=0` accept, `$0:=-1` reject) |
| `On Drop` | Perform the move |

**Drop position**: `Drop position` returns the position of the item the drop
lands on, or -1 if dropped below the last item.

**Implementation pattern for item move:**

```4d
// On Begin Drag Over: serialize source item
$context:=New object("itemRef"; $itemRef; "itemText"; $itemText)
VARIABLE TO BLOB($context; $data)
APPEND DATA TO PASTEBOARD("private.myapp.list.item"; $data)

// On Drop: move the item
$dropPos:=Drop position
// 1. Get source sublist BEFORE delete (preserve children)
GET LIST ITEM($listRef; $srcPos; $tmpRef; $tmpText; $subList; $expanded)
// 2. Get target item's ref BEFORE delete (INSERT IN LIST uses ref, not position)
GET LIST ITEM($listRef; $dropPos; $targetRef; $targetText)
// 3. Delete without trailing * (keeps sublist in memory)
DELETE FROM LIST($listRef; $srcItemRef)
// 4. Insert before target (or APPEND if dropped after last)
INSERT IN LIST($listRef; $targetRef; $srcText; $srcItemRef)
// 5. Re-attach sublist
If (Is a list($subList))
  SET LIST ITEM($listRef; $srcItemRef; $srcText; $srcItemRef; $subList; $expanded)
End if
```

**Direction matters**: when moving DOWN, the source is above the target. After
deleting the source, the target shifts up. To place the item at the target's
original position, insert before the item at `dropPosition+1` (or APPEND if
it was the last item).

### In-Place Editing

When `enterable: true`, items can be edited via Alt+click (Windows) /
Option+click (macOS), or a long click on the item text.

The `EDIT ITEM` command (ref: https://developer.4d.com/docs/commands/edit-item)
programmatically puts an item into edit mode:

```4d
// After inserting a new item, make it immediately editable
vlUniqueRef:=vlUniqueRef+1
INSERT IN LIST(hList; *; "New_item"; vlUniqueRef)
EDIT ITEM(*; "MyList")  // edits the current (last inserted) item
```

`EDIT ITEM` also works with list box columns and subforms. If the list is not
enterable, it only selects the item without entering edit mode.

For items created in the List editor, the **Modifiable Element** option
(in the Lists editor properties) controls whether individual items can be edited
(ref, legacy URL: https://doc.4d.com/4Dv20/4D/20.2/Setting-list-properties.300-6750359.en.html).

## Property Priority

When the same property is set in multiple ways, this priority applies:

1. **Hierarchical Lists commands** (highest) — e.g. `SET LIST ITEM PROPERTIES`
2. **Generic object property commands** — e.g. `OBJECT SET COLOR`
3. **Form property** (lowest) — JSON definition

Once an item property is set by a hierarchical list command, the equivalent
generic object command has no effect on that item.

## Modifiable Elements

You can control whether items are editable:

- **Object-level**: the `enterable` property (JSON or `OBJECT SET ENTERABLE`)
  controls the whole list
- **Item-level** (for choice-list-based lists): the "Modifiable Element" flag
  in the List editor controls individual items

Editing is triggered by:
- **Alt+click** (Windows) / **Option+click** (macOS)
- **Long click** on the item text
- `EDIT ITEM` command

## Generic Commands for Hierarchical Lists

These generic object commands also work with hierarchical list form objects:

| Command | Notes |
|---------|-------|
| `OBJECT SET FONT` | Affects all representations |
| `OBJECT SET FONT STYLE` | Affects all representations |
| `OBJECT SET FONT SIZE` | Affects all representations |
| `OBJECT SET COLOR` | Affects all representations |
| `OBJECT SET RGB COLORS` | Affects all representations |
| `OBJECT SET SCROLL POSITION` | Affects **only** the specified representation |
| `OBJECT SET ENTERABLE` | Affects all representations |
| `OBJECT SET VISIBLE` | Affects the specified representation |

**Note**: except `OBJECT SET SCROLL POSITION`, these commands modify **all**
representations of the same list, even when targeting by object name.

## CLI Verification Notes

Hierarchical lists require runtime initialization (programmatic `ListRef`
assignment). Static screenshots (`FORM SCREENSHOT` alone) will show an empty
list object. Use the `dialog_screenshot` pattern (Pattern 4 in the `4dcli` skill, `skills/4dcli/SKILL.md`)
with `On Load` initialization to capture a populated list.

Since hierarchical lists are interactive (expand/collapse), capturing different
states may require chained `CALL FORM` calls to programmatically expand items
and then screenshot.
