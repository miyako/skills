# What to Localise

Scan all three places; strings hide in each.

## 1. Menus -- `Project/Sources/menus.json`

Every menu or item `"title"` that is not already `:xliff:` must become one.
Leave separators (`"isSeparator": true`) and existing `:xliff:` titles
(e.g. `":xliff:CommonMenuFile"`) as they are.

```json
{ "title": "デモ", "method": "Demo" }
```
→
```json
{ "title": ":xliff:MenuItemDemo", "method": "Demo" }
```

Standard menus (File, Edit, Quit...) should use 4D's built-in `Common*` IDs
(see `../SKILL.md`). Menu structure itself: `skills/4dproject/references/menus.md`.

## 2. Forms -- `Project/Sources/Forms/*/form.4DForm` and `TableForms/`

Literal strings in:

* `"text"` -- static text, button labels, list box column header `text`
* `"labels"` -- tab control labels (array)
* `"title"` -- group boxes and similar
* `"windowTitle"` -- the form's window title
* `"placeholder"` -- input placeholder text

```json
"header": { "name": "Header3", "text": "値" }
"labels": ["説明", "サンプル"]
```
→
```json
"header": { "name": "Header3", "text": ":xliff:Main_HeaderValue" }
"labels": [":xliff:Main_TabDescription", ":xliff:Main_TabSample"]
```

## 3. Code -- every `.4dm` (methods, classes, form and object methods)

| Command | Arguments to localise |
|---|---|
| `ALERT` | message, button label |
| `CONFIRM` | message, OK and Cancel labels |
| `Request` | message, default value, OK and Cancel labels |
| `MESSAGE` | message |
| `DISPLAY NOTIFICATION` | title, message |
| `LOG EVENT` | message (when it is user-facing) |
| `OBJECT SET TITLE` | the title (3rd argument) |
| `SET WINDOW TITLE` | the title |

```4d
ALERT("File not found"; "Quit")
OBJECT SET TITLE(*; "btnQuit"; "Quit 4D")
```
→
```4d
ALERT(Localized string("AlertFileNotFound"); Localized string("AlertButtonQuit"))
OBJECT SET TITLE(*; "btnQuit"; Localized string("BtnQuit4D"))
```

Also look for literals assigned to anything that becomes visible text
(`$options.title:="..."`, status strings, labels built in code, list box
cell values computed in code), and for stray literals in a language other
than the source (e.g. French `"aucun"` in an English project).

Use `Get localized string` instead of `Localized string` before 20 R7 --
see "Referencing Strings" in `../SKILL.md`.
