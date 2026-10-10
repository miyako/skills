---
object: "groupBox"
json_type: "groupBox"
keywords: ["group box", "text", "title", "stroke", "textAlign", "static container"]
summary: "Group box object: static non-interactive framed container, correct JSON title key, no events/data source."
---

# 4D Group Box Object

Reference: https://developer.4d.com/docs/FormObjects/groupBox

## Basic Definition

```json
{
  "myGroup": {
    "type": "groupBox",
    "text": "Employee Info",
    "left": 60,
    "top": 160,
    "width": 200,
    "height": 100
  }
}
```

A group box is a static (non-interactive) object used to visually assemble other form objects inside a titled frame. It has **no data source and no supported events at all** -- unlike every other object type in this project, the group box overview page does not even have a "Supported Events" section. It exists purely to draw a rectangular border with an optional title label, as a visual organizing aid.

## Title Property: `text`, Not `title`

The official group box documentation's own inline JSON example uses `"title": "Employee Info"` as the label key (and that example is itself malformed JSON -- it is missing a comma after the `"title"` line). This is incorrect. The actual JSON key, confirmed by CLI rendering, is **`text`** -- the same generic Title property JSON key used by Button, Check Box, Radio Button, and Text Area:

```json
{ "type": "groupBox", "text": "Employee Info" }
```

Setting `"title"` instead of `"text"` produces a bare frame with no visible label at all. Always use `text` for a group box's title.

The title is a "localizable" static text, like any 4D label: it supports an XLIFF reference in the `":xliff:ResName"` form (see *XLIFF Architecture* in the 4D documentation), resolved to the corresponding `resname`'s `<source>`/`<target>` value from the form's `.xlf` resource file at render time.

## Visual Containment Is Overlay, Not True Parent-Child

4D forms are flat: a group box does not actually parent or own the objects visually placed inside its frame. "Containment" is achieved purely by overlapping the group box's rectangle with other objects and letting the group box's frame/title render around them -- there is no object hierarchy, and moving or deleting the group box does not affect the objects that visually sit inside it. Object placement order (z-order) determines whether the group box's border is drawn behind or in front of overlapping objects.

## Supported Properties

| Property | JSON Name | Notes |
|----------|-----------|-------|
| Title | `text` | Group box label; see caveat above. Supports XLIFF reference syntax |
| Font | `font` | |
| Font Size | `fontSize` | |
| Font Color | `stroke` | JSON grammar key is `stroke`, not `fontColor` |
| Bold | `bold` | |
| Italic | `italic` | |
| Underline | `underline` | |
| Horizontal Alignment | `textAlign` | JSON grammar key is `textAlign`, not `horizontalAlign`; `"left"` / `"center"` / `"right"` / `"automatic"` / `"justify"` |
| Horizontal Sizing | `horizontalSizing` | Resizing behavior |
| Vertical Sizing | `verticalSizing` | Resizing behavior |
| Visibility | `visibility` | `"visible"` / `"hidden"` |
| CSS Class | `class` | CSS class hook |
| Object Name | (JSON key) | Object identifier |
| Top/Left/Right/Bottom/Width/Height | `top`, `left`, `right`, `bottom`, `width`, `height` | Standard coordinates/sizing |
| Type | `"type": "groupBox"` | Fixed |

No `dataSource`, no `action` (standard action), no `focusable`, and no border-style property are supported.

## Supported Events

None. The group box overview documentation page has no "Supported Events" section, and the object supports no interaction of any kind.

## CLI Verification Notes

`FORM SCREENSHOT` renders the Form Editor's static template. For a group box, since there is no data source and no runtime behavior to distinguish from the design-time appearance, the static template render **is** the true runtime appearance:

- `"text": "Employee Info"` renders the title label inside the frame's top border. `"title": "Employee Info"` (the key used in the official doc's own example) renders **no label at all** -- confirming `text` is the correct key.
- A group box with no `text` property at all renders a bare rounded rectangle frame with no label.
- `bold`, `stroke` (font color), and `textAlign` are all honored: a bold, red (`"#FF0000"`), right-aligned title renders correctly positioned and styled within the frame.
- Objects visually overlapping a group box's frame (e.g. input fields and their labels) render on top of the frame with no clipping or masking, confirming the group box is a pure visual backdrop rather than a true container.
- A `":xliff:ResName"` reference in `text` resolves correctly to the referenced resource's translated string in the static template render, same as any other object's XLIFF-referenced label.

## Comparison with Rectangle

| Feature | Rectangle | Group Box |
|---------|-----------|-----------|
| Purpose | Generic decorative shape (fill, border, corner radius) | Titled frame for visually grouping other objects |
| Title/label | No | Yes (`text`) |
| Fill color | Yes (`fill`) | No |
| Corner radius | Yes (`borderRadius`) | No |
| Typical use | Background panel, outline-only box, decorative shape | Labeled section grouping (e.g. "Employee Info", "Contact Details") within a form |

Both are purely static: no data source, no events, no user interaction.
