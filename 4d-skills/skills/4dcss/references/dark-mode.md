# Dark Mode

References:
- Color scheme setting: https://developer.4d.com/docs/settings/interface#color-scheme
- `Get application color scheme`: https://developer.4d.com/docs/commands/get-application-color-scheme
- `FORM Get color scheme`: https://developer.4d.com/docs/commands/form-get-color-scheme
- CSS in 4D: https://developer.4d.com/docs/FormEditor/stylesheets

Dark/light rules are cross-platform: put them in `styleSheets.css`. File
locations, syntax and the specificity rule (form JSON beats CSS) are in
`../SKILL.md`.

## `prefers-color-scheme`

```css
@media (prefers-color-scheme: light) {
  .my-class {
	fill: #F1F6FB;
	stroke: #2C435A;
  }
}

@media (prefers-color-scheme: dark) {
  .my-class {
	fill: #1e2d3d;
	stroke: #B8D4E8;
  }
}
```

Colour schemes are not supported with the `win-classic` form theme.

## Automatic Color Values

4D provides special color keywords that adapt to the system color scheme automatically:

| Keyword | Applies to | Behaviour |
|---------|-----------|-----------|
| `"automatic"` | `stroke`, `fill` | Adapts text/foreground and background to light or dark mode |
| `"automaticAlternate"` | `alternateFill` | Adapts the alternate row background in listboxes |

### Rules

- Use `"automatic"` for text `stroke` and background `fill` whenever a fixed colour is not required.
- Use `"automaticAlternate"` for listbox alternate row fills instead of hardcoded near-white values like `#F8FCFF`.
- When a column-level property is the **same** as the listbox-level property and there is only one column, remove the column-level override and define it at the listbox level only. Column-level properties are for overrides, not repetition.
- Replace hardcoded `#000000` or `#FFFFFF` (or near-equivalents like `#212121`) in `stroke` for text and shape primitives with `"automatic"` **only if** you want them to adapt. If specific branded colours are needed, use CSS instead.
- Form objects that **omit** `fill` or `stroke` entirely use a 4D-internal default, which is **not** the same as `"automatic"`. To ensure they adapt to dark mode, explicitly set `"fill": "automatic"` and/or `"stroke": "automatic"`. This is especially important for full-form background rectangles that rely on the implicit default fill.

### ⚠️ Scope: `"automatic"` is a form-object CSS property value, not an HTML/rich-text colour

`"automatic"` and `"automaticAlternate"` are only meaningful as the value of a `fill`/`stroke`/`alternateFill` **property on a form object or CSS class** (in `form.4DForm`, `styleSheets*.css`). They are **not** valid inside inline HTML/rich-text markup such as `<span style="color:#000000">` embedded in JSON sample data, area/4D Write Pro content, or any other string that is rendered by an HTML/rich-text parser rather than 4D's own form-CSS engine.

A real mistake to avoid: a project-wide grep-and-replace for hardcoded hex colours accidentally rewrote `color:#000000`/`color:#01168B` inside `<span style="color:...">` tags in `Resources/*.json` sample text (data consumed by a styled-text/rich-text area, not a form object) to `color:automatic`. This silently breaks rendering, since `automatic` is not a real CSS/HTML colour keyword outside 4D's own form styling. Before replacing any hardcoded colour, confirm the string is a `.4DForm`/CSS property value, not the *content* of a JSON/text/HTML field that merely happens to contain colour-looking hex codes.


## Runtime Color Detection (Hidden Reference Objects)

### The Problem

4D has no API to directly query whether the current theme is dark or light in a boolean fashion. The commands:

- `Get application color scheme` (returns `"light"`, `"dark"`, or `"inherited"`)
- `FORM Get color scheme` (returns `"light"`, `"dark"`, or `"inherited"`)

…may return `"inherited"`, meaning the system theme is in use but you don't know which one it resolved to without additional logic.

### The Workaround

Use **hidden rectangle objects** on the form as colour references. Their rendered colours are set by CSS media queries, and at runtime you read the actual resolved colour with `OBJECT GET RGB COLORS`.

#### Step 1: Add Hidden Rectangles to the Form

