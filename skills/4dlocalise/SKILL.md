---
name: 4dlocalise
description: >
  Localise a 4D project with XLIFF: Resources/<lang>.lproj/*.xlf files,
  :xliff: references in menus.json and .4DForm JSON, Localized string in
  .4dm code (Get localized string before 20 R7), ID-based vs object-name
  <group> rules, 4D's built-in Common* IDs, placeholders for counts and word
  order, line breaks, and entity attributes that follow the UI language
  (computed get/orderBy). Use when adding a language or replacing
  hardcoded user-visible strings.
---

# 4D Localisation (XLIFF)

## Scope

* where XLIFF files live and how they are named
* referencing strings from JSON (`:xliff:ID`) and code (`Localized string`)
* XLIFF structure rules that make or break resolution
* what to localise in menus, forms and methods -- `references/what-to-localise.md`
* data that follows the UI language (`nameEN` / `nameJA` → computed
  `name`) -- `references/language-attributes.md`

### Not in this skill

| Topic | Skill |
|---|---|
| Version detection (`Localized string` needs 20 R7+), token suffixes, `.gitignore` | `4dproject` |
| `menus.json` structure and standard actions | `4dproject` (`references/menus.md`) |
| Form JSON, list box headers, tab controls | `4dform` |
| Startup window that shows a localised title | `4dstartup` |
| Checking changed `.4dm` | `4dlsp` |

## Route Table

| Task involves | Open |
|---|---|
| Finding the strings to replace in `menus.json`, forms, `.4dm` | `references/what-to-localise.md` |
| Names/labels stored per language in the data | `references/language-attributes.md` |
| XLIFF files, IDs, groups, Common IDs, line breaks, runtime language switch | this file |

References:
- `:xliff:` references in form object titles: https://developer.4d.com/docs/FormObjects/propertiesObject#title
- `Localized string`: https://developer.4d.com/docs/commands/localized-string
- Menu properties: https://developer.4d.com/docs/Menus/properties

## Survey first

Before changing anything, list the forms and their visible strings, the
user-facing strings in methods and classes (including stray literals in
another language), per-language fields in the catalog, and the startup
flow. Then agree with the user on: scope (UI labels only, or data and
messages too), the languages (source + targets, keep existing ones?), any
new per-language attributes, and whether displayed names should follow the
UI language.

## Files

```
Resources/
  en.lproj/  menuEN.xlf  messagesEN.xlf  {FormName}EN.xlf
  ja.lproj/  menuJA.xlf  messagesJA.xlf  {FormName}JA.xlf
```

* One `Resources/{lang}.lproj/` folder per language, **including the source
  language**. A language without its `.lproj` folder cannot be selected
  with `SET DATABASE LOCALIZATION` -- the call fails silently.
* File names carry a capitalised language suffix: `{name}{LANG}.xlf`
  (`menuEN.xlf`, never `menu.xlf`). Use the `.xlf` extension (files named
  `.xliff` were observed to be ignored).
* Group strings by purpose (menus, messages, one file per form) rather than
  in one monolithic file.

XLIFF 1.2, English in `<source>`, translation in `<target>` (identical to
the source in the English file):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file datatype="plaintext" original="messages" source-language="en" target-language="ja">
    <body>
      <trans-unit id="Welcome_Title" resname="Welcome_Title">
        <source>Welcome</source>
        <target>ようこそ</target>
      </trans-unit>
    </body>
  </file>
</xliff>
```

## Referencing Strings

| Where | Syntax |
|---|---|
| JSON (`menus.json` titles, form `text`, `windowTitle`, tab `labels`, list box header `text`) | `":xliff:Welcome_Title"` |
| `.4dm` code, 20 R7+ | `Localized string("Welcome_Title")` |
| `.4dm` code, before 20 R7 | `Get localized string("Welcome_Title")` |

Decide by `compatibilityVersion` ("4D Version Detection" in
`skills/4dproject/SKILL.md`). In a 20 R7+ project, replace
`Get localized string` with `Localized string` (same command, simplified
name). Write either without a token suffix unless the exact token already
appears in the project (token rules in `skills/4dproject/SKILL.md`).

**Counts and word order** -- never concatenate translated fragments; use a
template with a placeholder:

```4d
$text:=Replace string(Localized string("Welcome_SiteCount"); "{n}"; String($count))
```

with `{n} sites` in English and `観光名所 {n} 件` in Japanese.

**Where `:xliff:` resolves.** Only in static JSON properties. A value
built in code -- a drop-down or tab `values` collection, a label set with
`OBJECT SET TITLE` -- must use `Localized string`. An input `placeholder`
accepts `":xliff:ID"` only as its whole value, never mixed with static
text. `Localized string` returns `""` and sets `OK` to 0 when the ID is
missing; fall back to a default rather than displaying an empty label.

## Switching Language at Runtime

* `SET DATABASE LOCALIZATION("ja")` affects only what is displayed **after**
  the call. Forms and subforms already loaded keep their labels: reopen
  them, or re-apply titles with
  `OBJECT SET TITLE(*; "lblName"; Localized string("Name_Label"))`
  (labels and buttons take `OBJECT SET TITLE`, not `OBJECT SET VALUE`).
* Collections built with `Localized string` for drop-downs and tabs must be
  rebuilt after the switch; keep the selected `index` and restore it.
* Language codes use a dash (`"fr-ca"`), `.lproj` folders an underscore
  (`fr_ca.lproj`).

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## XLIFF Rules

* **ID-based vs object-name-based -- never mix them in one `<group>`.**
  * ID-based entries (referenced by `:xliff:ID` or `Localized string`) are
    standalone `<trans-unit>`s directly under `<body>`.
  * Object-name-based entries (automatic form localisation) are nested in
    `<group resname="[ProjectForm]">` → `<group resname="{FormName}">`, and
    each `resname` matches a form object name.
  * An ID-based entry placed inside a form group does not resolve through
    `:xliff:`, because 4D treats entries in form groups as object-name
    matches.
  Prefer explicit `:xliff:` IDs; they are clearer than object-name matching.
* **Built-in `Common*` IDs.** 4D ships its own XLIFF (`commonEN.xlf`, ...)
  with IDs such as `CommonMenuFile`, `CommonMenuEdit`, `CommonMenuItemQuit`,
  `CommonMenuItemCopy`, `CommonOK`, `CommonCancel`, `CommonYes`,
  `CommonNo`, `CommonClose`, `CommonTrue`, `CommonFalse`. Use them for
  standard menus and buttons, and **never redefine them** in project files.
* **Line breaks.** 4D strings use CR (`\r`, `Char(13)`) as the line break.
  Inspect the original bytes (e.g. `xxd`) of a multi-line string before
  moving it to XLIFF. A literal CR inside XML is normalised to LF by the
  parser, so write `&#13;` where a CR is required.
* **Escaping.** Escape `&`, `<` and `>` in XML text.
* **Source text changes.** If the meaning of the data or UI changed, update
  the English `<source>` too and tell the user.
* **Line endings of 4D files.** 4D source files mix CRLF and LF. Preserve
  each file's line endings; never convert them in bulk.

## ID Naming

Descriptive PascalCase IDs that show purpose and scope:

| Pattern | Example | Use |
|---|---|---|
| `MenuItem{Name}` | `MenuItemDemo` | menu item titles |
| `{Form}_{ObjectHint}` | `Main_HeaderValue` | form object text |
| `{Form}_Tab{Name}` | `Main_TabDescription` | tab labels |
| `Alert{Description}` | `AlertFileNotFound` | alert / confirm messages |
| `AlertButton{Name}` | `AlertButtonQuit` | alert / confirm buttons |
| `{Feature}_{Property}` | `Welcome_Title` | strings assigned in code |

## Verification

* Every ID referenced by `:xliff:` or `Localized string` exists in every
  language's files (grep the IDs on both sides).
* Each `.xlf` is well-formed XML (e.g. `python3 -c "import
  xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" file.xlf`).
* Changed `.4dm` files pass `4dlsp`.
* When 4D or tool4d is available (`4dcli`), run a test method that calls
  `SET DATABASE LOCALIZATION("ja")` then `Localized string` for several IDs,
  and again for the source language.
* Forms cannot be checked headlessly: ask the user to open them and check
  label fit (translations can be much longer or shorter).

## Checklist

- [ ] `compatibilityVersion` checked; correct command name used
- [ ] `menus.json`, every `form.4DForm` and every `.4dm` scanned (`references/what-to-localise.md`)
- [ ] `Resources/{lang}.lproj/` exists for every language, source included
- [ ] `{name}{LANG}.xlf` files exist for every language
- [ ] ID-based entries directly under `<body>`, not in form groups
- [ ] No `Common*` ID redefined
- [ ] Multi-line strings keep CR line breaks (`&#13;`)
- [ ] `<source>` is English; `<target>` translated (identical in the English file)
