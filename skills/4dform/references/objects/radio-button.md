---
object: "radio"
json_type: "radio"
keywords: ["radio button", "radioGroup", "mutual exclusion", "Form.property"]
summary: "Radio button object: 12 styles, radioGroup semantics vs Form Editor groups, default selection behavior."
---

# 4D Radio Button Object

Reference: https://developer.4d.com/docs/FormObjects/radiobuttonOverview

## Basic Definition

```json
{
  "RadioSP": {
    "type": "radio",
    "text": "SP",
    "radioGroup": "speed",
    "top": 20,
    "left": 20,
    "width": 100,
    "height": 20,
    "events": ["onClick"]
  },
  "RadioLP": {
    "type": "radio",
    "text": "LP",
    "radioGroup": "speed",
    "top": 44,
    "left": 20,
    "width": 100,
    "height": 20,
    "events": ["onClick"]
  },
  "RadioEP": {
    "type": "radio",
    "text": "EP",
    "radioGroup": "speed",
    "top": 68,
    "left": 20,
    "width": 100,
    "height": 20,
    "events": ["onClick"]
  }
}
```

A radio button allows the user to select one option from a group of mutually exclusive choices. Only one radio button in a group can be selected at a time -- selecting one automatically deselects all others in the same group.

The object name is the JSON key. As with buttons and checkboxes:
- It is the filename for the object method (`ObjectMethods/RadioSP.4dm`)
- It is the CSS ID selector (`#RadioSP { ... }`)
- It is available in code via `FORM Event.objectName`

## Relationship to Buttons and Checkboxes

Radio buttons are closely related to buttons and checkboxes. They share most of the same visual properties, events, and behavior patterns.

| Feature | Button | Checkbox | Radio Button |
|---------|--------|----------|--------------|
| Data source value | 1 during click, then 0 | Toggles: 0/1/2 | Selected: 1 (or True), Deselected: 0 (or False) |
| State persistence | Momentary (resets) | Persistent (toggle) | Persistent (mutual exclusion within group) |
| Three-states | No | Yes | No |
| Grouping | N/A | N/A | `radioGroup` property |
| Pop-up menu | Yes (`popupPlacement`) | No | No |
| Available styles | 11 styles | 12 styles (no `help`; adds `disclosure`, `collapseExpand`) | 12 styles (no `help`; adds `disclosure`, `collapseExpand`) |

## Radio Group

Reference: https://developer.4d.com/docs/FormObjects/propertiesObject#radio-group

The `radioGroup` property (a string) assigns a radio button to a named group. Only one button in a group can be selected at a time. Selecting one button sets it to 1 and all others in the same group to 0.

```json
{ "radioGroup": "speed" }
```

**JSON property**: `radioGroup` (string) -- the group name.

