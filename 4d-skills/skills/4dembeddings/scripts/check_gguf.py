#!/usr/bin/env python3
"""Acceptance check for a GGUF embedding model (stdlib only).

  check_gguf.py MODEL.gguf [--expect unigram|wordpiece|bpe]
                [--server http://127.0.0.1:PORT --text "domain sample" ...]

1. Reads the GGUF metadata: architecture, tokenizer.ggml.model, vocabulary
   size and the share of tokens carrying the SentencePiece "▁" prefix.
   A WordPiece label ("bert") on a SentencePiece vocabulary is a broken
   conversion.
2. --expect: the tokenizer type of the original model (tokenizer.json
   "model.type" on Hugging Face) must match the GGUF label.
3. --server: POSTs each --text to llama-server /tokenize (with_pieces)
   and fails on any <unk> piece.

Exit status 1 on any failure.
"""
import argparse
import json
import struct
import sys
import urllib.request

SCALAR = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?",
          10: "Q", 11: "q", 12: "d"}
EXPECT = {"unigram": {"llama", "t5"}, "wordpiece": {"bert"}, "bpe": {"gpt2"}}


def read_str(f):
    (n,) = struct.unpack("<Q", f.read(8))
    return f.read(n).decode("utf-8", "replace")


def read_value(f, t, keep):
    if t == 8:
        return read_str(f)
    if t == 9:
        (it,) = struct.unpack("<I", f.read(4))
        (n,) = struct.unpack("<Q", f.read(8))
        items = [read_value(f, it, keep) for _ in range(n)]
        return items if keep else len(items)
    fmt = "<" + SCALAR[t]
    return struct.unpack(fmt, f.read(struct.calcsize(fmt)))[0]


def metadata(path):
    meta = {}
    with open(path, "rb") as f:
        if f.read(4) != b"GGUF":
            sys.exit(f"{path}: not a GGUF file (HTML error page saved as .gguf?)")
        f.read(4 + 8)  # version, tensor count
        (kv,) = struct.unpack("<Q", f.read(8))
        for _ in range(kv):
            key = read_str(f)
            (t,) = struct.unpack("<I", f.read(4))
            meta[key] = read_value(f, t, key == "tokenizer.ggml.tokens")
    return meta


def main():
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--expect", choices=sorted(EXPECT))
    p.add_argument("--server")
    p.add_argument("--text", action="append", default=[])
    a = p.parse_args()

    failed = False
    meta = metadata(a.model)
    tok = meta.get("tokenizer.ggml.model")
    tokens = meta.get("tokenizer.ggml.tokens") or []
    spm = sum(1 for t in tokens if t.startswith("\u2581")) / max(len(tokens), 1)
    print(f"architecture: {meta.get('general.architecture')}")
    print(f"tokenizer.ggml.model: {tok}")
    print(f"vocabulary: {len(tokens)} tokens, {spm:.0%} with the '\u2581' prefix")
    if tok == "bert" and spm > 0.5:
        print("FAIL: SentencePiece vocabulary labelled WordPiece (bert)")
        failed = True
    if a.expect and tok not in EXPECT[a.expect]:
        print(f"FAIL: original tokenizer is {a.expect}, GGUF says {tok}")
        failed = True

    for text in a.text:
        if not a.server:
            sys.exit("--text needs --server")
        req = urllib.request.Request(
            a.server.rstrip("/") + "/tokenize",
            data=json.dumps({"content": text, "with_pieces": True}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            pieces = [t.get("piece") for t in json.load(r)["tokens"]]
        bad = sum(1 for x in pieces if x == "<unk>")
        print(f"{text!r}: {pieces}")
        if bad:
            print(f"FAIL: {bad} <unk> piece(s)")
            failed = True

    print("FAIL" if failed else "OK")
    sys.exit(1 if failed else 0)


main()
