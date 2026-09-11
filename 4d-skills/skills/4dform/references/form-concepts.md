---
object: "form"
json_type: null
keywords: ["form", "project form", "table form", "subform", "page", "windowTitle", "windowSizingX", "windowSizingY", "margins", "onLoad", "onUnload", "formClass", "file structure", "4DForm"]
summary: "Form-level concepts: project/table/subform types, file/directory structure, window & page properties, form-level events, form classes."
---

# 4D Form Concepts

## What is a Form

A Form is the basic unit of user interface definition in 4D. Forms are defined in JSON (file extension `.4DForm`).

- **Project form**: not associated with any data table.
- **Table form**: associated with a specific data table.
- **Subform**: a form embedded in another form (like an iframe in HTML). Subforms create a local coordinate system within their container. Subforms can themselves contain subforms.

Reference: https://developer.4d.com/docs/FormEditor/forms
JSON schema: https://developer.4d.com/docs/FormEditor/jsonReference

## File Structure

### Project Forms

```
Project/Sources/Forms/<FormName>/form.4DForm
```

Each form gets its own folder. The folder name **is** the form name. Naming is arbitrary but subject to filesystem constraints (unique within scope, no special characters).

### Table Forms

```
Project/Sources/TableForms/<TableNumber>/<FormName>/form.4DForm
```

Table forms are organized by **table number** (not table name). The table number is defined in `catalog.4DCatalog`.

### Methods

- **Form method**: `Forms/<FormName>/method.4dm`
- **Object methods**: `Forms/<FormName>/ObjectMethods/<ObjectName>.4dm`

### Example Directory Layout

```
Project/
  Sources/
    Forms/
      MyProjectForm/
        form.4DForm
        method.4dm
        ObjectMethods/
          Button.4dm
    TableForms/
      1/
        Input/
          form.4DForm
        Output/
          form.4DForm
    styleSheets.css
    styleSheets_mac.css
    styleSheets_windows.css
```

## Minimal Form JSON

Every form must have:

- `$4d` metadata (`version`, `kind`)
- Window sizing properties
- At least one event in the `events` array (typically `onLoad`)
- A `destination` value
- A `pages` array with at least 2 entries (page 0 and page 1)

```json
{
  "$4d": {
    "version": "1",
    "kind": "form"
  },
  "windowSizingX": "variable",
  "windowSizingY": "variable",
  "windowMinWidth": 0,
  "windowMinHeight": 0,
  "windowMaxWidth": 32767,
  "windowMaxHeight": 32767,
  "rightMargin": 20,
  "bottomMargin": 20,
  "events": ["onLoad", "onUnload"],
  "windowTitle": "window title",
  "destination": "detailScreen",
  "pages": [
    { "objects": {} },
    { "objects": {} }
  ]
}
```

### Key Properties

| Property | Description |
|----------|-------------|
| `$4d` | Metadata: `version` and `kind` (always `"form"`) |
| `windowSizingX/Y` | `"fixed"` or `"variable"` |
| `windowMinWidth/Height` | Minimum window dimensions |
| `windowMaxWidth/Height` | Maximum window dimensions (32767 = effectively unlimited) |
| `rightMargin` / `bottomMargin` | Define form size relative to rightmost/bottommost object |
| `width` / `height` | Explicit form size (alternative to margins) |
| `destination` | `"detailScreen"`, `"listScreen"`, `"detailPrinter"`, `"listPrinter"` |
| `geometryStamp` | Incremented by the form editor on each save |
| `method` | Path to the form method (e.g., `"method.4dm"`). **Required** to actually bind it -- creating a `method.4dm` file at the conventional path and declaring the top-level `events` array (`onLoad`/`onUnload`) is not enough; without this explicit property the file is never invoked, `On Load`/`On Unload` never fire, and any initialization code inside it is silently dead |

### Destination

- **`detailScreen`**: a detail form for screen display (used for both project forms and table input forms).
- **`listScreen`**: a list form for screen display (used for table output forms). Includes markers (`markerHeader`, `markerBody`) to define header/body row heights.

## Pages

The `pages` array defines logical rendering layers.

- **Index 0 = Page 0**: objects here are **always visible** regardless of which page is displayed.
- **Index 1+ = Pages 1, 2, ...**: only the active page's objects are rendered.

