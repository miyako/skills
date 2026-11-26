---
name: 4dlocalise
description: >
  Localise a 4D project with XLIFF: Resources/<lang>.lproj/*.xlf files,
  :xliff: references in menus.json and .4DForm JSON, Localized string in
  .4dm code (Get localized string before 20 R7), ID-based vs object-name
  <group> rules, 4D's built-in Common* IDs, placeholders for counts and word
  order, line breaks, entity attributes that follow the UI language
  (computed get/orderBy), stored enumerations (key in data, label in UI),
  an in-app language switch, styled text in XLIFF, moving UI text out of
  the data file, pages served by the 4D web server, Japanese UI text
  conventions, and scripts that generate paired XLIFF files, convert form
  literals and cross-check IDs. Use when adding a language or replacing
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
* enumerations stored as keys and shown as labels (status, category) --
  `references/stored-enumerations.md`
* UI text stored in the data file (styled-text rows, help pages) moved to
  XLIFF -- `references/data-text-migration.md`
* HTML pages served by the project's web server -- `references/web-pages.md`
* Japanese UI text: spacing, punctuation, what stays Latin --
  `references/japanese.md`
* generating paired XLIFF files, converting form literals and
  cross-checking IDs with scripts (`scripts/`)

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
| Status/category values stored as text and shown in lists, drop-downs, searches | `references/stored-enumerations.md` |
| UI text (descriptions, help, styled text) read from a table instead of the project | `references/data-text-migration.md` |
| An HTML page served by the project (`WEB FOLDER`, `/RESOURCES/`) that the demo opens in a browser | `references/web-pages.md` |
| Writing or reviewing Japanese strings | `references/japanese.md` |
| XLIFF files, IDs, groups, Common IDs, line breaks, runtime language switch, generating XLIFF | this file |

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

**UI language and data language are separate decisions.** A demo whose
data is Japanese may keep Japanese sample inputs (questions, search terms)
in both UI languages; ask early instead of translating them by default.

### Following the OS language

To open in the user's OS language with a fallback, in `On Startup`:

```4d
var $language:=Get database localization(User system localization)
SET DATABASE LOCALIZATION(($language="ja@") ? "ja" : "en")
```

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
* Group strings by purpose rather than in one monolithic file. A split
  that scales: `menu`, `messages` (alerts, window titles, formats),
  `fields` (labels shared by project forms, table input/output forms and
  print forms), `toolbar` (tooltips), plus one file per form only for
  form-only strings. One file per form duplicated ~30 shared field labels
  across 12 forms in one demo.
* Per-language documents other than XLIFF (sample-data JSON, help files)
  can sit in the same `.lproj` folders. `Localized document path("x.json")`
  returns the platform path of the file for the current language (verified
  en/ja); open it with `File($path; fk platform path)`. The command is not
  `Get localized document path` (look commands up with `4dlang`).

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

**Several values.** Use numbered placeholders and one invisible helper so
each language can reorder them (`{1} of {2} projects` /
`プロジェクト {2} 件中 {1} 件`). It also works in list box footer and
column expressions:

```4d
//%attributes = {"invisible":true}
// LocalizedFormat
#DECLARE($id : Text; $values : Collection) : Text
var $text:=Localized string($id)
If ($text="")
	$text:=$id  // a missing entry stays visible instead of blank
End if 
var $i : Integer
For ($i; 1; ($values=Null) ? 0 : $values.length)
	$text:=Replace string($text; "{"+String($i)+"}"; String($values[$i-1]))
End for 
return $text
```

**Window titles set in code** (`Open form window`, `SET WINDOW TITLE`) are
user-visible strings too. A "find my window by title" reuse loop
(`4dstartup`) must compare with the *localised* title.

**Where `:xliff:` resolves.** Only in static JSON properties. A value
built in code -- a drop-down or tab `values` collection, a label set with
`OBJECT SET TITLE` -- must use `Localized string`. An input `placeholder`
accepts `":xliff:ID"` only as its whole value, never mixed with static
text. `Localized string` returns `""` and sets `OK` to 0 when the ID is
missing; fall back to a default rather than displaying an empty label.

**Lists built in code.** Keep a short list in **one** trans-unit, `|`
separated, so the translator sees the whole list and its order in
context, and split it in `On Load`:

```4d
Form.tripType:={values: Split string(Localized string("NewTrip_TripTypes"); "|"); index: 0}
```

Remove `choiceList` / `saveAs` from the object in the form JSON when the
data source becomes such an object. The same works for parallel lists
(a decimals list `2|2|0` next to a currency list). Values that are
**stored** need a key, not the label (`references/stored-enumerations.md`).

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
* **Scope.** Without `*` the call applies to the host project **and every
  component**, in all processes; with `*` only to the project that called
  it. An in-app switch passes no `*` so components follow the UI.
* Built-in `Common*` IDs do **not** follow the switch (see "XLIFF Rules").
  4D's own design-mode windows do (the Explorer title turned Japanese);
  only `Common*` lookups from project code stay in the app language.
* **In-app language switch (verified, 4D 21 R5).** A language drop-down
  on the start screen calls an invisible `SwitchLanguage($code)`:

  ```4d
  If ($code=Get database localization(Current localization))
  	return 
  End if 
  SET DATABASE LOCALIZATION($code)
  CANCEL  // closes the current DIALOG(...; *)
  CALL WORKER(1; "<start method>"; {})  // 4dstartup: reopens it
  ```

  The start method's `SET MENU BAR(1)` re-localises `:xliff:` menu titles.
  Name the languages in their own language ("English", "日本語") and do
  not localise those names. Child windows already open keep their
  language until reopened. Stored data is not touched
  (`references/stored-enumerations.md`).
* Dates and numbers in list boxes and inputs follow the **OS** format
  ("Nov 25, 2026" on an English OS), not the database localisation. List
  it as a known gap rather than calling the UI fully localised.

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
  `CommonNo`, `CommonClose`, `CommonTrue`, `CommonFalse`, and **never
  redefine them** in project files. They resolve in the 4D application's
  language and ignore `SET DATABASE LOCALIZATION`: in the 4D 21 R5 GUI,
  `:xliff:CommonCancel` stayed "Cancel" after switching to `ja` (OS en-GB,
  4D app UI Japanese). Use them only when the UI language always equals
  the app's language. When the language is chosen at runtime, define
  project IDs instead (`Button_Cancel`: Cancel / キャンセル), and copy the
  wording from 4D's own files
  (`4D.app/Contents/Resources/<lang>.lproj/Common<LANG>.xlf`) so it matches
  the system. A project ID that happens to share a `Common*` name looks
  translated in English and fails silently in Japanese: check the `ja`
  capture.
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

IDs match `^[A-Za-z][A-Za-z0-9_]*$`: no dots or dashes (rename
`model.ready` to `Model_Ready`). Lint every `id`/`resname` and every
`:xliff:`/`Localized string` reference against it.

## Generating XLIFF

Keep one table of strings and generate the paired files instead of
editing languages × files XML by hand. In one demo, 12 files stayed in
sync through five rounds of string changes:

```sh
python3 skills/4dlocalise/scripts/xliff_pair.py strings.json Resources/
```

`strings.json` holds `"_languages": ["en", "ja"]` (first = source) and one
key per file name, each a list of `[id, text per language...]` rows. The
script fails on duplicate IDs, wrong column counts and redefined `Common*`
IDs, writes ID-based units directly under `<body>`, and writes line breaks
as `&#13;`. It overwrites the generated files: keep the table as the only
source, outside `Project/` (commit it under a `tools/` subfolder the
repository owns, or not at all).

**Styled text.** A multistyle string is stored as `<span style=...>`
markup, which must be XML-escaped **once** inside `<source>`/`<target>`.
Write the markup raw in `strings.json`; `xliff_pair.py` escapes it on
write. When many paragraphs share fragments (bold terms, coloured API
names), generate the table with small helpers (`b(t)`, `api(t)` returning
`<span style="font-weight:bold">t</span>`, ...) instead of typing spans:
hand-escaped `&lt;span ...&gt;` in XLIFF was the error-prone step in one
demo. Do not put `color:#000000` in spans: it stays black in dark mode
(`4dcss`, `references/dark-mode.md`). Show it in an input with
`"styledText": true`.

**Byte order mark.** 4D writes some JSON files (`menus.json`, some forms)
with a UTF-8 BOM. `jq` and `json.loads` on a `utf-8` read fail on it; read
with `utf-8-sig`, or strip and restore it (both scripts keep it).

**Converting form literals.** 4D-written `.4DForm` files round-trip
byte-exactly through `json.dumps(obj, indent="\t", ensure_ascii=False)`
with **no trailing newline** (all 15 forms of one demo). Prove it per file
before a scripted edit:

```sh
python3 skills/4dlocalise/scripts/localise_form_json.py mapping.json Project/Sources/Forms/*/form.4DForm --dry-run
```

`mapping.json` maps exact literals to IDs. The script skips any file that
does not round-trip, replaces whole-value `text`, `windowTitle`,
`tooltip`, `placeholder` and `labels` items with `:xliff:` IDs, and lists
the literals it did not map. Table forms (`Project/Sources/TableForms/`)
take the same path. Validate the result with `4dform`.

## Verification

* Every ID referenced by `:xliff:` or `Localized string` exists in every
  language's files, and every defined ID is used:

  ```sh
  python3 skills/4dlocalise/scripts/xliff_check.py .
  ```

  It reports `MISSING` and `PARTIAL` IDs (exit 1) and `UNUSED` ones.
  `Localized string("Step_Tab"+String($i))` is detected as a dynamic
  prefix; pass `--dynamic PREFIX` for IDs built in other ways.
* Each `.xlf` is well-formed XML (e.g. `python3 -c "import
  xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" file.xlf`).
