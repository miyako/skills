---
name: technote-localise-demo-data
description: >
  Replace a demo's sample data (e.g. foreign cities and landmarks) with
  equivalents relevant to the target audience, sourced from Wikidata, and
  recompute every example number in the translated text and figures. Use
  only after the user agreed to localise the data. Only applies in a 4D
  technote-localisation repository (one with technote.json at the root,
  created from miyako/4d-technote-localisation-template); do not use
  elsewhere.
---

# Localise demo data

> **Scope:** technote-localisation repositories only -- the repository root
> has a `technote.json`. The `make` targets, `src/`, `figures/`, `demo/` and
> `tools/` paths below belong to that template. In any other repository,
> do not use this skill.

## 1. Understand the current data
- Find the data files: JSON or CSV in the demo's `Resources/`, the `data/` folder, or files loaded by the startup
  or import code. Grep the 4D code for the file names to see how they are loaded and which fields are used.
- Write down the record format exactly: field names, types, nesting and coordinate order (`[lat, lon]` or
  `[lon, lat]`). Note the counts.
- List every place the data appears in the document:
  - the prose
  - ```` ```text ```` blocks
  - JSON examples
  - results tables
  - figure labels
  - counts ("100 sites")

## 2. Agree on the replacement (checkpoint)
Ask the user, with choices, about:
- the target country or region, and the equivalents of each example used in the text
  (e.g. the "reference city" of a worked example)
- the counts: keep the same number of records?
- the fields: keep all the original fields and **add** `name<Tgt>` (e.g. `nameJa`)? Recommended: keep the format
  identical so the demo code keeps working.
- where to keep the originals. Recommended: `data/<original>/` (or next to the new files), for reference.

## 3. Fetch from Wikidata
Use `tools/wikidata.py`:
- `query FILE.rq` tries `query.wikidata.org`, then falls back to QLever.
  - QLever needs explicit `PREFIX` lines.
  - Rank results by `?item wikibase:sitelinks ?l` to get the well-known items first.
- `entities Q1 Q2 … --langs en,fr,ja` returns labels, the coordinate (P625), population (the preferred P1082,
  otherwise the latest by P585) and the sitelinks count.

Query tips:
- Restrict by country (`wdt:P17 wd:Q17` = Japan) and require a coordinate (`wdt:P625`).
- **Places/landmarks:** filter on the relevant classes (`wdt:P31/wdt:P279*`), e.g. temples or shrines, castles,
  parks, museums, mountains, World Heritage sites, towers or gardens. Order by sitelinks.
- **Cities:** use the city classes for the country. Order by population. **Check that the capital and the
  major cities are included:** they are sometimes typed differently (e.g. Tokyo Q1490 is a prefecture, not a city).
- Remove duplicates, e.g. an area that duplicates its main monument, office buildings and non-tourist items.
  Tell the user what you excluded.
- Report empty labels per language.

## 4. Write the data
- Write the same format as the original, adding the new language field. Keep the encoding (UTF-8) and the same
  JSON formatting style.
- Update the demo's import code only if necessary, e.g. a file name changed or the new field must be stored.
  Follow the `technote-localise-4d-project` skill for 4D changes, and tell the user if the document's code blocks no longer match the
  demo.

## 5. Rewrite the examples in `src/<tgt>.md` and the figures
- Compute every number from the new data, with a script, never by hand:
  - **Distances:** haversine with R = 6371 km (or whatever the demo code uses), rounded the same way as the demo.
  - **DMS:** reproduce the demo's own conversion: degrees, integer minutes, rounded seconds, carry 60 → 1.
  - **Results tables:** run the same filter and sort as the demo (e.g. within the radius, sorted by distance).
- Replace in the prose, the ```` ```text ```` blocks, the results tables and the counts. **Never change
  non-`text` code blocks:** `make check` will refuse.
- Update the figure labels that show sample data, then `make review`.
- Leave `src/en.md` with the original examples (it is the untouched reference).

## 6. Verify and commit
- Grep `src/<tgt>.md` and `figures/*.<tgt>.txt` for the old place names and coordinates.
- `make`, review, commit the data and the text separately with clear messages. **Checkpoint:** show the user the
  new examples.
