---
object: "combo"
json_type: "combo"
keywords: ["combo box", "enterable", "automaticInsertion", "excludedList", "requiredList", "choiceList"]
summary: "Combo box object: enterable drop-down variant, object/array/choice-list data sources, automaticInsertion/excludedList."
---

# 4D Combo Box Object

Reference: https://developer.4d.com/docs/FormObjects/comboBoxOverview
Also: https://developer.4d.com/docs/FormObjects/dropdownList_Overview (shared data source mechanics)
Also: https://developer.4d.com/docs/FormObjects/properties_DataSource, https://developer.4d.com/docs/FormObjects/properties_RangeOfValues
Also: https://blog.4d.com/use-collections-and-lists-within-forms-objects/ (object as the modern, recommended data source shape)

## Basic Definition

```json
{
  "myCombo": {
    "type": "combo",
    "top": 20,
    "left": 20,
    "width": 180,
    "height": 20,
    "dataSource": "Form.myCombo",
    "dataSourceTypeHint": "object"
  }
}
```

A combo box is a drop-down list that also accepts free-form keyboard text entry: it is fundamentally an **enterable input area** that happens to offer a pop-up list of default values (from an object, array, or choice list) as a convenience, not a closed/finite selection control like a drop-down list. `"type"` is `"combo"`.

## Combo vs. Dropdown

A combo box shares its three data source shapes (object, array, choice list) with the drop-down list, but differs in fundamental ways:

| Aspect | Drop-down list | Combo box |
|--------|----------------|-----------|
| Keyboard text entry | Not enterable -- closed list only | **Enterable** -- user can type any value, not just list items |
| Object data source | `values`, `index` (bidirectional), `currentValue` (read-only except init) | `values`, **`currentValue` only** -- no `index`; `currentValue` receives whatever the user types |
| Array data source | Array variable itself holds the current **element number** (1-based selection index) | Typed text is written into **element `0`** of the array -- the array variable is not used as a selection index |
| Hierarchical choice list | Supported (`dataSourceTypeHint: "integer"` alone) | **Not supported** -- only the first level of a hierarchical list is shown/selectable, and there is no dedicated hierarchical mode |
| `saveAs` / Data Type (list) (reference storage) | Supported -- data source can hold a numeric item reference instead of the literal value | **Not supported** -- `saveAs` is not in the combo box's supported properties list; a choice-list combo box always stores the literal typed/selected text |
| Standard action | Supported (`gotoPage`, submenu actions) | **Not supported** -- not listed as a combo box feature at all |
| `Required List` (`requiredList`) | N/A (drop-down is already a closed list) | Documented as **not available** for combo boxes in the Combo Box overview page, and interactively confirmed: setting `requiredList` on a combo box has **no effect** -- keyboard entry of arbitrary text remains fully possible and `On Validate` raises no error, even though the generic Range of Values property page's "Objects Supported" line for `requiredList` lists Combo Box. To force a finite, keyboard-entry-free list of required values, use a drop-down list instead. |
| `Focusable` | Explicit `focusable` property (like a button) | Not a listed property -- a combo box is an ordinary enterable field and is always part of the tab order the same way an input is |
| `On Clicked` | Fires on mouse-down, like a button | **Fires only for a popup selection** -- clicking the chevron opens the popup, and choosing an item from it fires `On Clicked` (a click-driven data change), the same way it does for a drop-down list. Clicking directly into the text-entry part of a combo does **not** fire `On Clicked` -- that's ordinary text editing, tracked with `On Data Change`/`On After Edit` like a normal input. Clicking the chevron and then clicking elsewhere to dismiss the popup **without** selecting anything does not fire `On Clicked` either (confirmed interactively) |
| Combo-specific options | -- | `automaticInsertion` (add typed-but-unlisted values to the in-memory list) and `excludedList` (reject specific values from being typed/selected), neither of which exists for drop-down lists |

## Object-based

```json
"comboFruit": {
  "type": "combo",
  "dataSource": "Form.comboFruit",
  "dataSourceTypeHint": "object"
}
```

```4d
Form.comboFruit:=New object
Form.comboFruit.values:=New collection("Apple"; "Banana"; "Cherry")
Form.comboFruit.currentValue:="Banana"
```

- `values` (Collection, mandatory): same rules as the drop-down list's object data source -- all elements must be the same scalar type; an empty/undefined collection means an empty combo box.
- `currentValue`: unlike the drop-down list, this is the **only** selection-tracking property (there is no `index`), and it is **writable** both ways -- it holds the initial/displayed text, and when the user types or selects a value, 4D assigns that text into `currentValue`. There is no equivalent of the drop-down's "-1 index means placeholder" convention; a combo box's `currentValue` is just its current text.

## Array-based

```json
"comboArr": {
  "type": "combo",
  "dataSource": "asFruit",
  "dataSourceTypeHint": "arrayText"
}
```

```4d
ARRAY TEXT(asFruit; 3)
asFruit{1}:="Apple"
asFruit{2}:="Banana"
asFruit{3}:="Cherry"
```

