---
name: 4dproject
description: >
  Work with 4D project definition files (.4DProject), including their JSON
  structure, compatibility version, and tokenization settings.
---

# 4D Project Definition

## Scope

This skill covers the `.4DProject` file itself -- the JSON anchor file
that identifies a 4D project and its settings.

For project directory layout, boilerplate files, and methods, see the
project layout section in `AGENTS.md`.

## File Format

A `.4DProject` file is a JSON document:

```json
{
  "$comment": "The project file serves as an anchor to locate other project files",
  "compatibilityVersion": 2130,
  "tokenizedText": false
}
```

### Properties

- `compatibilityVersion`: 4D version code. `2130` = 4D 21 R3. Encoding:
  LTS = `major*100+minor` (e.g., 21.3 = 2103), Feature release =
  `major*100+R_number*10` (e.g., 21 R3 = 2130).

  | Value | Version |
  |-------|---------|
  | `2101` | 21.1 |
  | `2120` | 21 R2 |
  | `2130` | 21 R3 |
  | `2009` | 20.9 |
  | `20A0` | 20 R10 |

  A newer 4D or `tool4d` can safely run a project with an older
  `compatibilityVersion` (e.g. tool4d 21 R3 running a `2101` project).
  The reverse also works, but the project may use commands or features
  that do not exist in the older version. See `skills/4dcli/SKILL.md`
  for choosing a binary.
- `tokenizedText`: Set to `false` when the project is created/maintained
  by an agent (not the IDE). Tokens like `:C10` or `:5` are only useful
  in IDE workflows. When `false`, write **plain 4D code without token
  suffixes** in all `.4dm` files.

## Modification

When working with a `.4DProject` file:

* Treat it as a 4D-specific artifact, not merely as generic JSON.
* Preserve existing structure and properties.
* Make the smallest necessary changes.
* Do not remove unknown properties or fields.
* Do not assume that valid JSON implies a valid 4DProject.
* Do not invent schema rules or project-specific properties.