Each page contains an `objects` map (keyed by object name) and an optional `entryOrder` array.

```json
"pages": [
  {
    "objects": { }
  },
  {
    "objects": {
      "Button": {
        "type": "button",
        "text": "Click Me",
        "top": 20,
        "left": 20,
        "width": 146,
        "height": 24
      }
    }
  }
]
```

## Entry Order (Tab/Focus Order)

Reference: https://developer.4d.com/docs/FormEditor/overview#data-entry-order

The **entry order** determines how Tab and Return keys cycle focus among objects. It is independent of the rendering/layering order (which is determined by JSON object declaration order within `"objects"`).

### Default Entry Order

If no explicit entry order is defined, the default order is based on the **z-order** (layering) of objects — i.e. the order they appear in the JSON `"objects"` map. Objects declared first (bottom of the stack) come first in the default entry order.

### JSON `entryOrder` Property

Each page can declare an `entryOrder` array to explicitly control which objects participate in the tab cycle and in what order:

```json
{
  "objects": {
    "Input": { ... },
    "Input1": { ... },
    "Input2": { ... },
    "Input3": { ... },
    "Input4": { ... }
  },
  "entryOrder": [
    "Input",
    "Input3"
  ]
}
```

**Key rules:**
- Only objects listed in `entryOrder` participate in the Tab/Return cycle
- Objects NOT listed are **excluded** from the keyboard navigation cycle — they can still be focused programmatically via `GOTO OBJECT` or by clicking, but Tab/Return will skip them
- The array order defines the cycle order
- Only focusable objects are valid entries (non-focusable objects are ignored)
- Page 0 objects and inherited form objects also participate in the entry order

### Runtime Commands

| Command | Purpose |
|---------|---------|
| `FORM SET ENTRY ORDER($names)` | Set entry order dynamically for current process |
| `FORM GET ENTRY ORDER($names)` | Get the defined entry order |
| `FORM GET ENTRY ORDER($names; *)` | Get the **actual** entry order (only valid/focusable objects) |
| `GOTO OBJECT(*; "objectName")` | Move focus to a specific object |
| `GOTO OBJECT(*; "")` | **Remove focus** from all objects (clear selection) |

Reference:
- https://developer.4d.com/docs/commands/form-set-entry-order
- https://developer.4d.com/docs/commands/form-get-entry-order
- https://developer.4d.com/docs/commands/goto-object

### Auto-Focus on Page Load

Auto-focus behavior differs between page 1 and subsequent pages:

- **Page 1** (initial form load): the first object in entry order (from page 0 or page 1) **automatically receives focus**.
- **Pages 2+** (page change): **no object receives focus by default**. You must call `GOTO OBJECT(*; "objectName")` explicitly if you want a specific object focused after a page switch.

To clear unwanted auto-focus on page 1, call `GOTO OBJECT(*; "")` in `On Load`.

### Tab Behavior from an Object Outside Entry Order

If the user clicks on an object that is **not** in the entry order (or has no entry order defined), pressing Tab or Shift+Tab will jump focus to the **first** object in the entry order. This is because the system has no "current position" in the order to advance from, so it starts from the beginning.

### Entry Order vs. Rendering Order

| Concept | Determined by | Purpose |
|---------|---------------|---------|
| **Rendering order** (z-order/layering) | Declaration order in JSON `"objects"` map | Visual stacking (back-to-front) |
| **Entry order** (tab order) | `"entryOrder"` array, or default z-order | Keyboard focus cycling (Tab/Return) |

These are fully independent. An object can be at the front visually (last in `"objects"`) but first in entry order, and vice versa.

### `FORM SET ENTRY ORDER` Notes

- Ignores the **Tabbable** object property — only **focusable** matters
- Does **not** set the first focused object — use `GOTO OBJECT` in On Load for that
- Entry order within a subform is defined in the subform itself (call the command from the subform context)
- Invalid objects (non-existent, non-focusable, wrong page) are silently ignored

Forms subscribe to events via the `events` array. Only subscribed events will trigger a form event cycle.

Reference: https://developer.4d.com/docs/Events/overview

### Special Events: `onLoad` and `onUnload`

These two events are special **gate events**:

