---
object: "button"
json_type: "button"
keywords: ["button", "bevel", "roundedBevel", "gradientBevel", "texturedBevel", "office", "help style", "circular", "defaultButton", "keyboard shortcut", "popup placement", "focusable", "tooltip", "icon", "textPlacement"]
summary: "Button object: all 11 styles, visual/text properties, defaultButton, shortcuts, popup placement, sizing caveats, icon+text layout."
---

# 4D Button Object

Reference: https://developer.4d.com/docs/FormObjects/buttonOverview

## Basic Definition

```json
{
  "MyButton": {
    "type": "button",
    "text": "Click Me",
    "top": 20,
    "left": 20,
    "width": 146,
    "height": 24,
    "events": ["onClick"]
  }
}
```

The object name is the JSON key (e.g., `"MyButton"`). This name is used:
- As the filename for the object method (`ObjectMethods/MyButton.4dm`)
- As the CSS ID selector (`#MyButton { ... }`)
- In code with `FORM Event.objectName`

## Button Styles

Set via the `style` property. Each style has a distinct visual appearance.

| Style | Description |
|-------|-------------|
| `regular` | **(default)** Native macOS/Windows system button. Rounded with light gray background. |
| `flat` | Clean rectangle with thin border and rounded corners. Minimalist. |
| `toolbar` | Transparent background, no border. Appears as plain text until hovered. Designed for toolbars. |
| `bevel` | Rectangular with thin border, square corners. |
| `roundedBevel` | Like bevel but with rounded corners. |
| `gradientBevel` | Rounded with subtle gradient fill. |
| `texturedBevel` | Gray textured background, no visible border. |
| `office` | Light blue background with thin border. |
| `help` | Circular "?" icon. **Ignores the `text` property entirely.** |
| `circular` | Circular outline with text displayed below. |
| `custom` | No visible chrome. Designed for use with `customBackgroundPicture`. |

### Style-Specific Constraints

- **`defaultButton`** is only available for `regular` and `flat` styles.
- **`customBackgroundPicture`**, **`customBorderX`**, **`customBorderY`**, **`customOffset`** are only for `custom` style.
- **`popupPlacement`** works with `toolbar`, `bevel`, `roundedBevel`, `gradientBevel`, `texturedBevel`, `office` styles.

## Visual Properties

### Text and Font

| Property | Values | Description |
|----------|--------|-------------|
| `text` | string | Button label text |
| `textAlign` | `"left"`, `"center"`, `"right"` | Text alignment within the button (since v20). Also settable via `OBJECT SET HORIZONTAL ALIGNMENT`. |
| `fontWeight` | `"normal"`, `"bold"` | Font weight |
| `fontStyle` | `"normal"`, `"italic"` | Font style |
| `textDecoration` | `"none"`, `"underline"` | Text decoration |
| `fontSize` | integer | Font size in points |
| `fontFamily` | string | Font family name (e.g., `"Courier New"`, `"Georgia"`) |
| `stroke` | CSS color | **Text color**. Also affects border color on `flat`-style buttons. Works on all styles. |

All font properties can be combined (bold + italic + underline + custom size + custom font).
Font properties also combine naturally with icons — large `fontSize` scales text but not the icon.

### Appearance

| Property | Values | Description |
|----------|--------|-------------|
| `defaultButton` | boolean | Highlights as the recommended action. Only for `regular` and `flat`. |
| `borderStyle` | `"system"`, `"none"`, `"solid"`, `"dotted"`, `"raised"`, `"sunken"`, `"double"` | Border line style |
| `visibility` | `"visible"`, `"hidden"` | `"hidden"` = invisible **and inactive** (does not respond to clicks) |
| `display` | boolean | `false` = **not rendered but still active** (responds to clicks). Only for `custom` style. |
| `focusable` | boolean | Whether the button can receive keyboard focus (see below) |
| `tooltip` | string | Hover text displayed when the mouse rests over the button |

#### Tooltip Configuration

Tooltip display behavior is controlled globally at runtime via `SET DATABASE PARAMETER`:

| Selector | ID | Description |
|----------|-----|-------------|
| Tips enabled | 101 | Enable/disable tooltips |
| Tips delay | 102 | Delay before tooltip appears (ticks) |
| Tips duration | 103 | How long tooltip stays visible (ticks) |

Reference: https://developer.4d.com/docs/commands/set-database-parameter

#### `focusable` Behavior

Reference: https://developer.4d.com/docs/FormObjects/propertiesEntry#focusable

