#!/usr/bin/env python3
"""Convert "fake buttons" in .4DForm files into real, themeable buttons.

A fake button is an invisible button ("display": false) drawn on top of a
rectangle (the coloured background) and a text object (the label). It cannot
follow the form theme (Liquid Glass, Fluent UI), dark mode or keyboard focus,
and its label is a separate object to localise.

On each page the script pairs every invisible button with
  * the rectangles whose bounds match the button's (within --tolerance px), and
  * the text objects whose top-left corner lies inside the button.
It then deletes those rectangles and labels, moves the label's text to the
button ("text"), removes the button's display/height/bottom/borderStyle/
fontSize/fontWeight, adds the CSS class (default "default"; the height comes
from the theme rules in 4dcss) and recentres "top" for --height.

Each file is first round-tripped (BOM and trailing newline kept as found,
tab indent, ensure_ascii=False); a file whose bytes differ is SKIPPED. A button with no
label, or with several, is reported and left alone. Use --dry-run first.
"""
import argparse
import json

BOM = "\ufeff"
DROP = ("display", "height", "bottom", "borderStyle", "fontSize", "fontWeight")


def dump(obj):
    return json.dumps(obj, indent="\t", ensure_ascii=False)


def inside(o, b, tol):
    return (b["left"] - tol <= o.get("left", -1) <= b["left"] + b.get("width", 0)
            and b["top"] - tol <= o.get("top", -1) <= b["top"] + b.get("height", 0))


def same_bounds(o, b, tol):
    return all(abs(o.get(k, -10**6) - b.get(k, 0)) <= tol for k in ("left", "top", "width", "height"))


def convert_page(objects, args, report):
    changed = 0
    for name, button in list(objects.items()):
        if button.get("type") != "button" or button.get("display") is not False:
            continue
        labels = [n for n, o in objects.items() if o.get("type") == "text" and inside(o, button, args.tolerance)]
        backs = [n for n, o in objects.items() if o.get("type") == "rectangle" and same_bounds(o, button, args.tolerance)]
        if len(labels) != 1:
            report.append(f"   {name}: {len(labels)} label(s) {labels}, left alone")
            continue
        text = objects[labels[0]].get("text", "")
        report.append(f"   {name}: label {labels[0]} {text!r}, background {backs or 'none'}")
        changed += 1
        if args.dry_run:
            continue
        old_height = button.get("height", args.height)
        for key in DROP:
            button.pop(key, None)
        button["text"] = text
        button["top"] = button["top"] + (old_height - args.height) // 2
        classes = button.get("class", "").split()
        if args.css_class not in classes:
            button["class"] = " ".join(classes + [args.css_class])
        for n in labels + backs:
            del objects[n]
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("forms", nargs="+", help=".4DForm files")
    parser.add_argument("--class", dest="css_class", default="default", help="CSS class to add (default: default)")
    parser.add_argument("--height", type=int, default=27, help="theme height used to recentre top (default: 27, Liquid Glass)")
    parser.add_argument("--tolerance", type=int, default=2, help="pixels of slack when matching bounds (default: 2)")
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args()

    for path in args.forms:
        with open(path, encoding="utf-8", newline="") as f:
            raw = f.read()
        bom = BOM if raw.startswith(BOM) else ""
        eol = "\n" if raw.endswith("\n") else ""
        obj = json.loads(raw[len(bom):])
        if bom + dump(obj) + eol != raw:
            print(f"SKIP {path}: not byte-exact on round-trip")
            continue
        report, changed = [], 0
        for page in obj.get("pages") or []:
            if page and page.get("objects"):
                changed += convert_page(page["objects"], args, report)
        print(f"{path}: {changed} converted" + (" (dry run)" if args.dry_run else ""))
        for line in report:
            print(line)
        if changed and not args.dry_run:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(bom + dump(obj) + eol)


if __name__ == "__main__":
    main()
