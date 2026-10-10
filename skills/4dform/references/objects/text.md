---
object: "text"
json_type: "text"
keywords: ["text", "static text", "label", "title", "fontTheme", "textAngle", "rotation", "dynamic reference", "XLIFF", "SET TABLE TITLES", "OBJECT SET TITLE"]
summary: "Static text — a read-only counterpart to input with plain-text data source. Supports rotation, font themes, border styles, XLIFF references, embedded field/variable values, and dynamic table/field name display aliases. No events, no method, no data source."
---

# Text (Static Text)

Reference: https://developer.4d.com/docs/FormObjects/text

## Purpose

A text object is essentially a **read-only counterpart to the input object** with
a plain-text data source. It is often referred to as "static text," but the content
is not truly static — it supports XLIFF references, embedded field/variable values,
dynamic table/field name aliases, and runtime title changes via `OBJECT SET TITLE`.

Text objects display labels, titles, instructions, and section headings. They have
no events, no method, and no data source binding. They cannot receive focus, cannot
be edited, and do not participate in the tab order.

Like input (non-enterable), text objects support `textAngle` for orientation.
Unlike input, text objects support a special syntax for embedding table and field
names that respect display aliases (see Dynamic References below).

## Basic Definition

```json
{
  "myLabel": {
    "type": "text",
    "text": "Hello World!",
    "left": 60,
    "top": 160,
    "width": 100,
    "height": 20
  }
}
```

The `text` property (string) holds the displayed content. This is a design-time value — there is no runtime data source binding.

## Supported Properties (per JSON Schema)

The text object's properties come from five sources in the schema:

### Direct Properties

| JSON Key | Type / Enum | Notes |
|----------|-------------|-------|
| `type` | `"text"` | Required. Identifies the object type |
| `text` | string | The displayed text content |
| `fontTheme` | `"normal"`, `"main"`, `"additional"` | Platform-adaptive font theme (see below) |
| `textAlign` | `"automatic"`, `"right"`, `"center"`, `"justify"`, `"left"` | Horizontal text alignment |
| `textAngle` | `0`, `90`, `180`, `270` | Rotation angle in degrees (see Rotation below) |
| `borderRadius` | integer (≥ 0) | Corner radius for rounded borders |

### From `objectCommon`

| JSON Key | Type / Enum | Notes |
|----------|-------------|-------|
| `left` | integer | X position |
| `top` | integer | Y position |
| `width` | integer | Width in pixels |
| `height` | integer | Height in pixels |
| `right` | integer | Right anchor (alternative to width) |
| `bottom` | integer | Bottom anchor (alternative to height) |
| `sizingX` | `"move"`, `"grow"`, `"fixed"` | Horizontal resizing behavior |
| `sizingY` | `"move"`, `"grow"`, `"fixed"` | Vertical resizing behavior |
| `visibility` | `"visible"`, `"hidden"`, `"selectedRows"`, `"unselectedRows"` | Object visibility |
| `class` | string | CSS class name for styling |

### From `drawingSpec`

| JSON Key | Type | Notes |
|----------|------|-------|
| `fill` | color | Background color |
| `stroke` | color | Text color (foreground) |

### From `borderStyle`

| JSON Key | Enum | Notes |
|----------|------|-------|
| `borderStyle` | `"system"`, `"none"`, `"solid"`, `"dotted"`, `"raised"`, `"sunken"`, `"custom"`, `"double"` | Border appearance |

### From `fontSpec`

| JSON Key | Type / Enum | Notes |
|----------|-------------|-------|
| `fontFamily` | string | Font family name (e.g. `"Helvetica Neue"`, `"Courier New"`) |
| `fontSize` | integer | Font size in points |
| `fontStyle` | `"normal"`, `"italic"` | Italic style |
| `fontWeight` | `"normal"`, `"bold"` | Bold weight |
| `textDecoration` | `"none"`, `"underline"` | Underline decoration |

## No Events, No Method

The text object has **no events** and **no method property** in the schema. It cannot respond to clicks, mouse-overs, or any user interaction. It is a pure display element.

If you need a label that responds to clicks, use a **button** styled to look like text (flat appearance, no border), or an **input** with `enterable: false`.

