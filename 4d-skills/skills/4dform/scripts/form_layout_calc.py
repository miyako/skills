#!/usr/bin/env python3
"""
4D Form Layout Calculator
=========================
Computes the rendered visual extent of 4D form objects from their declared
JSON coordinates, accounting for 4D rendering offsets measured empirically
(macOS, logical pixels; Retina px = logical x 2):

  borderStyle solid   -> +1 px each side (stroke drawn OUTSIDE declared bounds)
  borderRadius r      -> +r px each side (arcs extend OUTWARD from the
                         declared corners -- opposite of web CSS)
  macOS focus ring    -> +5 px each side, ONLY in live rendering
                         (not drawn by the Form Editor)
  scrollbarVertical   -> +15 px, right side only

  rendered_w = declared_w + 2*(border + radius + focus_ring) + scrollbar_v
  rendered_h = declared_h + 2*(border + radius + focus_ring)

Pass live=False for Form Editor coordinates, live=True (default) for the
running form / screenshots.

Part of the 4dform skill; see references/layout.md. Standard library only.

USAGE (command line):
  python3 form_layout_calc.py                       # validate the constants
  python3 form_layout_calc.py --align               # alignment examples
  python3 form_layout_calc.py --solve 280 30 --border --radius 8 --editor
  python3 form_layout_calc.py --form Project/Sources/Forms/F/form.4DForm [--page 1] [--live]

  --form reports every object's declared and visual box on a page (page 0
  objects are always included) and flags visual overlaps between objects.
  Properties are inferred from the form JSON only: a borderStyle/borderRadius
  that comes from a CSS class is not seen -- pass --css-radius / --css-border
  for objects styled by CSS.

USAGE (import, with the scripts folder on sys.path):
  from form_layout_calc import (
      ControlProps, FILTER_INPUT, BUTTON, LISTBOX_SCROLL,
      visual_bbox, visual_left, visual_right,
      declared_left_for_visual_left, center_v_in_strip, visual_gap
  )

EXAMPLE PRESETS (adjust radius to the project's CSS):
  FILTER_INPUT   = ControlProps(border=True,  radius=8, focusable=True)   # inputs, combos
  DETAIL_TEXT    = ControlProps(border=True,  radius=8, focusable=False)  # read-only text areas
  BUTTON         = ControlProps(border=False, radius=0, focusable=True)   # roundedBevel / toolbar
  LISTBOX        = ControlProps(border=False, radius=0, focusable=False)
  LISTBOX_SCROLL = ControlProps(border=False, radius=0, focusable=False, scrollbar_v=True)
  RECT_PLAIN     = ControlProps(border=False, radius=0, focusable=False)
"""

# ── Constants (empirically measured) ──────────────────────────────────────────
BORDER_PX    = 1   # borderStyle: solid → 1 px outside each side
FOCUS_PX     = 5   # macOS focus ring, live rendering only (not in Form Editor)
SCROLLBAR_PX = 15  # scrollbarVertical: automatic, right side only


# ── Data class ─────────────────────────────────────────────────────────────────

class ControlProps:
    """Properties that affect a control's visual footprint beyond declared bounds."""

    def __init__(self, *, border=False, radius=0, focusable=False, scrollbar_v=False):
        self.border      = border       # borderStyle: solid
        self.radius      = radius       # borderRadius value (integer, no units)
        self.focusable   = focusable    # enterable input / combo / button
        self.scrollbar_v = scrollbar_v  # scrollbarVertical: automatic

    def __repr__(self):
        parts = []
        if self.border:       parts.append("border")
        if self.radius:       parts.append(f"radius={self.radius}")
        if self.focusable:    parts.append("focusable")
        if self.scrollbar_v:  parts.append("scrollbar_v")
        return f"ControlProps({', '.join(parts) or 'none'})"

    def _base(self, live=True) -> int:
        """
        Per-side base offset (excluding scrollbar).
        live=False = Form Editor view (no focus ring).
        """
        b = (BORDER_PX if self.border else 0) + self.radius
        if live and self.focusable:
            b += FOCUS_PX
        return b

    def edge_offset(self, side='left', live=True) -> int:
        """Render offset for a specific edge in logical pixels."""
        b = self._base(live)
        if side == 'right' and self.scrollbar_v:
            b += SCROLLBAR_PX
        return b

    # Legacy per-side properties (live=True) — kept for backward compatibility
    @property
    def left_offset(self):   return self.edge_offset('left',   live=True)
    @property
    def top_offset(self):    return self.edge_offset('top',    live=True)
    @property
    def right_offset(self):  return self.edge_offset('right',  live=True)
    @property
    def bottom_offset(self): return self.edge_offset('bottom', live=True)


