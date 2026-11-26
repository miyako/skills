---
object: "form"
json_type: null
keywords: ["FORM SCREENSHOT", "print form", "static template", "render", "PNG", "PDF", "CSS not applied", "preview", "verification"]
summary: "Standalone PNG previews with fourdform versus actual 4D runtime captures: the two capture commands, what the static template shows per object type, and which behaviors cannot be captured."
---

# Rendering a Form for Verification

A rendered preview or capture lets you see a `.4DForm` without opening the
IDE. It is a useful sanity check, but it is **not** validation -- schema
validation is the done-gate (see `skills/4dform/SKILL.md`). Use a capture to confirm
layout and styling, not correctness.

## Recommended Assessment Order

For a quick visual assessment on macOS or Windows, use `fourdform` first. Inspect
the PNG for the layout or appearance question at hand without starting
4D or installing capture methods. A clear static preview need not be
followed by a 4D capture automatically.

For a second opinion, an uncertain or unsupported preview, or a platform
where `fourdform` is unavailable, use the appropriate 4D/tool4d CLI
workflow in `skills/4dcli/SKILL.md`. Report a failed preview before
falling back, and identify which engine produced each result.

`project_form_to_image` uses `FORM SCREENSHOT` for the Form Editor's
static template, without executing form methods or applying CSS.
`print_form_to_file` supplies a CSS-aware printed PDF, not a screen
image. For runtime data or appearance after `On Load`, use full 4D
without `--headless` and the `dialog_screenshot` chain instead.
When the user explicitly requests one of these 4D-produced results,
skip the quick preview and use the requested capture directly.

Compare the relevant objects under matching page, language, and
appearance settings where supported. Explain renderer limitations and
differences; do not treat two agreeing images as validation of form code.
If the required engine is unavailable, state that the second opinion
is unavailable rather than manufacturing an equivalent result.

## Standalone PNG Preview -- No 4D Runtime

`fourdform`, built from
[miyako/4d-form](https://github.com/miyako/4d-form) and distributed in
`miyako/skills` releases, renders a `.4DForm` file to an actual PNG on
macOS 12+ or Windows 10+, arm64 or x64. The source pin is the merged
Windows-support revision from
[`miyako/4d-form#2`](https://github.com/miyako/4d-form/pull/2); the CLI
version remains `0.1.0`. Use the invocation in
`skills/4dform/SKILL.md`; installation belongs to `skills/4dtools/SKILL.md`.
The parser and HTML renderer reuse pinned `4d-ql` libraries, with
platform-specific raster adapters producing the image. Windows requires
the Evergreen Microsoft Edge WebView2 Runtime and the packaged companion
Swift/MSVC DLLs beside `fourdform.exe`. Linux is unavailable.

This is a static reference preview, not `FORM SCREENSHOT`, not a real
4D runtime capture or native screenshot, and not proof of pixel-identical
native controls. Theme selection chooses the preview appearance:

| Host | Accepted themes | Default |
|---|---|---|
| macOS | `classic-light`, `classic-dark`, `liquid-glass-light`, `liquid-glass-dark` | `classic-dark` if the form forces dark, otherwise `classic-light` |
| Windows | `classic`, `fluent-light`, `fluent-dark` | `fluent-dark` if the form forces dark; otherwise `fluent-light` if `fluentUI` is set, otherwise `classic` |

Cross-platform themes are rejected with exit code **2**, with no aliases
and no Windows preview on macOS. An explicitly incompatible theme does
not override a forced form color scheme. Windows tab controls and group
boxes are approximate; popups display the object name, not runtime values.

The preview does not run the form, execute `.4dm` methods, evaluate runtime
data bindings, or verify every 4D stylesheet property. Report unsupported
features and rendering errors rather than presenting an approximation as
runtime evidence. Observed gaps: it shows built-in `:xliff:Common*` IDs
unresolved, and does not draw 21 R5 coloured buttons
(`borderStyle: "custom"`), so a start screen made of coloured tiles
previews empty. It shows data sources (`Form.name`), not values: use it for
layout, and `4dcli` runtime captures for content. It also draws SVG
toolbar icons as literal text and does not render the 21 R5 `padding*` /
`verticalAlign` text placement on inputs and text, so never use it as
evidence for a demo or polish change about those properties. Project `:xliff:` IDs do
resolve with `--language ja` (from `Resources/ja.lproj`), a quick check for
literals left in a form.

## Deterministic Output

For a pinned `fourdform` build and theme, the same `.4DForm` renders to a
**byte-identical** PNG on every run (three separate invocations hashed the same
image; a preview committed a day earlier matched a fresh render too). That makes
a committed preview a usable regression fixture: re-render it in CI and compare
hashes instead of eyeballing the image. A mismatch then means either the form changed
(recommit the preview) or the renderer, theme or version changed (pin those
before concluding anything). Determinism is per platform, theme and tool
version; a different renderer is expected to produce different pixels.

Use actual 4D runtime captures below when their behavior is needed. The
static-template observations in the following sections describe
`FORM SCREENSHOT`, not a universal promise about `fourdform`.

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

`FORM SCREENSHOT` returns a picture with a real alpha channel when the
window renders in **dark appearance**: the form background comes back
only ~9 % opaque, so opening the raw PNG over white looks washed out and
the header can read as mid-grey. Composite over the colour you want to
present (`#1E1E1E` reproduces what the dark window actually looks like)
before committing a capture to a README
(`skills/4dcli/scripts/flatten_screenshot.py`). There is no per-form switch:
`FORM theme` is a getter, so the capture inherits the machine's colour
scheme. Set `FORM SCREENSHOT` expectations, or compare two runs, on the
same appearance setting -- and say which appearance a published image
came from.

Text inside an input whose border is `Border System Rounded` (set with
`OBJECT SET BORDER STYLE`) is not drawn by `FORM SCREENSHOT` (4D 21 R5).
For review or README images, capture the real window instead
(`skills/4dcli/references/shared-desktop.md`): it has an opaque background
and draws what the user sees. Keep `FORM SCREENSHOT` for layout checks.

`project_form_to_image` and `print_form_to_file` are project-specific
helper methods, not built-in 4D commands. A project that does not define
them cannot be captured this way until they are installed -- the `4dcli`
skill ships their source and the install procedure, see
`skills/4dcli/SKILL.md`.

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