- `onLoad`: fires before the form is loaded. Used for initialization.
- `onUnload`: fires before the form is destroyed from memory. Used for cleanup.

**Critical rule**: Individual form objects can subscribe to `onLoad` or `onUnload`, but these events are **only processed for objects if the form itself also subscribes to them**. If an object needs `onLoad`, the form must have `onLoad` in its `events` array.

All other events (e.g., `onClick`) can be enabled independently at the object level — they do not require the form to also subscribe.

### The `FORM Event` Command

Use `FORM Event` (C1606) to get information about the current event. It returns an **object** with:

| Property | Type | Description |
|----------|------|-------------|
| `code` | integer | Numeric event ID (e.g., 4 = On Clicked) |
| `description` | text | Human-readable name (e.g., "On Clicked") |
| `objectName` | text | Name of the object that triggered the event. Absent when the event is triggered by the form itself. |

Additional context-specific properties may be included depending on the object type (e.g., `columnName` for list box header clicks).

Reference: https://developer.4d.com/docs/commands/form-event

**Note**: The older `Form event code` (C388) only returns the integer code. Always prefer `FORM Event` which is more informative.

**Type**: `FORM Event` returns a plain `Object` — do NOT type it as `cs.EventObject` or any `cs.*` class. There is no built-in event class in 4D's class system.

```4d
var $event : Object
$event:=FORM Event

Case of 
  : ($event.code=On Clicked)
    // $event.objectName contains the button name
    // $event.description is "On Clicked"
End case 
```

### Event Execution Order

When an event fires on an object:

1. **Object method** executes first
2. **Form method** executes second
3. **Standard action** executes last

This means code always runs before any built-in standard action, allowing you to conditionally modify or block the action.

### Event Cycle Architecture

The form event cycle is **atomic, sequential, and cooperative**:

- Form objects (spinners, barber shop progress, etc.) are visually updated between event cycles
- While a user holds a mouse button down on a clickable object (e.g., a button), the event cycle **waits** for the click to complete (mouse release). During this time:
  - Animations (spinner, barber shop) are **paused** — not frozen at the runtime level, but the event cycle cannot refresh the display
  - `On Timer` events cannot fire
  - Any data source updates made during an event handler are **deferred** — they do not invalidate and refresh the form immediately, only at the end of the event cycle
- This means a long-running `On Clicked` handler will freeze the form's visual updates until it completes

## Form Objects

Every form object has a `type` property and positioning via `top` and `left` (required).

### Common Properties (`objectCommon`)

| Property | Type | Description |
|----------|------|-------------|
| `top` | integer | **Required**. Y position |
| `left` | integer | **Required**. X position |
| `width` | integer | Object width |
| `height` | integer | Object height |
| `bottom` | integer | Bottom position |
| `right` | integer | Right position |
| `visibility` | enum | `"visible"`, `"hidden"`, `"selectedRows"`, `"unselectedRows"` |
| `sizingX` | enum | `"move"`, `"grow"`, `"fixed"` — horizontal resizing behavior |
| `sizingY` | enum | `"move"`, `"grow"`, `"fixed"` — vertical resizing behavior |
| `class` | string | CSS class name(s) for stylesheet selectors |

### Sizing on Non-Visible Pages

Regular objects on page 2+ receive resize events even when not visible, so they are in the correct position when the page is shown. **Subform containers (widgets)** on page 2+ are an exception — they are not instantiated until the page is shown, so they miss resize events and may appear misaligned after a window resize.

### Available Object Types

`text`, `input`, `button`, `checkbox`, `radio`, `dropdown`, `combo`, `groupBox`, `tab`, `line`, `rectangle`, `oval`, `picture`, `write`, `view`, `webArea`, `subform`, `listbox`, `plugin`, `splitter`, `progress`, `ruler`, `spinner`, `stepper`, `list`, `buttonGrid`, `pictureButton`, `picturePopup`

## Font Themes (Automatic Font)

Reference: https://developer.4d.com/docs/FormObjects/propertiesText#font-theme

Font themes (called "style sheets" in legacy documentation -- not to be confused with CSS) control the default font properties of form objects.

When no `fontFamily`, `fontSize`, or `fontTheme` is explicitly set, the default theme is `"normal"` (internal name `__automatic__`).

