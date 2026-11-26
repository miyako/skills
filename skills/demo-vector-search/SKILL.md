---
name: demo-vector-search
description: >
  Build and present a 4D vector-search demo: realistic corpus scale, a
  real vector index (not a B-tree on a vector field), headless data build
  in batches, per-model threshold calibration on the real corpus, timing
  indexed vs full-scan queries side by side, a brute-force sanity check,
  and README numbers. Use when creating, fixing or presenting a demo of
  4D.Vector fields, vector indexes or semantic search.
---

# Vector-Search Demo

## Related

| Topic | Skill |
|---|---|
| Embedding model choice and acceptance test | `4dembeddings` |
| Vector field and index in the catalog | `4dcatalog` |
| Vector query syntax | `4dorda` (`references/queries.md`) |
| Shipping the data | `demo-data-distribution` |

## Data

* Generate a realistic corpus (tickets, FAQs, products) at the scale the
  point needs: 100k rows made the index ≈ 18× faster than a scan; at 1k
  rows there is nothing to see.
* Keep a plain `Vector` and an `IndexedVector` field with identical
  values, so the same query can run both ways.
* Check the catalog: the indexed field must carry a vector index
  (`type="20"`), on a table that is not in the trash (`4dcatalog`). An
  inherited demo had `type="3"` on both fields, so it compared two scans.

## Build (headless)

`BuildDemoData` started with tool4d `--startup-method` and
`--user-param '{"quit":true}'`:

1. Drop the vector index (faster import).
2. Import the seed with `fromCollection` in batches of 128 rows, embedding
   each batch with the document prefix (`4dembeddings`).
3. `CREATE INDEX` with the vector-index type and the cosine metric.
4. Stop the embedding server only if this run started it, then `QUIT 4D`.

Test on 200 rows first. Observed for 100k × 768 (q8, Apple Silicon):
embedding 494 s, index 18.7 s.

## Calibrate the Threshold

Cosine scales differ per model: ruri-v3 puts unrelated texts at ≈ 0.8,
so a 0.01 step changes hit counts tenfold. Probe on the real data:

| threshold | for each sample question: hits indexed / scan, ms indexed / scan |
|---|---|

Pick a threshold where every sample question returns tens to a few
thousand hits. Observed (ruri-v3-310m, 100k): 0.85 → 1.9k-7.3k; **0.87 →
48-3.5k (chosen)**; 0.88 → one query down to 1; 0.90 → 0 for two
queries. Loose thresholds erase the index advantage (indexed ≈ 2 s vs
scan ≈ 4 s when most rows match).

## Sanity Check

When results look wrong, separate "index wrong" from "embeddings wrong"
with the brute-force comparison in `4dorda` (`references/queries.md`).
Identical order = the index is fine; look at the model (`4dembeddings`).

## Present

* Sample questions in a dropdown (`demo-presentation`).
* Show **both** last timings ("indexed 142 ms / scan 2,431 ms") so the
  difference stays visible after toggling.
* A score column (`This.Vector.cosineSimilarity(Form.queryVector)`) makes
  the threshold meaningful.
* Quote the measured hit counts and timings in the README.

## Checklist

- [ ] Embedding model passed the `4dembeddings` acceptance test
- [ ] Indexed field has a real vector index on a live table
- [ ] Threshold calibrated on the shipped data; values in README
- [ ] Indexed and scan return the same hits; both timings shown
