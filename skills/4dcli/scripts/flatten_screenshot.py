#!/usr/bin/env python3
"""Flatten transparent FORM SCREENSHOT PNGs onto a window background colour, in place.

A window with a transparent background (Liquid Glass, some dialogs) captures
as a PNG with alpha, which most viewers show on white or a checkerboard.
Requires Pillow (pip install pillow).
"""
import argparse

BACKGROUNDS = {"light": (246, 246, 246), "dark": (30, 30, 30)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("appearance", choices=sorted(BACKGROUNDS), help="window background to composite onto")
    parser.add_argument("pngs", nargs="+", help="PNG files, rewritten in place")
    args = parser.parse_args()

    from PIL import Image

    background = BACKGROUNDS[args.appearance] + (255,)
    for path in args.pngs:
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
        out = Image.new("RGBA", rgba.size, background)
        out.alpha_composite(rgba)
        out.convert("RGB").save(path)
        print(f"flattened {path}")


if __name__ == "__main__":
    main()
