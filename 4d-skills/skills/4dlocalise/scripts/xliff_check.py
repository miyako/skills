#!/usr/bin/env python3
"""Cross-check XLIFF IDs against their references in a 4D project.

Collects every :xliff:ID in Project/Sources (forms, menus.json, any .json)
and every Localized string("ID") / Get localized string("ID") in .4dm code
(token suffixes such as :C991 are accepted), and every trans-unit id/resname
directly under <body> in Resources/<lang>.lproj/*.xlf (units nested in form
<group>s are object-name matches and are ignored). Reports:

  MISSING  an ID referenced in the project but absent from a language
  PARTIAL  an ID defined in some languages but not all
  UNUSED   an ID defined but never referenced (warning only)

An ID built in code, Localized string("Step_Tab"+String($i)), is reported as
a DYNAMIC prefix and every defined ID starting with it counts as referenced.
Pass --dynamic PREFIX for IDs built any other way (a variable, Replace string).
Exits 1 on MISSING or PARTIAL, 0 otherwise.
"""
import argparse
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

XLIFF_REF = re.compile(r":xliff:([A-Za-z0-9_.\-]+)")
CODE_REF = re.compile(r"(?:Get localized string|Localized string)(?::C\d+)?\s*\(\s*\"([^\"]+)\"\s*([)+])")
NS = "{urn:oasis:names:tc:xliff:document:1.2}"


def references(project):
    refs, prefixes = {}, set()
    sources = project / "Project" / "Sources"
    for path in sources.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in (".4DForm", ".json"):
            pattern = XLIFF_REF
        elif path.suffix == ".4dm":
            pattern = CODE_REF
        else:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for found in pattern.findall(text):
            if isinstance(found, tuple):
                found, end = found
                if end == "+":  # "Prefix"+String($i): an ID built in code
                    prefixes.add(found)
                    continue
            refs.setdefault(found, set()).add(str(path.relative_to(project)))
        if path.suffix == ".4dm":
            for found in XLIFF_REF.findall(text):
                refs.setdefault(found, set()).add(str(path.relative_to(project)))
    return refs, prefixes


def definitions(project):
    defs = {}
    for lproj in sorted((project / "Resources").glob("*.lproj")):
        lang = lproj.name[: -len(".lproj")]
        ids = defs.setdefault(lang, set())
        for xlf in lproj.glob("*.xlf"):
            try:
                root = ET.parse(xlf).getroot()
            except ET.ParseError as e:
                sys.exit(f"{xlf}: not well-formed XML: {e}")
            # ID-based units sit directly under <body>; units in <group>s are object-name matches
            for unit in (u for body in root.iter(NS + "body") for u in body.findall(NS + "trans-unit")):
                for key in ("id", "resname"):
                    if unit.get(key):
                        ids.add(unit.get(key))
    return defs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", nargs="?", default=".", help="repository root (holds Project/ and Resources/)")
    parser.add_argument("--dynamic", action="append", default=[], metavar="PREFIX",
                        help="prefix of IDs built in code; repeatable")
    parser.add_argument("--quiet-unused", action="store_true", help="do not list UNUSED IDs")
    args = parser.parse_args()

    project = pathlib.Path(args.project)
    refs, prefixes = references(project)
    prefixes |= set(args.dynamic)
    defs = definitions(project)
    if not defs:
        sys.exit("no Resources/*.lproj folders found")
    every = set().union(*defs.values())
    failed = False
    for ref in sorted(refs):
        if ref.startswith("Common"):
            continue  # 4D's built-in IDs, never in project files
        absent = [lang for lang, ids in defs.items() if ref not in ids]
        if absent:
            failed = True
            print(f"MISSING {ref} in {', '.join(absent)} (used in {', '.join(sorted(refs[ref]))})")
    for ident in sorted(every):
        absent = [lang for lang, ids in defs.items() if ident not in ids]
        if absent and ident in refs:
            continue  # already reported as MISSING
        if absent:
            failed = True
            print(f"PARTIAL {ident} missing in {', '.join(absent)}")
        if not args.quiet_unused and ident not in refs and not any(ident.startswith(p) for p in prefixes):
            print(f"UNUSED  {ident}")
    for prefix in sorted(prefixes):
        print(f"DYNAMIC {prefix}* ({sum(i.startswith(prefix) for i in every)} defined IDs)")
    print(f"{len(refs)} referenced IDs, {len(every)} defined IDs, languages: {', '.join(sorted(defs))}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
