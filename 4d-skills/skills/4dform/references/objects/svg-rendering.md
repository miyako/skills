---
object: "svg"
keywords: ["SVG", "SVG rendering", "SVG Tiny", "SVG SET ATTRIBUTE", "paint", "gradient", "filter", "clipPath", "textArea", "animation", "4D-text"]
summary: "4D's proprietary SVG rendering engine capabilities: supported elements, attributes, paint servers, filters, text properties, animation via SVG SET ATTRIBUTE, CSS2 styles, and 4D-specific reserved attributes."
---

# 4D SVG Rendering Engine Reference

4D has a **proprietary SVG rendering engine** based on SVG 1.1 (http://www.w3.org/TR/SVG11) with selected SVG Tiny 1.2 extensions. It is not a web browser — SMIL animation and embedded JavaScript are not supported. Instead, use `SVG SET ATTRIBUTE` for dynamic updates (see `picture-input.md`).

Based on the v12 specification sheet with updates through v17+.

## Platform Rendering Engines

| Platform | Engine | Since |
|----------|--------|-------|
| macOS | Core Graphics (Quartz 2D) | Always |
| Windows | **Direct2D** (software mode) | v14 R5 (replaced GDI+) |

The switch to Direct2D on Windows brought **filter effects** (blur, color matrix, blend, composite, offset) to Windows — previously Mac-only. Some v12-era Windows limitations (noted below) may no longer apply.

## Color Support

All CSS2 color types are supported:
- Named colors: all SVG 1.1 color keywords (e.g. `red`, `blue`, `cornflowerblue`)
- Hex: `#F00`, `#FF0000`
- `rgb()`: `rgb(255,0,0)`
- **`rgba()` is NOT supported** — use `fill-opacity`/`stroke-opacity` for transparency

Colors are expressed in the sRGB color space.

## Structure Elements

| Element | Supported | Notes |
|---------|-----------|-------|
| `<svg>` | Yes | `viewBox`, `preserveAspectRatio` supported; `viewport-fill`, `viewport-fill-opacity` (SVG Tiny 1.2) |
| `<g>` | Yes | Group element |
| `<a>` | Yes | Implemented as `<g>` |
| `<defs>` | Yes | |
| `<symbol>` | Yes | `viewBox`, `preserveAspectRatio` |
| `<use>` | Partial | Only `symbol`, `g`, `a`, or basic shapes — not `svg`. Use `<image>` for external SVG |
| `<switch>` | No | |

### Common Attributes

| Attribute | Supported | Notes |
|-----------|-----------|-------|
| `id` | Yes | |
| `style` | Yes | CSS2-compliant inline declarations |
| `class` | Yes (11.3+) | Used by CSS class selectors, inherited by children |
| `visibility` | Yes | |
| `display` | Yes | Implemented as `visibility` |
| `transform` | Yes | |
| `xml:lang` | Yes (11.3+) | Used by CSS `:lang()` pseudo-class |

## Shapes

All basic shapes are fully supported:

| Element | Supported | Notes |
|---------|-----------|-------|
| `<rect>` | Yes | `x`, `y`, `width`, `height`, `rx`, `ry` |
| `<circle>` | Yes | `cx`, `cy`, `r` |
| `<ellipse>` | Yes | `cx`, `cy`, `rx`, `ry` |
| `<line>` | Yes | `x1`, `y1`, `x2`, `y2` |
| `<polyline>` | Yes | `points` |
| `<polygon>` | Yes | `points` |
| `<path>` | Yes | `d` attribute, quadratic bezier from 11.3 |

## Paint Properties

| Property | Supported | Notes |
|----------|-----------|-------|
| `color` | Yes | |
| `opacity` | Yes | |
| `fill` | Yes | Pattern paint server from v12 |
| `fill-opacity` | Yes | |
| `fill-rule` | Yes (v12) | |
| `stroke` | Yes | Pattern paint server from v12 |
| `stroke-opacity` | Yes | |
| `stroke-linecap` | Yes | v12 note: on Windows/GDI+, `butt` was implemented as `square`; may be fixed with Direct2D (v14 R5+) |
| `stroke-linejoin` | Yes | |
| `stroke-miterlimit` | Yes (v12) | |
| `stroke-dasharray` | Yes (v12) | |
| `stroke-dashoffset` | Yes (v12) | |
| `shape-rendering` | Yes (v12) | `optimizeSpeed` disables anti-aliasing |

## Paint Servers

| Element | Supported | Notes |
|---------|-----------|-------|
| `<solidColor>` | Yes | `solid-color`, `solid-opacity` |
| `<linearGradient>` | Yes | All stop elements from v12; `gradientTransform` from v12 |
| `<radialGradient>` | Yes | All stop elements from v12; `gradientTransform` from v12 |
| `<stop>` | Yes | `offset`, `stop-color`, `stop-opacity` |
| `<pattern>` | Yes (v12) | Full support including `patternTransform` |

## Text

### Elements

| Element | Supported | Notes |
|---------|-----------|-------|
| `<text>` | Yes | `x`, `y`, `dx`, `dy` (single values only, not lists) |
| `<tspan>` | Yes | Same attribute constraints as `<text>` |
| `<textArea>` | Yes (11.3+) | **SVG Tiny 1.2** — auto-wrapping text in a bounding box |
| `<tbreak>` | Yes (11.3+) | **SVG Tiny 1.2** — explicit line break in `<textArea>` |
| `<tref>` | No | |
| `<textPath>` | No | |

### Text Properties

| Property | Supported | Notes |
|----------|-----------|-------|
| `font-family` | Yes | List of prioritized names + generic tokens from 11.3 (default: Times New Roman) |
| `font-style` | Yes | `italic` and `oblique` are identical |
| `font-weight` | Yes | ≥700 = bold, <700 = normal |
| `font-size` | Yes | Default: 12pt |
| `text-anchor` | Yes | `start`, `middle`, `end` |
| `text-decoration` | Partial | `blink` not supported; `overline` not supported in `<textArea>` |
| `kerning` | Yes (v12) | |
| `letter-spacing` | Yes (v12) | |
| `writing-mode` | Yes (v12) | `lr`, `rl`, `tb` — determines `direction` and `unicode-bidi` automatically |
| `text-rendering` | Yes (v12) | `optimizeSpeed` disables font smoothing |

### textArea Properties (SVG Tiny 1.2)

| Property | Supported | Notes |
|----------|-----------|-------|
| `text-align` | Yes (11.3+) | `start`, `end`, `center`, `justify` |
| `display-align` | Yes (11.3+) | `auto`, `before`, `after`, `center` — vertical alignment |

## Image

| Element | Supported | Notes |
|---------|-----------|-------|
| `<image>` | Yes | All 4D picture codecs supported (including SVG). Local/external file URIs + base64 embedding (11.3+) |

## Clipping

| Element | Supported | Notes |
|---------|-----------|-------|
| `<clipPath>` | Yes | v12: `rect`, `line`, `polyline`, `polygon`, `circle`, `ellipse`, `path` |
| `clip-path` | Yes | Only `clipPath` elements can be referenced |

## Markers

| Element/Property | Supported (11.3+) | Notes |
|-----------------|-------------------|-------|
| `<marker>` | Yes | `markerUnits`, `refX/Y`, `markerWidth/Height`, `orient`, `viewBox`, `preserveAspectRatio` |
| `marker-start` | Yes | Local URIs only |
| `marker-mid` | Yes | Local URIs only |
| `marker-end` | Yes | Local URIs only |

## Filters

| Element | Supported | Notes |
|---------|-----------|-------|
| `<filter>` | Yes | `filterUnits`, `primitiveUnits`, `x`, `y`, `width`, `height` |
| `<feGaussianBlur>` | Yes | Single `stdDeviation` value for both X and Y |
| `<feColorMatrix>` | Yes | All types |
| `<feOffset>` | Yes | `dx`, `dy` |
| `<feBlend>` | Yes | v12: Windows only `over`, Mac all types. With Direct2D (v14 R5+), all blend types should work cross-platform |
| `<feComposite>` | Yes | v12: Windows only `over`, Mac `normal`/`in`/`out`/`atop`. With Direct2D (v14 R5+), parity expected |

**Mac-only Shadow shortcut**: If a `<filter>` element has `id="Shadow"`, it is implemented as a native Quartz2D shadow layer (offset from `feOffset`, color from `feColorMatrix` last column, blur from `feGaussianBlur`).

Common filter input: only `SourceGraphic` and `SourceAlpha` are supported for the `in` attribute.

## CSS2 Styles

| Feature | Supported (11.3+) | Notes |
|---------|-------------------|-------|
| Selectors | Yes | Universal, type, class, attribute, ID, descendant, child, adjacent; `:first-child`, `:lang()` pseudo-classes |
| `!important` | Yes | Required to override explicitly-set (non-inherited) attributes |
| `@media` | Yes | Only `print`, `screen`, `all` |
| `@import` | Yes | Relative/absolute URIs |
| `xml-stylesheet` | Yes | CSS only (`type="text/css"`) |
| Embedded `<style>` | Yes | |

**Note**: CSS styles do **not** override attributes that are explicitly set on an element unless `!important` is used.

## Animation (via 4D Commands)

SMIL `<animate>` elements are **not supported**. Instead, animate via `SVG SET ATTRIBUTE` (rendering tree — fast, non-persistent) or `DOM SET XML ATTRIBUTE` (DOM tree — persistent, requires re-export).

### Animatable Elements

`svg`, `g`, `defs`, `use`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `path`, `rect`, `text`, `tspan`, `textArea`, `image`

**Caution**: If a parent element is not animatable (e.g. `<symbol>`), its children are not animatable either.

### Non-Animatable Attributes

`id`, `lang`, `class` (and their `xml:` prefixed variants) — can be **read** but not animated.

All common properties (`fill`, `stroke`, `marker`, etc.) are animatable.

### `SVG SET ATTRIBUTE` Behavior

- Modifies only the SVG graph tree attached to the form object (not the picture variable data source)
- Invalidates only the bounding box of the modified element (fast refresh)
- Ideal for animation/real-time feedback; **not for editing** (changes cannot be exported)
- Pass a trailing `*` to modify the SVG picture data itself (persistent)
- Non-modifiable elements: `linearGradient`, `radialGradient`, `stop`, `solidColor`, `marker`, `symbol`, `clipPath`, `fe*` children, `style`, `pattern`
- No error thrown for wrong element ID or attribute — command silently does nothing
- https://developer.4d.com/docs/commands/svg-set-attribute

### `SVG GET ATTRIBUTE` Behavior

- Can return **current** value (from form object rendering tree) or **initial** value (from parsed data source)
- Wrong element ID → empty string, `OK` set to 0
- Wrong attribute → empty string, `OK` unchanged
- https://developer.4d.com/docs/commands/svg-get-attribute

### `SVG SHOW ELEMENT`

- Scrolls/pans the SVG rendering to make the specified element visible in the form object
- https://developer.4d.com/docs/commands/svg-show-element

## 4D Reserved Attributes

| Attribute | Access | Description |
|-----------|--------|-------------|
| `4D-text` | Read/Write | Replace or read text node content. Only for `<text>`, `<tspan>`, `<textArea>`. Use with `SVG SET ATTRIBUTE` / `SVG GET ATTRIBUTE` |
| `4D-bringToFront` | Write | Set to `"true"` to move element to front of siblings |
| `4D-isOfClass-{names}` | Read | Returns `"true"` if element's inherited class contains all specified names. E.g. `4D-isOfClass-land` returns `"true"` if class is `"land department01"` |

## SVG Viewport Fill (SVG Tiny 1.2)

| Attribute | Default | Notes |
|-----------|---------|-------|
| `viewport-fill` | `white` | Background color of the SVG canvas |
| `viewport-fill-opacity` | `0.0` | Opacity of the viewport fill (default is transparent) |

Set on the `<svg>` root element to control the canvas background without adding a `<rect>`.