# ── Core size / position API ───────────────────────────────────────────────────

def visual_bbox(left, top, width, height, props: ControlProps, *, live=True) -> dict:
    """
    Returns the actual rendered bounding box in logical pixels.
    live=True  → live form rendering (includes focus ring)
    live=False → Form Editor view (no focus ring)
    """
    ol  = props.edge_offset('left',   live)
    ot  = props.edge_offset('top',    live)
    or_ = props.edge_offset('right',  live)
    ob  = props.edge_offset('bottom', live)
    return {
        'left':   left   - ol,
        'top':    top    - ot,
        'right':  left   + width  + or_,
        'bottom': top    + height + ob,
        'width':  width  + ol + or_,
        'height': height + ot + ob,
    }


def declared_for_visual(visual_w, visual_h, props: ControlProps, *, live=True) -> tuple:
    """
    Back-calculate: given a desired visual size, return (declared_width, declared_height).
    """
    dw = visual_w - props.edge_offset('left',  live) - props.edge_offset('right',  live)
    dh = visual_h - props.edge_offset('top',   live) - props.edge_offset('bottom', live)
    return dw, dh


# ── Alignment helpers ──────────────────────────────────────────────────────────

def visual_left(left: int, props: ControlProps, *, live=True) -> int:
    """Visual left edge of a control (may extend left of its declared left)."""
    return left - props.edge_offset('left', live)


def visual_right(left: int, width: int, props: ControlProps, *, live=True) -> int:
    """Visual right edge of a control (may extend right of its declared right)."""
    return left + width + props.edge_offset('right', live)


def declared_left_for_visual_left(target_visual_left: int, props: ControlProps,
                                   *, live=True) -> int:
    """
    Compute the declared left so the control's visual left edge equals target_visual_left.

    Example -- align an input (FILTER_INPUT) to a button whose visual left=12:
      declared_left_for_visual_left(12, FILTER_INPUT, live=False) → 21
      (because FILTER_INPUT left_offset in editor = border(1) + radius(8) = 9)
    """
    return target_visual_left + props.edge_offset('left', live)


def declared_right_for_visual_right(target_visual_right: int, declared_width: int,
                                     props: ControlProps, *, live=True) -> int:
    """Compute declared left so the control's visual right edge equals target_visual_right."""
    return target_visual_right - declared_width - props.edge_offset('right', live)


def center_v_in_strip(strip_top: int, strip_height: int, ctrl_height: int) -> int:
    """
    Declared top to visually center a control in a horizontal strip.
    No props needed: offsets are symmetric, so visual center == declared center.

    Examples:
      center_v_in_strip(104, 86, 30) → 132
      center_v_in_strip(60,  44, 28) → 74
    """
    return strip_top + (strip_height - ctrl_height) // 2


# ── Gap helpers ────────────────────────────────────────────────────────────────

def visual_gap(left1: int, width1: int, props1: ControlProps,
               left2: int,             props2: ControlProps, *, live=True) -> int:
    """
    Visual clearance between right edge of ctrl1 and left edge of ctrl2.
    Positive = gap (safe), negative = overlap.
    """
    r1 = visual_right(left1, width1, props1, live=live)
    l2 = visual_left(left2,          props2, live=live)
    return l2 - r1


def visual_gap_h(ctrl1_left, ctrl1_width, ctrl1_props: ControlProps,
                 ctrl2_left,              ctrl2_props: ControlProps,
                 *, live=True) -> int:
    """Alias for visual_gap (backward compatibility)."""
    return visual_gap(ctrl1_left, ctrl1_width, ctrl1_props,
                      ctrl2_left, ctrl2_props, live=live)


def min_declared_gap(props1: ControlProps, props2: ControlProps,
                     clearance=0, *, live=True) -> int:
    """
    Minimum declared gap between adjacent controls to achieve `clearance` visual px.
    Default clearance=0 = just touching (no overlap).
    """
    return props1.edge_offset('right', live) + props2.edge_offset('left', live) + clearance


# ── Example presets ───────────────────────────────────────────────────────────

