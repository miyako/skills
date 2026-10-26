---
name: technote-localise-screenshots
description: >
  Mechanically localise screenshot text using authoritative 4D or demo
  XLIFF strings and context-correct fonts, preserving nontext pixels.
  Distinguish 4D UI, demo UI, browser content/chrome and native OS dialogs;
  use full GUI 4D capture when rendering is uncertain. Use for screenshot
  figures, not diagram overlays. Only applies in a 4D technote-localisation
  repository (technote.json at the root, created from
  miyako/4d-technote-localisation-template); do not use elsewhere.
---

# Localise screenshots

> **Scope:** technote-localisation repositories only -- the repository root
> has a `technote.json`. All `figures/`, `demo/`, `build/` and `tools/`
> paths below belong to the consumer repository, not the skillset.

This skill owns screenshot text replacement and its evidence. Use existing
image/text tools and small task-specific scripts, not a new imaging
framework. Do not use generative image recreation, inpainting, or a generic
diagram overlay to approximate application UI.

## Related skills

| Task | Owner |
|---|---|
| Demo localisation and its survey/approval checkpoints | [technote-localise-4d-project](../technote-localise-4d-project/SKILL.md) |
| Demo XLIFF IDs, object-name groups, language switching | [4dlocalise](../4dlocalise/SKILL.md) |
| Running full GUI 4D and runtime form captures | [4dcli](../4dcli/SKILL.md) (Task Router, then the selected sections) |
| Validating any approved `.4dm` change | [4dlsp](../4dlsp/SKILL.md) |
| Glossary changes and confirmation | [technote-apply-glossary](../technote-apply-glossary/SKILL.md) |
| Contact sheets, diagram overlays and PDF review | [technote-review-figures](../technote-review-figures/SKILL.md) |

## 1. Inventory and agree the scope (checkpoint)

Read the consumer's `AGENTS.md`, glossary, `technote.json`, pipeline
reference and figure layout. Respect its translation checkpoints. Confirm
source/target locale, which figures and labels may change, and whether
mechanical replacement or a matching native capture is appropriate.
Preserve code, identifiers, paths and displayed values unless an approved
demo-data change requires otherwise.

For each screenshot, record the original file hash, dimensions and colour
mode; application/build, OS/version, locale, theme, display scale/DPI and
zoom; and the form/window/page/state shown. Mark unknown facts as unknown.
Classify **each text region**, not just the whole image:

| Region | Text authority | Font/rendering evidence |
|---|---|---|
| 4D's own UI, menus and built-in dialogs | Matching full 4D / 4D Server installation's target-language resources | That product/build on the pictured OS, theme and scale |
| Demo form, menu or demo-generated message | Demo's already translated resource and form/object/XLIFF reference | Form properties/styles plus runtime resolution and fallback |
| Browser page content | Localised page/application resources | Computed CSS, loaded webfont, weight and actual glyph fallback at the recorded browser zoom/device scale |
| Browser chrome | Matching browser/version/locale resources or actual localised UI | Browser chrome's own rendering, not page CSS |
| Native OS dialog, including one opened by 4D/browser | Matching OS/version/locale UI or resources | Actual native control and OS font/fallback at that DPI |

Do not translate a quoted official UI label from a glossary in preference
to its authoritative resource. Report a glossary/resource mismatch and
request confirmation; do not silently rewrite either. If the demo has not
yet been localised, route that work to `technote-localise-4d-project` first,
rather than inventing a second screenshot-only translation.

## 2. Resolve authoritative strings before drawing

### 4D's own UI: discover a local full installation

Locate an existing full **4D or 4D Server**, on the relevant platform and
version. `tool4d` is English-only and is not a target-language UI resource
authority. Check user-provided install locations first, then bounded
platform install locations if necessary. Inspect the actual installation;
do not guess a version-specific bundle resource path or treat the first
matching English string as a translation.

These are discovery examples, not promises about installation layout.
Set the variables to an **observed, user-approved installation root**:

```sh
# macOS: after identifying the full app's installation directory.
find "$APP_ROOT" -type f -iname '*.xlf' -print
rg -n -F --glob '*.xlf' -- "$SOURCE_LABEL" "$APP_ROOT"
```

```powershell
# Windows: after identifying the full application's installation directory.
Get-ChildItem -LiteralPath $AppRoot -Recurse -File -Filter *.xlf |
  Select-String -SimpleMatch -Pattern $SourceLabel
```

Search results are **candidates only** (XML escaping and line breaks can
hide matches). Parse candidate `.xlf` files with a namespace-aware XML
parser, inspect the file's source/target language and its actual structure,
and extract the complete source/target text, including inline content.
Resolve the screenshot label to the exact source, ancestor group/context,
`trans-unit` ID and `resname` where present. Disambiguate duplicates by
menu/dialog/control and version; retain placeholders, punctuation, case,
accelerators and line-break semantics, distinguishing resource markup from
what the UI actually displays. Record the selected target-language file
and entry, not just a search snippet. Empty/missing targets, unsupported
locale/version and unresolved duplicates are blockers, not permission to
guess.

Do not copy app bundles, bulk resource dumps or proprietary fonts into the
consumer repository or this skill. Keep only the minimal task mapping and
resource provenance needed to reproduce the selected labels.

### Demo UI: reuse its existing translation

Trace the visible control to its form and object, menu entry or runtime
assignment, then to its `:xliff:` / `Localized string` ID or object-name
group using `4dlocalise`. Record the relevant form/object and resource
path, group/ID, source and existing target. Resolve built-in `Common*`
entries through the matching full 4D resources rather than redefining
them in the demo.

