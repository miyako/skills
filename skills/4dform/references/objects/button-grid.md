---
object: "buttonGrid"
json_type: "buttonGrid"
keywords: ["button grid", "rowCount", "columnCount", "transparent overlay", "gotoPage", "cell numbering"]
summary: "Button grid object: grid overlay concept, 1-based cell numbering, gotoPage standard action."
---

# 4D Button Grid Object

Reference: https://developer.4d.com/docs/FormObjects/buttonGridOverview

## Basic Definition

```json
{
  "myGrid": {
    "type": "buttonGrid",
    "top": 20,
    "left": 20,
    "width": 200,
    "height": 200,
    "rowCount": 4,
    "columnCount": 4,
    "events": ["onClick"]
  }
}
```

A button grid is a transparent object designed to be placed on top of a background graphic. It divides its area into a row-by-column grid of clickable cells. When a cell is clicked, it appears sunken/pressed, and the object's value is set to the cell number.

The object name is the JSON key, following the same conventions as other form objects:
- Object method: `ObjectMethods/myGrid.4dm`
- CSS selector: `#myGrid { ... }`
- Available via `FORM Event.objectName`

## How It Works

The button grid is an **overlay** -- it does not display any content by itself. The typical workflow is:

1. Add a background graphic to the form (e.g., a color palette, a toolbar image, a set of icons arranged in a grid)
2. Place the button grid on top of the graphic, matching its dimensions
3. Set the `rowCount` and `columnCount` to match the grid layout of the graphic
4. Handle clicks in the object method based on the cell number

The button grid divides its width and height evenly by the column and row counts. Each resulting cell is a clickable region.

## Cell Numbering

Cells are numbered sequentially from **top-left to bottom-right**, starting at 1:

```
For a 4x4 grid:

 1  2  3  4
 5  6  7  8
 9 10 11 12
13 14 15 16
```

When no cell is selected, the value is **0**.

## Data Source

The button grid value is an **integer** representing the selected cell number (1 to `rowCount * columnCount`), or 0 if no cell is selected.

Like buttons, the value reflects the currently clicked cell. The data source can be a variable or expression.

## Properties

The button grid has a very limited set of properties compared to buttons, checkboxes, and radio buttons. It has **no styles, no text, no icon, no font properties** -- it is a purely positional/structural object.

### Grid Properties

| Property | Type | Description |
|----------|------|-------------|
| `rowCount` | integer | Number of rows in the grid |
| `columnCount` | integer | Number of columns in the grid |

Reference: https://developer.4d.com/docs/FormObjects/propertiesCrop#rows

### Positioning and Sizing

| Property | Type | Description |
|----------|------|-------------|
| `top` | integer | **Required**. Y position |
| `left` | integer | **Required**. X position |
| `width` | integer | Total grid width (divided evenly by `columnCount`) |
| `height` | integer | Total grid height (divided evenly by `rowCount`) |
| `sizingX` | enum | `"move"`, `"grow"`, `"fixed"` |
| `sizingY` | enum | `"move"`, `"grow"`, `"fixed"` |

### Other Properties

| Property | Type | Description |
|----------|------|-------------|
| `borderStyle` | string | Border line style |
| `visibility` | `"visible"`, `"hidden"` | Hidden = invisible and inactive |
| `tooltip` | string | Help tip text |
| `action` | string | Standard action (e.g., `"gotoPage"`) |
| `class` | string | CSS class |

## Standard Action: gotoPage

The button grid supports the `gotoPage` standard action. When assigned, clicking a cell automatically navigates to the form page matching the cell number. For example, clicking cell 3 displays page 3.

```json
{
  "myNavGrid": {
    "type": "buttonGrid",
    "action": "gotoPage",
    "rowCount": 1,
    "columnCount": 5,
    "top": 10,
    "left": 10,
    "width": 500,
    "height": 40,
    "events": ["onClick"]
  }
}
```

This is useful for tab-like navigation where a background graphic shows labeled sections.

Like drop-down list and picture pop-up menu, a `gotoPage` button grid becomes a persistent navigation control when placed on **page 0** (always visible regardless of the current page -- see `tab.md`'s page-0 navigation pattern, which applies identically here). A companion plain button with `"action": "gotoPage?value=N"` (see `button.md`) can add fixed one-off page jumps (e.g. "Home") that don't warrant their own grid cell.

## Events

Supported events:

- `onClick` (On Clicked) -- primary event; fires when a cell is clicked
- `onDoubleClick` (On Double Clicked)
- `onLoad` / `onUnload`
- `onMouseEnter` / `onMouseLeave` / `onMouseMove`
- `onBeginDragOver` / `onDragOver` / `onDrop`
- `onGettingFocus`
- `onHeader` / `onPrintingBreak` / `onPrintingDetail` / `onPrintingFooter`
- `onValidate`

### Object Method Pattern

```4d
var $event:=FORM Event

Case of 
  : ($event.code=On Clicked)
    var $cellNumber:=OBJECT Get value("myGrid")
    Case of 
      : ($cellNumber=1)
        // first cell clicked
      : ($cellNumber=2)
        // second cell clicked
    End case 
End case 
```

## Visual Appearance

Without a background graphic, the button grid renders as a bordered grid of cells with a raised/3D appearance. In practice, the grid should always be overlaid on a meaningful graphic so the user sees labeled/illustrated options rather than empty cells.

The grid always displays internal cell borders. The `borderStyle` property controls the outer border but does not hide the internal grid lines.

## Comparison with Other Objects

| Feature | Button | Checkbox | Radio | Button Grid |
|---------|--------|----------|-------|-------------|
| Purpose | Action trigger | Toggle state | Mutually exclusive selection | Positional click on graphic |
| Text/Icon | Yes | Yes | Yes | No |
| Styles | 11 | 12 | 12 | None |
| Data value | Momentary (1/0) | Toggle (0/1/2) | Group (1/0) | Cell number (1..N) |
| Visual | Self-rendering | Self-rendering | Self-rendering | Transparent overlay |

## Use Cases

- **Color palette**: Background image of color swatches, grid overlay to detect which color was clicked
- **Page navigation**: Combined with `gotoPage` standard action for tab-like UI
- **Toolbar**: Background image with tool icons arranged in a grid
- **Image map**: Any graphic where different regions trigger different actions

## Related Object: Picture Pop-up Menu

See `picture-popup.md`. A picture pop-up menu (`type: "picturePopup"`) shares the exact same `rowCount`/`columnCount` grid concept and the identical "1-based cell number, 0 = no selection" data source convention, but owns its picture directly (no separate background graphic to overlay) and presents its cells as a pop-up menu instead of leaving them all visible as an on-form overlay.

## CSS Styling

Very limited CSS support -- only basic properties like `borderStyle`:

```css
#myGrid {
  borderStyle: none;
}
```

## Localization

Button grids have no text property, so `:xliff:` references do not apply. The visual content comes entirely from the underlying background graphic.
