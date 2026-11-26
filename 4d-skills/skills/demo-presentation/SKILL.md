---
name: demo-presentation
description: >
  Make a 4D demo work live in front of an audience, especially in Japan:
  typo-free sample inputs, visible comparisons, readiness shown in the
  form, separate UI-language and data-language decisions, Japanese
  wording and fonts, and what must be checked on a Japanese OS before the
  session. Use when preparing a demo for a webinar, seminar or
  presentation, or when localising a demo for a Japanese audience.
---

# Live Demo and Japanese Audience

## Live UX

| Pattern | Why |
|---|---|
| Sample inputs in a dropdown; index 0 is a localised placeholder ("質問の例…"); choosing an item fills the input **and runs** the action | no typing on stage, no IME mistakes |
| Free input still allowed | the audience asks "what about …?" |
| Show both sides of a comparison at once (last indexed ms / last scan ms) | the point survives a toggle |
| Readiness in the form: status line, action disabled until ready | no "is it frozen?" moments |
| Numbers formatted (`###,###,##0`) with units | readable from the back row |
| Window sized for 1280×800 projection, no scroll bars | nothing hidden |

Warm up before the session: open the demo once so the first-launch
downloads and the model load are already done.

## Language Decisions (ask early)

1. **UI language**: follows the OS; ship en + ja XLIFF (`4dlocalise`).
2. **Data language**: the corpus and the sample inputs may stay Japanese
   in both UI languages. Say so in the English README ("Japanese
   questions work best").
3. **Presentation language**: slides and talk; independent of 1 and 2.

## Japanese Wording

* UI labels: short noun phrases (検索, 類似度 ≥, ベクトルインデックスを使う);
  status messages in です/ます form only where they are sentences.
* Keep 4D and API terms that Japanese 4D users know in katakana or as-is
  (ベクトルインデックス, `4D.Vector`); do not translate method names.
* Japanese labels are often shorter but taller in some fonts: re-check
  label fit in both languages (`polish-ui-pass`).

## Verification Gaps

Record what was not seen in a real Japanese environment:

* tool4d `Localized string` with `SET DATABASE LOCALIZATION("ja")`
  returned English for built-in `Common*` strings: check them in 4D on a
  Japanese OS (or with the 4D language set to Japanese).
* GUI rendering on a Japanese OS (fonts, IME in inputs).
* Windows / Fluent UI if only a Mac was available.

## Checklist

- [ ] Sample inputs in a dropdown that runs on selection
- [ ] Comparison values visible side by side
- [ ] Demo warmed up (downloads and model load done) before the session
- [ ] UI / data / presentation language decisions recorded
- [ ] Verification gaps listed in the PR
