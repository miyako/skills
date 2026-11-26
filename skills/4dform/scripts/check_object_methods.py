#!/usr/bin/env python3
"""Report orphaned object methods in 4D project forms.

An ObjectMethods/*.4dm file that no object references through a "method"
property is never called: no error, the control just does nothing.

Usage: check_object_methods.py [Project/Sources/Forms | <form dir> ...]
Exit code 0 when every form is wired, 1 otherwise.
"""
import json, os, sys


def walk(node, found):
    if isinstance(node, dict):
        if isinstance(node.get("method"), str):
            found.append(node)
        for v in node.values():
            walk(v, found)
    elif isinstance(node, list):
        for v in node:
            walk(v, found)


def check(form_dir):
    form = os.path.join(form_dir, "form.4DForm")
    if not os.path.isfile(form):
        return []
    with open(form, encoding="utf-8-sig") as fh:
        data = json.load(fh)
    nodes = []
    walk(data, nodes)
    refs = {n["method"]: n for n in nodes}
    problems = []
    om = os.path.join(form_dir, "ObjectMethods")
    files = sorted(os.listdir(om)) if os.path.isdir(om) else []
    for name in files:
        if name.endswith(".4dm") and f"ObjectMethods/{name}" not in refs:
            problems.append(f"{form}: ObjectMethods/{name} is never referenced (orphaned, will not run)")
    for ref, node in refs.items():
        if not os.path.isfile(os.path.join(form_dir, ref)):
            problems.append(f"{form}: \"method\": \"{ref}\" points to a missing file")
        elif ref.startswith("ObjectMethods/") and not node.get("events"):
            problems.append(f"{form}: {ref} has no \"events\" on its object (will not be triggered)")
    return problems


def main(argv):
    roots = argv or ["Project/Sources/Forms"]
    dirs = []
    for r in roots:
        if os.path.isfile(os.path.join(r, "form.4DForm")):
            dirs.append(r)
        elif os.path.isdir(r):
            dirs += [os.path.join(r, d) for d in sorted(os.listdir(r))]
    problems = [p for d in dirs for p in check(d)]
    print("\n".join(problems) if problems else f"ok: {len(dirs)} form(s), every object method is wired")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