Place them on page 0 (shared/always loaded) so they are available during `On Load`:

```json
"refMyColour": {
  "type": "rectangle",
  "top": 0,
  "left": 0,
  "width": 1,
  "height": 1,
  "class": "ref-my-colour",
  "stroke": "transparent"
}
```

#### Step 2: Define Colours in CSS

```css
@media (prefers-color-scheme: light) {
  .ref-my-colour {
	fill: #FFCCCC;
	visibility: hidden;
  }
}

@media (prefers-color-scheme: dark) {
  .ref-my-colour {
	fill: #5C2020;
	visibility: hidden;
  }
}
```

Note: `visibility: hidden` is set in **both** media queries to ensure the rectangle is always invisible regardless of scheme.

#### Step 3: Read at Runtime

```4d
var $fg; $bg : Integer
OBJECT GET RGB COLORS(*; "refMyColour"; $fg; $bg)
  // $bg contains the resolved fill colour as a longint (0x00RRGGBB)
```

#### Step 4: Convert to Hex String

Use a helper method to convert the longint to `#RRGGBB`:

```4d
  // RGBToHex method
#DECLARE($rgb : Integer)->$result : Text

var $r; $g; $b : Integer
$r:=($rgb >> 16) & 0x0000FF
$g:=($rgb >> 8) & 0x0000FF
$b:=$rgb & 0x0000FF

var $hex : Text
$hex:=""

var $i; $val : Integer
var $digits : Text
$digits:="0123456789ABCDEF"

For ($i; 1; 3)
  Case of 
	: ($i=1)
	  $val:=$r
	: ($i=2)
	  $val:=$g
	: ($i=3)
	  $val:=$b
  End case 
  $hex:=$hex+$digits[[$val\16+1]]+$digits[[$val%16+1]]
End for 

$result:="#"+$hex
```

### Use Case: Listbox Meta Expression

When a listbox uses `"metaSource"` to dynamically style rows/cells with fill colours, those colours are hardcoded strings. Use the hidden-rectangle technique to resolve theme-appropriate colours at form load time, then build the meta objects with those resolved values.

**This is easy to miss with a form-JSON-only audit.** A listbox's `rowFillSource` / `rowStrokeSource` / `rowStyleSource` properties (in `.4DForm`) just name an array or variable — the actual hardcoded colours live in `.4dm` method code (e.g. `_FontBackground{$i}:=0x00FFFFFF`), often in more than one file (an `On Load` initializer and a selection/refresh handler that has to stay in sync with it). A pure `grep`/scan of `.4DForm` for `fill`/`stroke` properties will never surface these. Always additionally:

1. `grep -rn "rowFillSource\|rowStrokeSource\|rowStyleSource" Project/Sources/Forms/` to find every listbox using a meta-expression.
2. For each hit, note the array/variable name(s) referenced.
3. `grep -rn` that exact name across **all** `.4dm` files (form method, object methods) to find every assignment site — there is often more than one (initial load vs. a change/refresh event).
4. If any assignment hardcodes an RGB/hex literal, replace it with a value resolved from a hidden reference rectangle (see above), and make sure every assignment site uses the same resolved variable so they can't drift out of sync.


## Listbox-Specific Guidelines

### alternateFill

- Use `"automaticAlternate"` at the **listbox level** for automatic dark/light adaptation.
- Do **not** repeat the same `alternateFill` at the column level unless it is a deliberate column-specific override.
- Remove column-level `alternateFill` if it matches the listbox-level value (it adds no value and creates maintenance burden).

### Odd-row (`fill`) colour with light/dark variants

If you want a custom odd-row background (instead of fully automatic), do it via CSS classes and media queries:

1. Assign a class to the listbox in `form.4DForm` (for example, `"class": "my-list"`).
2. Remove JSON `fill` from the listbox and its columns so CSS can apply (JSON wins on specificity).
3. Keep `alternateFill` as `"automaticAlternate"` for even rows.
4. Define light/dark odd-row colours in `styleSheets.css`:

   Define the rule on **both** the bare class and the compound
   `listbox.my-list` selector (the bare class alone does not always match a
   listbox at runtime -- see "Matching quirk" in `../SKILL.md`):

