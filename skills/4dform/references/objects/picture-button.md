---
object: "pictureButton"
json_type: "pictureButton"
keywords: ["picture button", "rowCount", "columnCount", "frame", "command button", "choice selector", "animation", "frameDelay", "switchContinuously"]
summary: "Picture button object: multi-frame source images, 0-based frame numbering, command-button vs choice-selector modes, animation."
---

# 4D Picture Button Object

Reference: https://developer.4d.com/docs/FormObjects/pictureButtonOverview

## Basic Definition

```json
{
  "myPicBtn": {
    "type": "pictureButton",
    "top": 20,
    "left": 20,
    "width": 100,
    "height": 100,
    "picture": "/RESOURCES/Images/myButton.png",
    "rowCount": 1,
    "columnCount": 4,
    "switchBackWhenReleased": true,
    "switchWhenRollover": true,
    "useLastFrameAsDisabled": true,
    "events": ["onClick"]
  }
}
```

A picture button displays a series of images from a single source picture, switching between them based on user interaction or animation settings. Unlike standard buttons (which have system-drawn styles), picture buttons derive their entire visual appearance from a developer-supplied image.

## Two Use Cases

### 1. Command Button (most common)

The picture button acts like a regular button, but uses different image frames for each visual state (enabled, clicked, rollover, disabled). This is the typical use case.

Recommended configuration:
```json
{
  "rowCount": 1,
  "columnCount": 4,
  "switchBackWhenReleased": true,
  "switchWhenRollover": true,
  "useLastFrameAsDisabled": true
}
```

The 4 frames represent:
1. Default (enabled)
2. Clicked (mouse down)
3. Rollover (mouse hover)
4. Disabled

### 2. Choice Selector

The picture button cycles through images on each click, letting the user choose from several options (like a visual popup menu). For example, choosing a language from a set of flag icons.

Recommended configuration:
```json
{
  "rowCount": 1,
  "columnCount": 3,
  "loopBackToFirstFrame": true
}
```

Each click advances to the next image. The variable value indicates which image is currently displayed.

## Picture Source

The `picture` property specifies the path to the source image. The image contains all frames arranged in a grid (row, column, or row-by-column).

### Path Syntax

Same as other form objects:
- **Resources folder**: `"/RESOURCES/Images/myButton.png"`
- **Adjacent to form**: `"myButton.png"` (resolved relative to the form folder)
- **Variable**: `"var:myPictureVar"` (from a 4D picture variable at runtime)

### Image Layout

Frames are arranged in rows and columns within a single image:
- Frames are numbered from **left to right, top to bottom**, starting at **0**
- For a 1-row, 4-column image: frames 0, 1, 2, 3 from left to right
- For a 2-row, 3-column image: frames 0-2 in row 1, frames 3-5 in row 2

**Important**: The designer must ensure the source image contains exactly the right number of frames to match `rowCount * columnCount`.

### High-Resolution and Dark Mode

Same conventions as other icon images:
- `@nx` suffix for high-resolution variants (`myButton@2x.png`)
- `_dark` suffix for dark mode variants (`myButton_dark.png`)

## Grid Properties

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Rows | `rowCount` | integer | Number of rows of frames in the source image |
| Columns | `columnCount` | integer | Number of columns of frames in the source image |

## Animation Properties

Reference: https://developer.4d.com/docs/FormObjects/propertiesAnimation

These properties control when and how the picture button switches between frames. They can be combined.

| Property | JSON Name | Type | Description |
|----------|-----------|------|-------------|
| Switch back when released | `switchBackWhenReleased` | boolean | Shows frame 0 normally; shows frame 1 when clicked (mouse down). Returns to frame 0 on release regardless of cursor position. |
| Switch when roll over | `switchWhenRollover` | boolean | Shows the **last available frame** when the mouse cursor hovers over the button. The initial frame is restored when the cursor leaves. |
| Switch continuously on clicks | `switchContinuously` | boolean | Holding down the mouse button cycles through frames continuously (animation). |
| Loop back to first frame | `loopBackToFirstFrame` | boolean | After reaching the last available frame, cycles back to frame 0. Without this, stops at the last frame. |
| Switch every x seconds | `frameDelay` | integer | Auto-cycles through ALL frames at the specified interval (in seconds). Ignores all other animation options. Only animates while the window is active. |
| Use last frame as disabled | `useLastFrameAsDisabled` | boolean | The last frame is reserved for the disabled state. It is excluded from all sequences (rollover, continuous, loop) and only shown when the button is disabled. |

### Frame Assignment Rules

The frame used for each state depends on the total number of frames and which animation properties are enabled.

