---
object: "progress"
json_type: "progress"
keywords: ["progress indicator", "thermometer", "barber shop mode", "scale", "enterable"]
summary: "Progress indicator (thermometer) object: scale properties, barber-shop running/stopped mode, enterable ruler-like behavior."
---

# 4D Progress Indicator (Thermometer) Object

Reference: https://developer.4d.com/docs/FormObjects/progressIndicator

## Basic Definition

```json
{
  "myThermometer": {
    "type": "progress",
    "left": 23,
    "top": 103,
    "width": 271,
    "height": 18,
    "min": 0,
    "max": 100,
    "enterable": true,
    "dataSource": "Form:C1466.progress",
    "dataSourceTypeHint": "number"
  }
}
```

A progress indicator (also called "thermometer") displays or sets numeric values graphically as a filled bar. It is very similar to a ruler but displays as a solid bar rather than a track with a cursor.

## Orientation

Determined by dimensions (same as ruler):
- **Horizontal**: `width > height`
- **Vertical**: `height > width`

## Two Modes

### 1. Default Thermometer

Standard progress bar with a min/max range. Supports all scale properties (graduations, labels, step) just like a ruler.

When `enterable: true`, the user can click, drag, or use the scroll wheel to set the value — behaving identically to a ruler.

When `enterable: false` (typical for progress display), it is display-only, updated by code.

### 2. Barber Shop

An indeterminate progress indicator that shows a continuous animation. Used when the duration of an operation is unknown.

**Enabled by omitting the `max` property** — this is the only trigger:

```json
{
  "myBarberShop": {
    "type": "progress",
    "left": 355,
    "top": 17,
    "width": 21,
    "height": 124,
    "dataSource": "1",
    "dataSourceTypeHint": "number"
  }
}
```

In barber shop mode:
- All scale properties are ignored (no min, max, step, graduations, labels)
- The data source controls only the animation state:
  - `1` = start animation (running indefinitely)
  - `0` = stop animation (empty/idle)
- There is no intermediate state — it is either running or not

## Data Source

Like rulers, progress indicators **can use `Form.property` expressions** as data sources.

Multiple progress indicators and other objects (e.g., inputs, rulers) can share the same data source and stay in sync:

```json
{
  "Thermometer": {
    "type": "progress",
    "max": 100,
    "enterable": true,
    "dataSource": "Form:C1466.progress"
  },
  "Input": {
    "type": "input",
    "dataSource": "Form:C1466.progress"
  }
}
```

## Scale Properties

Same as ruler:

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Minimum | `min` | number | Minimum value |
| Maximum | `max` | number | Maximum value. **Omit to enable barber shop mode.** |
| Step | `step` | integer | Minimum interval between values |
| Display graduation | `showGraduations` | boolean | Show/hide tick marks |
| Graduation step | `graduationStep` | integer | Interval between tick marks |
| Label location | `labelsPlacement` | string | `"none"`, `"top"`, `"bottom"`, `"left"`, `"right"` |

## Events

Same event model as ruler:

- `onDataChange` (On Data Change) -- fires repeatedly during drag (requires Execute Object Method)
- `onClick` (On Clicked) -- fires on mouse release
- `onDoubleClick` (On Double Clicked)
- `onLoad` / `onUnload`
- `onLosingFocus`
- `onMouseEnter` / `onMouseLeave` / `onMouseMove`
- `onBeginDragOver` / `onDragOver` / `onDrop`
- `onHeader` / `onPrintingBreak` / `onPrintingDetail` / `onPrintingFooter`
- `onValidate`

**Note**: Progress indicator does not support `onGettingFocus` (only `onLosingFocus`), unlike ruler which supports both.

## Other Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Enterable | `enterable` | boolean | Interactive (like ruler) or display-only |
| Border line style | `borderStyle` | string | Border style |
| Bold | `fontWeight` | string | Bold labels |
| Font | `fontFamily` | string | Label font |
| Font Color | `stroke` | string | Label color |
| Font Size | `fontSize` | integer | Label size |
| Italic | `fontStyle` | string | Italic labels |
| Underline | `textDecoration` | string | Underline labels |
| Number Format | `numberFormat` | string | Format for label values |
| Expression Type | `dataSourceTypeHint` | string | `"integer"`, `"number"`, `"date"`, `"time"` |
| Horizontal sizing | `sizingX` | string | Resize with form |
| Vertical sizing | `sizingY` | string | Resize with form |
| Help Tip | `tooltip` | string | Tooltip text |
| Class | `class` | string | CSS class |
| Visibility | `visibility` | string | `"visible"` or `"hidden"` |

## Comparison with Ruler

| Feature | Progress Indicator | Ruler |
|---------|-------------------|-------|
| Visual | Filled bar | Track with draggable cursor |
| Barber shop mode | Yes (omit `max`) | No |
| Enterable | Optional (default: false) | Default: true |
| Graduations/labels | Yes | Yes |
| Font properties | Yes (for labels) | Yes (bold only) |
| `Form.property` allowed | Yes | Yes |
| Sync multiple instances | Yes | Yes |
| `onGettingFocus` | No | Yes |
| Typical use | Display progress / set value | Set value interactively |
