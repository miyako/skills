---
object: "picturePopup"
json_type: "picturePopup"
keywords: ["picture popup", "picture pop-up menu", "rowCount", "columnCount", "gotoPage", "1-based position"]
summary: "Picture pop-up menu object: button-grid-style frame grid rendered as a native pop-up menu, 1-based position data source."
---

# 4D Picture Pop-up Menu Object

Reference: https://developer.4d.com/docs/FormObjects/picturePopupMenuOverview
Also: https://developer.4d.com/docs/FormObjects/pictureButtonOverview (shared frame-grid mechanics)
Also: https://developer.4d.com/docs/FormObjects/dropdownListOverview (shared pop-up/standard-action concepts)
Also: https://developer.4d.com/docs/FormObjects/properties_Crop.md (`rowCount`/`columnCount` JSON grammar)

## Basic Definition

```json
{
  "myPicPopup": {
    "type": "picturePopup",
    "top": 20,
    "left": 20,
    "width": 80,
    "height": 80,
    "picture": "/RESOURCES/Images/langSelector.png",
    "rowCount": 1,
    "columnCount": 5,
    "dataSource": "Form.myPicPopup"
  }
}
```

**The JSON `type` value is `"picturePopup"`**, not `"picturePopupMenu"` (the doc page title and object name use "Picture Pop-up Menu", but the `type` enum value in `properties_Object.md#type` is the shorter `picturePopup`).

A picture pop-up menu is conceptually a **Button Grid rendered as a pop-up menu** instead of a static overlay: the same source picture, sliced into a `rowCount` x `columnCount` grid of frames, but presented to the user as a clickable pop-up (native OS menu chrome) rather than a fixed set of clickable regions. Clicking the object opens a menu; each menu entry corresponds to one frame of the source picture, and choosing an entry assigns that frame's 1-based position to the data source.

## Picture Source and Grid

Same frame-grid mechanics as Picture Button (see `picture-button.md`):

- Frames are numbered **row by row, left to right, starting at the top row**.
- `rowCount` / `columnCount` must exactly match the number of frames actually present in the source picture.
- Same path syntax: `/RESOURCES/Images/...`, form-relative, or `var:name`.
- Same `@nx` (high-resolution) and `_dark` (dark mode) suffix conventions apply to the source picture.

Unlike Picture Button, a picture pop-up menu has **no animation properties** (no `switchBackWhenReleased`, `switchWhenRollover`, `frameDelay`, etc.) -- there is nothing to animate since only one frame (the currently selected item) is ever visible on the object itself; the rest of the frames only appear inside the pop-up menu when it is open.

## Data Source

The data source holds the **1-based position** of the selected menu entry, numbered row by row from the top-left frame:

- `0` = no selection (initial/default state)
- `1` = first frame (top-left)
- `2` = second frame
- ... and so on, row by row

This is **1-based**, unlike Picture Button's 0-based frame index. It is the exact same numbering convention as Button Grid's cell value (see `button-grid.md`) -- both are "1 to `rowCount * columnCount`, 0 = no selection" -- which makes sense since a picture pop-up menu is conceptually a Button Grid whose cells are presented as pop-up menu entries instead of an on-form transparent overlay.

The data source is bidirectional: assigning a value to it selects the corresponding menu entry (for read-back / initialization purposes); the user choosing a menu entry writes that entry's position back to the data source.

To initialize a picture pop-up menu with no selection, set the data source to `0`.

## Standard Action

Reference: https://developer.4d.com/docs/Desktop/standard-actions

A picture pop-up menu supports the `gotoPage` standard action, structurally identical to a drop-down list's `gotoPage` mode (see `dropdown.md`):

```json
{
  "type": "picturePopup",
  "picture": "/RESOURCES/Images/pageIcons.png",
  "rowCount": 1,
  "columnCount": 3,
  "action": "gotoPage"
}
```

No `dataSource` is needed for this mode. Selecting the Nth menu entry (Nth frame) navigates to the Nth form page. As with drop-down lists, this binding is **one-directional**: navigating to a page by code (`FORM GOTO PAGE`) does not update which entry the picture pop-up menu displays as selected -- if the object exposes the current selection visually (rare, since only the last-selected frame shows on the closed object), keep it in sync explicitly via `FORM Get current page` or drive navigation through `INVOKE ACTION` instead of `FORM GOTO PAGE` directly. Setting the standard action to `"None"` (no action) hands the click event to a form/object method for custom handling instead of automatic page navigation.

