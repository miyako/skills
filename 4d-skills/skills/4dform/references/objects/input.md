---
object: "input"
json_type: "input"
keywords: ["input", "field", "text", "multiline", "wordwrap", "entry filter", "placeholder", "picture format", "boolean format", "date format", "number format", "choice list", "enterable"]
summary: "Input object: general-purpose field/expression display and entry, all expression types (text/date/time/number/boolean/picture/object), format-per-type properties, entry filter, multiline/wordwrap, static template always shows literal dataSource text regardless of expression type."
---

# 4D Input Object

Reference: https://developer.4d.com/docs/FormObjects/inputOverview
Also: https://developer.4d.com/docs/FormObjects/properties_Entry (Enterable, Multiline, Placeholder, Entry Filter, Context Menu, Auto Spellcheck, Selection always visible, Writing Tools)
Also: https://developer.4d.com/docs/FormObjects/properties_Display (Alpha/Date/Number/Time/Picture/Boolean Format, Wordwrap, Visibility)
Also: https://developer.4d.com/docs/FormObjects/properties_Object.md#variable-or-expression, properties_Object.md#expression-type
Also: https://developer.4d.com/docs/FormObjects/properties_RangeOfValues (Default value, Choice List, Excluded List, Required List)
Also: https://developer.4d.com/docs/Concepts/quick-tour.md#assignable-vs-non-assignable-expressions

## Basic Definition

```json
{
  "myText": {
    "type": "input",
    "dataSource": "Form.myText",
    "dataSourceTypeHint": "text",
    "top": 20,
    "left": 20,
    "width": 220,
    "height": 20
  }
}
```

