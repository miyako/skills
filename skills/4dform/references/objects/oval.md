---
object: "oval"
json_type: "oval"
keywords: ["oval", "shape", "stroke"]
summary: "Oval shape object: basic static oval definition."
---

# 4D Oval Object

Reference: https://developer.4d.com/docs/FormObjects/shapesOverview#oval

## Basic Definition

```json
{
  "myOval": {
    "type": "oval",
    "left": 10,
    "top": 180,
    "width": 60,
    "height": 60,
    "stroke": "#000000",
    "fill": "transparent"
  }
}
```

An oval is a static (non-interactive) decorative object. When `width` equals `height`, it draws a perfect circle.

## Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Fill color | `fill` | string | Interior fill color. `"transparent"` for no fill. |
| Line color | `stroke` | string | Border line color |
| Line width | `strokeWidth` | integer | Border line thickness |
| Dotted line type | `strokeDashArray` | string | Dash pattern (e.g., `"6 2"`) |
| Horizontal sizing | `sizingX` | string | Resize behavior with form |
| Vertical sizing | `sizingY` | string | Resize behavior with form |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |
| Coordinates | `left`, `top`, `width`, `height`, `right`, `bottom` | integer | Bounding rectangle |

## Notes

- No events are supported -- ovals are purely decorative
- Set `width == height` for a perfect circle
- Properties are identical to rectangle except there is no `borderRadius` (the shape is inherently curved)
- Use `fill: "transparent"` with a visible `stroke` for an outline-only oval

## Comparison of Shapes

| Feature | Rectangle | Line | Oval |
|---------|-----------|------|------|
| Fill color | Yes | No | Yes |
| Border radius | Yes (`borderRadius`) | No | N/A (inherently curved) |
| Start point | No | Yes (`startPoint`) | No |
| Dash pattern | Yes | Yes | Yes |
| Line width | Yes | Yes | Yes |
| Line color | Yes | Yes | Yes |
| Interactive | No | No | No |
| Events | None | None | None |
