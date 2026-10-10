---
name: technote-localise-4d-project
description: >
  Localise the 4D demo project(s) under demo/ of a technote-localisation
  repository for the target language: the survey-and-plan checkpoint,
  which generic 4D skills to apply, headless verification with the
  repository's tools/tool4d.py, and how to split the commits. Use for any
  change to demo/**. Only applies in a 4D technote-localisation repository
  (one with technote.json at the root, created from
  miyako/4d-technote-localisation-template); do not use elsewhere.
---

# Localise the 4D demo project

> **Scope:** technote-localisation repositories only -- the repository root
> has a `technote.json`. The `demo/`, `tools/` and `make` paths below belong
> to that template. In any other repository, do not use this skill; use the
> generic 4D skills directly.

This skill is the technote-specific wrapper. The 4D know-how lives in the
generic skills, which apply to `demo/**`:

| Topic | Skill |
|---|---|
| XLIFF, `:xliff:`, `Localized string`, names that follow the UI language | `4dlocalise` |
| Startup / splash window, chaining forms (no blocking `DIALOG` chains) | `4dstartup` |
| `C_*` → `var` / `#DECLARE`, deprecated commands | `4dmodernise` |
| Method visibility | `4dmethods` |
| List box defaults, form JSON | `4dform` |
| Stylesheets, dark mode, Liquid Glass | `4dcss` |
| `menus.json`, `.gitignore`, version, token suffixes | `4dproject` |
| `.4dm` syntax | `4dlsp` |

## 0. Survey first, then make a plan (checkpoint)

Survey the project as described in "Survey first" in
`skills/4dlocalise/SKILL.md` (forms and their strings, user-facing strings in
code, per-language fields in `catalog.4DCatalog`, `On Startup` /
`On Server Startup` and any chained `DIALOG` calls). Present the plan and
ask about: scope (UI labels only, or data and messages too), languages,
new attributes (e.g. `nameJA`), whether displayed names should follow the
UI language, and whether to track `Settings/` in git.

## 1. Git hygiene

* The template's `.gitignore` already excludes `demo/*/Data/`,
  `userPreferences.*/`, `Project/DerivedData/` and `Logs/`; compare with the
  canonical list in `skills/4dproject/SKILL.md` and add what is missing.
* Preserve each 4D file's line endings (they mix CRLF and LF); never convert
  in bulk.

## 2. Verify headlessly with `tools/tool4d.py` (when available)

The template ships `tools/tool4d.py`, which runs tool4d on a **temporary
copy** of the project, never on the repository:

```sh
python tools/tool4d.py demo/<Name> --compile           # full compile: expect success true, no errors
python tools/tool4d.py demo/<Name> test.4dm [--data]   # run a custom test method
```

* Check individual `.4dm` files with `4dlsp` while editing; use `--compile`
  for a whole-project compile before committing (see "Syntax checking vs
  running code" in `skills/4dlsp/SKILL.md`).
* A test method writes its results to `File("/PACKAGE/agent-test.txt")` and
  then calls `QUIT 4D` (acceptable here: it runs headless in a throw-away
  copy). Useful tests: the XLIFF test in `skills/4dlocalise/SKILL.md`, the
  `orderBy` test in `skills/4dlocalise/references/language-attributes.md`,
  and a data import with `--data` (check counts and that new fields are
  filled).
* When tool4d is not available (e.g. the cloud agent), say clearly that the
  4D code was not compiled. Forms cannot be shown headlessly: ask the user to
  open the project in 4D and check the window flow, label fit (Japanese
  labels can be longer or shorter) and list box columns.

## 3. Commit

Commit each concern separately -- XLIFF, attributes, startup UX, data -- with
messages that explain the user-visible effect.
