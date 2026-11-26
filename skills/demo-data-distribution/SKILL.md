---
name: demo-data-distribution
description: >
  Decide how a 4D demo ships its data: estimate data-file size before
  generating, choose plain Git, Git LFS or a GitHub release asset, package
  Data.zip without logs and journals, verify it by extracting and querying
  headless, publish the release, and keep a backup outside the worktree.
  Use when a demo needs a large data file, vectors or generated records,
  or when Git / LFS limits come up.
---

# Demo Data Distribution

## Size Before You Generate

Estimate first; the answer decides the scale and the transport.

| Contribution | Estimate |
|---|---|
| Vector field | rows × dims × 4 bytes (float32) per field; 100k × 768 ≈ 300 MB, two fields ≈ 600 MB |
| Vector index (`.4DVI`) | of the order of the vectors it indexes |
| Text records | ≈ the source CSV size, plus indexes |

Observed: 100k tickets with two 768-dim vector fields gave 848 MB of
`Data/` and a 458 MB `Data.zip`.

Use realistic scale when the demo's point is performance (index vs scan
is invisible at 1k rows). Use small data when the point is a feature.

## Transport

| Size | Transport |
|---|---|
| file < 50 MB | plain Git (GitHub warns at 50 MB, rejects at 100 MB) |
| anything an attendee crowd will clone | **release asset** (2 GB per file) |
| Git LFS | avoid for shared demos: free bandwidth is 1 GB/month, used up by a few clones of a 500 MB file |

Check generated files (CSV seeds) on every regeneration: a 37 MB seed
grew to 47 MB.

## Package

1. Stop 4D (and helper servers) so the data file is closed.
2. Zip only `data.4DD`, `data.4DIndx` and `data.4DVI/`. Leave out `Logs/`, `*.journal`,
   `*.Match`, backups and `.DS_Store`.
3. Zip the `Data` folder itself, so extraction yields `Data/`.

```sh
ditto -c -k --keepParent --norsrc Data Data.zip   # macOS; then check the listing
unzip -l Data.zip
```

## Verify by Extracting

Extract to a temp folder and run a headless query (`4dcli`) against the
extracted copy, never the working copy: count the records and run one
indexed and one scan query, which must return the same hits.

## Publish

* `gh release create data-v1 Data.zip --title "Demo data" --notes "..."`.
  A **draft** release is invisible to attendees: publish it, then open the
  README's Releases link while logged out.
* The README says where to put the extracted folder (next to `Project/`).
* Version the tag (`data-v2`) when the schema or the model changes;
  embeddings from another model are incompatible.

## Backup

`Data/` is git-ignored (unless committed on purpose, `4dproject`), and
archiving a worktree deletes it. Keep a
verified copy of `Data.zip` (re-embedding took ≈ 8 min per 100k on
Apple Silicon, and longer elsewhere) outside the worktree until the
release is published and downloaded once.

## Checklist

- [ ] Size estimated before generating; scale matches the demo's point
- [ ] No file > 50 MB in Git; no LFS for attendee data
- [ ] Zip excludes logs, journal, Match files
- [ ] Extracted copy verified headless
- [ ] Release published (not draft); README link works logged out
- [ ] Backup outside the worktree
