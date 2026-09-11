---
object: "dropdown"
json_type: "dropdown"
keywords: ["dropdown", "dropdown list", "dataSourceTypeHint", "choiceList", "saveAs", "hierarchical list", "gotoPage", "standard action", "object-based", "array-based"]
summary: "Dropdown list object: five data-source kinds (object/array/choice-list/hierarchical/standard-action), binding rules, screenshot rendering caveats."
---

# 4D Dropdown List Object

Reference: https://developer.4d.com/docs/FormObjects/dropdownListOverview
Also: https://developer.4d.com/docs/FormObjects/propertiesDataSource (JSON grammar for data source properties)
Also: https://developer.4d.com/docs/Desktop/standard-actions (standard action syntax, `gotoPage`)

## Basic Definition

```json
{
  "myDrop": {
    "type": "dropdown",
    "top": 20,
    "left": 20,
    "width": 180,
    "height": 20,
    "dataSource": "Form.myDrop",
    "dataSourceTypeHint": "object"
  }
}
```

A drop-down list is a closed list of items presented as a single-line control; clicking it opens a list/menu of choices. On macOS it is rendered as a native pop-up menu (same object, platform-specific chrome only); the OS may render the control at a different height than the object's declared `height` depending on platform conventions. Available only in 4D **projects**, not in 4D classic databases (for the object/array-based variants below; choice-list variants work in both).

## Interaction Model

A drop-down list is an active object like button, checkbox, and radio button:

- `On Clicked` fires **on mouse-down** (press), not on mouse-up (release) -- same timing as buttons, checkboxes, and radio buttons.
- It supports `focusable` like a button. When focused: `Return`/`Tab` moves to the next object in tab order, `Shift+Return`/`Shift+Tab` moves to the previous object in tab order, and `Space` is equivalent to clicking it (opens the list).

Like progress indicators and rulers, a drop-down list's data source can be a live expression, and the binding is **bidirectional**: the object reads its displayed state from the expression, and user interaction writes the selection back into the expression -- there is no need to trap `On Clicked`/`On Data Change` just to copy the value back manually (though those events are still available for reacting to a change).

Across all data source shapes (object, array, or list), if the "no selection" placeholder is left unset the control simply renders blank until the user makes a selection; the "no selection" state can never be restored through the UI once a selection has been made -- only by resetting the data source back to its "no selection" state (`-1` index / `0` array-or-reference value / empty text) by code.

