---
object: "picture-input"
json_type: "input"
keywords: ["picture input", "SVG", "clickable map", "mouse tracking", "DOM tree", "rendering tree", "drawing tool", "onMouseMove", "onClicked", "MOUSE POSITION", "SVG Find element ID by coordinates"]
summary: "Picture-type input as an interactive SVG canvas: DOM tree vs rendering tree, mouse event set, hit testing, clickable maps, and drag-to-draw interactions."
---

# Picture Input — Interactive SVG Canvas

A picture-type input (`"dataSourceTypeHint": "picture"`) supports a richer set
of mouse events than a text input, making it the standard object for building
**clickable maps**, **GUI editors**, and **drag-to-draw/move** interactions —
especially with SVG as the data source.

Reference project: https://github.com/miyako/svgarea

## Two Trees: DOM Tree vs. Rendering Tree

When working with SVG in a picture input, there are **two distinct data
structures** in play:

| Tree | Created by | Modified by | Purpose |
|------|-----------|-------------|---------|
| **DOM tree** | `DOM Parse XML source` / `DOM Parse XML variable` / `DOM Create XML Ref` | `DOM SET XML ATTRIBUTE`, `DOM Create XML element`, etc. | Persistent data model — the "source of truth" for the SVG document |
| **Rendering tree** | `SVG EXPORT TO PICTURE` → assigned to form object | `SVG SET ATTRIBUTE(*; "objectName"; ...)` | What is displayed on screen — a rendered copy |

### Key Rules

1. **`SVG SET ATTRIBUTE` without trailing `*`** — modifies the **rendering tree
   only** (the displayed image in the form object). The DOM tree is unchanged.
   Fast, no re-export needed. Ideal for real-time visual feedback during drag.

2. **`SVG SET ATTRIBUTE` with trailing `*`** — modifies the **DOM tree itself**
   (the source picture variable/field). All form objects using that picture are
   updated. Use when you want the change to persist.

3. **`DOM SET XML ATTRIBUTE`** — modifies the DOM tree directly via its
   reference. You must call `SVG EXPORT TO PICTURE` afterward to update the
   display.

4. **Rendering tree is created on display** — `SVG SET ATTRIBUTE(*; "objectName"; ...)`
   only works once the picture is rendered on screen. If you modify the DOM and
   re-export to picture, you must wait for the next form event cycle before
   calling `SVG SET ATTRIBUTE` on the rendering tree.

### Pattern: Interactive Editing

The svgarea project demonstrates the standard pattern:

```
On Clicked / On Timer (drag):
  → SVG SET ATTRIBUTE(*; "area"; ...) — update rendering tree only (fast)
  → Visual feedback without touching the DOM

On Timer (mouse up detected) / finalize:
  → DOM SET XML ATTRIBUTE($dom; ...) — commit to DOM tree
  → SVG EXPORT TO PICTURE(DOM; $pic) — re-export
  → Assign $pic to Form.SVG — refresh display
```

This two-phase approach gives smooth real-time interaction (rendering-only
updates are instant) while preserving the ability to serialize/save the final
state from the DOM tree.

References:
- https://developer.4d.com/docs/commands/svg-set-attribute
- https://developer.4d.com/docs/commands/svg-get-attribute
- https://developer.4d.com/docs/commands/dom-parse-xml-source
- https://developer.4d.com/docs/commands/dom-parse-xml-variable
- https://developer.4d.com/docs/commands/svg-export-to-picture

## Mouse Event Lifecycle

| Event | Fires when | `MOUSEX`/`MOUSEY` updated |
|---|---|---|
| `On Clicked` | Mouse button pressed | Yes (object-relative) |
| `On Mouse Move` | Mouse moves (requires `On Clicked` first) | Yes |
| `On Mouse Up` | Mouse button released | Yes |

Reference: https://developer.4d.com/docs/Events/onClicked, https://developer.4d.com/docs/Events/onMouseUp

