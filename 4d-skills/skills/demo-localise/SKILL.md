---
name: demo-localise
description: >
  Ordered route for localising an attendee-shared 4D demo end to end (for
  example English source plus Japanese): the decisions to ask first,
  strings out of forms, code and the data file into XLIFF, the language
  switch, companion browser pages with their own language selection,
  Japanese review, per-language verification and the bilingual README.
  Routes each step to the owning skill. Use when asked to localise a demo,
  webinar or seminar project.
---

# Localising a Demo

This skill orders the work and routes it; the owning skill holds the
rules. Localise **before** polishing (`polish-ui-pass` step 2), so layout
is checked with real label lengths.

## Ask first

Ask the owner, one question at a time, and record the answers in the PR.
Defaults that one en/ja seminar demo chose (21 R5, Japan):

| Decision | Default |
|---|---|
| Source language | English source, `ja` XLIFF targets |
| UI language | follows the OS, plus an "English \| 日本語" switch on the start screen |
| Data and sample inputs | decided separately (`demo-presentation`, "Language Decisions") |
| Appearance | native themes (Liquid Glass, Fluent UI), dark-mode safe, real buttons (`polish-ui-pass`) |
| Series brand | kept in English (e.g. "How do I…"; `demo-hdi`) |

## Order

| # | Step | Owner |
|---|---|---|
| 1 | Survey: forms, methods, menus, alerts, served pages, and text stored in the data file; which strings are the demo's subject | `4dlocalise`, `4dproject` |
| 2 | Form and code strings to XLIFF (`:xliff:` IDs, `Localized string`) | `4dlocalise` |
| 3 | Text kept in the data file (help pages, tab titles) to XLIFF | `4dlocalise` (`references/data-text-migration.md`) |
| 4 | Language switch on the start screen; next form opened without breaking its `formClass` | `4dlocalise`, `4dstartup`; HDI splash: `demo-hdi` |
| 5 | Decide whether companion browser pages follow the native UI language or use the browser language and a persistent selector | `references/browser-localisation.md`; implementation details: `4dlocalise` (`references/web-pages.md`) |
| 6 | Japanese review: typography, wording, button names quoted exactly | `4dlocalise` (`references/japanese.md`), `demo-presentation` |
| 7 | Verify: `xliff_check.py`, runtime test per language, renders per language (light and dark once polished) | `4dlocalise` ("Verification"), `4dform` |
| 8 | Bilingual README (日本語 first, then English) | `demo-shareable-repo` (`references/readme.md`) |

## Chokepoints seen

* Text in a committed binary data file is invisible to greps of the
  project; look for queries feeding labels (step 3).
* Forms with a `formClass` lose their class functions when `DIALOG` gets
  an object (`4dstartup`).
* Styled-text sources carry `<span>` markup and CR line breaks; generate
  XLIFF with a script, not by hand (`4dlocalise`, "Styled text").
* Built-in `Common*` strings ignore a runtime language switch
  (`4dlocalise`).
* Native UI language and browser-page language are separate choices.
  Do not assume changing 4D's localization changes a page already open
  in a browser (`references/browser-localisation.md`).

## Checklist

- [ ] Decisions asked and recorded
- [ ] No user-facing literal left in forms, code, menus or the data file
- [ ] `xliff_check.py` clean; every unit has a `ja` target
- [ ] Switch reopens the start screen in the other language
- [ ] Served pages follow the 4D language
- [ ] Every form rendered in each language; no clipped Japanese text
- [ ] README in both languages says which language the data uses