## Font Theme (`fontTheme`)

Reference: https://developer.4d.com/docs/FormObjects/propertiesText#font-theme

`fontTheme` applies a platform-adaptive font style:

| Value | macOS | Windows |
|-------|-------|---------|
| `"normal"` | San Francisco Regular 13pt | Segoe UI Regular 12pt |
| `"main"` | San Francisco Regular 10pt | Segoe UI Semibold 10pt |
| `"additional"` | San Francisco Regular 9pt | Segoe UI Regular 9pt |

When `fontTheme` is set, `fontFamily`, `fontSize`, `fontWeight`, and `fontStyle` are ignored — the theme overrides them. To use custom font properties, leave `fontTheme` unset or set it to the value that matches the desired base, then override individual properties.

## Rotation (`textAngle`)

Reference: https://developer.4d.com/docs/FormObjects/propertiesText#orientation

`textAngle` rotates the text by the specified degrees. Only four values are valid: `0` (default), `90` (bottom-to-top), `180` (upside down), `270` (top-to-bottom).

```json
{
  "verticalLabel": {
    "type": "text",
    "text": "Sidebar",
    "textAngle": 90,
    "left": 10,
    "top": 50,
    "width": 20,
    "height": 120
  }
}
```

**Important**: the `width` and `height` properties define the bounding box, **not** the rotated dimensions. A 90° rotated text with `width: 20, height: 120` occupies a tall narrow space — the width/height refer to the **un-rotated** frame dimensions, which 4D then rotates.

Rotation can also be set at runtime with `OBJECT SET TEXT ORIENTATION`.

## Dynamic References in Static Text

Reference (legacy URL, may be retired):
https://doc.4d.com/4Dv20/4D/20.2/Using-references-in-static-text.300-6750154.en.html

The `text` property of a text object can contain **dynamic references** that 4D
evaluates when the form is displayed or printed. Three kinds of embedding are
supported: field/variable values, table/field display names, and XLIFF resources.

In the Form editor, **Object > Show Name / Show Resource** toggles between
displaying the raw reference syntax and the resolved values.

### Embedded Field and Variable Values

Enclose a field or variable name in `< >` delimiters:

- **Field (current table)**: `<FieldName>`
- **Field (other table)**: `<[TableName]FieldName>`
- **Variable**: `<VariableName>`

When displayed, 4D substitutes the current value. You can append a display format
after a semicolon:

```
<vTotal;$###,##0.00>
```

This is useful for mail-merge documents and report headers/footers.

### Embedded Table and Field Names (Display Aliases)

This is unique to text objects — input objects do **not** support this syntax.

Use `<?...>` to embed the **name** (not value) of a table or field. These names
update automatically when you rename tables/fields in the Structure editor, or
when `SET TABLE TITLES` / `SET FIELD TITLES` commands set display aliases:

| Syntax | Meaning |
|--------|---------|
| `<?[TableName]>` | Table name by name |
| `<?[2]>` | Table name by creation order (2nd table created) |
| `<?[TableName]FieldName>` | Field name (qualified by table name) |
| `<?[2]3>` | Field name by creation order (table 2, field 3) |
| `<?3>` | Field name by creation order (current table, field 3) |

Since the numbers correspond to creation order (not current position), you can
safely add or rename tables and fields without breaking references.

**Key commands for display aliases:**
- `SET TABLE TITLES` — https://developer.4d.com/docs/commands/set-table-titles
- `SET FIELD TITLES` — https://developer.4d.com/docs/commands/set-field-titles

These are particularly useful for **translating** the structure names visible to
users (e.g. showing "Clients" instead of "Customers" depending on locale).

### XLIFF References

XLIFF (XML-based) references can also appear in text objects, as well as in menu
and button labels. These are part of 4D's built-in localization architecture.

### When to Use Input Instead

For **expression-based dynamic content** like:

```
Form.firstName+" "+Form.lastName
```

it is easier to use an **input** object (non-enterable) bound to that expression.
Text objects cannot evaluate arbitrary 4D expressions — they only support the
specific embedding syntaxes described above.

## Visual Display Properties

Text objects share the same visual properties as input objects (see `input.md` for detailed descriptions):