The array is populated the same way as for a drop-down list (see https://developer.4d.com/docs/FormObjects/dropdownList_Overview#using-an-array), and the same `arrayNumber`/`arrayDate`/`arrayTime` hints apply. The key behavioral difference: since a combo box has no notion of a "currently selected element number" (the user can type text that matches no element at all), **the array variable itself is not used as an index** -- instead, whatever the user types or picks is written into **element `0`** of the array (`asFruit{0}`), regardless of what `asFruit{0}` held before. Read the current combo box value from `asFruit{0}` rather than `asFruit{asFruit}`.

## Choice list

```json
"comboPlain": {
  "type": "combo",
  "dataSource": "Form.comboPlain",
  "choiceList": ["Red", "Green", "Blue"]
}
```

Works the same way as a drop-down list's choice-list mode (inline array/collection, or the name of a toolbox list from `lists.json`, auto-instantiated/cleared with the form). The data source is bound directly to a field/variable, and the on-screen behavior lets the user either pick from the pop-up list or type any text. Unlike the drop-down list, there is **no `saveAs`/"Data Type (list)" option** -- the data source always holds the literal text, never a numeric item reference; this property simply is not in the combo box's supported properties set.

### Automatic Insertion

```json
"comboAutoIns": {
  "type": "combo",
  "dataSource": "Form.comboAutoIns",
  "choiceList": ["Red", "Green", "Blue"],
  "automaticInsertion": true
}
```

Reference: https://developer.4d.com/docs/FormObjects/properties_DataSource#automatic-insertion

When `automaticInsertion` is `true` and the user types a value not already present in the associated list, that value is added to the **in-memory** list as soon as the entry is validated (e.g. pressing Return) -- interactively confirmed to append the new value at the **bottom** of the pop-up list, so it appears as a selectable choice from then on. When `false` (default), the typed value is stored in the data source but the list itself is left unchanged. This applies both to a choice-list combo box and to one whose list comes from an object/array data source. If the choice list originated from a Design-mode-defined toolbox list, the on-disk list definition is never modified by automatic insertion -- only the form's in-memory copy changes.

### Excluded List

```json
"comboExcluded": {
  "type": "combo",
  "dataSource": "Form.comboExcluded",
  "choiceList": ["Red", "Green", "Blue"],
  "excludedList": ["Green"]
}
```

Reference: https://developer.4d.com/docs/FormObjects/properties_RangeOfValues#excluded-list

`excludedList` names values that cannot be entered into the combo box -- if the user types an excluded value and validates the entry, 4D rejects it and displays an alert dialog reading **"That value is not allowed."** (interactively confirmed). If the excluded list is hierarchical, only its first-level items are considered. This property has no drop-down list equivalent (a drop-down list only ever offers items already in its own list, so there is nothing to "exclude").

## Supported Properties Summary

Alpha Format, Bold, Bottom, Choice List, Class, Draggable, Droppable, Date Format, Expression Type, Font, Font Color, Font Size, Height, Help Tip, Horizontal Sizing, Italic, Left, Object Name, Right, Time Format, Top, Type, Underline, Variable or Expression, Vertical Sizing, Visibility, Width.

Notably absent compared to the drop-down list's property set: **Focusable** (a combo box is an ordinary enterable field, always focusable), **Standard action** (not supported at all), **Data Type (list)**/`saveAs` (no reference-storage mode), **Horizontal Alignment**, **Not rendered**, and **Save value**. Combo box adds **Draggable**/**Droppable**, which the drop-down list does not support.

## Supported Events

On Getting focus, On Load, On Losing focus, On Mouse Enter, On Mouse Leave, On Mouse Move, On Printing Break, On Printing Detail, On Printing Footer, On Unload, On Validate.

Notably absent compared to the drop-down list's event set: **On After Edit**, **On After/Before Keystroke**, **On Begin Drag Over**, **On Data Change**, **On Drag Over**, **On Drop**, **On Header**. Use `On Data Change` (https://developer.4d.com/docs/Events/onDataChange) to react to entries as with any ordinary input area -- despite `On Data Change` being present in the descriptive text of the official Combo Box overview page, it is **not** listed in that same page's own "Supported Events" enumeration, an inconsistency in the source documentation worth noting; behavior should be confirmed interactively if this event is depended upon.

`On Clicked` is likewise absent from this official list, yet **confirmed interactively to actually fire** -- but only for a popup-driven selection (click the chevron, then choose an item from the popup), the same click-is-a-data-change semantics as a drop-down list's `On Clicked`. It does not fire for ordinary typing in the text-entry part of the combo (that's `On Data Change`/`On After Edit` territory, same as any input), nor does it fire if the popup is opened and then dismissed without a selection (clicking outside it to cancel). As with `On Data Change`, it does not matter whether the newly selected value equals the value that was already there -- a click-driven selection fires `On Clicked` regardless.

## CLI Verification Caveat

Like the drop-down list, `FORM SCREENSHOT` called with a form name (`FORM SCREENSHOT(formName; formPict; pageNum)`) renders the **Form Editor's static template** for a given page, not a live/running form -- it never executes `On Load` and never reflects any `Form.xxx`/array/field value assigned by form-object-method code. Every combo box kind (object-based, array-based, choice list, with or without `automaticInsertion`/`excludedList`) renders the **literal `dataSource` expression text** as its label in a CLI screenshot (e.g. `Form.comboFruit`, `asFruit`), never a resolved value.

Some combo-box-specific behaviors are inherently interactive and cannot be observed via `FORM SCREENSHOT` at all (see `../screenshot-rendering.md` for static template rules) -- they require actually running the form interactively. Interactively confirmed results for this form:

- Typing an excluded value (`excludedList`) and validating the entry triggers an alert dialog reading "That value is not allowed."; the value is not accepted.
- `automaticInsertion` adds a newly typed value to the in-memory list as soon as the entry is validated (Return), appending it at the bottom of the pop-up list.
- `requiredList` on a combo box has no effect: arbitrary text can still be typed and validates without error -- confirming the Combo Box overview page's "not available" statement over the generic Range of Values page's "Objects Supported" listing.
- The visual chrome differs from a drop-down list: a combo box renders as a plain bordered rectangle with a small trailing chevron (an enterable field with an attached pop-up), rather than the drop-down list's native OS pop-up-menu/pill chrome.
