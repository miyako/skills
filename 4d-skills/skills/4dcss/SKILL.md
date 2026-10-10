---
name: 4dcss
description: >
  4D form stylesheets: styleSheets.css / styleSheets_mac.css /
  styleSheets_windows.css and the form "css" property, 4D CSS syntax and
  specificity (form JSON beats CSS), class assignment, dark mode with
  prefers-color-scheme and the "automatic" / "automaticAlternate" colour
  values, resolving theme colours at runtime with hidden reference objects,
  and macOS Tahoe Liquid Glass / Fluent UI form themes (form-theme media
  queries, 27px button and dropdown heights, FORM theme).
---

# 4D CSS, Dark Mode & Form Themes

## Scope

How 4D form objects get their appearance from stylesheets rather than from
hardcoded values in `.4DForm` JSON:

* where stylesheets live and how they are loaded
* 4D CSS syntax and specificity
* dark mode -- `automatic` colours, `prefers-color-scheme`, runtime colour
  resolution -- `references/dark-mode.md`
* platform form themes -- Liquid Glass (macOS Tahoe), Fluent UI (Windows),
  `form-theme` media queries, control heights -- `references/form-themes.md`

### Not in this skill

| Topic | Skill |
|---|---|
| Form JSON structure, object types, every property's JSON/CSS name | `4dform` (`references/property-reference.md`) |
| Icons and `_dark` picture variants | `4dform` (`references/form-concepts.md`) |
| Rendered border/radius/focus-ring offsets when laying out objects | `4dform` (`references/layout.md`) |
| Version detection (Fluent UI needs 21 R2, Liquid Glass 21 R3) | `4dproject` |

## Route Table

| Task involves | Open |
|---|---|
| Dark mode, hardcoded colours, `automatic`, listbox row colours, meta-source colours | `references/dark-mode.md` |
| Liquid Glass, Fluent UI, button/dropdown heights, `form-theme`, `FORM theme` | `references/form-themes.md` |
| Where to put a rule, specificity, syntax | this file |

References:
- CSS in 4D: https://developer.4d.com/docs/FormEditor/stylesheets
- Form `css` property: https://developer.4d.com/docs/FormEditor/propertiesForm#css
- Form object properties (camelCase names): https://developer.4d.com/docs/FormObjects/propertiesReference

## Stylesheet Files

4D loads these from `Project/Sources/` automatically, in this order:

| File | Scope |
|---|---|
| `styleSheets.css` | all platforms -- dark/light rules (`prefers-color-scheme`) go here |
| `styleSheets_mac.css` | macOS only -- `liquid-glass` / `mac-classic` rules go here |
| `styleSheets_windows.css` | Windows only -- `fluent-ui` / `win-classic` rules go here |

A form can load more stylesheets with its `"css"` property (loaded last).
Paths use the file-system prefixes `/DATA/`, `/LOGS/`, `/PACKAGE/`,
`/PROJECT/`, `/RESOURCES/`, `/SOURCES/`; a file next to the `.4DForm` can be
named by file name alone:

```json
{ "css": ["myCustomStyles.css"] }
```

## Syntax

4D CSS uses CSS **selector syntax**, but property names are **4D form object
property names** (`fill`, `stroke`, `alternateFill`, `borderStyle`,
`horizontalLineStroke`, ...), not web CSS properties. A few accept a web
alias (`background-color` for `fill`, `color` for `stroke`, `font-size`,
...); look names up in `skills/4dform/references/property-reference.md`
rather than assuming a web property exists.

* Hex colours are `#RRGGBB` only -- **no alpha channel** (`#RRGGBBAA` is not
  supported).
* Selectors: `button` (object type), `.myClass` (the object's `"class"`),
  `#myObject` (the object's name). Combine as `button.default`.
* Assign classes in the form JSON: `"class": "label primary"` (space
  separated).
* Media queries: `@media (prefers-color-scheme: light|dark)` and
  `@media (form-theme: liquid-glass|mac-classic|fluent-ui|win-classic)`;
  they can be nested.

## Specificity (critical)

From lowest to highest:

1. type selector -- `button { }`
2. class selector -- `.myClass { }`
3. name selector -- `#MyButton { }`
4. **a property written directly in the `.4DForm` JSON**
5. `!important` (discouraged)

A value left in the form JSON always wins over CSS. To move a value into
CSS:

1. **remove** the property from the object in `.4DForm`;
2. **add** a `"class"` to the object;
3. **define** the value for that class in the right stylesheet.

Do not reach for `!important` to override a JSON value -- remove the JSON
value instead.

**Matching quirk.** 4D does not always match a compound `type.class`
selector at runtime. When a rule must apply, define it on **both** the bare
class and the compound selector (`.default` and `button.default`,
`.my-list` and `listbox.my-list`).

## What stays in JSON

If removing a property from the JSON would change **which native widget is
drawn or how it behaves** (not just how it looks), keep it in the JSON:

| Keep in JSON (structural) | Why |
|---|---|
| `style` | selects the native widget (`roundedBevel`, `toolbar`, `regular`, ...) |
| `textPlacement` | icon position relative to text |
| `sizingX`, `sizingY` | resizing behaviour |
| `splitterMode` | resize vs collapse |
| `multiline`, `wordwrap`, `enterable` | entry behaviour |
| `scrollbarVertical`, `scrollbarHorizontal` | scrolling |
| `hideFocusRing` | focus ring |
| `rowHeight`, `headerHeight` | list box geometry |

Visual properties are safe in CSS: `fill`, `stroke`, `alternateFill`,
`fontSize`, `fontWeight`, `fontStyle`, `borderStyle`, `borderRadius`,
`textAlign`, `verticalAlign`.

* Write `borderRadius` **without a unit** (`borderRadius: 8;`): `8px`
  produced CSS parse error 555 in practice. `height` and `fontSize` accept
  `px`, as in 4D's own examples (`fontSize: 14px;`, `height: 27px;`).
* A CSS class for a `roundedBevel` button must set `textAlign: center` and
  an explicit `fontSize`; without `fontSize` the property list shows `0` and
  a runtime error follows.
* The Form Editor's CSS preview (v18 R5+) may not simulate structural
  properties set only in CSS -- one more reason to keep them in JSON.
* `borderStyle` / `borderRadius` change the rendered size of the object;
  see `skills/4dform/references/layout.md`.

## Verification

* Re-read the edited `.4DForm` files and confirm no JSON value still
  overrides the class you added.
* `grep` every form, not only the one you were asked about: appearance rules
  are project-wide.
* Test by toggling the system appearance (light/dark) and, for form themes,
  on the platform concerned.