An input is the general-purpose object for displaying and entering a field or expression. Unlike drop-down/combo/tab, an input is not restricted to any one data shape -- its `dataSource` can be Text, Integer, Numeric, Date, Time, Picture, Boolean, or Object, and each type unlocks a different set of display-format properties (`dateFormat`, `numberFormat`, `pictureFormat`, `booleanFormat`, etc.). `dataSourceTypeHint` (Expression Type) declares which one, exactly as it does for drop-down/combo/tab; the same compiler caveat applies (see `tab.md`'s Compiler Note) -- it is only an initialization hint for dynamic variables and picture variables, and does not retype an already-declared variable.

## Enterable vs. Non-Enterable

```json
{ "enterable": false }
```

Objects are enterable by default. A non-enterable input only displays its value -- the user cannot edit it directly, but `On Clicked`, `On Double Clicked`, `On Drag Over`, `On Drop`, `On Getting Focus`, and `On Losing Focus` still fire, which supports custom context menus, drag-and-drop, or click-to-select-only interfaces. An input is always focusable when it is enterable (per the generic Focusable property page); disabling Enterable does not disable focus by itself.

For a **non-picture** data source, `enterable: false` can be combined with `focusable: true`: the object can receive focus, and the user can place a caret or make a text selection within it (e.g. to copy the value), while still being prohibited from editing the content. This is a copy-only reading mode, distinct from a fully inert non-enterable, non-focusable display.

### Hide Focus Rectangle

```json
{ "enterable": false, "focusable": true, "hideFocusRing": true }
```

Reference: https://developer.4d.com/docs/FormObjects/propertiesAppearance#hide-focus-rectangle
Also: https://developer.4d.com/docs/commands/object-set-focus-rectangle-invisible, https://developer.4d.com/docs/commands/object-get-focus-rectangle-invisible

When a focusable input receives focus, the OS draws a focus rectangle around it. On a non-enterable-but-focusable (copy-only) input this can give the wrong impression that the input is editable. **Best practice**: set `hideFocusRing: true` on non-enterable, focusable inputs so the focus state is communicated only by the caret/selection, not by a misleading focus rectangle.

See the "Inputs" form for examples: both `Input` and `Input1` use `enterable: false` + `hideFocusRing: true` + `borderStyle: "none"` for clean, read-only date displays that still allow text selection and copying.

### Selection Always Visible

```json
{ "showSelection": true }
```

Reference: https://developer.4d.com/docs/FormObjects/propertiesEntry#selection-always-visible

By default, a text selection made inside an object is cleared from view once the window becomes inactive (loses frontmost status to another window or application) -- even though the object itself may still conceptually hold the selection. `showSelection` (Selection Always Visible) keeps the selection highlighted on screen even while the window is inactive, which is particularly useful for a non-enterable-but-focusable copy-only input, or for building interfaces where a style-editing toolbar must keep showing which text is selected while the user interacts with a floating palette window.

## Assignable vs. Non-Assignable Expressions

An input's `dataSource` can be any valid 4D expression (field, variable, object property, formula, or method name), not only a plain variable. Only an **assignable** expression (a simple variable, field, or object/collection property) can be written back into by user data entry; a **non-assignable** expression (e.g. a formula or a method call) can still be displayed and re-evaluated on every form event, but user keystrokes have nothing to write back to and the object behaves as effectively read-only regardless of the `enterable` setting.

## Multiline and Wordwrap

```json
{ "multiline": "yes", "wordwrap": "normal" }
```

`multiline` (Text-type expressions only): `"yes"`, `"no"`, or `"automatic"` (default). `"automatic"` wraps text with automatic line returns only when the object is tall enough to be treated as a multiline area; `"no"` forces a single line and strips everything after the first carriage return as soon as the value is edited. `wordwrap` only takes effect once `multiline` is `"yes"`: `"normal"` wraps long lines to fit the object's width; `"none"` truncates instead.

With `multiline: "no"`, the object continues on a single visual line and breaks only on explicit carriage returns already present in the value (any further line breaks the user types are stripped). With `multiline: "yes"`/`"automatic"` and `wordwrap: "normal"`, the object also wraps automatically at the object's width, in addition to breaking on explicit carriage returns.

**Confirmed at runtime**: with `wordwrap: "normal"`, a long line wraps automatically at word boundaries -- consistent with ICU-style word-break rules for space-delimited languages (English, etc.), never mid-word. **Not yet tested**: how wrapping behaves for languages without space delimiters (e.g. Japanese), where a naive space-based line breaker would fail to find any break point at all -- ICU's dictionary-based segmentation handles this for space-delimited scripts, but whether 4D applies the same dictionary-based approach for CJK text specifically (as opposed to falling back to arbitrary/character-boundary wrapping) has not been verified here.

### Line Break Encoding: CR, Not CRLF or LF

A 4D text value uses a single **carriage return (CR)** character as its line delimiter, on both macOS and Windows -- never CRLF (Windows) or LF-only (Unix/macOS native). This is a deliberate cross-platform normalization internal to 4D, independent of the host OS's native text-file convention. When the user presses Return/Enter while editing a multiline input, 4D inserts a CR.

This CR rule is only enforced for line breaks entered **through the keyboard** while editing. The runtime does not prevent an LF (or other) character from being inserted into a text value programmatically, and it does not normalize text that is copied in from an external source (clipboard paste, imported document, or read from a file). A pasted or command-populated text value can therefore contain a mix of CR, LF, or CRLF, and 4D will not silently rewrite it.

It is the developer's responsibility to normalize line breaks in imported text to CR before assigning it to a text/input data source, typically after reading with `Document to text`, `File.getText`, or `File.open`, replacing LF/CRLF sequences with CR (e.g. `Change string`/`Replace string` or a regex-based cleanup) as needed:

https://developer.4d.com/docs/commands/document-to-text
https://developer.4d.com/docs/API/FileClass#gettext
https://developer.4d.com/docs/API/FileClass#open

## Entry Filter

```json
{ "entryFilter": "&9" }
```

Restricts what characters can be typed, evaluated one character at a time as the user types (invalid keystrokes are simply rejected, not corrected after the fact). A filter is defined one of two ways:

- **Inline, using 4D's proprietary filter meta-language**: a short code string such as `~A` (letters, forced uppercase), `&9` (digits only), `&A` (capital letters only), `&a` (any letters), `&@` (alphanumeric only), plus a number of pre-built date/phone/SSN patterns (see the property reference for the full table).
- **By name, defined in `filters.json`**: a project-level filter defined once in the project's `filters.json` (see Project Architecture) and referenced from any object by name, prefixed with a vertical bar, e.g. `"|myFilter"`. This is the reusable/shareable equivalent of writing the meta-language code inline on every object.

https://developer.4d.com/docs/Project/architecture

An entry filter only constrains data entry -- it has no effect on how the value is displayed after the user leaves the object; combine it with a matching display format (`textFormat`, `dateFormat`, etc.) for both.

Defining an entry filter also **disables Front-End Processors (FEP)** for the object -- see Keyboard Layout, below, for why.

## Keyboard Layout and Front-End Processors (FEP)

```json
{ "keyboardDialect": "ar-ma" }
```

Reference: https://developer.4d.com/docs/FormObjects/propertiesEntry#keyboard-layout, https://developer.4d.com/docs/commands/object-get-keyboard-layout, https://developer.4d.com/docs/commands/object-set-keyboard-layout

`keyboardDialect` forces a specific installed keyboard layout (e.g. `"ar-ma"`, `"cs"`) to become active automatically whenever the object gets focus -- useful when a particular field must always be typed in a given language/layout regardless of the user's current system layout.

Front-End Processors (FEP) -- the input method system used by Chinese, Japanese, Korean, and other languages that require composing a character from multiple keystrokes before committing it -- are **disabled** on an object in two cases:

- A specific `keyboardDialect` is assigned to the object (FEP composition is incompatible with forcing a fixed non-FEP layout on focus)
- The object has an `entryFilter` defined (see above) -- an entry filter operates on raw, individual keystrokes as they are typed, which is fundamentally incompatible with FEP composition, where multiple keystrokes must be deferred and combined before a character is actually committed

## Spell Check and Writing Tools

```json
{ "spellcheck": true, "writingTools": true }
```

Reference: https://developer.4d.com/docs/FormObjects/propertiesEntry#auto-spellcheck, https://developer.4d.com/docs/FormObjects/propertiesEntry#writing-tools, https://developer.4d.com/docs/commands/spell-set-current-dictionary, https://blog.4d.com/apple-writing-tools-now-available-in-4d-write-pro-and-text-input/

`spellcheck` (Auto Spellcheck, Text type only) performs a spell-check automatically during data entry, using a **platform-dependent spelling engine**: Hunspell on Windows, the system spell-checking service on macOS (also invocable per-object via the `SPELL CHECKING` language command, and configured via `SPELL SET CURRENT DICTIONARY` for the active dictionary/language).

`writingTools` is a separate, newer property (added **21 R4**) that exposes Apple Intelligence Writing Tools (proofread, rewrite, summarize, change tone) inside a multiline input's context menu, and through the `writingTools` standard action assignable to a button/menu item. It is **macOS-only** and additionally requires Apple Intelligence & Siri to be enabled in System Settings on a compatible Mac; on Windows, or on a Mac without Apple Intelligence enabled, the property remains visible/settable in the Property List but the feature and its standard action are both inert at runtime (invoking the action does nothing). Where Auto Spellcheck is a basic, cross-platform, always-available dictionary check, Writing Tools is an AI-assisted, system-dependent, opt-in enhancement layered on top for macOS users specifically.

## Placeholder


```json
{ "placeholder": "Enter your name" }
```

Watermark text shown when the object's value is empty (string types), or for date/time when **Blank if null** is enabled; disappears once the user types a character and reappears if the value is cleared again. Supports an XLIFF reference (`":xliff:ResName"`), but a reference cannot be combined with static text -- it is one or the other.

## Choice List

```json
{ "choiceList": ["Red", "Green", "Blue"] }
```

An input can carry the same `choiceList` property used by drop-down list/combo box/hierarchical list (inline array/collection, or a named list from the toolbox). This turns the input into a value-constrained pop-up at runtime while keeping the object type `"input"` rather than `"combo"`. See Default value/Excluded List/Required List (`properties_RangeOfValues.md`) for the related "list of acceptable values" properties that also apply to inputs.

## Display Formats by Expression Type

| Expression type (`dataSourceTypeHint`) | Format property (JSON key) | Notes |
|---|---|---|
| `text` | `textFormat` (Alpha Format) | `#` placeholder characters plus literal punctuation, e.g. `"(###) ### ####"`. **The official Alpha Format property page's own "Objects Supported" list omits Input** (it lists only Drop-down List, Combo Box, List Box Column/Footer), despite Input's own overview page listing Alpha Format as a supported property -- the same kind of doc inconsistency seen previously with Group Box's Title property (see `group-box.md`) |
| `date` | `dateFormat` | Built-in (`systemShort`, `systemLong`, `iso8601`, etc.) or custom pattern; append `" blankIfNull"` to display an empty area instead of a zero date |
| `time` | `timeFormat` | Similar built-in/custom pattern support |
| `number` | `numberFormat` | Built-in or custom numeric pattern |
| `boolean` | `booleanFormat` | `"<textWhenTrue>;<textWhenFalse>"`, e.g. `"Assigned;Unassigned"` -- displays a boolean expression as text instead of a check box |
| `picture` | `pictureFormat` | `"scaled"`, `"truncatedCenter"`, `"truncatedTopLeft"`, `"proportionalTopLeft"`, `"proportionalCenter"`, `"tiled"` -- identical vocabulary to List Box Column/Footer picture display |

### Runtime Format and Filter Commands

Reference: https://developer.4d.com/docs/commands/object-set-format, https://developer.4d.com/docs/commands/object-set-filter

Display formats and entry filters can be changed at runtime with `OBJECT SET FORMAT` and `OBJECT SET FILTER`. This allows dynamic switching (e.g. toggling between currency and percentage format on the same number input based on user selection).

### Runtime Scrollbar and Multiline Commands

Reference: https://developer.4d.com/docs/commands/object-set-scrollbar, https://developer.4d.com/docs/commands/object-set-multiline

Scrollbar visibility and multiline mode can also be changed at runtime with `OBJECT SET SCROLLBAR` and `OBJECT SET MULTILINE`.

### Runtime-Confirmed: Alpha Format Never Applies, Number Format Only Applies While Unfocused

Manually testing each format at runtime (not just the static `FORM SCREENSHOT` template) on single-object pages confirmed:

- **`textFormat` (Alpha Format) never applies to an Input at all**, at runtime or design time -- a `textFormat: "(###) ### ####"` input holding `"5551234567"` displays the literal, unformatted `"5551234567"`. This matches the official Alpha Format page's "Objects Supported" list, which really does omit Input despite Input's own overview page claiming support.
- **`booleanFormat` and `dateFormat` apply correctly and unconditionally** -- a `booleanFormat: "Assigned;Unassigned"` input holding `True` displays `"Assigned"`; a `dateFormat: "systemLong"` input holding `!2024-03-25!` displays `"Monday, March 25, 2024"`, both regardless of whether the object currently has keyboard focus.
- **`numberFormat` only applies while the object does *not* have keyboard focus.** A `numberFormat: "###,##0.00"` input holding `1234.5` displayed the raw, unformatted `"1234.5"` -- not because the format doesn't work, but because the object had **automatically received keyboard focus** (it was the only/first enterable object on its page, and 4D auto-focuses the first object in entry order whenever a page loads or becomes active). While focused, a number-type input shows its raw editable value; the formatted display only appears once it loses focus. This is unlike Date, which displays formatted even while focused.

**Practical fix for pages that must display already-formatted values without user interaction**: handle `On Page Change` in the form method and call `GOTO OBJECT(*; "")` (empty object name) to clear the current focus/selection immediately after a page switch:

```4d
Case of
	: ($event.code=On Page Change)
		GOTO OBJECT(*; "")
End case
```

This defocuses whatever object auto-received focus from the page change, so number-type inputs (and similar focus-sensitive displays) immediately show their formatted value instead of the raw editable one. See https://developer.4d.com/docs/commands/goto-object.

### Date Entry Parsing Is Lenient, But Re-Entering the Formatted Display Can Produce a Null Date

Typing `1999.1.1` into a `dateFormat: "systemLong"` input and validating it produces `Friday, January 1, 1999` -- 4D's date parser accepts alternate separators (`.` here) and is not strictly limited to the documented `MM/DD/YYYY` entry format. However, typing the object's *own currently-displayed formatted text* back in as new input -- e.g. typing the literal string `Friday, January 1, 1999` into the same field -- does **not** round-trip; it fails to parse and the value resets to a null date (`00/00/00`). This is a real trap: a formatted date display is not necessarily valid as re-entered input, and the object does not switch to a raw/editable representation while being retyped, unlike some other apps' date fields. Treat this as effectively a display-only round-trip hazard -- possibly a bug -- rather than relying on users being able to re-type what they see.

## Picture-Type Input

A picture-type input (`dataSourceTypeHint: "picture"`) is the only input variant that displays and accepts image data (pasted from the Clipboard or dragged in) rather than character data. Its context menu (unless disabled) adds **Import...** and **Save as...** commands, plus temporary, non-persistent overrides of the display format (Truncated non-centered / Scaled to fit / Scaled to fit centered proportional). Per `properties_Object.md#expression-type`, a picture variable used as a process variable has a stricter typing requirement than other expression types: it must already be declared (`var varName : Picture`) and initialized *before* the form loads (in the method that calls `DIALOG`, not the form's own `On Load`) for correct display in interpreted mode -- otherwise the picture variable will not render correctly.

## Supported Properties (per JSON Schema)

All properties from the schema's `input` definition, with exact JSON keys and valid enum values:

| JSON Key | Type / Enum Values | Notes |
|----------|-------------------|-------|
| `type` | `"input"` (fixed) | |
| `dataSource` | string | Field, variable, or any expression |
| `dataSourceTypeHint` | `"text"`, `"object"`, `"number"`, `"integer"`, `"boolean"`, `"picture"`, `"date"`, `"time"` | Expression type hint |
| `method` | string | **Required to bind an object method** — e.g. `"ObjectMethods/Input.4dm"`. Without this, the `.4dm` file is orphaned and never invoked (same rule as the form-level `"method"` property) |
| `enterable` | boolean | Default `true` |
| `focusable` | boolean | When focusable, always tabbable |
| `hideFocusRing` | boolean | Hides the OS focus rectangle; best practice for non-enterable, focusable inputs |
| `showSelection` | boolean | Keeps selection highlighted when the window is inactive |
| `multiline` | `"automatic"`, `"yes"`, `"no"` | Text type only |
| `wordwrap` | `"automatic"`, `"normal"`, `"none"` | Only active when `multiline` is enabled |
| `placeholder` | string | Watermark text when empty |
| `entryFilter` | string | Built-in code, custom string, or `\|namedFilter` |
| `contextMenu` | `"automatic"`, `"none"` | Only works when `enterable: true` — see Context Menu section |
| `spellcheck` | boolean | Text type only; platform-dependent engine |
| `keyboardDialect` | string | e.g. `"ar-ma"`, `"cs"` — disables FEP |
| `memorizeValue` | boolean | Saves data source value when `memorizeGeometry` is active |
| `choiceList` | string or array | Same mechanism as drop-down/combo |
| `requiredList` | string or array | |
| `excludedList` | string or array | |
| `defaultValue` | string | |
| `min` / `max` | string or number | For number, date, time |
| `textFormat` | string | Alpha format — see caveat (does not apply to Input at runtime) |
| `numberFormat` | string | Only applies while unfocused |
| `dateFormat` | `"systemShort"`, `"systemMedium"`, `"systemLong"`, `"iso8601"`, `"rfc822"`, `"short"`, `"shortCentury"`, `"abbreviated"`, `"long"` (optionally + `" blankIfNull"`) | |
| `timeFormat` | `"hh_mm_ss"`, `"hh_mm"`, `"hh_mm_am"`, `"mm_ss"`, `"HH_MM_SS"`, `"HH_MM"`, `"MM_SS"`, `"systemShort"`, `"systemMedium"`, `"systemLong"`, `"iso8601"` (optionally + `" blankIfNull"`) | |
| `booleanFormat` | string | `"textWhenTrue;textWhenFalse"` |
| `pictureFormat` | `"scaled"`, `"truncatedTopLeft"`, `"truncatedCenter"`, `"tiled"`, `"proportionalTopLeft"`, `"proportionalCenter"` | |
| `textAlign` | `"automatic"`, `"right"`, `"center"`, `"justify"`, `"left"` | |
| `textAngle` | `0`, `90`, `180`, `270` | |
| `fontTheme` | `"normal"`, `"main"`, `"additional"` | |
| `styledText` | boolean | Rich per-character styling (multi-style) |
| `storeDefaultStyle` | boolean | Persists style tags with the value |
| `allowFontColorPicker` | boolean | Multi-style context menu extension |
| `printFrame` | `"fixed"`, `"variable"` | |
| `scrollbarHorizontal` | `"visible"`, `"hidden"`, `"automatic"` | |
| `scrollbarVertical` | `"visible"`, `"hidden"`, `"automatic"` | |
| `dragging` | `"none"`, `"automatic"`, `"custom"` | |
| `dropping` | `"none"`, `"automatic"`, `"custom"` | |
| `borderRadius` | integer (≥ 0) | Added 19 R7; **not** `cornerRadius` — that key is silently ignored |
| `tooltip` | string | |

Plus inherited from `objectCommon`: `top` (required), `left` (required), `width`, `height`, `bottom`, `right`, `sizingX` (`"move"`, `"grow"`, `"fixed"`), `sizingY` (`"move"`, `"grow"`, `"fixed"`), `class`, `visibility` (`"visible"`, `"hidden"`, `"selectedRows"`, `"unselectedRows"`).

Plus inherited from `borderStyle`: `borderStyle` (`"system"`, `"none"`, `"solid"`, `"dotted"`, `"raised"`, `"sunken"`, `"double"`).

Plus inherited from `drawingSpec`: `stroke` (color), `fill` (color).

Plus inherited from `fontSpec`: font properties (`fontFamily`, `fontSize`, `fontWeight`, `fontStyle`, `textDecoration`).

## Supported Events (JSON Schema Names)

The `events` array uses these exact JSON enum values (not the runtime `FORM Event.description` strings):

`onClick`, `onDoubleClick`, `onAfterEdit`, `onAfterKeystroke`, `onBeforeKeystroke`, `onDataChange`, `onGettingFocus`, `onLosingFocus`, `onSelectionChange`, `onBeginDragOver`, `onDragOver`, `onDrop`, `onMouseEnter`, `onMouseMove`, `onMouseLeave`, `onMouseUp` (picture type only), `onScroll` (picture type only), `onLoad`, `onUnload`, `onValidate`, `onHeader`, `onPrintingDetail`, `onPrintingBreak`, `onPrintingFooter`.

**Important**: JSON event names differ from runtime descriptions. Key mappings:

| JSON Schema (`events` array) | Runtime (`FORM Event.description`) |
|------------------------------|-------------------------------------|
| `onClick` | `On Clicked` |
| `onDoubleClick` | `On Double Clicked` |
| `onAlternateClick` | `On Alternative Click` |
| `onLongClick` | `On Long Click` |
| `onDataChange` | `On Data Change` |
| `onAfterEdit` | `On After Edit` |
| `onGettingFocus` | `On Getting Focus` |
| `onLosingFocus` | `On Losing Focus` |

In 4D code, compare against the runtime constant (e.g. `$event.code=On Clicked`), not the JSON key.

## On Data Change: The General-Purpose Event

Reference: https://developer.4d.com/docs/Events/onDataChange

`On Data Change` is the general-purpose event for reacting to a **validated** value change on an input. Two rules govern when it fires:

- It fires when the edit is **validated** -- the user tabs out, presses Return, or clicks outside the object -- ending the edit session for that object. It is not a per-keystroke or per-edit-action event; it fires once the object's content is committed, not while it is still being actively edited.
- **Important**: clicking outside the object only validates if there is somewhere for focus to go. If the current input is the **only focusable object** on the form, `On Data Change` will never fire via click-out — the input remains perpetually in edit mode. This is a form design issue (ensure at least two focusable objects, or rely on Return/Enter for validation).
- It only fires for changes made **through the user interface**. A code-driven assignment to the same variable/field/object property (e.g. `Form.myText:="new value"` in a method) does **not** trigger `On Data Change`.
- It fires even when the newly entered value is **identical** to the previous value -- unlike a typical "changed" semantics, `On Data Change` really means "the user interface validated this data source," not "the value is different from before."

An individual edit action within that session -- a keystroke, a paste, a cut, an automatic drop, an FEP composition commit, or an Undo -- is a **transitional** edit, not a validation, and is reported by `On After Edit` instead (see below), not `On Data Change`.

### `On Losing Focus` — Fires After `On Data Change`

Reference: https://developer.4d.com/docs/Events/onLosingFocus

`On Losing Focus` fires after `On Data Change` when the user moves away from the input. It is another possible hook for validation logic, but suffers from the same limitation: if the input is the **only focusable object**, focus never leaves, and `On Losing Focus` never fires.

### `REJECT` — Legacy Record-Level Command

Reference: https://developer.4d.com/docs/commands/reject

`REJECT` is a legacy command from the era when all forms were record input forms and all data sources were fields. It rejects the **entire record entry** at the form level, not an individual input's edit. It is not the right tool for field-level input validation in modern code — use `On Data Change` or `On After Edit` with explicit logic instead.

## Keystroke Events vs. `On After Edit`

Reference: https://developer.4d.com/docs/Events/onAfterKeystroke, https://developer.4d.com/docs/Events/onBeforeKeystroke, https://developer.4d.com/docs/Events/onAfterEdit

`On Before Keystroke` and `On After Keystroke` were designed for an era of applications/languages that work primarily with raw, individual keystrokes -- they fire once per physical key. This model does not map cleanly onto every way an input's content can change: a paste, a cut, an automatic drop, an FEP (Front-End Processor) composition commit, or an Undo all modify the content without corresponding to a single discrete keystroke.

A modern application should use `On After Edit` instead: it fires after **every** transitional edit action, whether that action was a single keystroke, a paste, a cut, an automatic drop, an FEP-composed edit, or an Undo -- one consistent event regardless of the mechanism that produced the change, rather than needing to separately special-case pastes/cuts/drops/FEP/Undo alongside keystroke handling. This is the event that fires for an automatically dropped text or picture -- `On Data Change` does not fire until the object is subsequently validated (tab/Return/click-out).

### `FILTER KEYSTROKE` — Intercepting Individual Keystrokes

Reference: https://developer.4d.com/docs/commands/filter-keystroke

When the keyboard layout is simple (i.e. no FEP composition), it is possible to intercept and override individual keystrokes using `On Before Keystroke` + `FILTER KEYSTROKE`. `On Before Keystroke` fires **before** the character is inserted into the input; calling `FILTER KEYSTROKE` inside this event replaces the character that is about to be inserted (or suppresses it entirely by passing an empty string or a null character).

This uses the same underlying mechanism as entry filters (`entryFilter`), but gives programmatic control — you can implement conditional logic, character transformations, or custom validation that a static filter pattern cannot express.

```4d
// Example: force uppercase on every keystroke
Case of
  : (FORM Event.code=On Before Keystroke)
    FILTER KEYSTROKE(Uppercase(Keystroke))
End case
```

**FEP caveat**: keystroke events (`On Before Keystroke`, `On After Keystroke`) are **not posted** during a Front-End Processor edit session (e.g. Japanese Input Method Editor, Chinese Pinyin). The FEP composes characters internally from multiple physical keystrokes before committing the final character — individual keystrokes are consumed by the FEP and never reach the 4D event system. Use `On After Edit` instead to process text changes from FEP input. For this reason, assigning a `keyboardDialect` to the input (which disables FEP — see above) is a natural companion to keystroke-level processing.

### Capturing Key Combinations with Invisible Buttons

An alternative to processing keystrokes inside an input's own method is to place a **button with a shortcut** on the form. The button intercepts the key combination globally on the form, regardless of which object has focus — the input never sees the keystroke.

To avoid disrupting the user's typing flow, the button must be:

1. **Not rendered** (`display: false`) — the button is invisible but still active
2. **Not focusable** (`focusable: false`) — pressing the shortcut fires the button's method without stealing focus from the text input

Reference: https://developer.4d.com/docs/FormObjects/propertiesDisplay#not-rendered, https://developer.4d.com/docs/FormObjects/propertiesEntry#shortcut, https://developer.4d.com/docs/FormObjects/propertiesEntry#focusable

```json
{
  "HiddenShortcut": {
    "type": "button",
    "style": "custom",
    "display": false,
    "focusable": false,
    "top": 0,
    "left": 0,
    "width": 0,
    "height": 0,
    "shortcutKey": "K",
    "shortcutAccel": true,
    "method": "ObjectMethods/HiddenShortcut.4dm",
    "events": ["onClick"]
  }
}
```

This pattern is useful for implementing global form hotkeys (e.g. Cmd+K to open a search, Ctrl+S to save) that must work while the user is typing in an input, without interrupting the current edit session or moving focus away.

## On Selection Change

Reference: https://developer.4d.com/docs/Events/onSelectionChange

For an input, the text caret is treated as a **zero-width selection**: every movement of the selection or caret fires `On Selection Change`. Per the reference, for Input (and 4D Write Pro) this event fires specifically "following a click or a keystroke" -- it is a direct response to the user actively moving the caret or selection with the mouse or arrow keys once the object has focus.

An automatic drop does **not** fire `On Selection Change`: at the moment a drop lands, the input has no active selection to move (there is no click or keystroke involved in the drop itself), so there is nothing for the event to report. Only a subsequent click or arrow-key press inside the now-focused input triggers `On Selection Change`.

## On Clicked on Input

An input can also process `On Clicked`, and this works regardless of whether the input is `enterable` or `focusable` -- a non-enterable, non-focusable input still receives `On Clicked` when clicked, which is one of the mechanisms that makes non-enterable inputs useful for click-driven, display-only UI (see Enterable, above).

**Contrast with a combo box's text-entry area** (`combo.md`): much of an input's text-entry behavior (typing, `entryFilter`, `On Data Change`/`On After Edit` on validation/edit, caret/selection mechanics) applies identically to the enterable text part of a combo box (conceptually its "element 0"), since a combo box is fundamentally an enterable text field with an attached pop-up. However, `On Clicked` does **not** fire for a click into that text-entry part -- a combo box's `On Clicked` fires only for a **popup-driven selection** (click the chevron, then choose an item from the list), the same click-is-a-data-change semantics as a drop-down list. Clicking the chevron and then dismissing the popup without choosing anything does not fire `On Clicked` at all.

### Distinguishing Edit Mode: `Is editing text`

Reference: https://developer.4d.com/docs/commands/is-editing-text

When an input (or combo box) receives an event such as `On Clicked` or
`On Before Keystroke`, the processing may need to differ depending on
whether the user is actively typing text or not. The command
`Is editing text` returns **True** if the user is entering values in the
object, and **False** otherwise.

**Supported objects**: input, list box (enterable and non-enterable),
combo box. For all other object types the command always returns False.

**Primary use case — list box type-ahead**: The most common use of this
command is within `On Before Keystroke` on a list box. The event fires
whenever the list box has focus and a key is pressed — even if no cell
is being edited. This allows implementing type-ahead search (filter or
jump to matching rows) without interfering with actual cell editing:

```4d
Case of
  : (FORM Event.code=On Before Keystroke)
    If (Not(Is editing text))
      // No cell is being edited — use the keystroke for search/navigation
      var $char : Text
      $char:=Uppercase(Keystroke)
      If (($char>="A") & ($char<="Z")) | (($char>="0") & ($char<="9"))
        // Perform incremental search / row selection
        Form.results:=ds.people.query("name = :1"; $char+"@")
      End if
    Else
      // Cell is being edited — optionally filter keystrokes
      If (Keystroke="+") | (Keystroke="-")
        FILTER KEYSTROKE("")  // disallow certain characters
      End if
    End if
End case
```

Reference (blog): https://blog.4d.com/type-ahead-made-easy/

**FEP note**: As with `On Before Keystroke` generally (see above),
IME/FEP composition keystrokes do not reach the 4D event system.
`Is editing text` returns True during a composition session because the
object is in edit mode, but the individual composition keystrokes are not
reported — use `On After Edit` for FEP input processing.

**Contrast with `On Clicked` on an input**: When you need to know
whether a click on an input is entering edit mode (first click) versus
clicking while already editing (e.g. repositioning the caret), you can
call `Is editing text` inside `On Clicked`. On the first click that
gives focus, the object is not yet in edit mode, so `Is editing text`
returns False. On subsequent clicks (while already typing), it returns
True. This can be used to differentiate "selection click" from
"editing click" in the same handler.

### Mouse Coordinates: `MOUSEX`/`MOUSEY`

Reference: https://developer.4d.com/docs/Concepts/variables#system-variables

During `On Clicked` on an input, the system variables `MOUSEX` and `MOUSEY` are **automatically assigned the local (object-relative) mouse coordinates only when the data source is a picture**. If the data source is not a picture, `MOUSEX`/`MOUSEY` are not updated by the click, and the current mouse position must instead be obtained with `MOUSE POSITION` (https://developer.4d.com/docs/commands/mouse-position).

To convert the object-relative coordinates to screen-relative coordinates, use `CONVERT COORDINATES` (https://developer.4d.com/docs/commands/convert-coordinates).

`MOUSEX`/`MOUSEY` are also automatically updated during the mouse-tracking events regardless of data source type: `On Mouse Enter`, `On Mouse Leave`, `On Mouse Move` (https://developer.4d.com/docs/Events/onMouseEnter, onMouseLeave, onMouseMove) -- the picture-only restriction is specific to `On Clicked`.

### SVG Hit-Testing and Interactive Canvas

For comprehensive coverage of picture-input-specific features — SVG hit-testing,
`On Mouse Up`, `Is waiting mouse up`, timer-based mouse tracking, DOM vs
rendering tree, and the full interactive SVG editor pattern — see
**`picture-input.md`**.

## Context Menu Behavior

Reference: https://developer.4d.com/docs/FormObjects/propertiesEntry#context-menu, https://developer.4d.com/docs/commands/object-set-context-menu, https://developer.4d.com/docs/commands/object-get-context-menu

The built-in contextual menu (`contextMenu: "automatic"`, the default) appears on Control+click or right-click. It works on both enterable and non-enterable inputs. However, the **`%password` pseudo-font suppresses the Copy standard action** — when `fontFamily: "%password"` is applied, the Copy menu item is not permitted (neither in the built-in context menu nor as a standard action bound to a custom popup menu), which prevents the user from copying the masked value.

This is why a non-enterable password-masked input may appear to have no context menu at all — the menu itself still exists, but its primary useful action (Copy) is disabled by the password font's security restriction.

The exact contents of the menu depend on the data source's expression type (plain text vs. picture vs. multi-style/styled text) and on the current Clipboard/pasteboard content. A picture-type input's menu adds **Import...** and **Save as...** commands (plus temporary picture-format overrides); a multi-style text input's menu adds font/size/style/color commands, generating `On After Edit` when a style attribute is changed through the menu.

## Password Pseudo-Font

```json
{ "fontFamily": "%password", "fontSize": 13 }
```

Reference: https://developer.4d.com/docs/commands/object-set-font, https://developer.4d.com/docs/commands/object-get-font

`%password` is a pseudo-font in 4D (not a real typeface) that replaces every character with `*` in inputs and combo boxes. It is set via the `fontFamily` JSON property (or `OBJECT SET FONT` / `OBJECT GET FONT` at runtime).

Key behaviors:
- Applies to inputs and combo boxes
- The Copy standard action is **suppressed** while `%password` is active — the value cannot be copied to the pasteboard through any standard mechanism (built-in context menu or custom menu with `ak copy`)
- The underlying data source value is **not** masked — it holds the real text; only the display is obfuscated
- `fontSize` should be set explicitly (the `*` character renders differently from normal text at the default font size)

### Custom Context Menu with Standard Actions

For a fully customized context menu, set `contextMenu: "none"` to suppress the built-in menu, then implement a custom popup in the object method. Use `SET MENU ITEM PROPERTY` to associate a **standard action** with each menu item — this lets 4D handle the action natively:

Reference: https://developer.4d.com/docs/commands/set-menu-item-property, https://developer.4d.com/docs/commands/get-menu-item-property

```4d
var $event : Object
$event:=FORM Event

Case of 
  : (($event.code=On Clicked) && (Contextual click))
    var $menu : Text
    $menu:=Create menu
    APPEND MENU ITEM($menu; ak standard action title)
    SET MENU ITEM PROPERTY($menu; -1; Associated standard action; ak copy)
    var $parameter : Text
    $parameter:=Dynamic pop up menu($menu)
    RELEASE MENU($menu)

End case 
```

Key points:
- `ak standard action title` automatically names the menu item from the standard action (e.g. "Copy"), including localization
- `SET MENU ITEM PROPERTY($menu; -1; Associated standard action; ak copy)` binds the Copy standard action to the last appended item — no manual pasteboard code needed
- The object must have `method` pointing to its `.4dm` file, `events: ["onClick"]`, and `contextMenu: "none"`

**However**, when `%password` is active, the `ak copy` standard action is blocked. To allow copying from a password-masked input, use manual pasteboard access with selection awareness:

### Copying Selected Text from a Password-Masked Input

Reference: https://developer.4d.com/docs/commands/get-highlight, https://developer.4d.com/docs/commands/get-edited-text

When the `%password` font blocks the Copy standard action, implement copy manually using:

- **`Get edited text`** — returns the text currently being edited (pre-validation), not the committed/stored data source value. This is important because during an edit session the displayed content may differ from the stored value.
- **`GET HIGHLIGHT`** — returns the selection start and end character positions in the focused object
- **`HIGHLIGHT TEXT`** — sets the selection range programmatically (same coordinate system as `GET HIGHLIGHT`)
- **`Substring`** — extracts only the selected portion

```4d
var $event : Object
$event:=FORM Event

Case of 
  : (($event.code=On Clicked) && (Contextual click))
    var $focusObjectName : Text
    $focusObjectName:=OBJECT Get name(Object with focus)
    var $start; $end : Integer
    GET HIGHLIGHT(*; $focusObjectName; $start; $end)
    var $selectedValue : Text
    $selectedValue:=Substring(Get edited text; $start; $end-$start)

    If ($selectedValue#"")
      var $menu : Text
      $menu:=Create menu
      APPEND MENU ITEM($menu; "Copy")
      SET MENU ITEM PARAMETER($menu; -1; "copy")
      var $parameter : Text
      $parameter:=Dynamic pop up menu($menu)
      RELEASE MENU($menu)

      If ($parameter="copy")
        SET TEXT TO PASTEBOARD($selectedValue)
      End If 
    End If 

End case 
```

Key differences from the naive approach (using `OBJECT Get pointer` / `OBJECT Get value`):
- **Only copies the selected text**, not the entire value — respects user intent
- **Uses `Get edited text`**, not the stored data source — captures the current edit state
- **Only shows the menu when text is selected** (`$selectedValue#""`) — no misleading empty-copy option
- **Works despite `%password`** because it bypasses the standard action system entirely

### Retrieving an Object's Value: `OBJECT Get pointer` vs `OBJECT Get value` vs `Get edited text`

Reference: https://developer.4d.com/docs/commands/object-get-pointer, https://developer.4d.com/docs/commands/object-get-value, https://developer.4d.com/docs/commands/get-edited-text

Three ways to access an input's value, each with different semantics:

| Command | Returns | Works with expressions (`Form.xxx`)? | Notes |
|---------|---------|--------------------------------------|-------|
| `OBJECT Get pointer` | Pointer to the data source variable | **No** — only works if the data source is a variable or field. Returns `Nil` for object property expressions like `Form.text` | Legacy approach (pre-v12, when data sources were always variables/fields) |
| `OBJECT Get value` | The validated/stored value as a variant | **Yes** — works regardless of whether the data source is a variable, field, or expression | Preferred for reading the committed value of any object |
| `Get edited text` | The text currently being edited (pre-validation) | **Yes** — works regardless of data source type | Only valid during an edit session; returns the in-progress content that may differ from the stored value |

**Rule of thumb**: use `Get edited text` when you need the current content as the user sees it mid-edit; use `OBJECT Get value` when you need the committed/stored value regardless of data source type; avoid `OBJECT Get pointer` for modern code where expressions are common.

### Styled Text Caveat

Reference: https://developer.4d.com/docs/commands/object-is-styled-text, https://developer.4d.com/docs/commands/st-get-plain-text

In 4D, styled text values are stored as a light version of HTML — the data source contains markup. `GET HIGHLIGHT` returns **character positions in the plain text**, not byte offsets in the HTML source. Therefore, calling `Substring` directly on the data source (which is HTML) returns wrong values when the input contains styled text.

Before extracting the selection, check `OBJECT Is styled text` and, if true, use `ST Get plain text` to obtain the plain text for substring:

```4d
var $text : Text
If (OBJECT Is styled text(*; $focusObjectName))
  $text:=ST Get plain text(*; $focusObjectName)
Else 
  $text:=Get edited text
End If 
$selectedValue:=Substring($text; $start; $end-$start)
```

### Styled Text Commands

Reference: https://developer.4d.com/docs/commands/theme/Styled-Text

When `styledText: true`, the full **Styled Text** command theme is available for programmatic rich text editing at runtime. These commands can set or get bold, italic, color, font, size, and other attributes on a specific character range — enabling rich text editor functionality.

**Important constraints (confirmed by test):**

1. **In/out parameter**: ST commands require a **variable or field**, not an expression like `Form.xxx`. Pattern:
   ```4d
   var $st : Text
   $st:="Hello World"
   ST SET ATTRIBUTES($st; 1; 6; Attribute bold style; 1)
   Form.st_bold:=$st
   ```

2. **Colors must be numeric `0x00RRGGBB`**: `ST SET ATTRIBUTES` is **not** in the list of commands extended to accept CSS color strings (see https://blog.4d.com/css-color-strings-for-better-readability/). Passing `"#FF0000"` raises error [7] "A Numeric argument was expected."
   ```4d
   // WRONG: ST SET ATTRIBUTES($st; 1; 6; Attribute text color; "#FF0000")
   // RIGHT:
   ST SET ATTRIBUTES($st; 1; 6; Attribute text color; 0x00FF0000)
   ```

3. **`ST GET ATTRIBUTES` returns Integer for color** (same `0x00RRGGBB` format). Returns **-1** for attributes not explicitly set on the range (inherited/default).

4. **Multiple attributes in one call** work — all values must be the same numeric type:
   ```4d
   ST SET ATTRIBUTES($st; 1; 10; Attribute bold style; 1; Attribute text color; 0x000000FF; Attribute underline style; 1)
   ```

**Key commands tested:**

| Command | Purpose | Notes |
|---------|---------|-------|
| `ST SET ATTRIBUTES` | Set style on range | Attributes: bold, italic, underline, strikethrough, font name, text size, text color, background color |
| `ST GET ATTRIBUTES` | Read style from range | Returns -1 for unset attributes |
| `ST SET TEXT` | Insert/replace with styled HTML | `<span style="...">text</span>` — interprets HTML tags |
| `ST SET PLAIN TEXT` | Insert/replace as literal text | Escapes `<` to `&lt;` — displays literal angle brackets |
| `ST Get plain text` | Strip markup | Returns character stream matching position model |

**Internal storage**: Styled text is stored as HTML. Setting `color: 0x00FF0000` produces `<span style="color:#FF0000">`. The data source contains the full HTML markup.

`ST Get plain text` strips all HTML/style markup and returns the character stream that matches `GET HIGHLIGHT`'s character-position indices.

### Character Position Model

Reference: https://developer.4d.com/docs/commands/get-highlight, https://developer.4d.com/docs/commands/highlight-text

`GET HIGHLIGHT` and `HIGHLIGHT TEXT` use the same position model. Positions represent the **spaces between characters** (like cursor positions), not character indices:

```
|A|B|C|
1 2 3 4
```

- Character "A" occupies range 1–2
- Character "B" occupies range 2–3
- Selecting "ABC" is range 1–4
- An empty selection (cursor between B and C) is start=3, end=3

`HIGHLIGHT TEXT` sets the selection programmatically using the same coordinate system:

```4d
HIGHLIGHT TEXT(*; "myInput"; 1; 4)  // selects "ABC"
HIGHLIGHT TEXT(*; "myInput"; 3; 3)  // places cursor between B and C
```

#### UTF-16 and Surrogate Pairs

4D text is stored internally as **UTF-16 little-endian**. Characters outside the Basic Multilingual Plane (emoji, some CJK characters) are represented as **surrogate pairs** — two UTF-16 code units for a single visible character. `GET HIGHLIGHT`, `HIGHLIGHT TEXT`, `Length`, `Substring`, and ST commands all measure positions in **code units**, not grapheme clusters.

**Confirmed by test**: `"Hi 😀 there"` → `Length` = **11** (not 9). The emoji 😀 (U+1F600) consumes 2 code units. `ST SET ATTRIBUTES($st; 4; 6; ...)` correctly targets just the emoji. The values from `GET HIGHLIGHT` can be passed directly to `Substring` and ST range parameters without conversion — they are consistent with each other.

This also means that `Length` returns code units, not visible characters. A string containing one emoji has `Length` = 2.

### Comparison: Built-in vs. Custom

The "Inputs" form demonstrates both approaches side by side:

| | `Input` (custom) | `Input1` (built-in) |
|---|---|---|
| `contextMenu` | `"none"` | `"automatic"` (default) |
| `method` | `"ObjectMethods/Input.4dm"` | not needed |
| `events` | `["onClick"]` | not needed |
| How Copy works | Custom popup with standard action | OS-provided context menu |
| When to use | Full control over menu items | Simplest approach for standard behavior |

## System Pickers (Font and Color)

Reference: https://developer.4d.com/docs/FormObjects/propertiesText (Allow Font/Color Picker)

Input objects with `styledText: true` can enable the **system font picker** and
**system color picker** — floating, non-modal panels (on macOS; modal on Windows)
that update the selected text **live** as the user changes settings.

### Enabling

Set the **"Allow Font/Color Picker"** property on the input object (in the Form
editor, or via the property list). This is a prerequisite — without it, the picker
commands do nothing for that object.

### Commands

| Command | Ref | Behavior |
|---------|-----|----------|
| `OPEN FONT PICKER` | https://developer.4d.com/docs/commands/open-font-picker | Opens the system font dialog. No parameters. Changes are applied to the current text selection in the focused object. Generates `On After Edit`. **macOS**: floating/non-modal. **Windows**: modal. |
| `OPEN COLOR PICKER` | https://developer.4d.com/docs/commands/open-color-picker | Opens the system color dialog. Optional parameter: `0` or omitted = text color, `1` = background color. Applied to selection in focused object. Generates `On After Edit`. **macOS**: floating/non-modal. **Windows**: modal. |

### Typical Pattern

A button (set to non-focusable) triggers the picker. The button must first give
focus to the input, then open the picker:

```4d
// Button object method (button must have "Focusable" unchecked)
Case of
  :(FORM Event.code=On Clicked)
    GOTO OBJECT(*; "myStyledInput")  // give focus to the input
    OPEN FONT PICKER
End case
```

For a color picker button:
```4d
Case of
  :(FORM Event.code=On Clicked)
    GOTO OBJECT(*; "myStyledInput")
    OPEN COLOR PICKER(0)  // 0 = text color, 1 = background color
End case
```

The picker modifies the selected text **in real time** — each change generates
`On After Edit` on the input object.

### Comparison with `Select RGB color`

| | `OPEN COLOR PICKER` | `Select RGB color` |
|---|---|---|
| **Purpose** | Edit styled text color in-place | Pick a color value for any purpose |
| **Requires** | Input with "Allow Font/Color Picker" | Nothing (standalone) |
| **UI** | System floating panel (macOS) | Modal dialog |
| **Updates** | Applies directly to selected text | Returns Integer (0x00RRGGBB) |
| **Result** | No return value; changes input live | Returns selected color or -1 (cancel on Windows) |
| **Ref** | https://developer.4d.com/docs/commands/open-color-picker | https://developer.4d.com/docs/commands/select-rgb-color |

`Select RGB color` is a general-purpose modal color dialog (ref: above). It returns
an RGB Integer value and sets `OK` to 1/0. It does **not** require any input object
and can be used anywhere you need to let the user pick a color. On macOS, the dialog
can only be closed via the close box or Esc — `OK` is always 1 regardless.

## Drag and Drop

Reference: https://developer.4d.com/docs/Desktop/drag-and-drop

See form "Inputs" for a working example of custom picture drag and drop.

### Automatic vs. Custom

An input supports **automatic drag and drop** with no extra configuration: dragging selected text out of the object, or dropping text/a picture into it, works as a mouse-driven substitute for the Copy/Cut/Paste edit actions.

Automatic drag and drop works in three scenarios:

1. **Between two 4D objects** on the same form or different forms — text or picture is automatically transferred via the pasteboard on both sides.
2. **From an external application (including the desktop shell — Finder/Explorer) into 4D** — files, folders, text, or pictures are automatically retrieved on the destination side.
3. **From 4D to an external application** — text or picture is automatically set on the pasteboard.

**Limitation**: the source application may use **file promises** (to avoid blocking on large files) or **metadata-triggered scripts** (to generate data on demand). These lazy-evaluation mechanisms are **not handled** by 4D on the destination side — only concrete pasteboard data is retrieved.

Automatic drag and drop between two text inputs is a **move (cut), not a copy**. To **copy** instead, hold **Ctrl** (Windows) or **Option** (macOS) *after the drag has already started*.

Holding the modifier key from the **very start** switches the operation from automatic to **custom** drag and drop. In custom mode, 4D no longer performs the built-in text transfer; instead it dispatches `On Drag Over`/`On Drop` to the destination's method.

For full programmatic control, set `"dragging": "custom"` and/or `"dropping": "custom"` explicitly on the objects.

### Source (`On Begin Drag Over`)

Reference: https://developer.4d.com/docs/commands/set-drag-icon, https://developer.4d.com/docs/commands/append-data-to-pasteboard, https://developer.4d.com/docs/commands/set-text-to-pasteboard, https://developer.4d.com/docs/commands/set-picture-to-pasteboard, https://developer.4d.com/docs/commands/set-file-to-pasteboard

**Prerequisite**: if the input's data source is undefined or null, `On Begin Drag Over` will **not fire** — the drag gesture is silently ignored. The data source must have a value.

In the `On Begin Drag Over` handler, transfer data via the pasteboard:

- **`SET FILE TO PASTEBOARD`** — transfers a file/folder path (platform path). The preferred approach when the data originates from a file on disk
- **`SET TEXT TO PASTEBOARD`** / **`SET PICTURE TO PASTEBOARD`** — for text or picture data directly
- **`APPEND DATA TO PASTEBOARD`** — for custom/composite data types (identified by a UTI string, e.g. `"private.myapp.data"`)

By default, a ghost image of the data source is used as the drag icon. Customise with **`SET DRAG ICON`**:

```4d
// Source: drag a file reference with a thumbnail icon
Case of
  : ($event.code=On Begin Drag Over)
    var $file : 4D.File
    $file:=File("/RESOURCES/images/grid2x2.png")
    SET FILE TO PASTEBOARD($file.platformPath)

    var $icon : Picture
    CREATE THUMBNAIL(Form.src; $icon; 32; 32)
    SET DRAG ICON($icon)
End case
```

Note: `SET FILE TO PASTEBOARD` takes a **platform path** (hence `.platformPath`), not a 4D filesystem pathname.

### Destination (`On Drag Over` / `On Drop`)

Reference: https://developer.4d.com/docs/commands/get-file-from-pasteboard, https://developer.4d.com/docs/commands/is-picture-file, https://developer.4d.com/docs/commands/pasteboard-data-size, https://developer.4d.com/docs/commands/get-picture-from-pasteboard, https://developer.4d.com/docs/commands/get-text-from-pasteboard

**`On Drag Over`** fires continuously while the drag hovers over the destination. The method must return a value to accept or reject:

- **Return `0`** — accept the drop (cursor shows accept indicator)
- **Return `-1`** — reject the drop (cursor shows reject indicator)

When the pasteboard contains files, use **`Get file from pasteboard($i)`** to iterate (1-based index, returns `""` when no more files). Validate each file before accepting — e.g. with **`Is picture file`** to check if the file is a supported image format. For non-file data, use `Pasteboard data size` to test for expected data types.

**Important**: do not use `TRACE` or any blocking call during `On Drag Over` — it fires continuously and a breakpoint will freeze the drag interaction. Use non-blocking measures (write to file, update a UI label) to debug.

**Note on `return` vs `$0`**: `return 0` exits the method immediately; `$0:=0` sets the return value but continues execution. If the handler is a subroutine, the return value must be propagated back to the object method itself.

Reference: https://developer.4d.com/docs/Concepts/control-flow#return-expression, https://developer.4d.com/docs/Concepts/parameters#return-expression

The mouse pointer automatically changes to accept/reject. **`SET CURSOR` is ignored** during both `On Drag Over` and `On Drop` — the system controls the cursor throughout the drag session.

**`On Drop`** fires only if `On Drag Over` previously accepted. Retrieve data from the pasteboard and process it:

```4d
// Destination: accept only picture files, load on drop
Case of
  : ($event.code=On Drag Over)
    var $i : Integer
    var $path : Text
    $i:=0
    Repeat
      $i+=1
      $path:=Get file from pasteboard($i)
      If (Is picture file($path))
        return 0  // accept — at least one picture file found
      End if
    Until ($path="")
    return -1  // reject — no picture files

  : ($event.code=On Drop)
    var $i : Integer
    var $path : Text
    $i:=0
    Repeat
      $i+=1
      $path:=Get file from pasteboard($i)
      If (Is picture file($path))
        var $image : Picture
        READ PICTURE FILE($path; $image)
        Form.dst:=$image
        return  // done — loaded first picture file
      End if
    Until ($path="")
End case
```

`Get file from pasteboard` returns **platform paths** — they can be passed directly to `READ PICTURE FILE` and other legacy file commands without conversion.

### Entry Filter Applies to Automatically Dropped Text

An automatic drop into a destination input with an `entryFilter` is filtered exactly like keyboard entry: only the characters that pass the filter make it into the destination, and any non-conforming characters are silently dropped. Confirmed with a source containing `"abc123"` dropped onto a destination with `entryFilter: "&9"` (digits only) — only `"123"` lands.

### `enterable: false` Alone Blocks Automatic Dropping

Setting `enterable: false` on a destination input is sufficient to block drops — `dropping: "none"` is unnecessary on top of it. A non-enterable object cannot receive any user-driven data entry, keyboard or drag-and-drop alike.

### Picture Drag Is a Copy, Not a Move

Dragging a picture between two picture-type inputs **copies** the picture rather than moving it — the source keeps its copy. This is the opposite of text drag (a move/cut).

### Drop Position

Reference: https://developer.4d.com/docs/commands/drop-position

If the exact position of the drop matters (e.g. inserting text at the cursor position in an input, or determining which row in a list box), use `Drop position` during `On Drop`. For a text-type input, it returns the character position (using the same inter-character position model as `GET HIGHLIGHT`) where the drop landed.

## Menu Bar Association

Reference: https://developer.4d.com/docs/FormEditor/menu, https://developer.4d.com/docs/commands/set-menu-bar, https://developer.4d.com/docs/Menus/sdi, https://developer.4d.com/docs/commands/open-form-window

A form can be associated with a **menu bar** through its properties. This association is critical for any form that contains input objects (or any active/editable objects), because the standard edit actions — **Copy, Paste, Cut, Undo, Redo** — are provided by the menu bar. If a form's window is frontmost but has no associated menu bar, or if the visible menu bar belongs to a *different* form, those edit actions silently do nothing. This is a common developer mistake.

### Why It Matters

When a form's window becomes frontmost, 4D activates the menu bar associated with **that form**. The menu bar's Edit menu provides the standard edit actions that text inputs depend on. Without an associated menu bar:

- **Cmd+C / Ctrl+C** (Copy), **Cmd+V / Ctrl+V** (Paste), **Cmd+X / Ctrl+X** (Cut) will not work
- **Cmd+Z / Ctrl+Z** (Undo), **Cmd+Shift+Z / Ctrl+Y** (Redo) will not work
- The context menu's Copy/Paste/Cut items will also fail if they rely on standard actions routed through the menu bar

**Rule**: if a form has input objects or any active objects, it **must** be associated with a menu bar that includes the Edit menu with standard actions.

### `SET MENU BAR` — Process-Level Menu Bar

Reference: https://developer.4d.com/docs/commands/set-menu-bar

`SET MENU BAR` associates a menu bar with the current **process**, not a specific form. This is useful when you need a menu bar visible even when no form window is open (e.g. when all windows are closed but the process is still running). However, this does **not** replace the form-level association — each form should still declare its own associated menu bar so that bringing that form's window to the front activates the correct menu bar.

### SDI Mode (Windows)

Reference: https://developer.4d.com/docs/Menus/sdi

On Windows, 4D can run in **SDI (Single Document Interface)** mode where each window is independent and has its own menu bar. In this mode, each form window carries its own menu bar rather than sharing a single application-level menu bar. The form-level menu bar association becomes even more important in SDI mode — each form must declare which menu bar it uses.

### Hidden Menu Bar

Reference: https://developer.4d.com/docs/commands/open-form-window

It is possible to open a form window with the menu bar **hidden** (e.g. for a floating palette or utility window). The hidden menu bar still functions — keyboard shortcuts for Copy/Paste/Cut/Undo/Redo still work — but the form must still have an associated menu bar for those actions to be routed correctly. Hiding the menu bar is a display choice, not a functional disconnection.

## Input Alternatives

The overview page notes several cases where a different object type is a better fit than a plain input:

- List-type data in a selection-type List Box column, instead of a field/variable input
- Drop-down List or Combo Box, for representing a list field/variable with a closed or semi-open set of choices
- Check Box or Radio Button, for a boolean expression

## Visual Display Properties

Reference: https://developer.4d.com/docs/FormObjects/propertiesBackgroundAndBorder, https://developer.4d.com/docs/FormObjects/propertiesAppearance

See form "InputStyles" for a comprehensive showcase.

### Border Style (`borderStyle`)

All seven values render correctly in both the Form Editor and `FORM SCREENSHOT`:

| Value | Visual effect |
|-------|--------------|
| `"none"` | No visible border — blends into the form background |
| `"system"` | Platform-native field border (macOS: light inset bezel) |
| `"solid"` | Thin single-line black border |
| `"dotted"` | Thin dotted border |
| `"raised"` | 3D raised/embossed effect (lighter top-left, darker bottom-right) |
| `"sunken"` | 3D sunken/inset effect (opposite of raised) |
| `"double"` | Double-line border |

### Corner Radius (`borderRadius`)

Rounds the corners of the input's border **and** background fill. Only meaningful when `borderStyle` is `"solid"` (other styles ignore or clip oddly). Setting the radius to half the object height creates a "pill" shape — e.g. `height: 22` + `borderRadius: 11`.

**Important:** The JSON key is `borderRadius`, not `cornerRadius`. Using `cornerRadius` is silently ignored (unrecognized key).

### Background Color (`fill`) and Text Color (`stroke`)

Both accept any CSS color value: named colors (`"red"`), hex (`"#2980B9"`), or `"transparent"`.

- `fill` — the object's background color (CSS equivalent: `background-color`)
- `stroke` — the text/foreground color (CSS equivalent: `color`)

Both are honored in the `FORM SCREENSHOT` static template. Combined with `borderRadius`, they allow creating "tag" or "badge" style inputs:

```json
{
  "type": "input",
  "borderStyle": "solid",
  "borderRadius": 12,
  "stroke": "#27AE60",
  "fill": "#EAFAF1",
  "fontWeight": "bold",
  "textAlign": "center"
}
```

### Font Properties

| JSON Key | Effect | Static template |
|----------|--------|-----------------|
| `fontFamily` | Font face — system fonts or `"%password"` pseudo-font | ✓ rendered |
| `fontSize` | Point size | ✓ rendered |
| `fontWeight` | `"bold"` or `"normal"` | ✓ rendered |
| `fontStyle` | `"italic"` or `"normal"` | ✓ rendered |
| `textDecoration` | `"underline"` or `"none"` | ✓ rendered |

All font properties are correctly rendered by `FORM SCREENSHOT`. They can be combined freely (bold+italic, bold+underline, etc.).

### Text Alignment (`textAlign`)

`"left"`, `"center"`, `"right"`, `"justify"`, `"automatic"` — all render correctly in the static template.

### Static Template Behavior for Display Properties

`FORM SCREENSHOT` renders **all visual styling properties** (borders, colors, fonts, alignment, corner radius) accurately. What it does NOT render is **runtime data** — the `dataSource` expression text is shown literally rather than evaluated. So a styled input with `"dataSource": "Current date:C33"` will display the text `Current date` in the specified font/color/border, not the actual date value.

This means `FORM SCREENSHOT` is a reliable tool for verifying:
- ✓ Layout and spacing
- ✓ Border styles and radii
- ✓ Color schemes (fill + stroke)
- ✓ Font choices, sizes, and styles
- ✓ Text alignment
- ✗ Runtime values, format results, or conditional logic

## CLI Verification Notes

`FORM SCREENSHOT` renders the Form Editor's static template. For an input with a `dataSource`, the template renders the **literal `dataSource` expression text** as a placeholder label -- the same rule already established for drop-down list, combo box, and tab control. This holds for **every** expression type tested, including `picture` and `boolean`: a picture-type input with `dataSourceTypeHint: "picture"` shows the literal text `Form.pic1`, not the actual image content and not a blank frame -- a contrast with the static Picture object and Picture Pop-up Menu, both of which render real image content (frame 0) in their static templates regardless of data source. This is because those two object types own their appearance directly from a `picture` source property, whereas an input's appearance is always driven through its `dataSource` expression, textual placeholder included.

`enterable: false` and a `choiceList` array produce **no visible difference** from a plain enterable text input in the static template -- both the disabled-entry affordance and the pop-up-list affordance are runtime-only behaviors not reflected in the design-time render. `fill` is honored visually (background tint) in the static template. The property named "Corner radius" in the property list is **`borderRadius`** in JSON, not `cornerRadius` -- setting `cornerRadius: 10` has **no effect at all** (unrecognized key, silently ignored, corners stay square), while `borderRadius: 10` renders correctly rounded. Confirmed by zoomed pixel inspection of the rendered PNG: square corners with `cornerRadius`, rounded corners with `borderRadius`.

## Comparison with Drop-down List / Combo Box

| Feature | Input | Drop-down List | Combo Box |
|---------|-------|----------------|-----------|
| Expression types supported | Text, Date, Time, Number, Boolean, Picture, Object | Object, array, or list (choice-list) shapes only | Object, array, or plain choice list |
| Free-text entry | Yes (unless constrained by filter/format) | No -- closed list only | Yes, plus optional choice list |
| `choiceList` | Yes (turns it into a constrained pop-up while remaining `type: "input"`) | Yes (its primary mechanism) | Yes |
| Picture display | Yes (`dataSourceTypeHint: "picture"`, dedicated `pictureFormat` values) | No | No |
| Multiline text | Yes | No | No |
| CLI static template rendering | Literal `dataSource` text, for every expression type including picture | Literal `dataSource` text | Literal `dataSource` text |