```css
@media (prefers-color-scheme: light) {
  .my-list { fill: #FDFED3; }
  listbox.my-list { fill: #FDFED3; }
}

@media (prefers-color-scheme: dark) {
  .my-list { fill: #3A2F1F; }
  listbox.my-list { fill: #3A2F1F; }
}
```

### Meta Source Colours

- Never hardcode light-mode-only colours in meta source methods.
- Use the hidden-rectangle reference technique described above.
- White text (`#FFFFFF`) on a coloured background (e.g., red `#FF4040`) is acceptable in both modes because the cell fill provides contrast.
- Do not stop at checking one assignment site. If a listbox's meta-source array is populated both on form load and on a selection-change/refresh event, both sites must resolve colours the same way (both via the hidden-rectangle technique, sharing the same resolved variables) — fixing only the load-time initializer and leaving a refresh handler with hardcoded hex reintroduces the bug the moment the user interacts with the listbox.


## Colour Palette Recommendations

When choosing dark-mode equivalents, follow these principles:

| Light mode | Dark mode | Rationale |
|-----------|-----------|-----------|
| Near-white backgrounds (`#FFFFFF`, `#F8FCFF`) | Dark grey (`#1E1E1E`, `#2A2A2A`) | Sufficient contrast without pure black |
| Near-black text (`#212121`, `#000000`) | Light grey (`#E0E0E0`) | Readable on dark backgrounds |
| Muted text (`#696969`) | Lighter muted (`#A0A0A0`) | Maintains hierarchy without being invisible |
| Link blue (`#1E90FF`) | Lighter blue (`#5CB8FF`) | Accessible contrast on dark |
| Alert red fill (`#FF4040`) | Muted red (`#CC3333`) | Less harsh on dark backgrounds |
| Light pink fill (`#FFCCCC`) | Dark red (`#5C2020`) | Retains semantic meaning |
| Light green fill (`#B8EDB8`) | Dark green (`#1E4D1E`) | Retains semantic meaning |
| Panel grey (`#C0C0C0`) | Dark panel (`#3A3A3A`) | Structural differentiation |


## Checklist for Dark Mode Migration

1. **Scan forms** for hardcoded `stroke` and `fill` colours across **every** object type, not just shapes — a `text` object's `fill` is its background and is just as easy to leave hardcoded as a rectangle's; check `stroke` and `fill` independently on each object since one can be `"automatic"` while the other is still a fixed hex value. Restrict this to `form.4DForm`/CSS property values, not colour-looking hex codes inside JSON/HTML/rich-text *content* fields (see scope note above).
2. **Scan forms** for objects that **omit** `fill` or `stroke` entirely — these use an internal default, not `"automatic"`. Add `"fill": "automatic"` or `"stroke": "automatic"` explicitly so they adapt to dark mode. Pay special attention to full-form background rectangles.
3. **Replace** `#000000`/`#FFFFFF` with `"automatic"` where appropriate.
4. **Replace** hardcoded `alternateFill` with `"automaticAlternate"`.
5. **Remove** column-level properties that duplicate listbox-level values.
6. **Move** branded/specific colours from `.4DForm` to CSS classes with media queries.
7. **For listboxes with custom odd-row colour**, set class-based `fill` in light/dark CSS and keep `alternateFill: "automaticAlternate"`.
8. **Add** hidden reference rectangles for any runtime colour logic (meta expressions, programmatic styling). Do not rely on a `.4DForm`-only scan to find these: `grep -rn "rowFillSource\|rowStrokeSource\|rowStyleSource"` across all forms, then `grep -rn` each referenced array/variable name across all `.4dm` files to find every assignment site (there is often more than one, e.g. load-time init plus a refresh/selection-change handler) and confirm none hardcode theme-specific RGB/hex.
9. **Create** `styleSheets.css` if it doesn't exist; define both `light` and `dark` media query blocks.
10. **Verify** no inline `.4DForm` property is overriding your CSS (specificity rule).
11. **Test** by toggling system appearance in System Preferences / Settings.