**Important constraints**:
- `On Mouse Up` fires **only for picture-type inputs** — never for text inputs
- If **Draggable** is enabled on the object, `On Mouse Up` is **never generated** — the drag-and-drop system takes over
- `MOUSEX`/`MOUSEY` are automatically updated for picture inputs on `On Clicked`; for non-picture inputs they are NOT (use `MOUSE POSITION` instead)

**Best practice for interactive SVG canvases**: always set `"dragging": "none"` and `"dropping": "none"` explicitly on picture inputs used as drawing/editing surfaces. A picture-type input supports automatic drag and drop by default — if left at defaults, the drag-and-drop system intercepts mouse gestures before `On Clicked` can fire, preventing any custom click/draw interaction.

## Timer-Based Mouse Tracking

Reference: https://developer.4d.com/docs/Events/onTimer

The `On Mouse Up` event only fires while the pointer is within the picture
object's bounds. If the user drags outside the object, `On Mouse Up` may not
fire. For applications where the drag must continue even outside the object
(e.g. a drawing tool), use **`On Timer`** with `SET TIMER` + `MOUSE POSITION` /
`MOUSE POSITION` instead:

```4d
// Form method handles On Timer
Case of
  : (FORM Event.code=On Timer)
    var $mouseX; $mouseY; $mouseB : Integer
    MOUSE POSITION($mouseX; $mouseY; $mouseB; *)
    // Convert screen coords to form-relative
    CONVERT COORDINATES($mouseX; $mouseY; XY Screen; XY Current form)
    // Subtract object origin for object-relative coords
    var $left; $top; $right; $bottom : Integer
    OBJECT GET COORDINATES(*; "area"; $left; $top; $right; $bottom)
    $mouseX:=$mouseX-$left
    $mouseY:=$mouseY-$top

    If (Bool($mouseB))
      // Button still held — continue tracking
      // ... update visual with SVG SET ATTRIBUTE
    Else
      // Button released — finalize
      SET TIMER(0)  // stop timer
      // ... commit to DOM, re-export picture
    End if
End case
```

### SET TIMER Values

| Value | Behavior |
|-------|----------|
| `SET TIMER(-1)` | Fire `On Timer` as fast as possible (every tick ≈ 1/60s) |
| `SET TIMER(0)` | Stop the timer |
| `SET TIMER(n)` | Fire after `n` ticks (1 tick = 1/60th second) |

### Why Timer over On Mouse Up

| Approach | Tracks outside object | Requires Draggable=false | Complexity |
|----------|----------------------|--------------------------|------------|
| `On Mouse Up` | No | Yes | Low |
| `On Timer` + `MOUSE POSITION` | **Yes** | No | Medium |

The svgarea project uses `On Timer` for exactly this reason — the user can drag
an object's handle outside the picture area and the tracking continues smoothly.

## `Is waiting mouse up`

Reference: https://developer.4d.com/docs/commands/is-waiting-mouse-up

Returns **True** if the current object was clicked and the mouse button has not
yet been released (and the parent window still has focus). Returns **False** if
the mouse-up was "lost" (e.g. an alert dialog appeared while button held).

Use this to guard `On Mouse Move` handlers against desynchronized state:

```4d
: (FORM Event.code=On Mouse Move)
  If (Not(Is waiting mouse up))
    // Mouse-up was lost — cancel tracking
    $tracking:=0
  Else
    // Continue tracking normally
  End if
```

This command is the picture-input counterpart to `Is editing text` (which guards
text-input keystroke handlers).

## SVG Hit-Testing

Reference: https://developer.4d.com/docs/commands/svg-find-element-id-by-coordinates, https://developer.4d.com/docs/commands/svg-find-element-ids-by-rect

When the picture data source is SVG, you can identify which element was
clicked/hovered:

| Command | Returns | Use case |
|---------|---------|----------|
| `SVG Find element ID by coordinates(*; "obj"; x; y)` | Text (element `id`) | Point-click hit test |
| `SVG Find element IDs by rect(*; "obj"; x; y; w; h; $arr)` | Text array | Rubber-band selection |

