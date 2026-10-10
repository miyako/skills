---
object: "layout"
json_type: ""
keywords: ["layout", "left", "top", "width", "height", "align", "alignment", "gap", "overlap", "spacing", "center", "borderRadius", "borderStyle", "focus ring", "scrollbar", "rendered size", "visual edge"]
summary: "Rendered vs declared geometry of form objects (border +1, radius +r outward, focus ring +5 live only, vertical scrollbar +15 right), alignment / gap / centering formulas, and the scripts/form_layout_calc.py calculator."
---

# Form Layout: Declared vs Rendered Geometry

Open this file whenever you set or change `left`, `top`, `width` or
`height` of a form object, align two objects to the same visual edge,
centre objects in a strip or toolbar, check for overlap between neighbours,
or investigate why the Form Editor and the running form look different.

Calculator: `skills/4dform/scripts/form_layout_calc.py` (Python 3, standard
library only; run it in place from the skillset).

## Rendering Offsets

Measured on macOS, in logical pixels (screenshot pixels on Retina = x2).

| Effect | Offset | Sides | When |
|---|---|---|---|
| `borderStyle: "solid"` | +1 | all four | always |
| `borderRadius: r` | +r | all four | always -- the arc extends **outward** from the declared corners (unlike web CSS) |
| macOS focus ring | +5 | all four | **running form only**, focusable objects; not drawn in the Form Editor |
| `scrollbarVertical: "automatic"` | +15 | right only | always |

```
rendered_w = declared_w + 2 x (border + radius + focus_ring) + scrollbar_v
rendered_h = declared_h + 2 x (border + radius + focus_ring)
```

Measured: an input declared 280 wide with a solid border and radius 8 is
282 px wide in the editor with radius 0, 298 px with radius 8, and 308 px
in the running form (focus ring added).

* A `roundedBevel` button draws its bevel about 4 px **inside** its declared
  bounds: its declared left edge is its visual left edge.
* Bordered inputs and combos extend **outside** their declared bounds
  (9 px per side in the editor with radius 8).
* Offsets are symmetric (except the scrollbar), so the visual centre equals
  the declared centre.

Use editor offsets (`live=False`) when arranging objects relative to each
other; use live offsets for screenshots of the running form (see also
`references/screenshot-rendering.md`).

## Typical Presets

The calculator defines these presets; adjust `radius` to the project's CSS.

| Object | Preset | border | radius | focusable |
|---|---|---|---|---|
| `input` (enterable), `combo` | `FILTER_INPUT` | yes | 8 | yes |
| `input` with `enterable: false` | `DETAIL_TEXT` | yes | 8 | no |
| `button` (any style) | `BUTTON` | no | 0 | yes |
| `listbox` without / with vertical scrollbar | `LISTBOX` / `LISTBOX_SCROLL` | no | 0 | no |
| `rectangle`, `line`, `text` | `RECT_PLAIN` | no | 0 | no |

## Workflow

1. Identify each object's border, radius (from the JSON **or its CSS
   class**), focusability and vertical scrollbar.
2. Report the current page:

   ```sh
   python3 skills/4dform/scripts/form_layout_calc.py --form Project/Sources/Forms/<Form>/form.4DForm --page 1
   ```

   The report lists declared and visual boxes (page 0 is always included)
   and exits non-zero if two objects overlap visually. Properties are read
   from the JSON only; for objects styled by CSS add `--css-border` and/or
   `--css-radius N`. Add `--live` for running-form offsets.
3. Compute new coordinates with the formulas below (or import the module).
4. Re-run step 2 until no unintended overlap remains, then validate the form
   as described in `skills/4dform/SKILL.md`.

## Formulas

| Goal | Formula | Calculator |
|---|---|---|
| Visual left / right | `left - offset_left` / `left + width + offset_right` | `visual_left`, `visual_right` |
| Align visual left to X | `left = X + offset_left` | `declared_left_for_visual_left` |
| Keep the visual right edge while moving left | `width = visual_right - new_left - offset_right` | `declared_right_for_visual_right` |
| Centre vertically in a strip | `top = strip_top + (strip_h - ctrl_h) // 2` | `center_v_in_strip` |
| Gap between neighbours (negative = overlap) | `visual_left(2) - visual_right(1)` | `visual_gap` |
| Minimum declared gap for a clearance c | `offset_right(1) + offset_left(2) + c` | `min_declared_gap` |
| Declared size for a target visual size | `visual - offset_left - offset_right` | `declared_for_visual`, `--solve W H` |

Examples (editor offsets, bordered input with radius 8 = 9 px per side):

* Align an input to a button whose left is 12: declare the input at
  `left = 21`.
* Two such inputs side by side need a declared gap of at least 18 px to
  touch and 20 px for a 2 px visual clearance.
* `--solve 300 30 --border --radius 8 --editor` → declare `width 282`.

## Runtime Geometry

| Command | Meaning |
|---|---|
| `OBJECT SET COORDINATES(*; name; left; top {; right; bottom})` | **Absolute** form coordinates; `right` / `bottom` are corner coordinates, not width / height. |
| `OBJECT MOVE(*; name; dx; dy {; dw; dh})` | Relative move / resize (add `*` as last parameter to make it absolute). |
| `OBJECT GET COORDINATES(*; name; $l; $t; $r; $b)` | Current rectangle, after automatic resizing. |

To size from a width: `OBJECT SET COORDINATES(*; $n; $l; $t; $l+$width; $t+$height)`.
`sizingX` / `sizingY` (`grow`, `move`) already follow window resizes; use
these commands only for layouts the static properties cannot express (e.g.
a collapsible side panel), and recompute in `On Resize` if the window is
resizable.

Reference: https://developer.4d.com/docs/commands/object-set-coordinates

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Pitfalls

- [ ] Editor vs live: measuring the Form Editor? editor offsets. Measuring a screenshot? live offsets.
- [ ] The focus ring never appears in the Form Editor: a button's editor offset is 0, not 5.
- [ ] Check every adjacent pair after moving objects, not only the one you moved.
- [ ] `borderRadius` grows the object outward: a wider radius means a wider rendering.
- [ ] Moving styling to CSS must not move structural properties out of the JSON -- see "What stays in JSON" in `skills/4dcss/SKILL.md`.
