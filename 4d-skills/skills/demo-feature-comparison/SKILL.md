---
name: demo-feature-comparison
description: >
  Build a 4D demo that compares an old technique with a new release's
  feature (for example rectangles behind borderless inputs vs 21 R5
  padding, verticalAlign and borderRadius on the input itself): one shared
  form class driving two forms so only the technique differs, version
  gates, keeping compatibilityVersion, honest before/after runtime
  captures per language for the README, and why static previews cannot
  show the feature. Use when a webinar, blog or seminar demo shows
  "before / after" or "R-x vs R-y" forms.
---

# Old vs New Technique Demo

The audience must see that the **only** difference is the technique. The
running example is one form built twice: once with the 21 R4 technique
(rectangles behind borderless text and inputs) and once with the 21 R5
properties (`padding*`, `verticalAlign`, `borderRadius`, `fill` on the
objects). The names are examples.

## Related

| Topic | Skill |
|---|---|
| Launcher, side-by-side windows, language toggle | `demo-launcher` |
| Form JSON, properties per version, layout offsets | `4dform` |
| Version gates, `compatibilityVersion` | `4dproject` |
| CSS limits per version | `4dcss` |
| Runtime captures | `4dcli` |
| README, screenshots, shareable repository | `demo-shareable-repo` |

## Structure

* **One class, two forms.** Both form methods are one line,
  `cs.<Feature>Form.new().handle(FORM Event)`. Lists, formats, computed
  positions and event handling live in the class, so behaviour cannot
  drift between the two forms. Name the forms after the technique
  (`<Form>_21R4`, `<Form>_21R5`).
* **Same data, same strings.** Both forms use the same XLIFF IDs and the
  same `Form` properties. Only the window title says which is which.
* **The new form uses the new feature for everything it can**, including
  places where the old technique would still work. Where the new feature
  cannot do something, say so in the README rather than mixing techniques
  silently. (Example: a coloured custom button needs `style` and
  `borderStyle` both `custom`; check `skills/4dform/references/objects/button.md`
  before deciding a feature "does not work".)
* **The old form stays idiomatic for its release**: no new-release
  property in it, even where it would be harmless, or the comparison lies.

## Version

* Check every property and command against the release that introduced it
  (`skills/4dform/references/property-reference.md`, 4D docs
  "propertiesReference"). The schema accepts unknown properties, so
  `4dform` validation passing does not prove a property exists.
* Run `4dlsp` with the tool4d of the **new** release: an older one reports
  false errors on new syntax (`4dlsp`, "Pin the build").
* Leave `compatibilityVersion` as the owner set it unless they ask: it
  changes behaviour for attendees (`demo-shareable-repo`, step 2). If it is
  below the gate of a property the new form uses (`4dproject`, "Feature
  gates"), say so and ask; do not raise it as a side effect. Name the exact
  4D build the captures were made with in the README.

## Geometry

New styling properties have their own drawing rules. Measured on 21 R5:
`borderRadius` on a text with `fill` paints `r` px beyond the object on
the left and right; on a rectangle it does not
(`skills/4dform/references/layout.md`). When converting a rectangle-based
layout, inset such objects by `r` on each side or they overlap neighbours.
Measure a capture; do not assume.

## Captures

The README's before/after images are the point of the repository:

* **Runtime only.** Capture each form in each UI language with full 4D
  (`4dcli`, `dialog_screenshot_with_data`, which sets the language and the
  `formClass` data; or the real-window capture in
  `skills/4dcli/references/shared-desktop.md` for README images), into
  `docs/images/<Form>_<lang>.png`. A static
  preview (`fourdform`) does not draw `padding*` or `verticalAlign` and
  shows SVG icons as text: never use it as evidence for the feature.
* Wrap every capture in `timeout` (e.g. 90 s) and kill stragglers by PID,
  so a capture loop is not cut off by the agent's own timeout instead.
* Capture from a scratch copy of the project, so harness methods never
  enter the shipped demo.
* Look at every capture: a misplaced label (operator precedence) or
  clipped Japanese text shows in a capture, not in the syntax checker.

## Checklist

- [ ] Both forms driven by one class; one-line form methods
- [ ] Old form uses only old-release properties; new form uses the feature throughout
- [ ] Every new property checked against the docs for its release
- [ ] `4dlsp` run with the new release's tool4d
- [ ] `compatibilityVersion` unchanged unless the owner asked; README names the verified build
- [ ] Radius and other drawing offsets checked in a capture
- [ ] Runtime captures per form and language under `docs/images/`; none from a static preview
