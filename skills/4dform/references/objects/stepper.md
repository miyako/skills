---
object: "stepper"
json_type: "stepper"
keywords: ["stepper", "min", "max", "step", "vertical", "arrow keys", "dataSourceTypeHint"]
summary: "Stepper object: vertical-only control, min/max/step, keyboard interaction, date/time support."
---

# 4D Stepper Object

Reference: https://developer.4d.com/docs/FormObjects/stepper

## Basic Definition

```json
{
  "myStepper": {
    "type": "stepper",
    "left": 44,
    "top": 41,
    "width": 14,
    "height": 34,
    "min": 0,
    "max": 100,
    "step": 1,
    "events": ["onDataChange"],
    "dataSource": "Form:C1466.stepper"
  }
}
```

A stepper is a pair of up/down arrow buttons (like the end of a traditional scroll bar) that increments or decrements a numeric value by a predefined step. It is typically placed next to an input object that shares the same data source.

## Orientation

**Vertical only** -- unlike rulers, there is no horizontal variant. The stepper always displays as a vertical pair of up/down arrows.

The `width` controls the size of the stepper. Two size variants are visible in the user's form (width=14 and width=19).

## Data Source

Like rulers, the stepper **can use `Form.property` expressions** as data sources (unlike splitters which require variables).

Multiple steppers and other objects (e.g., inputs) can share the same data source and stay in sync:

```json
{
  "Stepper": {
    "type": "stepper",
    "dataSource": "Form:C1466.stepper",
    "max": 100
  },
  "Input": {
    "type": "input",
    "dataSource": "Form:C1466.stepper",
    "dataSourceTypeHint": "integer"
  }
}
```

Clicking the up arrow increments the value; clicking down decrements it. The input field reflects the change immediately.

## Scale Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Minimum | `min` | number | Minimum value (default: 0) |
| Maximum | `max` | number | Maximum value |
| Step | `step` | integer | Increment/decrement amount per click (default: 1) |

The value is clamped to the min/max range -- it cannot go below min or above max.

### Date and Time Support

When associated with a date type value, `min` and `max` are ignored and `step` represents days.
When associated with a time type value, `min` and `max` represent seconds and `step` represents seconds.

## Keyboard Interaction

When the stepper is **focusable**:
- **Up arrow** / **Right arrow**: increase value by step
- **Down arrow** / **Left arrow**: decrease value by step

## Events

- `onDataChange` (On Data Change) -- fires when the value changes (primary event)
- `onClick` (On Clicked)
- `onDoubleClick` (On Double Clicked)
- `onLoad` / `onUnload`
- `onGettingFocus` / `onLosingFocus`
- `onMouseEnter` / `onMouseLeave` / `onMouseMove`
- `onBeginDragOver` / `onDragOver` / `onDrop`
- `onHeader` / `onPrintingBreak` / `onPrintingDetail` / `onPrintingFooter`
- `onValidate`

## Other Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Enterable | `enterable` | boolean | Whether the user can interact |
| Border line style | `borderStyle` | string | Border style |
| Horizontal sizing | `sizingX` | string | Resize with form |
| Vertical sizing | `sizingY` | string | Resize with form |
| Help Tip | `tooltip` | string | Tooltip text |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |
| Expression Type | `dataSourceTypeHint` | string | `"integer"`, `"number"`, `"date"`, `"time"` |

## Comparison with Ruler

| Feature | Stepper | Ruler |
|---------|---------|-------|
| Visual | Up/down arrow buttons | Slider track with cursor |
| Orientation | Vertical only | Horizontal or vertical |
| Interaction | Click buttons or arrow keys | Drag cursor, click, scroll wheel |
| Value change | Discrete steps only | Continuous (snaps to step if set) |
| Graduations/labels | No | Yes (optional) |
| `Form.property` allowed | Yes | Yes |
| Sync multiple instances | Yes | Yes |
| Typical use | Paired with input field | Standalone or paired |