| Theme | Internal Name | Description |
|-------|---------------|-------------|
| `normal` | `__automatic__` | System default font. Adapts size to object height. |
| `main` | `__system__` | System main font (typically larger). |
| `additional` | `__systemMini__` | Smaller system font. |

The `"normal"` theme has a special behavior: **the system automatically reduces the font size** when the object height is too small for the normal font size. This is decided by the OS and applies to native controls like buttons, checkboxes, and radio buttons.

### Best Practice

For native controls (buttons, checkboxes, radio buttons), use the default `"normal"` theme without setting explicit font properties. This produces a professional, platform-native desktop appearance where the OS determines the appropriate font size for the object height.

### Height and Size Variants

Native controls (regular/flat styles) have system-defined size variants based on `height`:
- The height selects from discrete size variants (not smooth scaling)
- Both the control shape (bullseye, checkbox square, button capsule) and the font size adapt together
- Available variants are OS-dependent (may differ between macOS and Windows)

Reference: https://developer.4d.com/docs/commands/get-style-sheet-info

## Icons and Pictures for Form Objects

Reference: https://developer.4d.com/docs/FormObjects/propertiesTextAndPicture#number-of-states

Buttons, checkboxes, and radio buttons can display icons. The `custom` style (referred to as "3D button" in legacy documentation) is specifically designed for fully customized appearance using icons and/or background pictures, with developer control over offset and margins.

### Picture Locations

Images can be stored in two locations:

1. **Resources folder**: `"/RESOURCES/Images/myIcon.png"` -- shared across all forms in the project
2. **Adjacent to the form**: `"myIcon.png"` -- resolved relative to the form folder (e.g., `Forms/MyForm/myIcon.png`). Useful when the image should travel with the form.
3. **Variable**: `"var:myPictureVar"` -- loaded from a 4D picture variable at runtime

### Path Syntax Differences

The syntax differs between JSON properties and CSS:

**In JSON (.4DForm)** -- plain path string:
```json
{
  "icon": "/RESOURCES/Images/edit.png",
  "customBackgroundPicture": "/RESOURCES/Images/bg.png"
}
```

**In CSS** -- wrapped in `url()`:
```css
button {
  icon: url("/RESOURCES/Images/edit.png");
  customBackgroundPicture: url("/RESOURCES/Images/bg.png");
}
```

Adjacent (relative) paths also work:
```json
{ "icon": "edit.png" }
```
```css
button { icon: url("edit.png"); }
```

### Custom Style Properties

The `custom` style supports additional properties for appearance control:

| Property | Type | Description |
|----------|------|-------------|
| `icon` | string | Path to the icon image |
| `iconFrames` | number | Number of states in the icon (1-6) |
| `customBackgroundPicture` | string | Path to background image |
| `customBorderX` | number | Horizontal margin in pixels |
| `customBorderY` | number | Vertical margin in pixels |
| `customOffset` | number | Click offset in pixels (3D click effect) |

### Icon States (Multi-State Icons)

Reference: https://developer.4d.com/docs/FormObjects/propertiesTextAndPicture#number-of-states

Icons can have multiple states stacked vertically in a single image. It is the **designer's responsibility** to ensure the source image contains exactly the correct number of frames to match the object's `iconFrames` value. Mismatched frames will cause images to display incorrectly.

**Supported image formats**: PNG, JPEG, SVG (preferred). TIFF, BMP, GIF are also supported.

Reference: https://developer.4d.com/docs/Concepts/picture
Reference: https://developer.4d.com/docs/commands/picture-codec-list

### High-Resolution Images (Retina / HiDPI)

Reference: https://developer.4d.com/docs/FormEditor/pictures#scale-factor

For raster image formats (PNG, JPEG, etc.), supply high-resolution variants for Retina/HiDPI displays. 4D uses a naming convention with `@nx` suffix:

| File | Scale |
|------|-------|
| `icon.png` | 1x (standard) |
| `icon@2x.png` | 2x (Retina) |
| `icon@3x.png` | 3x (high-density) |

Place all variants in the same folder. 4D automatically selects the highest available resolution for the current display. SVG images scale natively and do not need `@nx` variants.

### Dark Mode Images

Reference: https://developer.4d.com/docs/FormEditor/pictures#dark-mode-pictures