FILTER_INPUT   = ControlProps(border=True,  radius=8, focusable=True)   # inputs, combos
DETAIL_TEXT    = ControlProps(border=True,  radius=8, focusable=False)  # read-only text areas
BUTTON         = ControlProps(border=False, radius=0, focusable=True)   # roundedBevel / toolbar
LISTBOX        = ControlProps(border=False, radius=0, focusable=False)
LISTBOX_SCROLL = ControlProps(border=False, radius=0, focusable=False, scrollbar_v=True)
RECT_PLAIN     = ControlProps(border=False, radius=0, focusable=False)


# ── CLI helpers ────────────────────────────────────────────────────────────────

def _section(title):
    print(f"\n{'─'*64}")
    print(f"  {title}")
    print(f"{'─'*64}")


def _gap_row(n1, l1, w1, p1, n2, l2, p2, live=False):
    decl_gap = l2 - (l1 + w1)
    vgap     = visual_gap(l1, w1, p1, l2, p2, live=live)
    status   = "✓" if vgap >= 0 else f"← {abs(vgap)}px OVERLAP"
    print(f"  {n1} → {n2:<20}  decl:{decl_gap:4d}px   visual:{vgap:4d}px   {status}")


def run_validation():
    """Reproduce empirical measurements to validate constants."""
    _section("EMPIRICAL VALIDATION  (retina px = logical × 2)")
    cases = [
        ("input w280 radius=0  (Form Editor)", ControlProps(border=True, radius=0,  focusable=False), 280, 26, 564),
        ("input w280 radius=8  (Form Editor)", ControlProps(border=True, radius=8,  focusable=False), 280, 26, 596),
        ("input w280 radius=8  (Live form)  ", ControlProps(border=True, radius=8,  focusable=True),  280, 26, 616),
    ]
    for label, props, w, h, expected_retina in cases:
        bbox   = visual_bbox(0, 0, w, h, props)
        retina = bbox['width'] * 2
        ok = "✓" if retina == expected_retina else f"✗ expected {expected_retina}"
        print(f"  {label}: visual={bbox['width']:3d}px  retina={retina}px  {ok}")


FOCUSABLE_TYPES = {"input", "combo", "button", "dropdown", "checkbox", "radio",
                   "listbox", "hierarchicalList", "webArea"}


def props_from_json(obj: dict, css_border=False, css_radius=0) -> ControlProps:
    """Infer ControlProps from a form object's JSON (CSS-defined values are invisible here)."""
    otype = obj.get("type", "")
    border = obj.get("borderStyle", "solid" if css_border else "none") in ("solid", "dotted", "double", "raised", "sunken")
    radius = obj.get("borderRadius", css_radius)
    if isinstance(radius, str):
        radius = int("".join(ch for ch in radius if ch.isdigit()) or 0)
    focusable = (otype in FOCUSABLE_TYPES and obj.get("enterable", True) is not False
                 and not obj.get("hideFocusRing", False))
    scroll = otype in ("listbox", "input", "hierarchicalList") and \
        obj.get("scrollbarVertical", "automatic" if otype == "listbox" else "hidden") in ("automatic", "visible")
    return ControlProps(border=border, radius=radius, focusable=focusable, scrollbar_v=scroll)


def _box(obj: dict):
    """Declared (left, top, width, height) of a form object, or None."""
    left, top = obj.get("left"), obj.get("top")
    if left is None or top is None:
        return None
    width = obj.get("width", (obj["right"] - left) if "right" in obj else None)
    height = obj.get("height", (obj["bottom"] - top) if "bottom" in obj else None)
    if width is None or height is None:
        return None
    return left, top, width, height


def run_form_check(form_path, page=1, live=False, css_border=False, css_radius=0):
    """Report declared vs visual boxes for one page of a .4DForm and flag visual overlaps."""
    import json
    with open(form_path, encoding="utf-8") as f:
        form = json.load(f)
    pages = form.get("pages") or []
    rows = []
    for index in sorted({0, page}):
        if index >= len(pages) or not isinstance(pages[index], dict):
            continue
        for name, obj in (pages[index].get("objects") or {}).items():
            if not isinstance(obj, dict) or obj.get("type") == "line":
                continue
            box = _box(obj)
            if box is None:
                continue
            props = props_from_json(obj, css_border, css_radius)
            rows.append((name, obj.get("type", "?"), box, props,
                         visual_bbox(*box, props, live=live)))

    mode = "live" if live else "Form Editor"
    _section(f"{form_path}  page {page} (+ page 0)  [{mode}]")
    print(f"  {'Object':<24} {'type':<12} {'Declared [L T W H]':<24} {'Visual [L T R B]':<24} props")
    for name, otype, (l, t, w, h), props, bb in rows:
        print(f"  {name:<24} {otype:<12} [{l:4d} {t:4d} {w:4d} {h:4d}]   "
              f"[{bb['left']:4d} {bb['top']:4d} {bb['right']:4d} {bb['bottom']:4d}]   {props}")

    containers = {"rectangle", "groupBox", "tab", "subform"}
    overlaps = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            n1, t1, _, _, a = rows[i]
            n2, t2, _, _, b = rows[j]
            if t1 in containers or t2 in containers:
                continue
            dx = min(a["right"], b["right"]) - max(a["left"], b["left"])
            dy = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
            if dx > 0 and dy > 0:
                overlaps.append((n1, n2, dx, dy))
    _section("VISUAL OVERLAPS  (containers such as rectangles, group boxes and tabs ignored)")
    if not overlaps:
        print("  none")
    for n1, n2, dx, dy in overlaps:
        print(f"  {n1} x {n2}: {dx}px horizontally, {dy}px vertically")
    return overlaps


