---
object: "docs"
json_type: ""
keywords: ["documentation", "URL", "slug", "developer.4d.com", "supported properties", "events", "FormObjects", "FormEditor"]
summary: "URL index of the official 4D documentation pages for form object types, property groups, form events and form-level pages; use to fetch the authoritative Supported Properties list."
---

# 4D Form Documentation Index

When the object file in `references/objects/` does not answer a question,
fetch the official page and read its **Supported Properties** section. Do
not guess a property -- fetch the page. Every slug below was checked to
resolve.

Form objects: `https://developer.4d.com/docs/FormObjects/<slug>`

| Object | JSON `type` | Slug |
|---|---|---|
| (all objects) | | `formObjectsOverview` |
| Button | `button` | `buttonOverview` |
| Button grid | `buttonGrid` | `buttonGridOverview` |
| Check box | `checkbox` | `checkboxOverview` |
| Combo box | `combo` | `comboBoxOverview` |
| Drop-down list | `dropdown` | `dropdownListOverview` |
| Group box | `groupBox` | `groupBox` |
| Hierarchical list | `list` | `listOverview` |
| Input | `input` | `inputOverview` |
| List box | `listbox` | `listboxOverview` |
| List box column | (`columns[]`) | `listbox-column` |
| Picture button | `pictureButton` | `pictureButtonOverview` |
| Picture pop-up menu | `picturePopup` | `picturePopupMenuOverview` |
| Plug-in area | `plugin` | `pluginAreaOverview` |
| Progress indicator | `progress` | `progressIndicator` |
| Radio button | `radio` | `radiobuttonOverview` |
| Ruler | `ruler` | `ruler` |
| Shapes (rectangle, line, oval) | `rectangle`, `line`, `oval` | `shapesOverview` |
| Spinner | `spinner` | `spinner` |
| Splitter | `splitter` | `splitters` |
| Static picture | `picture` | `staticPicture` |
| Static text | `text` | `text` |
| Stepper | `stepper` | `stepper` |
| Subform | `subform` | `subformOverview` |
| Tab control | `tab` | `tabControl` |
| Web area | `webArea` | `webAreaOverview` |
| 4D Write Pro area | `write` | `writeProAreaOverview` |

Check the `type` value against `schemas/4dform/formsSchema.json` before
writing it; the schema is authoritative for JSON names.

Property groups: `https://developer.4d.com/docs/FormObjects/<slug>`

| Topic | Slug |
|---|---|
| All properties (A-Z, with JSON names) | `propertiesReference` |
| Action | `propertiesAction` |
| Animation | `propertiesAnimation` |
| Appearance | `propertiesAppearance` |
| Background and border | `propertiesBackgroundAndBorder` |
| Coordinates & sizing | `propertiesCoordinatesAndSizing` |
| Crop | `propertiesCrop` |
| Data source | `propertiesDataSource` |
| Display | `propertiesDisplay` |
| Entry | `propertiesEntry` |
| Footers / headers / gridlines (list box) | `propertiesFooters`, `propertiesHeaders`, `propertiesGridlines` |
| Help | `propertiesHelp` |
| Hierarchy | `propertiesHierarchy` |
| List box | `propertiesListBox` |
| Object (name, type, class...) | `propertiesObject` |
| Picture | `propertiesPicture` |
| Print | `propertiesPrint` |
| Range of values | `propertiesRangeOfValues` |
| Resizing options | `propertiesResizingOptions` |
| Scale | `propertiesScale` |
| Subform | `propertiesSubform` |
| Text | `propertiesText` |
| Text and picture | `propertiesTextAndPicture` |
| Web area | `propertiesWebArea` |

Form level: `https://developer.4d.com/docs/FormEditor/<slug>` --
`forms` (overview), `propertiesForm` (form properties), `stylesheets`
(CSS; see the `4dcss` skill), `objectLibrary`, `macros`.

Events: `https://developer.4d.com/docs/Events/<slug>` -- `overview`, then
one page per event named after its JSON key (`onLoad`, `onActivate`,
`onDataChange`, `onSelectionChange`, `onAfterSort`, `onResize`, ...).
Exception: the JSON key `onClick` is documented at `onClicked`.

| JSON key (`"events"`) | 4D constant |
|---|---|
| `onLoad` / `onUnload` | `On Load` / `On Unload` |
| `onClick` | `On Clicked` |
| `onDataChange` | `On Data Change` |
| `onSelectionChange` | `On Selection Change` |
| `onAfterSort` | `On After Sort` |
| `onResize` | `On Resize` |
| `onActivate` / `onDeactivate` | `On Activate` / `On Deactivate` |

For anything else, use the documentation and forum search described in
"When the lookup tools have no answer" in `skills/4dlang/SKILL.md`.
