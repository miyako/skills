---
name: demo-hdi
description: >
  Conventions for 4D "How do I" (HDI) example repositories: the HDI splash
  form (options object with title, info, blog, minimum version and
  license; title-less card window; Demo / Close button and version or
  license error state; splash XLIFF keys), chaining to the demo form, an
  optional "English | 日本語" switch on the splash, and the HDI README
  intro and modernisation-branches table. Replaces the HDI_Template
  instruction files. Use when converting, modernising, localising or
  documenting an HDI repository (topic 4d-hdi, a form named HDI).
---

# HDI Example Repositories

HDI ("How do I") demos are small 4D examples, each showing one feature.
They open on a branded splash (form `HDI`) that checks the 4D version and
license, then chain to the demo form (often `HDI2`). This skill holds
only the HDI-specific parts; the generic rules live in the skills linked
below. It replaces the instruction files of the archived `HDI_Template`
repository (`startup`, `readme.structure`, `readme.branches`). Those
files were a baseline: confirm current choices with the owner.

`HDI_Template` is **archived and not canonical**: build a new splash from
this skill instead of copying its form or assets. Copying the template
splash wholesale carries stale artefacts that the skill does not describe
(a v17-era 4D icon, XLIFF key names that predate the spec --
`HDI_TxtTitle`/`HDI_Heading`/`HDI_ErrorMainText`/`HDI_ErrorSubText`
instead of `HDI_Title`/`HDI_HowDoI`/`HDI_ErrorMain`/`HDI_ErrorSub`, keys
split between the `HDI` pair and `messagesEN.xlf`, template-only objects).
Found the hard way in [miyako/HDI_ManageIndexes](https://github.com/miyako/HDI_ManageIndexes).

## Related

| Topic | Skill |
|---|---|
| Startup worker, window reuse loop, `DIALOG(*)`, chaining forms, `formClass` forms | `4dstartup` |
| Attendee-shareable repository, survey, clean-up, `.agents` | `demo-shareable-repo` |
| README structure and rules | `demo-shareable-repo` (`references/readme.md`) |
| XLIFF, language switch, data text to XLIFF, served pages | `4dlocalise` |
| Theme, dark mode, real buttons | `polish-ui-pass` |
| Localising the whole demo | `demo-localise` |

## Branches

"The demo is the point": change only what the effort needs, one branch
per effort (convert, modernise, localise, polish, README), each reviewed
by the owner. The README "Modernisation notes" table lists them.

## Splash Form (`HDI`)

The start method runs the `4dstartup` pattern (worker 1, bring an open
window to the front, `SET MENU BAR`), then passes an options object to
the splash. Every property is optional; the splash hides the matching
row when it is absent.

```4d
$options:={}
$options.title:=Localized string("HDI_Title")
$options.info:=Localized string("HDI_Info")
$options.blog:="blog.4d.com"           // blog host or post URL
$options.minimumVersion:="2150"        // Application version format: 2150 = 21 R5
// $options.license:=4D View license   // only if the demo needs one

$window:=Open form window("HDI"; Plain form window; Horizontally centered; Vertically centered)
SET WINDOW TITLE($title; $window)
DIALOG("HDI"; $options; *)
```

* **Window title:** the splash is a title-less card, so `$title` is
  `""`; the reuse loop and the next window use the same title
  (`4dstartup`, "Moving to the Next Form").
* **Version check (`On Load`):** `minimumVersion` gives the label
  "4D 21 R5 and above" (`HDI_TxtVersion` with `{version}`) and swaps the
  4D icon for the R icon when the release digit is not 0. If
  `Application version` is lower, show the error state.
* **License check:** if `license` is set and `Is license available` is
  false, show the error state with the matching text.
* **Error state:** `Form.quit:=True`, the Demo button title becomes
  `BtnClose`, and the hidden objects `ErrorMainText`, `ErrorSubText` and
  the translucent `White90` cover become visible.
* **Demo button** (`BtnDemo`, standard action `accept`):

  ```4d
  If (FORM Event.code=On Clicked)
  	If (Form.quit)
  		INVOKE ACTION(ak return to design mode)
  	Else 
  		$window:=Open form window("HDI2"; Plain form window; Horizontally centered; Vertically centered)
  		SET WINDOW TITLE(Get window title(Current form window); $window)
  		DIALOG("HDI2"; *)  // HDI2 has a formClass: do not pass Form
  	End if 
  End if 
  ```

  Pass `Form` only when the demo form has no `formClass` and needs the
  splash data.
* **Picture:** the splash artwork (with its baked-in English "How do I"
  title) is the series brand; keep it in every language and give it a
  `_dark` variant rather than redrawing it.

### Splash XLIFF keys

One `HDI` XLIFF pair per language. Keep the IDs so the splash form can be
copied between HDI repositories.

| ID | English source |
|---|---|
| `HDI_Title` | the demo title (per repository) |
| `HDI_Info` | one sentence on what the demo shows (per repository) |
| `HDI_HowDoI` | `How do I…` (series brand; usually not translated) |
| `HDI_LabelVersion`, `HDI_LabelInfo`, `HDI_LabelBlog` | `Version:`, `Info:`, `Blog:` |
| `HDI_TxtVersion` | `{version} and above` |
| `HDI_BtnDemo`, `BtnClose` | `Demo`, `Close` |
| `HDI_ErrorMain` | `Sorry, this "How do I" (HDI) example must be used with a newer version of 4D ({version} and above)` |
| `HDI_ErrorSub` | `Do not attempt to open this HDI in design mode using this version; if you do so, forms and/or methods could be altered because of missing functionality.` |
| `ErrorViewProMain`, `ErrorViewProSub`, `ErrorWriteProMain`, `ErrorWriteProSub` | license errors for 4D View Pro / 4D Write Pro |

The keys are not all in the same file: the splash form's own `:xliff:`
references resolve from the `HDI` pair, but keys read from code with
`Localized string()` -- `HDI_Title` and `HDI_Info` in the start method's
options object, `BtnClose` in the error state -- may live in
`messagesEN.xlf` instead. Verify where each key actually lives before
adding a new one; a key present in only one file still resolves, but the
split is easy to miss when copying the splash into a new repository.
Consolidating every `HDI_*` key into the `HDI` pair (so both the form's
`:xliff:` references and `Localized string()` calls resolve from one
file) is the cleaner arrangement; a missing key fails silently --
`Localized string` returns an empty string and the row renders blank.

### Language switch (optional)

When the demo is presented in both languages, put an
`English | 日本語` dropdown on the splash, initialised from
`Get database localization(Current localization)`. On change:
`SET DATABASE LOCALIZATION($lang)`, `CANCEL`, then
`CALL WORKER(1; "<start method>"; {})` (`00_Start` in the template) so the splash reopens and every
`:xliff:` reference resolves again (`4dlocalise`, "Switching
Language at Runtime"; `4dstartup`, "Hub Start Screen").

## Repository

* Commit `Data/` when the demo needs its records (the template ignored
  it): `4dproject`, `demo-sample-data`.
* The `.agents` skills submodule is a per-project choice: the template
  had it; a demo handed to attendees may leave it out
  (`demo-shareable-repo`, "Skills submodule").
* **Regenerate the shipped data with the shipped generator before
  release.** The committed data file may predate the final generator
  code, so a generator bug surfaces only when a fresh clone first runs
  (or when a schema change forces a regeneration) -- in
  [miyako/HDI_ManageIndexes](https://github.com/miyako/HDI_ManageIndexes)
  the generator subscripted 0-based collections with a 1-based index
  (`[($i-1)%$length+1]`, error `-10713 Index in collection is out of
  range` at the last element) and never wrote a field the UI needed;
  the committed data predated both defects and hid them. Regenerate,
  re-run the headless self-tests against the fresh file, then commit.

## README

Follow `skills/demo-shareable-repo/references/readme.md`, with these
HDI parts:

* **Intro:** one sentence on the feature, then "Originally published by
  4D as a **HDI** (*How Do I*) example for **4D <version>**; converted
  from the binary `.4DB` to the `.4DProject` architecture so it runs on
  current 4D releases." Restored (pre-blog) demos say "restored" and have
  no Modernisation notes.
* **Key commands** table: 4-10 commands central to the demo; no
  boilerplate (`ALERT`, `Localized string`, `ARRAY TEXT`).
* **References:** the 4D blog post, the 4D documentation page, the
  original download, and the index
  [miyako/4d-hdi](https://github.com/miyako/4d-hdi).
* **Screenshots:** keep the existing `<img>` tags.
* **Modernisation notes:** this intro sentence and header, verbatim:

  ```markdown
  Each branch represents a distinct modernisation effort, guided by a 4D skill or a repository instruction file.

  | Branch | Description | Guidance |
  |--------|-------------|----------|
  | [`<branch>`](../../tree/<branch>) | <one sentence: what changed and why> | [`<skill>`](https://github.com/miyako/skills/tree/main/4d-skills/skills/<skill>) |
  ```

  One row per branch **that exists on the remote** (`git branch -r`),
  oldest first; no transient branches (README-only, merge); every
  Guidance link must resolve. Fabricated history is worse than none.

## Checklist

- [ ] Splash: options object; rows hidden when absent; version and license error states tested
- [ ] Title-less splash window; demo window copies its title; only one untitled window in worker 1
- [ ] `DIALOG("HDI2"; *)` without `Form` when HDI2 has a `formClass`
- [ ] Splash XLIFF IDs kept; series brand kept in English unless the owner decides otherwise
- [ ] Language switch reopens the splash (if added)
- [ ] README: HDI intro, Key commands, References with the 4d-hdi index, branch table from real remote branches
