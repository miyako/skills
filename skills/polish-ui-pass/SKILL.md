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
| 1 | Survey: form list, existing stylesheets, hard-coded colours and heights, window sizing | `4dform`, `4dcss` |
| 2 | Localise first (strings to XLIFF), so later layout is checked with real label lengths | `4dlocalise` |
| 3 | Stylesheet split: brand and typography in `styleSheets.css`; control heights per theme in `styleSheets_mac.css` / `styleSheets_windows.css` | `4dcss` |
| 4 | Header band and background: full-bleed, `rightMargin: 0` when a band spans the form | `4dform` (`references/form-concepts.md`) |
| 5 | Dark mode: every custom colour has a `prefers-color-scheme: dark` pair | `4dcss` (`references/dark-mode.md`) |
| 6 | Control heights: buttons and dropdowns ≥ 27 px under Liquid Glass; Fluent UI not verified (say so) | `4dcss` (`references/form-themes.md`) |
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
* Button height: 27 px for `liquid-glass`, 23 px for `mac-classic`
  (the Windows sheet mirrored this unverified).

## Verify

1. `fourdform` quick preview and the 4dform done-gate for structure.
2. Real rendering with 4D in the background, captured by window ID with
   no clicks or keystrokes (`4dcli`, `references/shared-desktop.md`).
3. For each UI language (en, ja): no truncated labels, no clipped
   buttons, no horizontal list-box scroll bar.
4. Light and dark appearance.
5. Write down what you could not verify (Windows / Fluent UI; ja `Common*`
   strings in tool4d) in the PR. Do not claim it.

## Checklist

- [ ] Behaviour unchanged; polish in separate commits
- [ ] No hard-coded colours or button heights left in form JSON
- [ ] Every custom colour has a dark-mode value
- [ ] Every form captured in each UI language, light and dark
- [ ] Unverified platforms listed in the PR