**Key rule**: `switchWhenRollover` always uses the **last available frame** (i.e., the last frame that isn't reserved for disabled). `switchBackWhenReleased` always uses **frame 1** for the clicked state.

| Frames | `lastDisabled` | Frame 0 | Frame 1 | Middle frames | Second-to-last | Last |
|--------|---------------|---------|---------|---------------|----------------|------|
| 4 | yes | normal | clicked | rollover (fr 2) | rollover (fr 2) | disabled (fr 3) |
| 4 | no | normal | clicked | — | — | rollover (fr 3) |
| 6 | yes | normal | clicked | unused (fr 2,3) | rollover (fr 4) | disabled (fr 5) |
| 6 | no | normal | clicked | unused (fr 2,3,4) | — | rollover (fr 5) |

**Important**: When using `switchBackWhenReleased` + `switchWhenRollover`, frames between 1 and the rollover frame are **unused**. This means for command buttons, use exactly the minimum number of frames needed (typically 4 with disabled, or 3 without).

### Click Behavior Without switchBack

Without `switchBackWhenReleased`, each click advances the data source by 1 (cycling through frames). The click is **positional**:
- If the mouse is **released over the button**: the new frame value sticks
- If the mouse is **released outside the button**: the value reverts to the previous frame (the click is cancelled)

This is the behavior used for **choice selector** buttons.

### switchContinuously Behavior

When `switchContinuously` is true with `loopBackToFirstFrame` and `useLastFrameAsDisabled`, the animation loops through frames 0 to N-2 (excluding the disabled frame). Without `loopBackToFirstFrame`, it stops at the last available frame.

### frameDelay Behavior

When `frameDelay` is set, it overrides all other animation properties. The button auto-cycles through **all** frames (including the last, even if `useLastFrameAsDisabled` is set — `frameDelay` ignores it). Animation only runs while the parent window is the active/focused window.

### Typical Combinations

**Command button** (4-state: default, clicked, rollover, disabled):
```json
{
  "columnCount": 4,
  "switchBackWhenReleased": true,
  "switchWhenRollover": true,
  "useLastFrameAsDisabled": true
}
```

**Choice selector** (cycle through options):
```json
{
  "columnCount": 5,
  "loopBackToFirstFrame": true
}
```

**Animated display** (auto-cycling):
```json
{
  "columnCount": 8,
  "frameDelay": 2,
  "loopBackToFirstFrame": true
}
```

## Data Source

The picture button's variable returns the **0-based index** of the currently displayed frame. This is different from button grids (which are 1-based).

- Frame 0 = first image
- Frame 1 = second image
- Frame N-1 = last image

The data source is an integer variable or expression.

## Other Properties

| Property | Type | Description |
|----------|------|-------------|
| `borderStyle` | string | Border line style |
| `focusable` | boolean | Whether the button can receive keyboard focus |
| `tooltip` | string | Help tip text |
| `action` | string | Standard action |
| `shortcutKey` | string | Keyboard shortcut key |
| `shortcutAccel` | boolean | Cmd (Mac) / Ctrl (Win) modifier |
| `text` | string | Title text (rarely used with picture buttons) |
| `fontStyle` | string | Italic support (for title text) |
| `visibility` | string | `"visible"` or `"hidden"` |
| `class` | string | CSS class |

## Events

Supported events:

- `onClick` (On Clicked) -- primary event
- `onDoubleClick` (On Double Clicked)
- `onLoad` / `onUnload`
- `onMouseEnter` / `onMouseLeave` / `onMouseMove`
- `onBeginDragOver` / `onDragOver` / `onDrop`
- `onHeader` / `onPrintingBreak` / `onPrintingDetail` / `onPrintingFooter`
- `onValidate`

### Object Method Pattern

```4d
var $event:=FORM Event

Case of 
  : ($event.code=On Clicked)
    var $frame:=OBJECT Get value("myPicBtn")
    // $frame is the 0-based index of the current frame
    Case of 
      : ($frame=0)
        // first image selected
      : ($frame=1)
        // second image selected
    End case 
End case 
```

## Visual Appearance

Without a `picture` property, the picture button is **invisible** -- it renders as an empty rectangle with no system-drawn UI. The entire visual appearance comes from the source image.

This is fundamentally different from standard buttons, checkboxes, and radio buttons, which all have system-drawn styles (regular, flat, bevel, etc.).

## Comparison with Related Objects

| Feature | Button (custom style) | Picture Button | Button Grid |
|---------|----------------------|----------------|-------------|
| Image source | `icon` + `customBackgroundPicture` | `picture` (single image with frames) | None (overlay on background) |
| Frame numbering | Icon states (up to 6) | 0-based index (unlimited) | 1-based cell number |
| Animation | No | Yes (`frameDelay`, `switchContinuously`) | No |
| Text support | Yes | Limited (title) | No |
| System styles | Custom only | None | None |
| Click behavior | Momentary | Configurable (switch back, cycle, etc.) | Positional |

## CSS Styling

Limited CSS support -- mainly `borderStyle` and positioning properties. The visual appearance is controlled by the source image, not CSS.

```css
#myPicBtn {
  borderStyle: none;
}
```
