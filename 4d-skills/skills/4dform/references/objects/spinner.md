---
object: "spinner"
json_type: "spinner"
keywords: ["spinner", "running", "stopped", "circular"]
summary: "Spinner object: binary running/stopped state, circular shape, minimal configuration."
---

# 4D Spinner Object

Reference: https://developer.4d.com/docs/FormObjects/spinner

## Basic Definition

```json
{
  "mySpinner": {
    "type": "spinner",
    "left": 29,
    "top": 226,
    "width": 100,
    "height": 100,
    "dataSource": "1"
  }
}
```

A spinner is a circular indeterminate activity indicator. It displays a continuous rotation animation to indicate that an operation (network connection, calculation, etc.) is in progress. It is functionally identical to the barber shop variant of the progress indicator, but with a circular shape instead of a linear bar.

## Two States Only

The spinner has no scale, no min/max, no graduations. It is purely binary:

- **1** (or any non-zero value) = animation running
- **0** = animation stopped (empty/idle)

The animation does not start automatically when the form loads. You must set the data source to 1 by code or use a static value like `"dataSource": "1"`.

## Data Source

The data source controls only the running/stopped state. Any non-zero value starts the animation.

## Properties

The spinner has a very minimal set of properties compared to other indicator objects:

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Border line style | `borderStyle` | string | Border style |
| Expression Type | `dataSourceTypeHint` | string | Type hint |
| Horizontal sizing | `sizingX` | string | Resize with form |
| Vertical sizing | `sizingY` | string | Resize with form |
| Help Tip | `tooltip` | string | Tooltip text |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |
| Coordinates | `left`, `top`, `width`, `height`, `right`, `bottom` | integer | Position and size |

No scale properties, no font properties, no `enterable` property.

## Events

- `onClick` (On Clicked) / `onDoubleClick` (On Double Clicked)
- `onDataChange` (On Data Change)
- `onLoad` / `onUnload`
- `onGettingFocus` / `onLosingFocus`
- `onMouseEnter` / `onMouseLeave` / `onMouseMove`
- `onBeginDragOver` / `onDragOver` / `onDrop`
- `onHeader` / `onPrintingBreak` / `onPrintingDetail` / `onPrintingFooter`
- `onValidate`

## Comparison with Barber Shop Progress Indicator

| Feature | Spinner | Barber Shop (Progress) |
|---------|---------|----------------------|
| Shape | Circular | Linear bar (horizontal or vertical) |
| Type | `"spinner"` | `"progress"` (with `max` omitted) |
| States | 0 = stopped, non-zero = running | 0 = stopped, non-zero = running |
| Scale properties | None | None (ignored in barber shop mode) |
| Typical use | Inline loading indicator | Progress bar placeholder |
