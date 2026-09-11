---
object: "picture"
json_type: "picture"
keywords: ["static picture", "pictureFormat", "scaled", "tiled", "truncatedCenter", "dark mode", "@nx", "_dark", "SVG", "WEBP"]
summary: "Static picture object: pictureFormat modes, resource paths, high-res/dark-mode naming conventions, SVG/WEBP support."
---

# 4D Static Picture Object

Reference: https://developer.4d.com/docs/FormObjects/staticPicture
Also: https://developer.4d.com/docs/FormEditor/pictures (native picture format support, high-res, dark mode)

## Basic Definition

```json
{
  "myPicture": {
    "type": "picture",
    "top": 20,
    "left": 20,
    "width": 180,
    "height": 120,
    "picture": "/RESOURCES/Images/logo.png",
    "pictureFormat": "scaled"
  }
}
```

A static picture is a **static object** (no data source, no interaction). It is stored **outside the form**, referenced by path, and inserted by reference rather than embedded. Placing it on **page 0** makes it a background shared by all pages of the form (and reusable across inherited forms) -- cheaper than duplicating the picture on every page.

## Pathname

The `picture` property is a POSIX-syntax path. Three forms:

| Form | Example | Resolution |
|------|---------|------------|
| Resources folder | `"/RESOURCES/Images/logo.png"` | Shared across forms in the project |
| Form-local folder | `"4D.png"` / `"Images/logo.png"` | Resolved relative to the form's own folder; keeps the form portable/movable |
| Picture variable | `"var:myPictureVar"` | Picture must already be loaded into the named variable at runtime |

Both `/RESOURCES/Images/...` and form-relative filenames (bare filename or `Images/...` next to `form.4DForm`) are valid and render correctly.

## Display (`pictureFormat`)

| JSON value | Effect |
|------------|--------|
| `"scaled"` | **Scaled to fit**: picture is resized to exactly fill the object's width/height. Not aspect-ratio aware -- if the box's aspect ratio differs from the source picture, the image visibly distorts (stretches/squashes). |
| `"tiled"` | **Replicated**: picture repeats (tiles) to fill an enlarged area, undistorted. If the box is smaller than the source, it is truncated (non-centered). |
| `"truncatedCenter"` | **Center**: picture is centered at its native pixel size; anything beyond the box is cropped equally from all edges. |
| `"truncatedTopLeft"` | **Truncated (non-centered)**: picture's top-left corner is pinned to the box's top-left at native pixel size; overflow is cropped from right/bottom only. Scrollbars can be added to this format. |

Only these four values are supported for the static picture object (`OBJECT Get format` / `OBJECT SET FORMAT` commands).

## High-Resolution Pictures (`@nx`)

Add `@2x`, `@3x`, etc. to a filename placed **next to** the base picture (`icon.png`, `icon@2x.png`, `icon@3x.png`) to supply pre-rendered high-DPI variants. 4D automatically substitutes the highest-resolution variant available for the current screen -- you still reference only the base name (`"picture": "/RESOURCES/Images/icon.png"`) in the JSON; you never reference the `@nx` file directly. This prioritization only happens for on-screen display, never for printing. In a headless render with no physical high-DPI display, the `1x` (base) variant is always used.

## SVG Pictures

SVG is a native, fully supported picture format. A plain-text SVG file (`<?xml version="1.0"?><svg xmlns="...">...</svg>`) can be referenced from `"picture"` exactly like a PNG/JPEG; vector content (shapes, text) is rasterized into the object at whatever size/crop the `pictureFormat` dictates, following the same distortion/cropping rules as raster formats.

### `vector-effect="non-scaling-stroke"`

Reference: https://blog.4d.com/svg-non-scaling-stroke-attribute-support/

