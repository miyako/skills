---
name: technote-apply-glossary
description: >
  Change a term or proper noun consistently across the glossary, the
  translated text and the figure label files. Use when the user changes
  terminology or asks to make wording consistent. Only applies in a 4D
  technote-localisation repository (one with technote.json at the root,
  created from miyako/4d-technote-localisation-template); do not use
  elsewhere.
---

# Apply a glossary change

> **Scope:** technote-localisation repositories only -- the repository root
> has a `technote.json`. The `make` targets, `src/`, `figures/`, `demo/` and
> `tools/` paths below belong to that template. In any other repository,
> do not use this skill.

1. Re-read `glossary.md` (the user may have edited it). Update or add the row: `| English | <tgt> | Notes |`.
2. If the user asked only to commit the glossary, commit it alone first.
3. Find the occurrences of the old term:
   ```sh
   grep -n "<old>" src/<tgt>.md figures/*.<tgt>.txt
   ```
   Also check inflected or compound forms. For Japanese, the term inside longer compounds: e.g. 観光地 inside
   観光地名. Report the counts per file to the user.
4. Replace only after confirmation. Respect the context: don't change code blocks, inline code or quoted UI strings
   that must match the demo. Show any ambiguous cases to the user instead of replacing them.
5. If figure labels changed: `make figures`, then `make review FIGS="…"` for the affected figures (labels may now
   be longer).
6. Run `make`, then commit: "Glossary: <old> → <new>".
