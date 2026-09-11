---
object: "line"
json_type: "line"
keywords: ["line", "shape", "startPoint"]
summary: "Line shape object: basic static line definition with start point."
---

# 4D Line Object

Reference: https://developer.4d.com/docs/FormObjects/shapesOverview#line

## Basic Definition

```json
{
  "myLine": {
    "type": "line",
    "left": 20,
    "top": 40,
    "width": 100,
    "height": 80,
    "startPoint": "topLeft",
    "stroke": "#000000"
  }
}
```

A line is a static (non-interactive) decorative object drawn between two points within its bounding rectangle.

## Start Point

The `startPoint` property controls the direction of the line within its bounding rectangle:

| Value | Direction |
|-------|-----------|
| `"topLeft"` | From top-left corner to bottom-right corner (default) |
| `"bottomLeft"` | From bottom-left corner to top-right corner |

### Special Cases

- **Horizontal line**: set `height: 0` -- draws a horizontal line at `top`
- **Vertical line**: set `width: 0` -- draws a vertical line at `left`

## Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Start point | `startPoint` | string | `"topLeft"` or `"bottomLeft"` -- line direction |
| Line color | `stroke` | string | Line color |
| Line width | `strokeWidth` | integer | Line thickness |
| Dotted line type | `strokeDashArray` | string | Dash pattern (e.g., `"8 4"`) |
| Horizontal sizing | `sizingX` | string | Resize behavior with form |
| Vertical sizing | `sizingY` | string | Resize behavior with form |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |
| Coordinates | `left`, `top`, `width`, `height`, `right`, `bottom` | integer | Bounding rectangle |

## Notes

- No events are supported -- lines are purely decorative
- The `startPoint` property is unique to lines among all form objects
- Lines have no `fill` property (they are one-dimensional)
- Lines can be at any angle determined by the width/height ratio of the bounding rectangle
- Unlike rectangles, lines have no `borderRadius`
