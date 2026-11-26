#!/usr/bin/env python3
"""Replace literal user-visible strings in .4DForm files with :xliff: references, byte-safely.

mapping.json: {"<literal text>": "<XLIFF id>", ...}   (exact, whole-value matches only)

Touched properties: text, windowTitle, tooltip, placeholder, and string items
of labels. Each file is first round-tripped (json.loads -> json.dumps with tab
indent, ensure_ascii=False, no trailing newline). A file whose bytes differ is
SKIPPED, because 4D wrote it in a form this script cannot reproduce: edit it
by hand. Unmatched literals are listed so that nothing is missed silently.
"""
import argparse
import json

PROPS = ("text", "windowTitle", "tooltip", "placeholder")


def dump(obj):
    return json.dumps(obj, indent="\t", ensure_ascii=False)


def walk(node, mapping, hits, misses):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in PROPS and isinstance(value, str) and value.strip() and not value.startswith(":xliff:"):
                if value in mapping:
                    node[key] = ":xliff:" + mapping[value]
                    hits.append(value)
                else:
                    misses.append(f"{key}={value!r}")
            elif key == "labels" and isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str) and item.strip() and not item.startswith(":xliff:"):
                        if item in mapping:
                            value[i] = ":xliff:" + mapping[item]
                            hits.append(item)
                        else:
                            misses.append(f"labels[{i}]={item!r}")
            else:
                walk(value, mapping, hits, misses)
    elif isinstance(node, list):
        for value in node:
            walk(value, mapping, hits, misses)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mapping", help="JSON object: literal text -> XLIFF id")
    parser.add_argument("forms", nargs="+", help=".4DForm files")
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args()

    with open(args.mapping, encoding="utf-8") as f:
        mapping = json.load(f)
    skipped = 0
    for path in args.forms:
        with open(path, encoding="utf-8", newline="") as f:
            raw = f.read()
        obj = json.loads(raw)
        if dump(obj) != raw:
            print(f"SKIP {path}: not byte-exact on round-trip")
            skipped += 1
            continue
        hits, misses = [], []
        walk(obj, mapping, hits, misses)
        print(f"{path}: {len(hits)} replaced, {len(misses)} unmatched")
        for miss in misses:
            print("   unmatched", miss)
        if hits and not args.dry_run:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(dump(obj))
    if skipped:
        print(f"{skipped} file(s) skipped: edit them by hand")


if __name__ == "__main__":
    main()
