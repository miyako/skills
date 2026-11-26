---
name: demo-sample-data
description: >
  Sample data for a 4D demo that is presented and shared: per-language
  Resources/<lang>.lproj/sampleData.json loaded with Localized document path,
  a generator method and a "regenerate data" button, realistic names per
  audience (e.g. Japanese person and project names), stored keys rather than
  labels, unique values, a sentence separator per language, and whether to
  commit Data/. Use when a demo's data must match the presentation language
  or look plausible to a local audience.
---

# Demo Sample Data

## Scope

* where sample texts live and how the generator finds the right language
* what makes generated data look plausible to the audience
* shipping data with the project

### Not in this skill

| Topic | Skill |
|---|---|
| XLIFF, `Localized string`, `Localized document path` details | `4dlocalise` |
| Values stored as keys and shown as labels (status, category) | `4dlocalise` (`references/stored-enumerations.md`) |
| Free text stored per language in the catalog (`nameEN`/`nameJA`) | `4dlocalise` (`references/language-attributes.md`) |
| ORDA create/drop/save | `4dorda` |
| `.gitignore` for `Data/` | `4dproject` |
| Replacing a technote's data set and the examples in its text | `technote-localise-demo-data` |
| Large data or data shipped as a release asset | `demo-data-distribution` |
| Hub start screen hosting the regenerate button | `4dstartup` |

## Files

```
Resources/
  en.lproj/sampleData.json
  ja.lproj/sampleData.json
```

One JSON per language with the same keys, for example:

```json
{
  "separator": "",
  "projectNames": ["CRMシステム導入", "社内ポータル刷新"],
  "managers": ["佐藤 美咲", "田中 健"],
  "taskNames": ["要件定義", "テスト計画の作成"],
  "commentStarts": ["..."],
  "projectStatusComments": {"To Do": ["..."], "In Progress": ["..."]}
}
```

* `separator` joins generated sentences: `" "` in English, `""` in Japanese.
  Never hard-code a space between fragments.
* Comment pools keyed by the **stored status key** ("In Progress"), not the label.
* Keep the files next to the XLIFF so that a translator sees all
  per-language material in one folder.

## Generator

```4d
var $path:=Localized document path("sampleData.json")
var $file : 4D.File
If ($path#"")
	$file:=File($path; fk platform path)
End if
If ($file=Null) || (Not($file.exists))
	$file:=Folder(fk resources folder).file("en.lproj/sampleData.json")
End if
var $data : Object:=JSON Parse($file.getText())
```

* `GenerateData` drops existing records, resets the table sequence numbers,
  and creates records **in the current display language**. It returns counts
  (`{projects; tasks}`) for a confirmation message.
* **Unique where users look for uniqueness:** create one record per entry in
  the name list instead of drawing names at random. Random draws produced
  duplicate project names in a list.
* Statuses, categories and similar enumerations are written as keys; the UI
  translates them.
* Keep randomness where it reads naturally (progress, dates, assignee), and
  make derived values consistent with the stored key: "Completed" at
  100 %, "To Do" at 0 %, anything else in between.

## In the demo UI

A "Generate sample data" button on the start screen (`4dstartup` hub)
confirms, calls `GenerateData`, and reports the counts with a localised
message (`LocalizedFormat`). Combined with the language switch, the presenter
can show Japanese data, and attendees can regenerate data in their own language.

## Audience realism

* Japanese audience: family name + given name with a space (`佐藤 美咲`),
  project names that mix kanji/katakana with Latin acronyms the way Japanese
  companies write them (`CRMシステム導入`, `ECサイトリニューアル`), sentences
  ending in 。 with no inter-sentence space.
* English data: plausible international names. Avoid famous people and real
  companies.
* No personal data, no real customer names, nothing that dates quickly.

## Shipping data

* If attendees should open the project with data, commit `Data/data.4DD`
  (narrow the canonical `.gitignore` as described in `4dproject`), generated
  in the **source language**, and point to the regenerate button in the
  README. Data too large for the repository: `demo-data-distribution`.
* Regenerate it with the final generator before the handoff commit.

## Checklist

- [ ] `sampleData.json` exists in every `.lproj` with identical keys
- [ ] Generator falls back to `en.lproj` when the file for the current language is missing
- [ ] Separator per language; no hard-coded spaces between fragments
- [ ] Enumerations written as keys
- [ ] Names unique where the UI lists them
- [ ] Shipped data regenerated with the final generator, in the source language
- [ ] Runtime screenshot of the main list in each language (`4dcli`)
