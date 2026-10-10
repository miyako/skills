---
object: "ruler"
json_type: "ruler"
keywords: ["ruler", "min", "max", "step", "showGraduations", "graduationStep", "labelsPlacement", "scale"]
summary: "Ruler object: scale properties, orientation, integer-only values, event model (On Data Change vs On Clicked)."
---

# 4D Ruler Object

Reference: https://developer.4d.com/docs/FormObjects/ruler

## Basic Definition

```json
{
  "myRuler": {
    "type": "ruler",
    "left": 10,
    "top": 25,
    "width": 300,
    "height": 25,
    "min": 0,
    "max": 100,
    "events": ["onDataChange"]
  }
}
```

A ruler is an interactive slider control that allows the user to set or view a numeric value by dragging a cursor along a graduated track. The ruler is bidirectional -- dragging changes the data source, and updating the data source by code moves the cursor.

## Orientation

Like splitters, orientation is determined by dimensions:
- **Horizontal**: `width > height`
- **Vertical**: `height > width`

The height (horizontal) or width (vertical) also determines the size variant of the cursor, similar to how button/checkbox height selects size variants.

## Data Source

Unlike splitters, a ruler **can use `Form.property` expressions** as data sources. This makes rulers more flexible for form-based data binding.

Multiple rulers can share the same data source and they will **stay in sync** -- moving one ruler updates all others bound to the same expression. This is different from splitters, where one splitter cannot drive another via a shared data source.

```json
{
  "ruler1": {
    "type": "ruler",
    "dataSource": "Form:C1466.ruler",
    ...
  },
  "ruler2": {
    "type": "ruler",
    "dataSource": "Form:C1466.ruler",
    ...
  }
}
```

The data source value represents the current position within the min/max range. **Values are integer only.** To work with real/decimal values, use a large integer range (e.g., 0-1000 for 0.0-100.0), hide the ticker labels, and convert by code.

## Scale Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Minimum | `min` | number | Minimum value of the ruler (left/top end) |
| Maximum | `max` | number | Maximum value of the ruler (right/bottom end) |
| Step | `step` | integer | Minimum interval between selectable values (snapping). Minimum: 1 |

### Step

The `step` property controls the granularity of value selection. For example, with `min: 0`, `max: 50`, `step: 5`, the user can only select values 0, 5, 10, 15, ..., 50.

## Display Properties

### Graduation

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Display graduation | `showGraduations` | boolean | Show/hide tick marks along the track |
| Graduation step | `graduationStep` | integer | Interval between graduation tick marks |

Graduation ticks are small marks along the ruler track. They are purely visual and independent of the `step` property (though typically they match or are multiples of `step`).

### Enterable

Setting `enterable: false` makes the ruler non-interactive (no dragging, no scroll wheel). It can only be updated by code. Unlike disabled buttons/checkboxes, the ruler does **not** appear greyed out — it looks identical to an enterable ruler.

### Labels

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Label location | `labelsPlacement` | string | Where to display numeric labels |

Values for `labelsPlacement`:
- `"none"` -- no labels (default)
- `"top"` -- labels above (horizontal) or to the left (vertical)
- `"bottom"` -- labels below (horizontal) or to the right (vertical)
- `"left"` -- labels to the left
- `"right"` -- labels to the right

Labels display the numeric values at each graduation mark. Labels require `showGraduations: true` and a `graduationStep` to know where to place them.

**Note**: The ruler needs sufficient height (horizontal) or width (vertical) to accommodate labels. A height of ~40px works well for horizontal rulers with labels.

## Other Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Border line style | `borderStyle` | string | Border around the ruler |
| Enterable | `enterable` | boolean | Whether the user can interact with the ruler |
| Bold | `fontWeight` | string | Bold text for labels |
| Horizontal sizing | `sizingX` | string | Resize behavior with form |
| Vertical sizing | `sizingY` | string | Resize behavior with form |
| Help Tip | `tooltip` | string | Tooltip text |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |
| Number Format | `numberFormat` | string | Format for label values |
| Expression Type | `dataSourceTypeHint` | string | Type hint for the data source |

## Events

### Event Behavior

The ruler's event model is similar to a button but with important additions:

**On Clicked**: Fires when the mouse is **released** after interacting with the ruler. The new value is calculated based on the click position relative to the ruler's width (horizontal) or height (vertical). Unlike a button, the release does **not** need to be above the ruler -- the event fires regardless of where the mouse is released.

**On Data Change** (requires "Execute Object Method" property): Fires repeatedly during drag interaction:
1. Fires as soon as the mouse is pressed on the lever/handle
2. Fires again on every mouse move while the button is held down
3. Does **not** fire when the mouse is released (that triggers On Clicked instead)

Despite its name, On Data Change fires even if the new value equals the old value. This is a general rule for this event across all form object types.

**Important**: On Data Change is **not** fired when the data source is updated by code -- only by user interaction.

### Execute Object Method

The `methodExecutionMode` property (called "Execute Object Method" in the form editor) enables On Data Change events. When enabled, both On Data Change and On Clicked events fire during interaction. When disabled, only On Clicked fires on mouse release.

### Mouse Wheel

If the ruler is **focusable**, the mouse scroll wheel interacts with it when the pointer hovers over the ruler. The scroll direction can be:
- Vertical scroll on a **horizontal** ruler
- Horizontal scroll on a **vertical** ruler

At the end of a scroll sequence, On Data Change fires (if enabled).

### Supported Events

- `onDataChange` (On Data Change) -- fires repeatedly during drag/scroll (requires Execute Object Method)
- `onClick` (On Clicked) -- fires on mouse release
- `onDoubleClick` (On Double Clicked)
- `onLoad` / `onUnload`
- `onGettingFocus` / `onLosingFocus`
- `onMouseEnter` / `onMouseLeave` / `onMouseMove`
- `onBeginDragOver` / `onDragOver` / `onDrop`
- `onHeader` / `onPrintingBreak` / `onPrintingDetail` / `onPrintingFooter`
- `onValidate`

## Comparison with Splitter

| Feature | Ruler | Splitter |
|---------|-------|----------|
| Purpose | Set/display a value | Resize form areas |
| Data source value | Current position in min/max range | Distance traveled (resets) |
| `Form.property` allowed | Yes | No (must use variable) |
| Sync multiple instances | Yes (shared data source syncs all) | No (can't drive another splitter) |
| Affects other objects | No | Yes (moves/resizes neighbors) |
| Orientation | width vs height | width vs height |
| Visual options | Graduations, labels, track | Border line only |
| Scale control | min, max, step, graduationStep | None |

## Relationship to Thermometer / Progress Indicator

The ruler and thermometer (progress indicator) share the same scale properties (`min`, `max`, `step`, `showGraduations`, `graduationStep`, `labelsPlacement`). The difference is:

- **Ruler**: always interactive (user drags cursor)
- **Thermometer**: typically display-only (set by code), though it can be made enterable

Reference: https://developer.4d.com/docs/FormObjects/progressIndicator#using-indicators