* Changed `.4dm` files pass `4dlsp`.
* When 4D or tool4d is available (`4dcli`), run a test method that calls
  `SET DATABASE LOCALIZATION("ja")` then `Localized string` for several IDs,
  and again for the source language. On a temporary copy of the project, a
  throw-away startup method can loop over the languages, call the real
  init code and write the results with
  `File($path; fk posix path).setText(JSON Stringify($results; *))`; the
  JSON proves the XLIFF resolves without a GUI. Built-in `Common*` IDs were observed
  to stay English in tool4d (`CommonMenuItemQuit` → "Quit" under `ja`)
  and in the 4D GUI after a runtime switch (above). On a Japanese OS they
  have not been checked.
* `xliff_check.py` cannot see the `Common*` problem above: treat every
  `:xliff:Common*` as a warning when the project has more than one
  `.lproj`.
* `fourdform <form> --language ja` (`4dform`) resolves `:xliff:` from
  `Resources/ja.lproj`: a quick way to spot a literal left in a form.
* **Per-language runtime captures** are possible without anyone at the
  screen: full 4D with `--startup-method` + `--user-param`, a method that
  calls `SET DATABASE LOCALIZATION(<lang>)` before opening the form, and
  the `dialog_screenshot` chain (`4dcli`, "Startup-Method Patterns").
  tool4d alone cannot show forms. This is the recommended visual check.
