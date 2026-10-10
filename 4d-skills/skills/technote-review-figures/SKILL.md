---
name: technote-review-figures
description: >
  Visually review and fix localised figures (diagram text overlays) using
  contact sheets and per-label layout overrides. Use after translating
  figures/fig-NN.<tgt>.txt, when the user reports a figure problem, or
  before release. Only applies in a 4D technote-localisation repository
  (one with technote.json at the root, created from
  miyako/4d-technote-localisation-template); do not use elsewhere.
---

# Review localised figures

> **Scope:** technote-localisation repositories only -- the repository root
> has a `technote.json`. The `make` targets, `src/`, `figures/`, `demo/` and
> `tools/` paths below belong to that template. In any other repository,
> do not use this skill.

1. `make review` (or `make review FIGS="03 07"`) builds `build/contact-N.png`, with the original above the localised
   version, three figures per sheet. Look at each sheet: the image viewer shows one image per call.
2. For each figure, check:
   - **leftovers:** fragments of the English text not erased (the OCR box is too small, so enlarge `box` or `erase_pad`)
   - **collateral erasure:** arrows, dots, borders or icons removed (the box is too large, so shrink `box` or shift `dx`)
   - **clipping or overflow:** text outside its shape (shorten the translation first; otherwise `size` or `scale`)
   - **hierarchy:** titles larger than items, consistent sizes within a group (`scale`, `weight`)
   - **alignment:** list-like labels left-aligned (`align: "left"`), centred labels centred
   - **colour:** text colour matches the original (`fg`); background patched cleanly (`bg`)
   - **content:** identifiers, code and numbers unchanged unless the demo data changed
3. Fix by editing `figures/layout/fig-NN.json` → `items[N]` (N = 0-based line index), then `make figures` and
   `make review FIGS="NN"` again.
   - Overrides: `scale`, `size` (px), `weight` (`light`/`regular`/`bold`), `align` (`left`/`center`), `dx`, `dy`,
     `box` `[x,y,w,h]` in image pixels, `bg`/`fg` `[r,g,b,a]`, `erase_pad`.
   - If OCR merged two labels into one line: split the line in `fig-NN.<src>.txt` and `fig-NN.<tgt>.txt`, and give
     each new item an explicit `box`. Measure the boxes on the original image, e.g. crop it with PIL and view it.
   - To merge two lines into one label: put the full text on the first line, leave the second empty, and enlarge
     the first `box` if needed.
4. Screenshots of the app UI (`"localize": false`): don't overlay text. Ask the user for a screenshot of the
   localised app, save it as `figures/fig-NN-<tgt>.png` and set `"replace": "fig-NN-<tgt>.png"`.
5. Finally, run `make` and spot-check the PDF pages with the changed figures: render them with pymupdf
   `page.get_pixmap(dpi=80)` and view.
6. Commit with a message listing the figures that were changed.
