---
name: polish-ui-pass
description: >
  Ordered checklist for a visual polish pass on an existing 4D project:
  stylesheet split per platform, brand header band, typography classes,
  dark mode, Liquid Glass / Fluent UI control heights, fitted list boxes,
  callback-driven status lines, label fit in every UI language, and
  verification captures that do not disturb the user's desktop. Routes
  each step to the skill that owns it. Use when asked to polish, modernise
  the look of, or "make presentable" a 4D form or demo.
---

# UI Polish Pass

This skill only orders the work and routes it. The owning skill holds the
rules. Polish comes **after** the code works: never restyle and
change behaviour in the same commit.

## Order

| # | Step | Owner |
|---|---|---|
| 1 | Survey: form list, existing stylesheets, hard-coded colours and heights, window sizing; which colours are the demo's subject (exempt) | `4dform`, `4dcss` |
| 2 | Localise first (strings to XLIFF), so later layout is checked with real label lengths | `4dlocalise` |
| 2a | Real controls: fake buttons (hidden button over a rectangle and a label) become real buttons; remove per-object `fontFamily` (no Lucida Grande, no CJK glyphs) | `4dform` (`scripts/fake_buttons.py`), `4dcss` ("Fonts") |
| 3 | Stylesheet split: brand and typography in `styleSheets.css`; control heights per theme in `styleSheets_mac.css` / `styleSheets_windows.css` | `4dcss` |
| 4 | Header band and background: full-bleed, `rightMargin: 0` when a band spans the form | `4dform` (`references/form-concepts.md`) |
| 5 | Dark mode: every custom colour has a `prefers-color-scheme: dark` pair, unless every form pins `colorScheme` (demos: `demo-presentation`, "Appearance"); remove JSON `fill`/`stroke` that override the classes; strip colours from styled-text spans | `4dcss` (`references/dark-mode.md`) |
| 6 | Control heights: buttons and dropdowns ≥ 27 px under Liquid Glass; Fluent UI opt-in (`"fluentUI": true` on shared forms) and not verified (say so). Heights set in code must hold after every theme switch (best-size inputs shrank to ~18 px) | `4dcss` (`references/form-themes.md`) |
| 7 | Layout: alignment grid, spacing, no overlaps | `4dform` (`references/layout.md`) |
| 8 | List boxes: defaults, or the fitted exception for a fixed window | `4dform` (`references/objects/listbox.md`) |
| 9 | Status and feedback: callback-fed status lines, disabled actions until ready | `4dform` (`references/async-ui.md`) |
| 10 | Verify: render every form in every UI language, light and dark | below |

## Values That Worked (demo, 4D 21)

* Header band: light `#0F3D6E`, dark `#12263D`; title `#FFFFFF` /
  `#F2F6FB`; subtitle `#C9DCF2` / `#9DB7D5`.
* Feature-prefixed typography classes in `styleSheets.css` (`tfHeaderTitle`
  22 px bold, `tfHeaderSubtitle` 13 px, `tfQuery` 15 px, `tfCaption`
  12 px) instead of per-object fonts; colours only inside the
  `prefers-color-scheme` blocks.
* List box class: `alternateFill: automaticAlternate`, transparent grid
  lines, `verticalAlign: middle`.
* Button height: 27 px for `liquid-glass`, 23 px for `mac-classic`; one
  later demo used 32 px `fluent-ui` / 23 px `win-classic` (unverified on
  Windows).
* Semantic colour classes in `styleSheets.css` with dark overrides
  (`brand`, `muted`, `panel`); platform sheets hold only fonts and
  heights. A brand blue `#289FE8` became `#5CB8FF` in dark mode for
  contrast.
* Theme swatch buttons (a button that switches to a theme) mirror that
  theme: same fill, border and corner radius (e.g. 8 / 4 / 14 px), so the
  button previews the result. Coloured buttons need `style` and
  `borderStyle` both `custom` (`4dform`, `references/objects/button.md`).

## Japanese Label Fit

Each Japanese glyph is about one font size wide, whatever the word. Budget
`width ≥ characters × fontSize + horizontal padding` for a Japanese label,
button or tab, and check the English width separately. Do not set
`fontFamily` for Japanese text: the system font (Hiragino Sans on macOS)
is the fallback and matches the platform. Measure in a runtime capture.

## Exemption: colours that are the feature

"No hard-coded colours" is for the product's own chrome. When a demo
exists to show colour APIs (`OBJECT SET RGB COLORS`, coloured buttons,
themes set in code), those colours are the subject: keep them in the
form JSON and code, and move only the surrounding chrome to CSS.

## Verify

1. `fourdform` quick preview and the 4dform done-gate for structure.
2. Real rendering with 4D in the background, captured by window ID with
   no clicks or keystrokes, selecting only the PID you started
   (`4dcli`, `references/shared-desktop.md`). Never quit 4D by app name
   or path: the user may have their own 4D open.
3. For each UI language (en, ja): no truncated labels, no clipped
   buttons, no horizontal list-box scroll bar.
4. Light and dark appearance (only the pinned one when forms pin `colorScheme`).
5. Write down what you could not verify (Windows / Fluent UI; light mode
   if the machine is dark; `Common*` strings on a Japanese OS) in the PR.
   Do not claim it.

## Checklist

- [ ] Behaviour unchanged; polish in separate commits
- [ ] No hard-coded colours or button heights left in form JSON, except colours the demo is about
- [ ] Every custom colour has a dark-mode value
- [ ] No fake buttons, no Latin-only fonts on localised text
- [ ] Every form captured in each UI language, light and dark
- [ ] Unverified platforms listed in the PR
