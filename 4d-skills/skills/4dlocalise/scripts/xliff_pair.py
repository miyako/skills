#!/usr/bin/env python3
"""Generate paired XLIFF 1.2 files ({name}{LANG}.xlf) for every language from one JSON table.

strings.json:
  {
    "_languages": ["en", "ja"],
    "menu":     [["MenuItem_Quit", "Quit", "終了"], ...],
    "messages": [["Alert_Deleted", "{1} deleted", "{1} を削除しました"], ...]
  }

The first language is the source language (English, per 4dlocalise). Each key
other than "_languages" is a file name; each row is [id, text per language...].
ID-based trans-units are written directly under <body> (never inside form groups).
Fails on duplicate IDs, wrong column counts and redefinition of 4D's built-in
Common* IDs. A line break in a string is written as &#13; (CR, the 4D line
break); a literal CR would be normalised to LF by the XML parser.
"""
import argparse
import json
import os
import sys
from xml.sax.saxutils import escape, quoteattr


def xml_text(text):
    return escape(text).replace("\r\n", "&#13;").replace("\n", "&#13;").replace("\r", "&#13;")


def check(table, langs):
    ids = {}
    for name, rows in table.items():
        for row in rows:
            if not isinstance(row, list) or len(row) != 1 + len(langs):
                sys.exit(f"{name}: {row!r} needs {1 + len(langs)} columns (id + {', '.join(langs)})")
            if row[0] in ids:
                sys.exit(f"duplicate id {row[0]} in {name} and {ids[row[0]]}")
            if row[0].startswith("Common"):
                sys.exit(f"{row[0]}: never redefine 4D's built-in Common* IDs")
            ids[row[0]] = name
    return ids


def render(name, rows, langs, index):
    lang = langs[index]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">',
           f'\t<file datatype="plaintext" original={quoteattr(name)} '
           f'source-language="{langs[0]}" target-language="{lang}">',
           '\t\t<body>']
    for row in rows:
        out += [f'\t\t\t<trans-unit id={quoteattr(row[0])} resname={quoteattr(row[0])}>',
                f'\t\t\t\t<source>{xml_text(row[1])}</source>',
                f'\t\t\t\t<target>{xml_text(row[1 + index])}</target>',
                '\t\t\t</trans-unit>']
    out += ['\t\t</body>', '\t</file>', '</xliff>', '']
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("strings", help="JSON table (see above)")
    parser.add_argument("resources", help="Resources/ folder; <lang>.lproj/ subfolders are created")
    args = parser.parse_args()

    with open(args.strings, encoding="utf-8") as f:
        table = json.load(f)
    langs = table.pop("_languages", ["en", "ja"])
    ids = check(table, langs)
    for index, lang in enumerate(langs):
        code = lang.replace("-", "_")
        folder = os.path.join(args.resources, f"{code}.lproj")
        os.makedirs(folder, exist_ok=True)
        for name, rows in table.items():
            path = os.path.join(folder, f"{name}{code.upper()}.xlf")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(render(name, rows, langs, index))
    print(f"{len(ids)} ids x {len(langs)} languages -> {args.resources}")


if __name__ == "__main__":
    main()