When **focusable is true** (default):
- Clicking the button **claims focus** from the current focus object (e.g., a text input)
- The previously focused object's edited text is **validated** (its data source is updated)
- The button in focus can be triggered by pressing the **space bar**
- Use `Focus object` to get the currently focused object name

When **focusable is false**:
- Clicking the button does **not** claim focus
- The current focus object (e.g., a text input being edited) **remains in edit mode**
- Useful for toolbar-style buttons that should not interrupt text entry

Related commands:
- https://developer.4d.com/docs/commands/focus-object
- https://developer.4d.com/docs/commands/get-edited-text
- https://developer.4d.com/docs/commands/object-get-data-source

#### `defaultButton` Behavior

- **`regular` + `defaultButton`**: blue background with white text (macOS accent). If an icon is present, it renders inside the blue button.
- **`flat` + `defaultButton`**: thick black border. If `stroke` is set, the stroke color is used for both text AND the thick border.

#### `borderStyle` Behavior by Style

- **`flat`**: respects all border styles clearly — `solid`, `raised`, `sunken`, `dotted`, `double` are all visually distinct.
- **`bevel`**: responds to border overrides. `"none"` removes the border entirely.
- **`regular`**: largely ignores border overrides (native capsule shape dominates). `"none"` shows dashed outline (like hidden).

### Icon and Popup

| Property | Values | Description |
|----------|--------|-------------|
| `icon` | path | Path to icon image (e.g., `"/SOURCES/Forms/MyForm/icon.png"`) |
| `textPlacement` | `"left"`, `"right"`, `"top"`, `"bottom"`, `"center"` | Position of text **relative to the icon** |
| `iconFrames` | integer (min 1) | Number of frames in the icon image |
| `imageHugsTitle` | boolean | Whether icon stays close to the text (see below) |
| `popupPlacement` | `"none"`, `"linked"`, `"separated"` | Popup menu indicator (see below) |

#### `textPlacement` Details

- `"right"`: icon on the left, text on the right
- `"left"`: text on the left, icon on the right
- `"top"`: text above, icon below (vertical stacking)
- `"bottom"`: icon above, text below (vertical stacking)
- `"center"`: icon and text overlap in the center

Icons work with all button styles. The `regular` style renders the icon inside its native capsule shape.

#### `imageHugsTitle` Details

Controls how icon and text are positioned within the button area:

- **`false` (default)**: icon is anchored to the edge of the button. Text is centered independently. On wide buttons, icon and text appear far apart.
- **`true`**: icon and text move together as a unit, staying close to each other regardless of button width.

Best demonstrated on wide buttons where the difference is clearly visible.

#### `popupPlacement` Details

- **`"none"` (default)**: no popup menu.
- **`"linked"`**: small triangle indicator in the bottom-right corner. The entire button triggers the popup.
- **`"separated"`**: vertical divider line creating a separate clickable triangle zone on the right. The main button area and the popup trigger are independent click targets.

Works with `toolbar`, `bevel`, `roundedBevel`, `gradientBevel`, `texturedBevel`, `office` styles. Combines with icons — the icon, text, and popup triangle all coexist.

**Important**: The `popupPlacement` property only defines the visual representation. No popup menu is displayed by default — you must implement it in the object method.

#### Popup Event Behavior

| Mode | Main button area | Triangle zone |
|------|-----------------|---------------|
| `"linked"` | `On Alternative Click` (mouse **down**) | `On Alternative Click` (mouse **down**) |
| `"separated"` | `On Clicked` / `On Double Clicked` / `On Long Click` (mouse **up**) | `On Alternative Click` (mouse **down**) |

- With **`"linked"`**: `On Clicked`, `On Double Clicked`, and `On Long Click` are **never fired** because every click triggers `On Alternative Click` on mouse down.
- With **`"separated"`**: both regular click events and popup events work independently.

#### Popup Menu Implementation Pattern

```4d
Case of 
  : (FORM Event.code=On Alternative Click)

    var $menu : Text
    $menu:=Create menu
    APPEND MENU ITEM($menu; "Item 1")
    SET MENU ITEM PARAMETER($menu; -1; "one")
    APPEND MENU ITEM($menu; "Item 2")
    SET MENU ITEM PARAMETER($menu; -1; "two")
    var $parameter : Text
    $parameter:=Dynamic pop up menu($menu)
    RELEASE MENU($menu)

    Case of 
      : ($parameter="")
        // no item selected (dismissed)
      : ($parameter="one")
        // handle item 1
      : ($parameter="two")
        // handle item 2
    End case

End case
```