4D automatically loads dark mode variants when the form uses the dark color scheme. The convention:

- Name the dark variant with a `_dark` suffix: `icon_dark.png`
- Store it next to the standard (light) version: `icon.png`

At runtime, 4D selects the light or dark image based on the form's current color scheme. This combines with the `@nx` convention: `icon_dark@2x.png` for high-resolution dark mode.

### CSS-Based Icon Switching

You can also use CSS media queries to switch icons based on platform or color scheme:

```css
@media (prefers-color-scheme: dark) {
  #myButton {
    icon: url("/RESOURCES/Images/icon_dark.png");
  }
}

@media (form-theme: fluent-ui) {
  #myButton {
    icon: url("/RESOURCES/Images/icon_fluent.png");
  }
}
```

This gives explicit control over which icon is used per platform/theme, as an alternative to the automatic `_dark` naming convention.

| Frames | States (buttons) | States (checkbox/radio) |
|--------|-------------------|-------------------------|
| 1 | Single image for all states | Single image for all states |
| 2 | Normal, Clicked | Unchecked, Checked |
| 3 | Normal, Clicked, Rollover | Unchecked, Checked, Rollover |
| 4 | Normal, Clicked, Rollover, Disabled | Unchecked, Checked, Rollover, Disabled |
| 5 | -- | Unchecked, Checked, True Rollover, False Rollover, Disabled |
| 6 | -- | Unchecked, Checked, True Rollover, False Rollover, True Disabled, False Disabled |

5 and 6-state icons are only available for checkboxes and radio buttons (since v20).

## CSS Stylesheets

4D supports CSS for styling form objects. This uses CSS **syntax** but is not the web CSS specification.

Reference: https://developer.4d.com/docs/FormEditor/stylesheets

### Specificity (lowest → highest)

