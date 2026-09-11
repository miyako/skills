---
object: "form"
json_type: null
keywords: ["FORM SCREENSHOT", "print form", "static template", "render", "PNG", "PDF", "CSS not applied", "preview", "verification"]
summary: "How a form renders when captured from the CLI: the two capture commands, what the static template shows per object type, which properties are and are not reflected, and which behaviors cannot be captured at all."
---

# Rendering a Form for Verification

A rendered capture is the only way to see a `.4DForm` without opening the
IDE. It is a useful sanity check, but it is **not** validation -- schema
validation is the done-gate (see `skills/4dform/SKILL.md`). Use a capture to confirm
layout and styling, not correctness.

For the tool4d binary, its version requirements, and the runtime patterns
that drive these captures, see the `4dcli` skill
(`skills/4dcli/SKILL.md`).

## The Two Capture Commands

### Screenshot -- `FORM SCREENSHOT`, no CSS applied

```bash
/Applications/4D\ 21\ R3/tool4d.app/Contents/MacOS/tool4d \
  --startup-method=project_form_to_image \
  --dataless \
  --project=<path>/example.4DProject \
  --user-param=<FormName>:<PageNumber>:<OutputPath.png>
```

### Print to PDF -- CSS applied

```bash
/Applications/4D\ 21\ R3/tool4d.app/Contents/MacOS/tool4d \
  --startup-method=print_form_to_file \
  --dataless \
  --project=<path>/example.4DProject \
  --user-param=<FormName>:<PageNumber>:<OutputPath.pdf>
```

`FORM SCREENSHOT` does **not** apply CSS stylesheets. To verify anything
driven by a stylesheet, use the print-to-PDF output instead.

`project_form_to_image` and `print_form_to_file` are project-specific
helper methods, not built-in 4D commands. A project that does not define
them cannot be captured this way until they are written.

## Static Template Behavior

`FORM SCREENSHOT` called with a form name
(`FORM SCREENSHOT(formName; formPict; pageNum)`) renders the Form Editor's
**static template** for that page, not a live running form. It never
executes `On Load` and never reflects any `Form.xxx` value, array content,
or field value assigned by form-object-method code.

This is the single most common source of false alarms: an object that
"shows the wrong text" in a screenshot is usually rendering correctly --
the static template is showing the data-source expression itself.

### What the Static Template Renders per Object Type

| Object type | Static template shows |
|-------------|----------------------|
| **Input** (all expression types, including picture/boolean) | Literal `dataSource` expression text (e.g. `Form.myText`) -- never the actual value/image |
| **Drop-down list** (object/array/choice-list/hierarchical) | Literal `dataSource` expression text -- never a resolved value or first list item |
| **Drop-down list** (`gotoPage`, no `dataSource`) | Object name in quotes (e.g. `"dropGotoPage"`) |
| **Combo box** (all kinds) | Literal `dataSource` expression text |
| **Tab control** (object/array/hierarchical) | Literal `dataSource` expression text (single tab) |
| **Tab control** (static `labels` list, no `dataSource`) | **Real tab strip with all configured labels** (the one exception -- content is fully known at design time) |
| **Picture pop-up menu** | **Frame 0** of the picture at the object's declared size -- never literal text |
| **Static picture** | Real image content |
| **Group box** | True runtime appearance (static by nature) |
| **Button / Checkbox / Radio** | True runtime appearance (label, style) |

### Properties Fully Rendered in the Static Template

- All **visual styling**: `borderStyle`, `borderRadius`, `fill`, `stroke`,
  `fontFamily`, `fontSize`, `fontWeight`, `fontStyle`, `textDecoration`,
  `textAlign`
- Hex colors, named colors, and `"transparent"` all honored
- `%password` font shows the literal dataSource text (not masked characters
  -- masking is runtime-only)

### Properties Not Reflected in the Static Template

- `enterable: false` -- no visible difference from enterable
- `choiceList` on an input -- no pop-up affordance shown
- Runtime values, array contents, `Form.xxx` bindings -- always show the
  literal expression text
- `%password` character masking -- literal text shown instead

### Interactive-Only Behaviors

Some behaviors cannot be observed via `FORM SCREENSHOT` at all and require
running the form interactively (see Pattern 4 in `skills/4dcli/SKILL.md`):

- Drop-down / combo box populated/selected state
- Combo box `automaticInsertion`, `excludedList` alerts
- Animated GIF playback in static picture objects
- Any behavior driven by `On Load` or user interaction