Match the demo version and approved data state. Do not translate code,
object names, record values or placeholders merely because OCR found
them. Do not modify demo `.4dm` files, forms or startup behaviour just to
obtain a capture without approval.

## 3. Establish fonts and geometry (checkpoint)

For each region, record the font's actual family/face, version or local
file provenance, weight, size in image pixels, baseline, alignment,
foreground, line spacing and glyph fallback. Confirm the required font
and target-language glyphs exist locally. A CSS family list or a generic
system-font name alone does not prove which face rendered the text.

Use the actual context/version/locale: macOS may resolve Latin UI through
SF and Japanese through Hiragino; Windows may use Segoe UI with Yu Gothic
or Meiryo depending on the OS and control. These are examples to
investigate, **not defaults**. A 4D form's explicit font can differ from
4D chrome, a web page from browser chrome, and an OS dialog from both.
Account for font fallback per script, DPI/Retina scaling, browser zoom,
hinting, antialiasing and theme. Check font-loading success and glyph
coverage explicitly; do not accept a renderer's silent substitution or
missing-glyph boxes.

Measure the complete authoritative label before editing. Do not arbitrarily
shrink, condense or abbreviate official labels to make them fit. If a
target UI genuinely wraps, resizes or changes control geometry, establish
that through its native rendering. Otherwise stop for confirmation of
the fit problem; do not redesign the screenshot.

Native capture is a verification/fallback path, **not an unconditional
prerequisite** when text, fonts and rendering are already established.
If the app, font, platform or matching version is missing, report exactly
what is unavailable and use `ask_user` for the required evidence or manual
confirmation. Do not download applications/fonts or claim fidelity.

## 4. Replace text mechanically

Keep `figures/fig-NN.png` byte-for-byte unchanged. Work from it each time;
never iteratively edit a previous translated raster.

Use deterministic text/image processing with existing tools (for example
Pillow/ImageMagick and a suitable installed text shaping engine). Record
tool versions, font selection, shaping/fallback behaviour and exact
parameters. Use OCR only to locate candidate regions; manually verify its
text and boxes against the original.

* Define precise erasure masks including old glyph antialiasing/halos,
  and separate draw masks. Preserve icons, borders, shadows and nearby
  labels. Use a measured flat background only where it really is flat.
* On gradients, textures, transparency or overlapping controls, use a
  justified deterministic restoration from matching untouched background
  pixels or a matching native capture. Never cover a complex background
  with an indiscriminate flat rectangle. If faithful restoration cannot
  be established, stop and use the capture/confirmation gate.
* Shape and render the exact resolved text with the verified fonts and
  geometry. Keep original scale, appearance, colour profile and nontext
  pixels. Record any unavoidable encoding/profile change explicitly;
  do not silently flatten or rescale.
* Save the deterministic replacement as `figures/fig-NN-<tgt>.png`.
  Keep the masks, label mapping, replay command/script and font evidence
  in the consumer's approved figure-artifact location, scoped to these
  figures (not generic app/font dumps).

Inspect the consumer renderer before changing configuration. The template
has global figure fonts, **no per-item `font` key**; do not invent one or
change global diagram fonts to approximate screenshot typography.
In `figures/layout/fig-NN.json`, preserve other fields and set:

```json
{
  "localize": false,
  "replace": "fig-NN-<tgt>.png"
}
```

Keep `localize: false` so generic diagram overlays never process the
screenshot. Do not wire an unreviewed replacement into final output:
complete the next gate first.

## 5. Verify uncertain rendering with actual UI

When font resolution, fit or runtime appearance is uncertain, use
`4dcli`'s Task Router to run the **full GUI 4D** from the CLI and capture
the relevant rendered window/state in the target locale. Follow that
skill's invocation protocol, method-installation approval and output
checks; do not invent CLI flags here. Validate any approved `.4dm`
changes through `4dlsp`. Work in an approved temporary project copy where
possible; do not alter the demo or user data merely for capture.

A `tool4d`/Form Editor snapshot is not proof of runtime or native-dialog
rendering. Even a runtime form screenshot may omit native dialogs or
application chrome: capture the actual task window/control on the matching
platform when those are at issue. For browser content/chrome or OS dialogs,
use the corresponding actual application and native capture.

Capture only the task window or crop/mask immediately to the required
region. Exclude unrelated windows, notifications, private files and user
data before retaining or sharing evidence. A replacement native capture
must match the original state, framing, dimensions, theme and scale; do
not silently accept unrelated visual changes.

If native rendering still cannot be established, use `ask_user` with the
specific unresolved label/font/region and request manual confirmation or
a matching capture. **Stop that figure** until answered. Mark manually
accepted approximations as such; never describe them as runtime-verified.

## 6. Review and repeatability gate

Before enabling `replace`, verify:

* Every changed label has source/target provenance and an unambiguous
  context/ID mapping; approved glossary and demo wording agree.
* Original hash is unchanged; replacement dimensions and scale match.
  A decoded-pixel diff against the original has no changes outside the
  approved erasure/draw masks. Investigate every unexpected change.
* At native resolution and magnified crops, no source glyph fragments,
  collateral erasure, clipping, missing glyphs, font substitutions or
  altered code/values remain. Review native evidence where required.
* Re-running from the unchanged original with the recorded resources,
  fonts and parameters reproduces the output (compare decoded pixels;
  compare file hashes too when the encoder is deterministic).

Then set `replace`, run `make figures` and `make review FIGS="NN"`,
and follow `technote-review-figures` for contact-sheet/PDF review with
`make`. Report which figures passed mechanical checks, which have actual
runtime evidence, and which remain blocked/manual-only. Commit only
approved outputs and minimal reproducibility artifacts, listing the
figures changed; never call an unresolved screenshot verified.
