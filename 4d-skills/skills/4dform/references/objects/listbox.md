---
object: "listbox"
json_type: "listbox"
keywords: ["listbox", "list box", "column", "footer", "truncateMode", "withEllipsis", "resizingMode", "legacy", "rightToLeft", "column width", "minWidth"]
summary: "List box display defaults: no truncate-with-ellipsis on columns and footers, legacy (last column grows) resizing, column width properties, audit script."
---

# 4D List Box -- Display Defaults

References:
- List box overview: https://developer.4d.com/docs/FormObjects/listboxOverview
- List box column properties: https://developer.4d.com/docs/FormObjects/listbox-column
- Truncate with ellipsis: https://developer.4d.com/docs/FormObjects/propertiesDisplay#truncate-with-ellipsis
- Resizing options: https://developer.4d.com/docs/FormObjects/propertiesResizingOptions
- `LISTBOX SET PROPERTY`: https://developer.4d.com/docs/commands/listbox-set-property

This file covers the two display defaults that apply to **every** list box
written or audited with this skillset. Colours (`alternateFill`, odd-row
fill, meta-source colours) are in `skills/4dcss/references/dark-mode.md`.

| Where | Property | Value |
|---|---|---|
| every column (`columns[]`) and every footer | `truncateMode` | `"none"` |
| the list box object itself | `resizingMode` | `"legacy"` |

Set both explicitly; do not rely on defaults.

## Structure

```json
"myListBox": {
	"type": "listbox",
	"resizingMode": "legacy",
	"columns": [
		{
			"name": "colName",
			"dataSource": "This.name",
			"width": 160,
			"minWidth": 80,
			"truncateMode": "none",
			"header": { "name": "hdrName", "text": "Name" },
			"footer": { "name": "ftrName", "truncateMode": "none" }
		}
	]
}
```

`columns` is always an **array** of column objects. List boxes can sit on
page 0 (shared by all pages) or on any numbered page -- check all pages.

## `truncateMode`: `"none"`

The default `"withEllipsis"` hides part of the text behind an ellipsis --
at the **right** on Windows and in the **middle** on macOS, which makes
short values unreadable. If text does not fit, the column is too narrow:
fix `width` / `minWidth` instead of truncating.

| Property | Type | Values | Default | Applies to |
|---|---|---|---|---|
| `truncateMode` | string | `"withEllipsis"`, `"none"` | `"withEllipsis"` | list box column, list box footer |

* With `wordwrap` on a Text column, `truncateMode` has no effect.
* Boolean columns shown as checkboxes are always clipped; as pop-up menus,
  `truncateMode` applies.
* Runtime equivalent (prefer the static JSON property):
  `LISTBOX SET PROPERTY(*; "colName"; lk truncate mode; lk without ellipsis)`.

## `resizingMode`: `"legacy"`

Set on the **list box object**, not on columns.

| Value | Behaviour |
|---|---|
| `"legacy"` | Last column grows: only the rightmost column follows the list box width; the other columns keep their `width`. |
| `"rightToLeft"` | Column auto-resizing: columns are redistributed proportionally, overriding widths chosen for their content. |

Use `"rightToLeft"` only as a deliberate design decision, never as a
side effect of a default. With `"legacy"`, the column properties `width`,
`minWidth`, `maxWidth` and `resizable` are respected; a sensible `minWidth`
keeps content visible.

## Audit

1. Find every form: `Project/Sources/Forms/*/form.4DForm` and
   `Project/Sources/TableForms/*/*/form.4DForm`.
2. In every page, find objects with `"type": "listbox"`.
3. Set `resizingMode` on each list box, and `truncateMode` on each column
   and each column footer.

Scripted fix (stdlib Python; preserves tab indentation used by 4D):

```python
import json, pathlib

def fix_listboxes(form_path):
    path = pathlib.Path(form_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for page in data.get("pages") or []:
        if not isinstance(page, dict):
            continue
        for obj in (page.get("objects") or {}).values():
            if not isinstance(obj, dict) or obj.get("type") != "listbox":
                continue
            if obj.get("resizingMode") != "legacy":
                obj["resizingMode"] = "legacy"; changed += 1
            for col in obj.get("columns") or []:
                for target in (col, col.get("footer")):
                    if isinstance(target, dict) and target.get("truncateMode") != "none":
                        target["truncateMode"] = "none"; changed += 1
    if changed:
        path.write_text(json.dumps(data, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
    return changed
```

The script re-serialises the whole file. Review the diff: if it changes
more than the added properties (line endings, number formatting, key
spacing), make the edits by hand instead.

Validate changed forms against the schema as described in
`skills/4dform/SKILL.md`.

## Checklist

- [ ] Every form scanned, page 0 and numbered pages
- [ ] Every list box has `"resizingMode": "legacy"` (or a documented reason for `"rightToLeft"`)
- [ ] Every column and every footer has `"truncateMode": "none"`
- [ ] Column `minWidth` values reviewed so content stays visible