def run_align_demo():
    """Show how to compute declared positions for common alignment patterns."""
    _section("ALIGNMENT EXAMPLES  (editor mode, live=False)")

    # Align an input's visual left to 12
    target = 12
    dl = declared_left_for_visual_left(target, FILTER_INPUT, live=False)
    vl = visual_left(dl, FILTER_INPUT, live=False)
    print(f"  Align FILTER_INPUT visual-left to {target}:  declare left = {dl}  →  visual left = {vl}  ✓")

    # Gap between an input and the combo next to it
    input_l, input_w = 21, 271
    combo_l = 322
    gap_e = visual_gap(input_l, input_w, FILTER_INPUT, combo_l, FILTER_INPUT, live=False)
    gap_l = visual_gap(input_l, input_w, FILTER_INPUT, combo_l, FILTER_INPUT, live=True)
    print(f"\n  Gap input(21,w271) → combo(322):  editor={gap_e}px  live={gap_l}px")

    # Center 30px control in filter strip
    top = center_v_in_strip(104, 86, 30)
    print(f"\n  Center 30px control in strip (top=104, h=86):  declare top = {top}")

    # Center 28px button in toolbar
    top2 = center_v_in_strip(60, 44, 28)
    print(f"  Center 28px button  in toolbar (top=60,  h=44):  declare top = {top2}")


def run_solver(visual_w, visual_h, props: ControlProps, live=True):
    """Given desired visual size, compute declared dimensions."""
    mode = "live" if live else "editor"
    _section(f"SOLVER  →  visual {visual_w}×{visual_h}  with {props}  [{mode}]")
    dw, dh = declared_for_visual(visual_w, visual_h, props, live=live)
    bb = visual_bbox(0, 0, dw, dh, props, live=live)
    print(f"  Declare width={dw}, height={dh}")
    print(f"  Roundtrip: visual width={bb['width']} (want {visual_w})  {'✓' if bb['width']==visual_w else '✗'}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="4D Form Layout Calculator")
    parser.add_argument('--form',      metavar='PATH', help='Report a .4DForm page: declared vs visual boxes, overlaps')
    parser.add_argument('--page',      type=int, default=1, help='Page for --form (page 0 always included)')
    parser.add_argument('--live',      action='store_true', help='Use live offsets for --form (default: Form Editor)')
    parser.add_argument('--css-border', action='store_true', help='--form: assume solid border when JSON has none')
    parser.add_argument('--css-radius', type=int, default=0, help='--form: assume this borderRadius when JSON has none')
    parser.add_argument('--align',     action='store_true', help='Show alignment pattern examples')
    parser.add_argument('--solve',     metavar=('W', 'H'), nargs=2, type=int,
                        help='Compute declared size for desired visual W×H')
    parser.add_argument('--editor',    action='store_true', help='Use editor mode for --solve (no focus ring)')
    parser.add_argument('--border',    action='store_true')
    parser.add_argument('--radius',    type=int, default=0)
    parser.add_argument('--focusable', action='store_true')
    parser.add_argument('--scroll',    action='store_true')
    args = parser.parse_args()

    if args.form:
        found = run_form_check(args.form, page=args.page, live=args.live,
                               css_border=args.css_border, css_radius=args.css_radius)
        raise SystemExit(1 if found else 0)

    run_validation()

    if args.align:
        run_align_demo()

    if args.solve:
        props = ControlProps(
            border=args.border, radius=args.radius,
            focusable=args.focusable, scrollbar_v=args.scroll
        )
        run_solver(args.solve[0], args.solve[1], props, live=not args.editor)