Key commands:
- `Create menu` — creates an empty menu
- `APPEND MENU ITEM` — adds an item
- `SET MENU ITEM PARAMETER` — assigns a string identifier to the last added item (`-1` = last item)
- `Dynamic pop up menu` — **(preferred)** displays the menu, returns the selected item's parameter (empty string if dismissed)
- `RELEASE MENU` — frees the menu resource

Reference: https://developer.4d.com/docs/commands/dynamic-pop-up-menu

#### Legacy `Pop up menu` Command

The older `Pop up menu` command takes a semicolon-delimited string and returns an integer index:

```4d
var $item : Integer
$item:=Pop up menu("Item 1;Item 2;Item 3")
// $item = 0 (dismissed), 1, 2, or 3
```

Reference: https://developer.4d.com/docs/commands/pop-up-menu

Prefer `Dynamic pop up menu` for new code — it's more flexible and identifies items by parameter strings rather than fragile index positions.

#### `On Long Click` as Popup Trigger

`On Long Click` can also be used to display a popup menu, triggered when the user presses and holds the button. This works with **separated** popup buttons (where the main area handles regular clicks) or with any button style.

Reference: https://developer.4d.com/docs/Events/onLongClick

### Special Style Notes

#### `help` Style

- Always renders as a circular "?" button.
- The `text` property is **completely ignored**.
- Scales the circle to fit the smaller of `width`/`height`.
- The question mark appearance is fixed and cannot be customized.

#### `circular` Style

- Renders a circular outline with text displayed **below** the circle.
- If an `icon` is provided, it replaces the circle content.
- `stroke` colors the text below but not the circle outline.
- `fontWeight` and other font properties apply to the text below the circle.

### Custom Style Properties

Only applicable when `style` is `"custom"`:

| Property | Description |
|----------|-------------|
| `customBackgroundPicture` | Path to background image |
| `customBorderX` | Horizontal internal margin (pixels) |
| `customBorderY` | Vertical internal margin (pixels) |
| `customOffset` | Icon offset (pixels) |

A `custom` button with `"display": false` creates an **invisible but active clickable area**. This is useful for defining clickable regions over a graphic element or background image.

Reference: https://developer.4d.com/docs/FormObjects/propertiesDisplay#not-rendered

### Visibility vs Display (Active State)

| State | Visible | Active (responds to clicks) |
|-------|---------|----------------------------|
| Normal (`visibility: "visible"`) | ✓ | ✓ |
| Hidden (`visibility: "hidden"`) | ✗ | ✗ |
| Not rendered (`display: false`, custom style) | ✗ | ✓ |

- Use `OBJECT SET VISIBLE` to hide/show at runtime (also makes inactive).
- Reference: https://developer.4d.com/docs/commands/object-set-visible

## Positioning and Sizing

| Property | Type | Description |
|----------|------|-------------|
| `top` | integer | **Required**. Y position from form top |
| `left` | integer | **Required**. X position from form left |
| `width` | integer | Button width |
| `height` | integer | Button height |
| `bottom` | integer | Bottom position |
| `right` | integer | Right position |
| `sizingX` | enum | `"move"`, `"grow"`, `"fixed"` — horizontal behavior on form resize |
| `sizingY` | enum | `"move"`, `"grow"`, `"fixed"` — vertical behavior on form resize |

### Sizing Behavior on Non-Visible Pages

- **Regular objects** (buttons, inputs, etc.) on page 2+ still receive window resize events and grow/move accordingly, even when the page is not visible. When the user switches to that page, objects are already in the correct position.
- **Subform containers (widgets)** on page 2+ are **not instantiated** until the page is shown, so they do **not** receive resize events while hidden. This can cause widgets to appear out of sync with regular objects after a window resize.
- In **nested subforms**: regular objects on page 2+ of a subform still receive resize events when the parent container is resized.

## Keyboard Shortcut

A button can have a keyboard shortcut that triggers its click event.

| Property | Type | Description |
|----------|------|-------------|
| `shortcutKey` | string | The key character (e.g., `"c"`, `"f"`) |
| `shortcutAccel` | boolean | ⌘ Command on Mac / Ctrl on Windows (the platform accelerator) |
| `shortcutShift` | boolean | Shift modifier |
| `shortcutAlt` | boolean | ⌥ Option on Mac / Alt on Windows |
| `shortcutControl` | boolean | ⌃ Control (Mac-specific) |

Example — ⌘C triggers the button:

```json
{
  "shortcutKey": "c",
  "shortcutAccel": true,
  "shortcutShift": false,
  "shortcutAlt": false,
  "shortcutControl": false
}
```