By default, an SVG's stroke width scales along with the rest of the shape when the containing object is enlarged -- fine for filled shapes, but wrong for things like grid lines or map overlays that should stay a constant on-screen thickness regardless of zoom/scale. Adding `vector-effect="non-scaling-stroke"` to a stroked element keeps its stroke width fixed under scaling:

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <line x1="0" y1="20" x2="100" y2="20" stroke="black" stroke-width="1"
        vector-effect="non-scaling-stroke"/>
</svg>
```

Without the attribute, a stroke drawn at `stroke-width="1"` in a 100x100 viewBox scales up proportionally with the object (e.g. to ~3px when the object is enlarged 3x). With `vector-effect="non-scaling-stroke"`, the stroke stays hairline-thin regardless of enlargement.

This is the mechanism 4D recommends as a substitute for drawing grid lines with shape primitives/4D drawing code: author the grid as an SVG with `non-scaling-stroke` on every line, drop it into a static picture object with `pictureFormat: "scaled"`, and the line weight will not visually thicken as the box is resized.

## Dark Mode Pictures (`_dark` suffix)

Reference: form-level `colorScheme` property (`"dark"` / `"light"`), https://developer.4d.com/docs/FormEditor/propertiesForm#color-scheme

Placing `theme.png` and `theme_dark.png` side by side in the same folder, and referencing only `theme.png` in the JSON, makes 4D substitute `theme_dark.png` automatically whenever the form's current color scheme is dark (`"colorScheme": "dark"` on the form).

## Other Native Formats

| Format | Support |
|--------|---------|
| PNG | Both platforms |
| JPEG | Both platforms |
| BMP | Both platforms |
| TIFF | Both platforms |
| SVG | Both platforms |
| GIF (single frame) | Both platforms |
| GIF (animated) | Both platforms; animates at runtime (see below) |
| WEBP | macOS |
| PDF | macOS; first page only, and typically lower-fidelity than raster formats |

Exact codec availability is queryable at runtime via `PICTURE CODEC LIST`.

## Animated GIF

An animated GIF placed in a static picture object plays its animation **at runtime** in the live 4D application/interpreter. A single-frame screenshot (`FORM SCREENSHOT`) only captures one static frame -- it cannot show the animation and is not a way to verify animated-GIF playback; that requires interactive observation.

## Supported Properties Summary

| Property | JSON Name | Notes |
|----------|-----------|-------|
| Pathname | `picture` | POSIX path; `/RESOURCES/...`, form-relative, or `var:name` |
| Display | `pictureFormat` | `"scaled"`, `"tiled"`, `"truncatedCenter"`, `"truncatedTopLeft"` |
| Top/Left/Width/Height | `top`, `left`, `width`, `height` | Standard coordinates/sizing |
| Horizontal/Vertical Sizing | `sizingX` / `sizingY` | Resizing behavior, same as other objects |
| Visibility | `visibility` | `"visible"` / `"hidden"` |
| CSS Class | `class` | CSS class hook |
| Object Name | (JSON key) | Object identifier |
| Type | `"type": "picture"` | Fixed |

Static pictures have **no data source** and no configurable event set of their own beyond the generic object identity/positioning properties -- they are purely visual/static, unlike picture buttons or picture pop-up menus which share the same `picture`/pathname mechanics but add interactivity. See `picture-button.md` and `picture-popup.md` for those object types.

## Comparison with Related Picture-Based Objects

| Feature | Static Picture | Picture Button | Picture Pop-up Menu |
|---------|----------------|----------------|----------------------|
| Interactive | No | Yes | Yes |
| Multi-frame grid (`rowCount`/`columnCount`) | No -- single image only | Yes | Yes |
| `pictureFormat` (scaled/tiled/truncated) | Yes | No (uses frame grid instead) | No |
| Typical use | Decoration, background, logos | Buttons with custom art | Icon-driven popup selection |
| Data source | None | 0-based frame index | Selection value |

## CLI Verification Note

See `../screenshot-rendering.md` for static template rendering rules, and `skills/4dcli/SKILL.md` for version requirements. `FORM SCREENSHOT` works in `tool4d` 21 R3+ and in the full 4D application.