1. Object **type** selector: `button { ... }`
2. Object **class** selector: `.myClass { ... }` (matches the object's `class` property)
3. Object **name/ID** selector: `#MyButton { ... }` (matches the object's JSON key name)
4. **JSON property** defined directly on the object (strongest)
5. `!important` declaration overrides the default priority

### System Stylesheets (always loaded)

```
/SOURCES/styleSheets.css
/SOURCES/styleSheets_mac.css
/SOURCES/styleSheets_windows.css
```

### Custom Stylesheets

Additional stylesheets can be loaded via the form's `css` property. They must use **file system paths** with reserved prefixes:

- `/DATA/`, `/LOGS/`, `/PACKAGE/`, `/PROJECT/`, `/RESOURCES/`, `/SOURCES/`

A CSS file adjacent to the `.4DForm` file can be referenced by filename only.

### Media Queries

```css
@media (form-theme: mac-classic) { }
@media (form-theme: win-classic) { }
@media (form-theme: fluent-ui) {
  @media (prefers-color-scheme: light) { }
  @media (prefers-color-scheme: dark) { }
}
@media (form-theme: liquid-glass) { }
```

| Theme | Minimum Version |
|-------|----------------|
| `fluent-ui` | 4D 21 R2 |
| `liquid-glass` | 4D 21 R3 |

### CSS Example

```css
button {
  text: "Click Me";
  style: flat;
}

@media (prefers-color-scheme: light) {
  button {
    stroke: #000080;
  }
}

@media (prefers-color-scheme: dark) {
  button {
    stroke: #7FFFD4;
  }
}
```

## Filesystem Paths: POSIX vs. Platform

Reference: https://developer.4d.com/docs/Concepts/paths#filesystem-pathnames, https://developer.4d.com/docs/commands/file, https://developer.4d.com/docs/API/FileClass

### 4D Filesystem Pathnames

4D defines virtual **filesystem pathnames** that map to project-relative folders. These are not real POSIX paths — they are 4D-specific aliases resolved at runtime:

| Filesystem | Designates |
|-----------|-----------|
| `/DATA` | Current data folder |
| `/LOGS` | Logs folder (inside data) |
| `/PACKAGE` | Project root folder |
| `/PROJECT` | Project folder |
| `/RESOURCES` | Current project resources folder |
| `/SOURCES` | Project sources folder |

These provide **OS independence** (no hardcoded platform paths) and **security** (sandboxed — code cannot access above the filesystem root).

### `File()` and `.platformPath`

`File()` and `Folder()` accept only **absolute pathnames** — either a filesystem pathname or a full platform path (with `fk platform path` constant). Relative paths are not accepted.

Many legacy commands (`READ PICTURE FILE`, `WRITE PICTURE FILE`, `DOCUMENT TO BLOB`, etc.) expect a **platform path** (macOS: `/Users/.../`, Windows: `C:\...`), not a filesystem pathname. The `File` object bridges the two:

```4d
var $file : 4D.File
$file:=File("/RESOURCES/Images/grid2x2.png")  // 4D filesystem pathname
READ PICTURE FILE($file.platformPath; $image) // .platformPath → native OS path
```

This is cleaner than manually building platform paths with `Get 4D folder` + `Folder separator`:

```4d
// Verbose legacy approach — avoid
READ PICTURE FILE(Get 4D folder(Current resources folder)+"Images"+Folder separator+"grid2x2.png"; $image)
```

**Key properties of `4D.File`:**

| Property | Returns | Use for |
|----------|---------|---------|
| `.path` | 4D filesystem path (`/RESOURCES/...`) | 4D API calls that accept filesystem paths |
| `.platformPath` | Native OS path (`/Users/.../` or `C:\...`) | Legacy commands expecting platform paths |
| `.name` | Filename with extension | Display, logging |
| `.exists` | Boolean | Guard before reading |

The same pattern applies to `Folder()` for directory references. Use `.file()` and `.folder()` on a folder object for **relative** navigation within a known root:

```4d
$folder:=Folder("/RESOURCES/Images")
$file:=$folder.file("grid2x2.png")  // relative path within the folder
```

## Data Sources

Interactive form objects can have an associated data source.

Reference: https://developer.4d.com/docs/FormObjects/propertiesDataSource

It is recommended to use **form local variables** (dynamic variables) rather than process variables, because the scope and lifecycle of a form local variable matches that of the form.

Reference: https://developer.4d.com/docs/FormObjects/propertiesObject#dynamic-variables

Use `OBJECT Get pointer` to dereference the dynamic variable data source of a form object.

Reference: https://developer.4d.com/docs/commands/object-get-pointer

## Form Class

Since 4D 20 R8, you can associate a user class with a form. This enables:
- **Auto-instantiation** of the class when the form loads
- **Auto-completion** — `Form.` suggests class properties/functions in the code editor
- **Syntax checking** — errors caught in real-time in both code editor and property list expressions
- **Compilation** — the compiler validates form expressions against the class

Reference: https://developer.4d.com/docs/FormEditor/propertiesForm#form-class
Blog: https://blog.4d.com/empower-your-development-process-with-your-forms/

### Defining a Form Class

Create a user class in `Sources/Classes/<ClassName>.4dm`:

```4d
property count : Integer

Class constructor
  This.count:=0

Function onClicked() : cs.MyFormController
  This.count+=1
  return This
```

Reference: https://developer.4d.com/docs/Concepts/classes

### Approach 1: By `formClass` Property

Set `"formClass": "MyFormController"` in the form JSON. 4D automatically creates an instance when the form loads. The `Form` command returns the class instance.

```json
{
  "formClass": "MyFormController",
  "events": ["onLoad", "onClick"]
}
```

The object method can then call class functions:

```4d
Form.onClicked()
```

### Approach 2: By Code

Explicitly instantiate the class and pass it to `DIALOG`:

```4d
var $form : cs.MyFormController
$form:=cs.MyFormController.new()
var $window : Integer
$window:=Open form window("MyFirstProjectForm")
DIALOG("MyFirstProjectForm"; $form)
// After dialog closes, $form still holds accumulated state
ALERT("You clicked "+String($form.count)+" times!")
```

Reference: https://developer.4d.com/docs/commands/dialog

### Precedence Rules

- **Object passed to `DIALOG`** takes precedence over the `formClass` property
- **`formClass` only** (no object passed) → 4D auto-instantiates the class
- **Neither** → `Form` returns a generic empty object

### Lifecycle

- With `formClass`: the instance is scoped to the form's lifetime. It is created on load and destroyed on unload.
- With `DIALOG($form)`: **you** control the lifecycle. The instance exists before and after `DIALOG`, so you can read its state after the form closes. It is cleared when the last reference to it goes out of scope.

### Property Declarations and Compiler Warnings

When a form uses `formClass`, the compiler checks that all `Form.propertyName`
accesses correspond to declared properties. Undeclared properties generate
**"Undeclared property 'xxx' used"** warnings.

Fix by adding `property` declarations to the class:
```4d
property txt1 : Text
property pic1 : Picture
property count : Integer

Class constructor
  This.count:=0
```

Reference: https://developer.4d.com/docs/Concepts/classes#property

## Variable Declarations

All local variables should be explicitly declared with `var`:
```4d
var $name : Text
var $count : Integer
var $list : Object
```

Undeclared variables generate **compilation errors** (not just warnings).
The syntax checker (`Compile project` with empty `targets`) catches these.

**Function return values**: If a function returns a value, you must capture it.
Calling a function as a procedure (ignoring the return value) generates an error:
```4d
// ERROR: "This function has been called as a procedure"
Get database parameter(User param value; $text)

// CORRECT: capture the return value
var $unused : Real
$unused:=Get database parameter(User param value; $text)
```

## Object Method Wiring

An object method file in `ObjectMethods/<ObjectName>.4dm` is **not automatically
connected** to its form object. You must set the `"method"` property in the
form JSON:

```json
{
  "MyButton": {
    "type": "button",
    "method": "ObjectMethods/MyButton.4dm",
    "events": ["onClick"]
  }
}
```

Without the `"method"` property, the `.4dm` file is orphaned and never invoked.
Similarly, without `"events"`, the method won't receive any events even if wired.

## Version Encoding

The `.4DProject` file's `compatibilityVersion` encodes the 4D version:

| Value | Version |
|-------|---------|
| `2101` | 21.1 |
| `2120` | 21 R2 |
| `2130` | 21 R3 |
| `2009` | 20.9 |
| `20A0` | 20 R10 |

A newer tool4d can safely run an older `compatibilityVersion` project (e.g. tool4d 21 R3 running a `2101` project). The reverse also works, but the project may use commands or features that do not yet exist in the older version.

## CLI Commands for Testing

See `98-tool4d-cli.md` for centralized CLI reference (version requirements, binary paths, `FORM SCREENSHOT` behavior).

### Screenshot (no CSS applied)

```bash
/Applications/4D\ 21\ R3/tool4d.app/Contents/MacOS/tool4d \
  --startup-method=project_form_to_image \
  --dataless \
  --project=<path>/example.4DProject \
  --user-param=<FormName>:<PageNumber>:<OutputPath.png>
```

### Print to PDF (CSS applied)

```bash
/Applications/4D\ 21\ R3/tool4d.app/Contents/MacOS/tool4d \
  --startup-method=print_form_to_file \
  --dataless \
  --project=<path>/example.4DProject \
  --user-param=<FormName>:<PageNumber>:<OutputPath.pdf>
```

Note: `FORM SCREENSHOT` does **not** apply CSS stylesheets. Use print form output to verify CSS styling.

## Application Settings

Application settings are stored in `Project/Sources/settings.4DSettings` (XML format).

Reference: https://developer.4d.com/docs/settings/overview

**Important**: Default values are NOT explicitly stored in the file. Only non-default settings appear. For example, Enter to accept and Escape to cancel are defaults that work without any explicit configuration.

### Keyboard Shortcuts (Accept / Cancel)

The settings file can define application-wide keyboard shortcuts for form interaction:

```xml
<shortcuts>
  <accept_input_form alt="false" command="false" ctrl="false" key_code="19459" shift="false"/>
  <cancel_input_form alt="false" command="false" ctrl="false" key_code="13595" shift="false"/>
  <add_subform alt="false" command="false" ctrl="false" key_code="0" shift="false"/>
</shortcuts>
```

- **`accept_input_form`** (default: Enter) -- validates and accepts the current form
- **`cancel_input_form`** (default: Escape) -- cancels and dismisses the current form
- **`add_subform`** (default: none) -- adds a subrecord in a subform

These interact with form objects: when a focusable object (checkbox, input, etc.) has focus, pressing Return either advances to the next object in entry order, or triggers the **default button** if one exists. The default button is typically associated with the accept action.
