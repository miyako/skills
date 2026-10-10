---
object: "rectangle"
json_type: "rectangle"
keywords: ["rectangle", "shape", "stroke"]
summary: "Rectangle shape object: basic static rectangle definition."
---

# 4D Rectangle Object

Reference: https://developer.4d.com/docs/FormObjects/shapesOverview#rectangle

## Basic Definition

```json
{
  "myRect": {
    "type": "rectangle",
    "left": 10,
    "top": 25,
    "width": 80,
    "height": 50,
    "stroke": "#000000",
    "fill": "#DBEAFE",
    "borderRadius": 12
  }
}
```

A rectangle is a static (non-interactive) decorative object. It has no events, no data source, and no user interaction. It is purely visual.

## Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Corner radius | `borderRadius` | integer | Roundness of corners. 0 = sharp corners. Higher values = more rounded. |
| Fill color | `fill` | string | Background fill color. `"transparent"` for no fill. |
| Line color | `stroke` | string | Border line color |
| Line width | `strokeWidth` | integer | Border line thickness |
| Dotted line type | `strokeDashArray` | string | Dash pattern (e.g., `"6 2"` = 6px dash, 2px gap) |
| Horizontal sizing | `sizingX` | string | Resize behavior with form |
| Vertical sizing | `sizingY` | string | Resize behavior with form |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |
| Coordinates | `left`, `top`, `width`, `height`, `right`, `bottom` | integer | Position and size |

## Notes

- No events are supported -- rectangles are purely decorative
- The `borderRadius` property is unique to rectangles among shapes
- Use `fill: "transparent"` with a visible `stroke` for an outline-only rectangle
- Rectangles are commonly used as visual grouping containers or background panels