There are five distinct kinds of drop-down list, distinguished entirely by which JSON properties are present -- not by a separate `type` value. `"type"` is always `"dropdown"`. The underlying data source is always one of three shapes -- **object**, **array**, or **list** (choice list / hierarchical list) -- with **object being the modern, recommended shape** (see https://blog.4d.com/use-collections-and-lists-within-forms-objects/).

## The Five Kinds

| Kind | Trigger (JSON) | Data source shape |
|------|-----------------|--------------------|
| Object-based | `dataSourceTypeHint: "object"` | `Form.xxx` = `{ values, index, currentValue }` |
| Array-based | `dataSourceTypeHint: "arrayText"` / `"arrayNumber"` / `"arrayDate"` / `"arrayTime"` | `dataSource` names a 4D array variable directly (e.g. `"asColor"`) |
| Choice list (value) | `choiceList: [...]` + `saveAs: "value"` (default) | `dataSource` is a plain field/variable holding the literal selected value |
| Choice list (reference) | `choiceList: [...]` + `saveAs: "reference"` | `dataSource` is a plain field/variable holding a numeric item reference into the list |
| Hierarchical | `dataSourceTypeHint: "integer"` **alone** (no `choiceList`, `list`, object, or array) | `dataSource` is the hierarchical list reference itself; resolved via Hierarchical Lists language commands |

Only one kind can be active on a given object. Binding `dataSource` directly to a field/variable (rather than to an object or array) always forces choice-list behavior; it cannot be combined with `dataSourceTypeHint: "object"` or an array hint.

### Object-based

```json
"dropFruit": {
  "type": "dropdown",
  "dataSource": "Form.dropFruit",
  "dataSourceTypeHint": "object"
}
```

```4d
Form.dropFruit:=New object
Form.dropFruit.values:=New collection("Apple"; "Banana"; "Cherry")
Form.dropFruit.index:=1
Form.dropFruit.currentValue:="Banana"
```

- `values` (Collection, mandatory): all elements must be the same scalar type (text, number, date, or time). Collections are always **0-based**, so `index` is 0-based too (see https://developer.4d.com/docs/API/CollectionClass).
- `index` (Integer, 0-based): **bidirectional**. Assigning it selects the specified item (e.g. `Form.dropFruit.index:=2` programmatically selects the 3rd item); when the user selects an item, 4D assigns its position back into `index`. `-1` means "no selection" -- the control displays `currentValue` instead, acting as a placeholder.
- `currentValue`: **read-only** from the form's perspective. Assigning it directly is ignored -- the value reverts to whatever the actual selection is (or to the placeholder when `index` is `-1`). When the user selects an item, 4D assigns that item's value into `currentValue`. It only has a meaningful assignable role once, as the placeholder text, at initialization time (see below).

To initialize an object-based drop-down list, set `index` to `-1` and, optionally, `currentValue` to a placeholder message (e.g. `"Select a fruit"`) -- this is the only time `currentValue` should be assigned.

### Array-based

```json
"dropColor": {
  "type": "dropdown",
  "dataSource": "asColor",
  "dataSourceTypeHint": "arrayText"
}
```

```4d
ARRAY TEXT(asColor; 3)
asColor{1}:="item 1"
asColor{2}:="item 2"
asColor{3}:="item 3"
asColor{0}:="please select item"
asColor:=0
```

The `dataSource` string is the array's own name (not `Form.xxx`); the object name and the array name do not need to match, but the array must exist as a form-local array. Populate it (and clear it) in `On Load` / `On Unload`. The `arrayNumber`/`arrayDate`/`arrayTime` hints work the same way for arrays of other scalar types.

4D arrays are **1-based** (see https://developer.4d.com/docs/Concepts/arrays), unlike the 0-based `values` Collection used by the object-based kind:

- `asColor{1}`, `asColor{2}`, `asColor{3}` are the three selectable items.
- `asColor{0}` is reserved for the "no selection" placeholder message (e.g. `"please select item"`).
- The **current element number** is held by the array variable itself, not by a separate index property: `asColor:=1` selects element 1. The idiom `asColor{asColor}` therefore always yields the currently selected value.
- The array reference is **bidirectional**: assigning a number to the array variable selects that item; when the user selects an item, 4D assigns the selected element's number back into the array variable.

To initialize an array-based drop-down list, set the array variable to `0` and, optionally, populate element `0` with an initialization message.

### Choice list (value vs. reference)

```json
"dropSaveValue": {
  "type": "dropdown",
  "dataSource": "Form.dropSaveValue",
  "choiceList": ["Red", "Green", "Blue"],
  "saveAs": "value"
},
"dropSaveReference": {
  "type": "dropdown",
  "dataSource": "Form.dropSaveReference",
  "choiceList": ["Red", "Green", "Blue"],
  "saveAs": "reference"
}
```

`choiceList` can be either a static list/collection of items inlined directly in the object's JSON, or the name of a list defined in the project's toolbox (`lists.json` -- see https://developer.4d.com/docs/Project/architecture). A named toolbox list is automatically instantiated when the form is loaded and cleared when the form is unloaded -- no manual lifecycle code is needed for it, unlike array-based or hierarchical-by-code data sources. `OBJECT SET LIST BY NAME` (https://developer.4d.com/docs/commands/object-set-list-by-name) achieves the same effect at runtime as setting a toolbox list's name directly in `choiceList`.

`saveAs` (the "Data Type (list)" property) defines what is stored in the data source, and the on-screen behavior is identical either way -- only the code working with the data source is affected:

- `"value"` (default, "Selected item value"): the data source holds the literal selected item's text (e.g. `"Blue"`) directly -- no need to resolve which position/item-reference is selected.
- `"reference"` ("Selected item reference"): the data source holds a numeric item reference associated with the selected item (via `APPEND TO LIST`'s `itemRef` parameter, `SET LIST ITEM`, or the list editor -- not necessarily the item's 1-based position). The bound field/variable must be Number type. This decouples the displayed text (which a user sees, and which can be relabeled or localized) from the reference code actually keys off of.

The data source is **bidirectional**: assigning a value (or reference number) to it selects the corresponding item; when the user selects an item, its value (or reference number) is assigned back into the data source.

To initialize a choice list drop-down list: set the data source to `0` when using `saveAs: "reference"`, or to an initialization message (e.g. `"please select item"`) when using `saveAs: "value"`.

A choice list dropdown cannot be combined with an object or array data source -- entering a field/variable name directly in "Variable or Expression" always forces this mode.

### Hierarchical

Setting only `"dataSourceTypeHint": "integer"` (with `"type": "dropdown"` and no `choiceList`/object/array data source) declares a **hierarchical** drop-down list ("List reference" mode of the "Data Type (list)" property), limited to two levels in forms. In this mode the data source itself is the **hierarchical list reference** (an integer) -- resolving the actual selected item requires the Hierarchical Lists language commands (e.g. `Selected list items`, `Select list items by reference`, `Select list items by position`), unlike the `"value"`/`"reference"` choice-list modes above where the data source already holds a usable selected value or item reference.

A hierarchical list can be attached in two ways:

- **By name**: `OBJECT SET LIST BY NAME` (https://developer.4d.com/docs/commands/object-set-list-by-name) attaches a toolbox-defined list by name -- equivalent to setting that list's name directly in `choiceList`/`list`. 4D instantiates it when the form loads and clears it when the form unloads; no manual `Clear list` call is needed.
- **By reference**: build the list at runtime with `New list` (https://developer.4d.com/docs/commands/new-list) or `Load list` (https://developer.4d.com/docs/commands/load-list), each returning an integer list reference, and assign that reference directly to the object via `OBJECT SET LIST BY REFERENCE` (https://developer.4d.com/docs/commands/object-set-list-by-reference) or by assigning it to the data source expression. The dropdown retains its own reference count on the list, so the caller may call `Clear list` (https://developer.4d.com/docs/commands/clear-list) immediately after assigning it -- the list itself is only actually released once the dropdown's reference count reaches zero, which happens when the form is unloaded.

### Standard action (submenu-style)

```json
"dropGotoPage": {
  "type": "dropdown",
  "action": "gotoPage"
}
```

Reference: https://developer.4d.com/docs/Desktop/standard-actions

A standard action is a built-in behavior identified by name (`action` property, or the "Standard action" property list entry) that 4D executes without requiring a method. Some standard actions accept one parameter using URL-like syntax: `standardActionName{?nameParameter=valueParameter}`, e.g. `gotoPage?value=5`. This syntax is valid anywhere a standard action can be set: property list, Menu editor, or via language commands.

If an object (or menu command) has both a method and a standard action assigned, the method runs first, then the standard action runs after it -- the only exception is `deleteRecord`, which runs before any attached method. When a style-related standard action (`fontSize`, `backgroundColor`, `bold`, etc.) is triggered, 4D generates the `On After Edit` form event.

Drop-down lists (and hierarchical choice lists) can only be directly associated with standard actions that generate a submenu, such as `gotoPage`, `backgroundColor`, or `fontSize`. With `action: "gotoPage"` the list is auto-populated with the form's page numbers; selecting item *N* navigates to page *N*. No `dataSource` is required or used for this mode. Custom per-item actions (e.g. `backgroundColor?value="red"`) can replace the automatic values by setting them on a choice list via `SET LIST ITEM PARAMETER` and assigning that list as the object's choice list -- only standard actions that themselves take a value parameter related to the submenu's main action are valid for this substitution.

A dropdown is a natural UI for a standard action with a small, finite set of options -- e.g. a 3-page form exposed as a 3-item `gotoPage` dropdown page selector. However, **this binding is one directional**: selecting an item in the dropdown executes the action (e.g. navigates to the page), but the reverse is not automatic -- changing the underlying state by code (e.g. `FORM GOTO PAGE`, https://developer.4d.com/docs/commands/form-goto-page) does not update the dropdown's displayed selection. To keep a `gotoPage` dropdown in sync after a code-driven page change, read the new page back explicitly (`FORM Get current page`, https://developer.4d.com/docs/commands/form-get-current-page) and assign it to the dropdown's own data source/index, or invoke the standard action programmatically instead of changing state directly (`INVOKE ACTION`, https://developer.4d.com/docs/commands/invoke-action) so the dropdown's normal action path executes and its state stays consistent. `FORM Get properties` (https://developer.4d.com/docs/commands/form-get-properties) can be used to read a form's current object/page properties for this kind of synchronization logic.

This one-directional limitation becomes structurally hard to work around for standard actions with an **unbounded or open-ended** value set, such as `fontSize` on a styled text or 4D Write Pro area. A `fontSize` dropdown can only offer a fixed, finite list of choices (e.g. 8, 9, 10, 11), but the actual current font size of the user's selection is not constrained to that list -- if the selection's font size is some other value (e.g. 13, or a mixed selection with several sizes), none of the dropdown's items corresponds to the true current state, so the dropdown cannot reflect it and is simply left showing its last-clicked item or blank. This is a general caveat for any standard-action dropdown whose target property is open-ended (font size, in particular, for 4D Write Pro toolbars) rather than a small closed set (like page number): https://developer.4d.com/docs/WritePro/standard-actions, https://blog.4d.com/easily-design-your-own-4d-write-pro-toolbar-with-standard-actions/, https://blog.4d.com/4d-write-pro-adding-a-margin-automatically-when-bullets-are-set-using-standard-actions/, https://blog.4d.com/4d-write-pro-new-automated-actions-for-tables-rows-and-cells/

A `gotoPage` dropdown placed on **page 0** becomes a persistent navigation control, since page-0 objects are always visible regardless of which page is currently displayed (see `tab.md`'s page-0 navigation pattern, which applies identically here and to button grid/picture pop-up menu). A plain button cannot auto-populate a page list the way a dropdown does, but it can still jump to one specific fixed page via `"action": "gotoPage?value=N"` (see `button.md`) -- a useful companion on page 0 for one-off jumps (e.g. a permanent "Home" button) alongside a dropdown-driven page selector.

## `Data Type (list)` Properties

Reference: https://developer.4d.com/docs/FormObjects/propertiesDataSource#data-type-list

Three named options, all controlled by the same `saveAs` JSON property:

| Option | `saveAs` value | Data source holds |
|--------|-----------------|--------------------|
| List reference | *(omit `saveAs`; use `dataSourceTypeHint: "integer"` alone instead)* | The hierarchical list reference (integer) -- declares the drop-down hierarchical |
| Selected item value (default) | `"value"` | The literal selected item's value |
| Selected item reference | `"reference"` | A numeric item reference (via `APPEND TO LIST`'s `itemRef`, `SET LIST ITEM`, or the list editor); requires a Number-type field/variable |

| Property | JSON Name | Type | Notes |
|----------|-----------|------|-------|
| Choice list | `choiceList` | list / collection | Inline static list, or the name of a toolbox list (`lists.json`) -- auto-instantiated on load, auto-cleared on unload |
| Hierarchical list reference | `list` | list / collection | Also used when a hierarchical list is built by code (`New list`/`Load list`) and assigned by integer reference |
| Data source hint | `dataSourceTypeHint` | text | `"object"`, `"arrayText"`, `"arrayNumber"`, `"arrayDate"`, `"arrayTime"`, or `"integer"` (hierarchical trigger) |
| Save as | `saveAs` | text | `"value"` (default) or `"reference"` |

## Supported Properties Summary

Alpha Format, Bold, Bottom, Button Style, Choice List, Class, Data Type (expression type), Data Type (list), Date Format, Expression Type, Focusable, Font, Font Color, Font Size, Height, Help Tip, Horizontal Alignment, Horizontal Sizing, Italic, Left, Not rendered, Object Name, Right, Standard action, Save value, Time Format, Top, Type, Underline, Variable or Expression, Vertical Sizing, Visibility, Width.

`Button Style` (JSON `style`; https://developer.4d.com/docs/FormObjects/properties_TextAndPicture#button-style) is listed as officially supported for drop-down lists, and accepts the same enumeration as for buttons: `"regular"` (default), `"flat"`, `"toolbar"`, `"bevel"`, `"roundedBevel"`, `"gradientBevel"`, `"texturedBevel"`, `"office"`, `"help"`, `"circular"`, `"disclosure"`, `"roundedDisclosure"`, `"custom"`. In practice, setting any of these values on a drop-down list produces **no visible difference** -- every style renders as the same native pop-up-menu control (blue rounded rectangle with up/down chevrons on macOS). Unlike buttons, checkboxes, and radio buttons, where `style` dramatically changes appearance, a drop-down list's rendered chrome is controlled entirely by the platform/OS, not by this property.

## Supported Events

On After Edit, On After Keystroke, On Before Keystroke, On Begin Drag Over, On Clicked, On Data Change, On Drag Over, On Drop, On Header, On Load, On Mouse Enter, On Mouse Leave, On Mouse Move, On Printing Break, On Printing Detail, On Printing Footer, On Unload.

## CLI Verification Caveat

`FORM SCREENSHOT` called with a form name (`FORM SCREENSHOT(formName; formPict; pageNum)`) renders the **Form Editor's static template** for that page, not a live/running form. It never executes `On Load` and never reflects any `Form.xxx` value, array content, or field value assigned by form-object-method code. Concretely, for every kind of drop-down list -- object-based, array-based, choice list (value or reference), and hierarchical -- the CLI screenshot renders the **literal `dataSource` expression text** as the visible label (e.g. `Form.dropFruit`, `asColor`, `Form.dropSaveValue`, `Form.dropHierarchical`), never a resolved value, never the first `choiceList` item, and never blank. Only a drop-down list with **no `dataSource` at all** (the `gotoPage` standard-action form, which needs none) renders differently: it shows its own **object name in quotes** (e.g. `"dropGotoPage"`), the generic fallback 4D uses for an unbound object in the editor template.

There is no way to preview a drop-down list's actual populated/selected state -- for any of the five kinds -- without running the form interactively. See `../screenshot-rendering.md` for static template rendering rules, and `skills/4dcli/SKILL.md` for CLI version requirements.