**Important**: Do not confuse `radioGroup` with **Form Editor groups**. Editor groups (https://developer.4d.com/docs/FormEditor/overview#grouping-objects) are a visual convenience for manipulating multiple objects together in the design environment (move, resize, align). They have **no runtime effect**. Only `radioGroup` enforces mutual exclusion at runtime.

Without a `radioGroup` property, each radio button acts independently -- all can be selected simultaneously, effectively behaving like checkboxes.

### Radio Group is UI-Only

The `radioGroup` property only controls **user interaction** behavior. It does not prevent code from assigning 1 or True to all data sources in the group simultaneously. Mutual exclusion is enforced only when the user clicks a radio button.

### No Default Selection

When a form opens, all radio buttons initialize to 0 (unchecked). It is the **developer's responsibility** to set one radio button's data source to 1 if a pre-selected default is the expected behavior.

### Same-Page Restriction

Radio buttons in the same `radioGroup` can technically be placed on different pages, but **mutual exclusion only applies to radio buttons on the same page**. Clicking a radio on page 1 will not deselect a radio on page 0, even if they share the same group name.

## Data Source

A radio button can be associated with an **integer** or **boolean** variable or expression.

- **Integer**: 0 = not selected, 1 = selected
- **Boolean**: False = not selected, True = selected

When a radio button in a group is selected, its variable becomes 1 (or True), and all other buttons in the group become 0 (or False).

The value is NOT automatically saved -- radio button values must be stored in their variables and managed with methods (unless using `memorizeValue` with "Save Geometry").

Like checkboxes, radio buttons **can** use `Form.property` expressions as their data source (unlike buttons, which are limited to variables because their value toggles back to 0/False at the end of the form event cycle):

```json
{
  "dataSource": "Form.speed"
}
```

### Save Value

When the form's "Save Geometry" option is enabled, radio buttons support the `memorizeValue` property to persist their selection across sessions:

```json
{ "memorizeValue": true }
```

## Styles

Radio buttons support 12 styles (all button styles except `help`, plus `disclosure` and `collapseExpand`):

| Style | Description |
|-------|-------------|
| `regular` | **(default)** Standard system radio button (small bullseye with text). |
| `flat` | Minimalist radio button (bullseye with text). |
| `toolbar` | Transparent background, highlighted on hover. Usually with icon. |
| `bevel` | Rectangular with thin border. Usually with icon. |
| `roundedBevel` | Like bevel but with rounded corners. |
| `gradientBevel` | Rounded with subtle gradient fill. |
| `texturedBevel` | Gray textured background. |
| `office` | Light blue background with thin border. |
| `circular` | Circular outline with text below. |
| `disclosure` | Disclosure triangle style. |
| `collapseExpand` | Collapse/expand toggle style. |
| `custom` | Fully customizable appearance using background picture. |

### Style Notes

- **`regular` and `flat`**: Display the traditional radio button appearance (a small filled/empty circle next to the label text). Like checkboxes, the bullseye retains its native system appearance regardless of text styling.
- **Other styles** (toolbar, bevel, etc.): Render as **toggle buttons** -- visually identical to their button/checkbox counterparts. They stay pressed/highlighted when selected. Usually associated with a multi-state icon (`iconFrames: 4` or more).
- **`disclosure`**: Renders as a right-pointing triangle/chevron (`>`). Text is not displayed. Typically used for show/hide toggles. The chevron faces sideways (collapsed) or downwards (expanded). Note: disclosure only changes the icon -- it does not automatically push objects down to make space. The developer must implement object layout for disclosure behavior.
- **`collapseExpand`**: Renders similar to a regular bullseye circle with text. Used for expand/collapse toggles. Same caveat as disclosure regarding layout management.
- **`custom`**: Fully customizable appearance using a background picture. Supports additional properties:
  - `customBackgroundPicture` (string) -- path to background image
  - `customBorderX` / `customBorderY` (number) -- horizontal/vertical margin in pixels
  - `customOffset` (number) -- 3D click offset effect in pixels

### Pop-up Menu

Radio buttons do **not** support `popupPlacement`. Pop-up menus are button-only.

### Icon States

Same as checkboxes -- when using non-regular styles with an icon, up to 6 states (since v20):

| Frames | States |
|--------|--------|
| 1 | Single image for all states |
| 2 | Unchecked, Checked |
| 3 | Unchecked, Checked, Rollover |
| 4 | Unchecked, Checked, Rollover, Disabled |
| 5 | Unchecked, Checked, True Rollover, False Rollover, Disabled |
| 6 | Unchecked, Checked, True Rollover, False Rollover, True Disabled, False Disabled |

## Visual Properties

Same as checkboxes:

| Property | Values | Description |
|----------|--------|-------------|
| `text` | string | Radio button label text |
| `textAlign` | `"left"`, `"center"`, `"right"` | Text alignment (since v20) |
| `fontWeight` | `"normal"`, `"bold"` | Font weight |
| `fontStyle` | `"normal"`, `"italic"` | Font style |
| `textDecoration` | `"none"`, `"underline"` | Text decoration |
| `fontSize` | integer | Font size in points |
| `fontFamily` | string | Font family name |
| `stroke` | CSS color | Text color |
| `icon` | path | Path to icon image |
| `textPlacement` | `"left"`, `"right"`, `"top"`, `"bottom"`, `"center"` | Text position relative to icon |
| `iconFrames` | integer | Number of frames in the icon image |
| `imageHugsTitle` | boolean | Whether icon stays close to text (since v20) |
| `visibility` | `"visible"`, `"hidden"` | Hidden = invisible and inactive |
| `focusable` | boolean | Whether the radio button can receive keyboard focus |
| `tooltip` | string | Hover text |

## Keyboard Interaction

When a radio button has focus:

| Key | Action |
|-----|--------|
| **Space** | Selects the radio button (same as clicking) |
| **Tab** / **Return** | Moves focus to the next object in entry order |
| **Shift+Tab** / **Shift+Return** | Moves focus to the previous object in entry order |

**Exception**: If the form has a **default button**, the Return key triggers that button instead of advancing.

## Keyboard Shortcuts

Radio buttons support the same shortcut properties as buttons and checkboxes:

```json
{
  "shortcutKey": "1",
  "shortcutAccel": true,
  "shortcutShift": false,
  "shortcutAlt": false,
  "shortcutControl": false
}
```

## Events

Radio buttons support the same click events as buttons and checkboxes:

- `onClick` (On Clicked) -- fires when the radio button is selected
- `onDoubleClick` (On Double Clicked)
- Modifier key detection works the same way

### Event Execution Order

Same as buttons and checkboxes:
1. **Object method** runs first
2. **Form method** runs second
3. **Standard action** runs last

### Object Method Pattern

```4d
var $event:=FORM Event

Case of 
  : ($event.code=On Clicked)
    Case of 
      : ($event.objectName="RadioSP")
        // SP selected
      : ($event.objectName="RadioLP")
        // LP selected
      : ($event.objectName="RadioEP")
        // EP selected
    End case 
End case 
```

Alternatively, each radio button can have its own object method:

```4d
// ObjectMethods/RadioSP.4dm
var $event:=FORM Event

Case of 
  : ($event.code=On Clicked)
    // SP was selected
End case 
```

## Positioning and Sizing

| Property | Type | Description |
|----------|------|-------------|
| `top` | integer | **Required**. Y position |
| `left` | integer | **Required**. X position |
| `width` | integer | Radio button width |
| `height` | integer | Radio button height -- selects from system-defined size variants for regular/flat styles |
| `sizingX` | enum | `"move"`, `"grow"`, `"fixed"` |
| `sizingY` | enum | `"move"`, `"grow"`, `"fixed"` |

## CSS Styling

Same selectors and specificity rules as buttons and checkboxes:

```css
/* All radio buttons */
radio {
  style: regular;
}

/* By class */
.speedOption {
  stroke: #333333;
}

/* By name */
#RadioSP {
  fontWeight: bold;
}
```

## Localization

Same as buttons and checkboxes -- use `:xliff:` references:

```json
{ "text": ":xliff:RadioOptionSP" }
```
