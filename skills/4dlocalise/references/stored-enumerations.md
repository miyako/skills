# Stored enumerations: key in the data, label in the UI

A status, category or priority stored as English text ("To Do", "In Progress")
and shown as-is cannot be localised by replacing strings: the stored value is
both the data and the label. Keep the **key** in the data and show a **label**
that is looked up at display time. Changing the language then never touches the
data. This differs from `language-attributes.md`, which covers free text stored
per language (`nameEN` / `nameJA`).

## Pieces (all verified in a 4D 21 R5 demo)

| Piece | Implementation |
|---|---|
| Key list | `StatusKeys() : Collection` → `["To Do"; "Pending"; "In Progress"; "Completed"]` (the order used in drop-downs) |
| Label lookup | `StatusLabel($key) : Text` → `Localized string("Status_"+Replace string($key; " "; ""))`, returning `$key` for unknown keys or a missing entry |
| XLIFF | `Status_ToDo`, `Status_Pending`, `Status_InProgress`, `Status_Completed` in every `.lproj` |
| ORDA list boxes | entity class: `Function get statusLabel` → `StatusLabel(This.status)` and `Function orderBy statusLabel` → sorts by `status` (by key, so the label order differs per language; document it or sort by a key index) |
| Classic table forms (input/output/print) | the field object becomes an expression `StatusLabel([Task]status)` with `enterable: false` |
| Editable drop-downs | `StatusDropdown($key) : Object` returns `{values: labels; index; currentValue}` built from `StatusKeys()` + `StatusLabel`; on `On Data Change`, write `StatusKeys()[$dropdown.index]` back to the entity or field |
| Search | match the typed text against the *labels*, collect the matching keys, then `query("status in :1"; $keys)` |
| Sample-data generation | keeps writing keys |

## Checklist

- [ ] No displayed status reads the stored value directly (grep the field name in forms and `.4dm`)
- [ ] `choiceList` / static `values` on status inputs removed (they would show and write labels)
- [ ] Search by label works in each language
- [ ] Rebuild drop-down `values` after a language switch (SKILL.md, "Switching Language at Runtime")
