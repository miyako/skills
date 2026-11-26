---
name: 4dembeddings
description: >
  Local text embeddings for 4D vector search: running a GGUF model with the
  miyako/llama-cpp component and calling it through 4D AI Kit (no API key,
  no AIProviders.json), downloading models from Hugging Face, model prefixes,
  server lifecycle in GUI and headless runs, and the acceptance test every
  embedding model must pass before data is built (GGUF tokenizer metadata,
  <unk> pieces from /tokenize, precision@10 on the real corpus). Use when
  choosing, adding or debugging an embedding model.
---

# 4D Local Embeddings

## Scope

* a self-contained local embedding model: component setup, class pattern
* choosing a model and proving it works **before** embedding the data
* starting and stopping the llama.cpp server without orphans

### Not in this skill

| Topic | Skill |
|---|---|
| AI Kit calls, async callbacks | `4daikit` |
| Vector fields and the vector index in the catalog | `4dcatalog` |
| Vector queries, thresholds, sanity check | `4dorda` (`references/queries.md`) |
| Calibrating a demo threshold, timing indexed vs scan | `demo-vector-search` |
| Declaring components, `Components/` staging | `4dproject` (`references/dependencies.md`) |
| Process hygiene on a shared desktop | `4dcli` (`references/shared-desktop.md`) |

## Setup

`Project/Sources/dependencies.json` declares `4d/4D-AIKit` and
`miyako/llama-cpp` with the components it needs (`miyako/event`,
`miyako/workers`, `miyako/tcp`, `miyako/hash`); take the versions from
their releases (`4dproject`, `references/component-releases.md`).

Wrap the model in one class (`cs.EmbeddingModel`) holding: port,
Hugging Face repository and file, local folder (`~/.GGUF/<repo>`), model
name, and the query/document prefixes. Its functions:

| Function | Does |
|---|---|
| `isReady()` | `GET /health` with a 2 s timeout; status 200 |
| `start()` | if not ready: start `cs.llama.llama` from the local file, or let it download the file first; report status through callbacks (`cs.event.event`: `onData` progress, `onSuccess`, `onError`, `onTerminate`) |
| `stop()` | `cs.llama.llama.new(port).terminate()` if ready |
| `embedQuery` / `embedDocuments` | `cs.AIKit.OpenAI.new({baseURL: "http://127.0.0.1:<port>/v1"; apiKey: "local"}).embeddings.create(prefix+text; model)` |

Server options that worked for a 768-dim model: `embeddings: True`,
`pooling: "mean"`, `ctx_size`/`batch_size`/`ubatch_size` 8192,
`n_gpu_layers: -1`. Callbacks run in other processes: forward status to
the form with `CALL FORM` (`4dform`, `references/async-ui.md`).

Check the model card for **prefixes**: ruri-v3 expects `検索クエリ: ` on
queries and `検索文書: ` on documents; e5 uses `query: ` / `passage: `.
Missing prefixes cost accuracy silently.

## Downloading from Hugging Face

Use `https://huggingface.co/<repo>/resolve/main/<file>` with `curl -fL`.
Other URL shapes returned a 55 KB HTML page that was saved as `.gguf`;
`check_gguf.py` reports such a file as "not a GGUF file".

## Acceptance Test (mandatory)

"It returns 768 numbers" proves nothing. A mis-converted ruri-v3 GGUF
passed that smoke test and gave near-random retrieval. Before building
data, run all three:

1. **Tokenizer metadata.** The GGUF `tokenizer.ggml.model` must match the
   original `tokenizer.json` `model.type`: Unigram → `llama`/`t5`,
   WordPiece → `bert`, BPE → `gpt2`.
2. **Domain tokens.** `/tokenize` with `with_pieces` on a few real
   sentences: any `<unk>` rejects the model.
3. **Retrieval quality.** Precision@10 for ~6 natural queries over a
   1-2k random sample of the real corpus, judged by reading the hits.
   Also look at the score spread (top vs median): "hub" documents topping
   every query and a high floor mean the embeddings are broken.

Steps 1-2 are scripted (stdlib only; start any llama-server on the model
first for `--server`):

```sh
python3 skills/4dembeddings/scripts/check_gguf.py ~/.GGUF/<repo>/<file>.gguf \
  --expect unigram --server http://127.0.0.1:18083 --text "プリンターで印刷できない"
```

Observed:

| Model (GGUF q8) | Check | p@10 (6 queries, ja tickets) | Scores |
|---|---|---|---|
| `keisuke-miyako/ruri-v3-310m-gguf-q8_0` | `bert` label on a SentencePiece vocab; `['<unk>',' 印',' 刷','<unk>']` | 36/60 | floor ≈ 0.8-0.9 |
| `Targoyle/ruri-v3-310m-GGUF` | `llama`; clean pieces | 58/60 | top ≈ 0.9, median ≈ 0.80 |
| bge-m3 | -- | 58/60 | top ≈ 0.7, median ≈ 0.45; 1024 dims, 2× slower |
| multilingual-e5-base | -- | 56/60 | top ≈ 0.88, median ≈ 0.80 |

Do not use the `keisuke-miyako` ruri-v3 GGUFs (all sizes) until they are
re-converted with a SentencePiece vocabulary.

## Lifecycle

* Start in the main form's `On Load`; show download/loading/ready in the
  form; disable search until ready.
* Stop in `On Exit`.
* Headless builds: stop only a server **this run** started, before
  `QUIT 4D` (`4dcli`, `references/shared-desktop.md`).

Throughput observed on Apple Silicon (q8, batch 128): 100k Japanese
tickets in ≈ 8 min; vector index build 100k × 768 ≈ 19 s.

## Checklist

- [ ] Model passes the three acceptance steps; results recorded
- [ ] Prefixes from the model card applied to queries and documents
- [ ] No git-ignored provider file needed to run
- [ ] First launch shows download progress; search disabled until ready
- [ ] Server stopped in `On Exit` and at the end of headless runs