- **`borderStyle`**: `"none"` (default for labels), `"solid"`, `"dotted"`, `"raised"`, `"sunken"`, etc.
- **`borderRadius`**: rounded corners
- **`fill`**: background color
- **`stroke`**: text (foreground) color
- **`fontFamily`**, **`fontSize`**, **`fontStyle`**, **`fontWeight`**, **`textDecoration`**: standard font properties

### Styling Tips

For section headers:
```json
{
  "SectionTitle": {
    "type": "text",
    "text": "Personal Information",
    "fontFamily": "Helvetica Neue",
    "fontSize": 16,
    "fontWeight": "bold",
    "stroke": "#2C3E50",
    "textAlign": "left"
  }
}
```

For subtle labels:
```json
{
  "FieldLabel": {
    "type": "text",
    "text": "First Name:",
    "fontTheme": "additional",
    "stroke": "#7F8C8D",
    "textAlign": "right"
  }
}
```

## Runtime Commands

Although text objects have no events, several commands can modify them at runtime:

| Command | Purpose |
|---------|---------|
| `OBJECT SET TITLE` | Change the displayed text (ref: https://developer.4d.com/docs/commands/object-set-title). Targets static text areas, buttons, checkboxes, radio buttons, list box headers, group boxes |
| `OBJECT SET TEXT ORIENTATION` | Change rotation angle (ref: https://developer.4d.com/docs/commands/object-set-text-orientation) |
| `OBJECT SET FONT` | Change font family |
| `OBJECT SET FONT SIZE` | Change font size |
| `OBJECT SET FONT STYLE` | Change bold/italic |
| `OBJECT SET COLOR` | Change text color |
| `OBJECT SET RGB COLORS` | Change text and/or background color |
| `OBJECT SET VISIBLE` | Show/hide |
| `OBJECT MOVE` | Reposition |

These commands target text objects by name (using `*` and the object name string).

**Multi-line titles**: use `\\` in the title string as a line separator
(in code editor: `"Line 1\\\\Line 2"`).

```4d
// Change a label at runtime
OBJECT SET TITLE(*; "myLabel"; "Updated: "+String(Current date))
```

## Text vs. Input for Labels

| Need | Use |
|------|-----|
| Simple label with no interaction | **Text** object |
| Label showing embedded field/variable values | **Text** with `<FieldName>` or `<VariableName>` syntax |
| Label showing structure names (with aliases) | **Text** with `<?[2]>` / `<?[2]3>` syntax |
| Label with expression-based dynamic content (e.g. `Form.firstName+" "+Form.lastName`) | **Input** with `enterable: false` — easier than text for arbitrary expressions |
| Label that updates from a data source | **Input** with `enterable: false` |
| Label that responds to clicks | **Button** (flat style) or **Input** with method |
| Label with styled text (bold/italic ranges) | **Input** with `styledText: true` |

## CLI Verification Notes

**Known `FORM SCREENSHOT` limitations with text objects (tested with 4D 21 R3):**

1. **Default text color is invisible** — text objects without an explicit `stroke`
   color do not appear in `FORM SCREENSHOT` output. Always set `stroke` when you
   need screenshot verification.

2. **Rotated text (`textAngle` ≠ 0) does not render** in `FORM SCREENSHOT`. The
   bounding box is captured but the text itself is absent. Rotation must be verified
   visually in the IDE.

3. **`borderStyle: "raised"` and `"sunken"`** render with very subtle relief that
   may be invisible in screenshots. `"solid"` and `"dotted"` work well.

4. **Colors (`stroke` + `fill`)** render correctly in screenshots. Font properties
   (`fontWeight`, `fontStyle`, `fontSize`, `fontFamily`, `textDecoration`) also render
   when `stroke` is explicitly set.

**Recommendation**: for any text object you intend to verify via CLI screenshots,
always set `stroke` to a visible color (e.g. `"#000000"` for black).

The `dialog_screenshot` pattern (Pattern 4 in the `4dcli` skill, `skills/4dcli/SKILL.md`) works for text
objects — if runtime code changes text via `OBJECT SET TITLE`, the screenshot
captures the updated content (provided `stroke` is set).
