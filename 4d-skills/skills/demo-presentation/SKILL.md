---
name: demo-presentation
description: >
  Make a 4D demo work live in front of an audience, especially in Japan:
  typo-free sample inputs, visible comparisons, readiness shown in the
  form, separate UI-language and data-language decisions, Japanese
  wording, and what must be checked on a Japanese OS (fonts, IME,
  built-in strings) before the session. Use when preparing a demo for a webinar, seminar or
  presentation, or when localising a demo for a Japanese audience.
---

# Live Demo and Japanese Audience

## Related

| Topic | Skill |
|---|---|
| Start screen, language toggle, side-by-side windows | `demo-launcher` |
| Old vs new technique, before/after captures | `demo-feature-comparison` |
| Shareable repository, README | `demo-shareable-repo` |

## Live UX

| Pattern | Why |
|---|---|
| Sample inputs in a dropdown; index 0 is a localised placeholder ("質問の例…"); choosing an item fills the input **and runs** the action | no typing on stage, no IME mistakes |
| Free input still allowed | the audience asks "what about …?" |
| Show both sides of a comparison at once (last indexed ms / last scan ms) | the point survives a toggle |
| Readiness in the form: status line, action disabled until ready | no "is it frozen?" moments |
| Numbers formatted (`###,###,##0`) with units | readable from the back row |
| Window sized for 1280×800 projection, no scroll bars | nothing hidden |
| Cancel leaves nothing behind (no blank row after "New" → Cancel) | the audience notices; `4dorda`, "Save only on confirmation" |

Warm up before the session: open the demo once so the first-launch
downloads and the model load are already done.

## Language Decisions (ask early)

1. **UI language**: follows the OS; ship en + ja XLIFF (`4dlocalise`).
   Add an in-app switch when the presenter shows both languages or
   attendees run a 4D in another language (`4dlocalise`).
   Localising a whole demo end to end: `demo-localise`.
2. **Data language**: the corpus and the sample inputs may stay Japanese
   in both UI languages. Say so in the English README ("Japanese
   questions work best").
3. **Presentation language**: slides and talk; independent of 1 and 2.

## Japanese Wording

Typography and wording rules (spacing around Latin words, full-width
colons, API names kept in Latin script, quoted button names matching the
labels) are in `skills/4dlocalise/references/japanese.md`. For a demo,
also:

* Sample inputs read naturally to a Japanese audience (類似度 ≥,
  ベクトルインデックスを使う); no machine-translated phrasing on screen.
* Keep the series or product brand the owner keeps in English (the HDI
  "How do I..." title); ask.
* Re-check label fit in both languages (`polish-ui-pass`).

## Appearance

Pin `"colorScheme"` (`"light"` or `"dark"`) on **every** demo form,
launchers and dialogs included, as a deliberate choice for the projector.
A launcher left on automatic, on a machine in dark mode, got white text
from its dark CSS rules on a light background in captures. When the
scheme is pinned, remove the other scheme's media query for those forms;
if the demo must support both, capture both. This is a decision about the
deliverable, not a capture trick (`4dcli`).

## Verification Gaps

Record what was not seen in a real Japanese environment:

* Built-in `Common*` strings ignore `SET DATABASE LOCALIZATION("ja")` (tool4d
  and the 4D GUI): a runtime language switch needs project IDs
  (`4dlocalise`). Their behaviour on a Japanese OS is unverified.
* Dates in list boxes follow the OS format, not the UI language.
* GUI rendering on a Japanese OS (fonts, IME in inputs).
* Windows / Fluent UI if only a Mac was available. When Fluent UI is the
  subject of the demo, get Windows captures before the talk.

## Checklist

- [ ] Sample inputs in a dropdown that runs on selection
- [ ] Comparison values visible side by side
- [ ] Demo warmed up (downloads and model load done) before the session
- [ ] UI / data / presentation language decisions recorded
- [ ] `colorScheme` pinned on every demo form (or both schemes captured)
- [ ] Verification gaps listed in the PR