Both work on the **rendering tree** — you pass the object name with `*`.
Elements must have an `id` attribute to be found.

```4d
Case of
  : (FORM Event.code=On Clicked)
    var $id : Text
    $id:=SVG Find element ID by coordinates(*; "area"; MouseX; MouseY)
    Case of
      : ($id="btn_@")
        // Clicked a button element
      : ($id="region_@")
        // Clicked a region
    End case
End case
```

## Architecture: svgarea Component

The svgarea project demonstrates a complete interactive SVG editor
implemented as a 4D component (subform). Key architectural decisions:

### Classes

| Class | Responsibility |
|-------|---------------|
| `Area` | Holds DOM reference, document dimensions, grid; exports picture |
| `Event` | Tracks interaction state: isResizing, isDrawing, isMoving, isSelecting; determines current tool; identifies clicked element via SVG hit-testing |
| `Timer` | Wraps `SET TIMER(-1)` / `MOUSE POSITION` / `CONVERT COORDINATES`; polls mouse position and button state each tick |
| `Selection` | Tracks which SVG element IDs are currently selected |
| `Objects` | Registry of all user-created element IDs |

### Event Flow

```
On Clicked (object method "area.4dm"):
  1. timer.start() — begins SET TIMER(-1) polling
  2. Record ClickX/ClickY from timer.MouseX/MouseY
  3. event.update() — SVG hit-test to find clicked element
  4. Dispatch based on tool + state (select/draw/resize/move)

On Timer (form method):
  1. timer.update() — MOUSE POSITION, CONVERT COORDINATES, check button
  2. If button still held:
     - SVG SET ATTRIBUTE(*; "area"; ...) — rendering tree only (fast)
  3. If button released:
     - timer.stop()
     - DOM SET XML ATTRIBUTE(...) — commit to DOM tree
     - SVG EXPORT TO PICTURE → Form.SVG — refresh display
     - Notify container (if used as subform)
```

### Custom `editor:` Attributes

The project stores original positions in custom namespaced attributes
(`editor:x`, `editor:y`, `editor:cx`, `editor:width`, etc.) alongside
standard SVG attributes. During drag, the visual attributes are offset from
the `editor:` values. On finalize, both are updated to the new position.

This pattern prevents cumulative floating-point drift during repeated drags
and provides a "last committed position" reference.

### Rendering Tree vs DOM — When to Use Each

| Operation | Target | Why |
|-----------|--------|-----|
| Real-time drag feedback | Rendering tree (`SVG SET ATTRIBUTE *; "area"`) | Speed — no re-export needed |
| Finalize position after drag | DOM (`DOM SET XML ATTRIBUTE`) + re-export | Persistence — DOM is the source of truth |
| Read current visual position | Rendering tree (`SVG GET ATTRIBUTE *; "area"`) | Reads the live displayed state |
| Add/remove elements | DOM (`DOM Append XML element`, `DOM REMOVE XML ELEMENT`) + re-export | Structure changes require DOM |
| Hit-testing | Rendering tree (`SVG Find element ID by coordinates *; "area"`) | Tests against what's displayed |
| Save/export document | DOM (`SVG EXPORT TO PICTURE` or `DOM EXPORT TO FILE`) | DOM holds authoritative state |

### Subform Container Communication

The svgarea component uses `OBJECT SET SUBFORM CONTAINER VALUE` to push
the current picture/DOM back to the parent form. The parent binds a
Picture or Text variable to the subform widget; the component updates it
on every finalized interaction.

## Summary: Choosing the Right Approach

| Need | Solution |
|------|----------|
| Simple clickable map (no drag) | `On Clicked` + `SVG Find element ID by coordinates` |
| Drag within object bounds | `On Clicked` → `On Mouse Move` → `On Mouse Up` + `Is waiting mouse up` guard |
| Drag that extends beyond object | `On Clicked` + `SET TIMER(-1)` + `MOUSE POSITION` in `On Timer` |
| Full SVG editor (draw/move/resize) | Timer-based tracking + two-tree pattern (rendering for feedback, DOM for commit) |