**Important**: A button shortcut **overrides the keyboard shortcut** for system commands (e.g., ⌘C overrides Copy via keyboard) but does **not** override the Edit menu item. Be cautious about assigning shortcuts that conflict with standard system shortcuts.

## Events

The most important event for a button is **`onClick`** (On Clicked).

- `onClick` fires on **mouse up** (while the cursor is still hovering over the button).
- If the user presses and drags away before releasing, the event does **not** fire.
- The `onClick` event does **not** require the form to also subscribe to `onClick` — it works independently at the object level (unlike `onLoad`/`onUnload`).

### Event Execution Order

When a button is clicked:

1. **Object method** runs first
2. **Form method** runs second
3. **Standard action** runs last

### Click Events in Detail

#### Single and Double Click

- `onClick` (On Clicked) fires on every click.
- `onDoubleClick` (On Double Clicked) fires on the 2nd rapid click **instead of** `onClick` — the click event is consumed/replaced.
- After the double-click, subsequent rapid clicks fire only `onClick` with incrementing `Clickcount`.

Example: 10 rapid clicks produces:

```
On Clicked (Clickcount=1)
On Double Clicked (Clickcount=2, replaces On Clicked)
On Clicked (Clickcount=3)
On Clicked (Clickcount=4)
...
On Clicked (Clickcount=10)
```

#### Clickcount

