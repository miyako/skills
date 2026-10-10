---
name: 4dproject
description: >
  Work with a 4D project as a whole: the .4DProject file (compatibilityVersion,
  tokenizedText), detecting the 4D version a project targets, the rules for
  command/constant token suffixes (:C123, :K12:34) in .4dm code, the project
  folder layout and boilerplate files (folders.json, menus.json, roles.json,
  catalog_editor.json), menus.json standard actions, and the canonical
  .gitignore for 4D projects.
---

# 4D Project

## Scope

This skill owns project-level knowledge that every other 4D skill relies on:

* the `.4DProject` file itself -- the JSON anchor that identifies a project
* **4D version detection** from `compatibilityVersion` (other skills link here)
* **token suffix rules** for `.4dm` code (other skills link here)
* the canonical **`.gitignore`** for a 4D project
* project layout and boilerplate files -- `references/layout.md`
* `menus.json` standard actions vs method wrappers -- `references/menus.md`

### Not in this skill

| Topic | Skill |
|---|---|
| `catalog.4DCatalog` | `4dcatalog` |
| `.4DForm` | `4dform` |
| `.4DSettings` | `4dsettings` |
| `.4dm` validation / code intelligence | `4dlsp` |
| method attributes (`//%attributes`, invisible) | `4dmethods` |
| `C_*` → `var`/`#DECLARE`, deprecated commands | `4dmodernise` |
| XLIFF / `Localized string` | `4dlocalise` |

## Route Table

| Task involves | Open |
|---|---|
| Creating a project, the folder tree, `folders.json`, `roles.json`, `catalog_editor.json`, default `menus.json` | `references/layout.md` |
| Adding/changing menu items, replacing `m_Quit`-style wrappers with `"action"` | `references/menus.md` |
| Version, tokens, `.gitignore` | this file |

## File Format

A `.4DProject` file is a JSON document:

```json
{
  "$comment": "The project file serves as an anchor to locate other project files",
  "compatibilityVersion": 2130,
  "tokenizedText": false
}
```

### `tokenizedText`

Set to `false` when the project is created or maintained by an agent (not
the IDE). When `false`, write **plain 4D code without token suffixes** in
all `.4dm` files. When absent, 4D defaults to the IDE's tokenized form; see
"Token Suffixes" below for what that means for code you write.

## 4D Version Detection

Read `compatibilityVersion` from `Project/{ProjectName}.4DProject`. It is a
four-character code `MMRL`:

* `MM` -- major version (`20`, `21`)
* `R` -- feature-release number, one character: `0`-`9`, then `A` = 10,
  `B` = 11, ... (`0` for an LTS line)
* `L` -- LTS minor version (`0` for a feature release)

| Value | Version |
|-------|---------|
| `2000` | 20 (LTS) |
| `2009` | 20.9 (LTS) |
| `2070` | 20 R7 |
| `20A0` | 20 R10 |
| `2101` | 21.1 (LTS) |
| `2120` | 21 R2 |
| `2130` | 21 R3 |

**Comparing versions.** Decode to the tuple `(major, R, L)` and compare
tuples; do not compare the raw value as a number (`20A0` is not numeric) or
as a string. Examples: `2009` = (20, 0, 9) < `2070` = (20, 7, 0) <
`20A0` = (20, 10, 0) < `2100` = (21, 0, 0). A 21.x LTS includes every
20 Rx feature.

Feature gates used by other skills:

| Gate | Condition |
|---|---|
| `C_*` declarations deprecated; simplified command names such as `Localized string` | >= 20 R7 (`2070`) |
| Fluent UI form theme | >= 21 R2 |
| Liquid Glass form theme | >= 21 R3 |
| Any project in `.4DProject` form | >= v17 (version checks against older releases are dead code) |

A newer 4D or `tool4d` can run a project with an older
`compatibilityVersion` (e.g. tool4d 21 R3 running a `2101` project). The
reverse also works, but the project may use commands or features that do
not exist in the older version. See `skills/4dcli/SKILL.md` for choosing a
binary.

## Token Suffixes

4D source may carry token suffixes on commands (`ALERT:Cnnn`) and constants
(`Plain form window:Knn:nn`). This is the single set of rules for them;
other skills link here rather than restating them.

* **Suffixes are optional.** A plain name works; 4D resolves it and adds the
  token on next save if the project is tokenized.
* **Never invent, guess or recall a token number.** A wrong token silently
  resolves to a *different, real* command or constant -- not to an error.
  A confidently remembered token is exactly as dangerous as a random one
  (a real incident: `Size of array:C267` was written from memory; `C267` is
  another command).
* **Mandatory grep-first check, every time:** before writing any `:CNNN` or
  `:KNN:NN`, grep the project's own source for that exact
  `Name:CNNN` / `Name:KNN:NN` string.
  * Match found → copy it character for character.
  * No match → write the plain name with no suffix.
* Verifying one command's token does not license guessing another in the
  same line or file.
* `var`, `#DECLARE`, `Function`, `Class`, `property` and other keywords
  never take tokens.
* Preserve tokens already present in code you are not otherwise changing.
  When you rewrite a statement (e.g. `C_LONGINT:Cnnn($x)` → `var $x : Integer`)
  the old token simply goes away.
* `tokenizedText: false` → write no suffixes at all.
* Do not "fix" a deprecated command by changing only its token -- see the
  `4dmodernise` skill.

To check what an unfamiliar command really is, use the `4dlang` skill
(lookup) or `hover` in the `4dlsp` skill -- never a remembered token.

## .gitignore

This is the canonical `.gitignore` for a 4D project. Add missing entries to
a repository's existing `.gitignore` without disturbing its other entries.

```gitignore
# 4D data, logs and derived files
[dD][aA][tT][aA]/
Logs/
DerivedData/
Libraries/
userPreferences.*/

# Uncomment to ignore the trash
# Project/Trash

# System files
.DS_Store
ehthumbs.db
Thumbs.db

# Tools provisioned by the 4D skills (see the 4dtools skill)
/tools/4dcatalog/
/tools/4dform/
/tools/4dlsp/
/tools/4dlang/
/tools/4dcli/
```

When the project sits in a subfolder of the repository (e.g. `demo/<Name>/`),
the unanchored patterns above still match; keep the `/tools/...` entries
anchored to the repository root, where the tools are provisioned.

Rules:

* **Ignore only the provisioned per-skill tool directories**, never the
  whole `tools/` folder: some repositories commit their own scripts under
  `tools/` (the technote-localisation template does).
* **`Documentation/` is source.** It holds developer-written `.md` files
  attached to methods, classes and forms -- track it.
* **`Settings/` is a per-repository decision.** It holds *user settings*
  (`settings.4DSettings`, `Backup.4DSettings`, `directory.json`, an optional
  `AIProviders.json`). Track it when those settings are meant to be shared
  (build, backup, users and groups); ignore it in demo/template repositories
  where they are machine-specific. If the repository has no rule yet, ask
  the user. Never commit a `Settings/AIProviders.json` (or any file) that
  contains API keys or other secrets, whichever way the folder is handled.
* A repository may add project-specific entries (build output, `.venv/`,
  ...); this list is the 4D baseline, not a ceiling.

## Modification

When working with a `.4DProject` file:

* Treat it as a 4D-specific artifact, not merely as generic JSON.
* Preserve existing structure and properties.
* Make the smallest necessary changes.
* Do not remove unknown properties or fields.
* Do not assume that valid JSON implies a valid 4DProject.
* Do not invent schema rules or project-specific properties.