* **Width in every language, at runtime.** Japanese is wider at the same
  font size; two truncations in one demo (a tile subtitle, list box names)
  showed only in `ja` runtime captures. Capture each form in each language
  (`4dcli`: `dialog_screenshot_with_data`, or the real-window capture in
  `references/shared-desktop.md` for review images); static previews do not show
  strings built in code. Without 4D, ask the user to check label fit.

## Checklist

- [ ] `compatibilityVersion` checked; correct command name used
- [ ] `menus.json`, every `form.4DForm` and every `.4dm` scanned (`references/what-to-localise.md`)
- [ ] `Resources/{lang}.lproj/` exists for every language, source included
- [ ] `{name}{LANG}.xlf` files exist for every language
- [ ] ID-based entries directly under `<body>`, not in form groups
- [ ] No `Common*` ID redefined; none used where the language is switched at runtime
- [ ] Multi-line strings keep CR line breaks (`&#13;`)
- [ ] IDs match `^[A-Za-z][A-Za-z0-9_]*$`
- [ ] `xliff_check.py` reports no `MISSING` / `PARTIAL`; `UNUSED` reviewed
- [ ] No user-visible text left in the data file or in served HTML (`references/data-text-migration.md`, `references/web-pages.md`)
- [ ] Stored enumerations displayed through labels, never the stored key
- [ ] Every form captured at runtime in every language; no truncation
- [ ] `<source>` is English; `<target>` translated (identical in the English file)