`Clickcount` (command #1332) returns how many clicks have occurred in a rapid sequence. It keeps incrementing as long as clicks are rapid enough (governed by the system double-click interval). It resets when the user pauses.

Reference: https://developer.4d.com/docs/commands/clickcount

#### Modifier Keys

Detect modifier keys during a click using these commands. Despite platform-specific names, they work **cross-platform**:

| Command | Mac Key | Windows Key |
|---------|---------|-------------|
| `Shift down` | Shift | Shift |
| `Macintosh command down` | ⌘ Command | Ctrl |
| `Macintosh option down` | ⌥ Option | Alt |
| `Macintosh control down` | ⌃ Control | — |
| `Windows Ctrl down` | ⌘ Command | Ctrl |
| `Windows Alt down` | ⌥ Option | Alt |
| `Caps lock down` | Caps Lock | Caps Lock |
| `Contextual click` | Ctrl+click / right-click | Right-click |

References:
- https://developer.4d.com/docs/commands/shift-down
- https://developer.4d.com/docs/commands/macintosh-command-down
- https://developer.4d.com/docs/commands/macintosh-option-down
- https://developer.4d.com/docs/commands/macintosh-control-down
- https://developer.4d.com/docs/commands/windows-ctrl-down
- https://developer.4d.com/docs/commands/windows-alt-down
- https://developer.4d.com/docs/commands/caps-lock-down

#### Recommended Pattern

Test modifiers in a `Case of` with priority ordering — the first match wins:

```4d
var $event:=FORM Event

Case of 
  : (FORM Event.code=On Double Clicked)
    // double-click action

  : ((FORM Event.code=On Clicked) && Contextual click)
    // right-click / Ctrl+click

  : ((FORM Event.code=On Clicked) && Shift down)
    // Shift+click

  : ((FORM Event.code=On Clicked) && Macintosh command down)
    // ⌘+click (Mac) / Ctrl+click (Win)

  : ((FORM Event.code=On Clicked) && Macintosh option down)
    // ⌥+click (Mac) / Alt+click (Win)

  : (FORM Event.code=On Clicked)
    // plain click (fallback)

End case 
```

### Object Method File

The object method file is at `ObjectMethods/<ObjectName>.4dm`.

## Data Source

A button's data source can be an **integer** or **boolean**.

- The value becomes **1** (or `True`) when the button is pressed.
- It returns to **0** (or `False`) after the event cycle completes.
- **During the `onClick` event**, the value is still **1** — it resets after the event methods finish.

### Important Exception

Unlike most form objects, a button can only use a **variable** as its data source (not a `Form.property` expression).

**Recommended**: use a form local (dynamic) variable rather than a process variable. The scope and lifecycle of a dynamic variable matches the form.

```json
{
  "MyButton": {
    "type": "button",
    "dataSource": "myButton",
    "top": 20,
    "left": 20,
    "width": 146,
    "height": 24
  }
}
```

To read the value in code:

```4d
// Get pointer to the button's data source variable
OBJECT Get pointer(Object named; FORM Event.objectName)->
// Returns 1 during onClick, 0 otherwise
```

## Standard Actions

Buttons can have a `action` property for built-in behaviors (e.g., `"accept"`, `"cancel"`, `"gotoPage"`).

Reference: https://developer.4d.com/docs/FormObjects/propertiesAction#standard-action

A button can have **both** a method and a standard action. The method runs first, then the standard action. This allows code to conditionally modify or block the built-in behavior.

### `gotoPage?value=N`: Fixed-Page Jump Button

Unlike a multi-value object (drop-down list, tab control, button grid, picture pop-up menu -- see `tab.md`), where `action: "gotoPage"` alone auto-populates a submenu/selection with one entry per form page and the *clicked item's own position* supplies the target page number, a **button** is a single fixed control with no "position" of its own -- so its `action` must instead carry the target page **explicitly** as a parameter, using the standard action's URL-like syntax (see https://developer.4d.com/docs/Desktop/standard-actions): `"action": "gotoPage?value=2"` always jumps to page 2, regardless of anything else on the form. This is the general pattern for any parameterized standard action, not unique to page navigation (e.g. `"backgroundColor?value=red"`).

```json
{
  "type": "button",
  "text": "Page 2",
  "action": "gotoPage?value=2"
}
```

This makes a button on **page 0** (always visible, see `tab.md`'s page-0 navigation pattern) a simple, code-free way to add one-off "jump to page N" controls -- e.g. "Home"/"Back to page 1" buttons -- alongside or instead of a full multi-value nav tab/dropdown, with no method required.

The same parameterized action string can be triggered from code instead of a click, via `INVOKE ACTION` (https://developer.4d.com/docs/commands/invoke-action): `INVOKE ACTION("gotoPage?value=3")` runs the identical standard action programmatically in the current form (pass `ak main form` as the second parameter to target the frontmost document/dialog form instead). This is the recommended way to drive standard-action-based navigation from a form method while keeping any bound multi-value object's displayed selection in sync (see the one-directional-binding caveat in `dropdown.md`), rather than calling `FORM GOTO PAGE` directly.



Button properties can be set via CSS stylesheets.

```css
/* All buttons */
button {
  style: flat;
  text: "Default Label";
}

/* Buttons with class "primary" */
.primary {
  stroke: #FFFFFF;
  fontWeight: bold;
}

/* A specific button by name */
#SubmitButton {
  text: "Submit";
  defaultButton: true;
}

/* Light/dark mode */
@media (prefers-color-scheme: light) {
  button { stroke: #000080; }
}
@media (prefers-color-scheme: dark) {
  button { stroke: #7FFFD4; }
}
```

CSS property names match the JSON property names. Specificity follows the standard cascade: type < class < name/ID < JSON < `!important`.

CSS values can use `:xliff:` references for localization:

```css
button {
  text: ":xliff:ButtonClick";
}
```

Reference: https://developer.4d.com/docs/FormEditor/stylesheets

## Localization

Button labels can be localized using XLIFF. Set the `text` property (in JSON or CSS) to a `:xliff:` reference:

```json
{ "text": ":xliff:ButtonClick" }
```

Then create XLIFF files in `Resources/{lang}.lproj/`:

```xml
<trans-unit id="ButtonClick" resname="ButtonClick">
  <source>Click</source>
  <target>クリック</target>
</trans-unit>
```

4D resolves the reference at runtime based on the application language.

## Runtime Commands

Button properties can be modified at runtime via `OBJECT SET *` commands.

### Applicable to Buttons

| Command | Description |
|---------|-------------|
| `OBJECT SET ENABLED` | Enable/disable the button |
| `OBJECT SET FONT` | Change the font |
| `OBJECT SET TITLE` | Change the button label |
| `OBJECT SET FORMAT` | Change the button label **and/or icon** |
| `OBJECT SET ACTION` | Change the standard action |
| `OBJECT SET VISIBLE` | Show/hide the button |

References:
- https://developer.4d.com/docs/commands/object-set-enabled
- https://developer.4d.com/docs/commands/object-set-title
- https://developer.4d.com/docs/commands/object-set-format
- https://developer.4d.com/docs/commands/object-set-font
- https://developer.4d.com/docs/commands/object-set-action

### Not Applicable to Buttons

| Command | Reason |
|---------|--------|
| `OBJECT SET ENTERABLE` | Buttons are not enterable |
| `OBJECT SET CORNER RADIUS` | Not supported for buttons |
| `OBJECT SET FILTER` | Buttons have no input filter |

References:
- https://developer.4d.com/docs/commands/object-set-enterable
- https://developer.4d.com/docs/commands/object-set-corner-radius
- https://developer.4d.com/docs/commands/object-set-filter