Placed on **page 0**, a `gotoPage` picture pop-up menu becomes a persistent, icon-driven navigation control, since page-0 objects are always visible regardless of which page is displayed (see `tab.md`'s page-0 navigation pattern, shared identically by drop-down list and button grid). A companion plain button with `"action": "gotoPage?value=N"` (see `button.md`) can add fixed one-off page jumps that don't warrant their own menu entry.

## Supported Properties

| Property | JSON Name | Notes |
|----------|-----------|-------|
| Pathname | `picture` | POSIX path; `/RESOURCES/...`, form-relative, or `var:name` |
| Rows | `rowCount` | Number of grid rows in the source picture |
| Columns | `columnCount` | Number of grid columns in the source picture |
| Variable or Expression | `dataSource` | 1-based selected position; 0 = no selection |
| Standard action | `action` | e.g. `"gotoPage"` |
| Border Line Style | `borderStyle` | |
| Top/Left/Right/Bottom/Width/Height | `top`, `left`, `right`, `bottom`, `width`, `height` | Standard coordinates/sizing |
| Horizontal/Vertical Sizing | `horizontalSizing` / `verticalSizing` | Resizing behavior |
| Visibility | `visibility` | `"visible"` / `"hidden"` |
| CSS Class | `class` | CSS class hook |
| Help Tip | `tooltip` | |
| Object Name | (JSON key) | Object identifier |
| Type | `"type": "picturePopup"` | Fixed |

No `pictureFormat` (scaling/tiling/truncation), no `focusable`, no font/text properties -- a picture pop-up menu is a pure picture-driven object, not a text-capable one.

## Supported Events

`onClick` (On Clicked) -- primary event, fires when a menu entry is chosen -- plus `onBeginDragOver`, `onDragOver`, `onDrop`, `onHeader`, `onLoad`, `onUnload`, `onMouseEnter`, `onMouseLeave`, `onMouseMove`, `onPrintingBreak`, `onPrintingDetail`, `onPrintingFooter`, `onValidate`. Notably **no** `onDoubleClick` (unlike Picture Button).

## CLI Verification Notes

`FORM SCREENSHOT` renders the Form Editor's static template, never a live/running form: it does not execute `On Load` and does not reflect any `Form.xxx` value assigned by code. For a picture pop-up menu, the template always renders **frame 0** (the first grid position, top-left) at the object's declared `width`/`height` -- regardless of what the data source is assigned to in code, and regardless of whether `dataSource` is even present (a `gotoPage`-only object with no `dataSource` still renders frame 0). This differs from drop-down lists and combo boxes, whose static template instead renders the literal `dataSource` expression text as a label placeholder: a picture pop-up menu's visible appearance always comes from the picture itself, never from the data source text, because the object has no text-rendering capability to fall back to.

If the object's declared `width`/`height` does not match the source frame's native pixel dimensions, the displayed frame is **stretched (scaled) to exactly fill the object's bounding box** -- both upscaling and downscaling. There is no letterboxing, cropping, or aspect-ratio preservation; this is consistent with Picture Button's grid rendering and with the general absence of a `pictureFormat` property on this object type (there is no "scaled/tiled/truncated" choice to make -- the single displayed frame is always stretched to fit).

## Comparison with Button Grid

Button Grid is the closest structural relative -- both divide a grid area into `rowCount * columnCount` cells and share the **identical** "1 to N, 0 = no selection" data source convention -- but the two objects are fundamentally different in presentation and content ownership:

| Feature | Button Grid | Picture Pop-up Menu |
|---------|-------------|----------------------|
| `picture` property | None -- purely transparent, has no picture of its own | Yes -- owns and displays the source picture |
| Visual content | None by itself; must be manually overlaid on a separate background picture/graphic object | Self-contained; the picture *is* the object |
| Presentation | Static on-form overlay; all cells occupy fixed screen regions simultaneously | Pop-up (OS native menu); only the selected frame is shown when closed, all frames are listed as menu entries when open |
| Cell/position numbering | 1-based, top-left to bottom-right, row by row; 0 = no selection | 1-based, top-left to bottom-right, row by row; 0 = no selection (**identical** convention) |
| Data source | Integer, bidirectional | Integer, bidirectional |
| Standard action | Yes (`gotoPage`) | Yes (`gotoPage`) |
| Typical use | Custom hit-regions on a static image (e.g. a map, a color palette) | Icon-driven pop-up selection (a compact space-saving alternative to a Button Grid or a text drop-down) |

In effect, a picture pop-up menu behaves like a Button Grid that supplies its own background picture and collapses its cells into a pop-up menu instead of leaving them all visible and clickable at once.

## Comparison with Related Picture-Based Objects

| Feature | Static Picture | Picture Button | Picture Pop-up Menu |
|---------|----------------|----------------|----------------------|
| Interactive | No | Yes | Yes |
| Multi-frame grid (`rowCount`/`columnCount`) | No -- single image only | Yes | Yes |
| `pictureFormat` (scaled/tiled/truncated) | Yes | No (frame always stretched to object size) | No (frame always stretched to object size) |
| Frame numbering | N/A | 0-based | 1-based (0 = no selection) |
| Presentation | Static display | Fixed on-form control | Pop-up (OS native menu) |
| Standard action | No | Yes (general `action` property) | Yes (`gotoPage`) |
| Animation properties | No | Yes (`frameDelay`, `switchContinuously`, etc.) | No |
| Typical use | Decoration, background, logos | Buttons with custom art | Icon-driven popup selection |
| Data source | None | 0-based frame index | 1-based selection position |

## Comparison with Drop-down List

| Feature | Drop-down List | Picture Pop-up Menu |
|---------|----------------|----------------------|
| Content of each menu entry | Text (from `values`/array/choice list) | One frame of a picture grid |
| Selection value | Object (`index`, 0-based) / array (1-based, element = current) / choice list (value or reference) | Always a single 1-based position integer (0 = none) |
| `focusable` / keyboard interaction | Yes | No |
| `On Clicked` trigger timing | On mouse-down | On mouse-down (same "active object" family) |
| Standard action support | Yes (`gotoPage` and others, submenu-generating actions only) | Yes (`gotoPage` only) |
| CLI static template rendering | Literal `dataSource` expression text | Frame 0 of the picture, always |

Both objects are one-directionally bound when used with a standard action: code-driven state changes (e.g. `FORM GOTO PAGE`) do not update the object's displayed selection.
